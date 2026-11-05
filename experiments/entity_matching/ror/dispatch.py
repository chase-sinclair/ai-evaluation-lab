"""One-shot development prefix. Default command only verifies the frozen proposal."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import httpx
import openai

from eval_lab.core.hashes import canonical, digest
from eval_lab.core.result_store import read_records, write_once
from eval_lab.core.runner import run
from eval_lab.providers.openai_adapter import OpenAIProvider
from scripts.audit_crossref_pairs import ROOT
from scripts.cache_policy_proposal import assess

from .human_review import check_review
from .prepare import experiment, load, proposal
from .report import replay

RUN_ID = "crossref-development-3e-once"
ENDPOINT = "https://api.openai.com/v1/responses"
PREFIX = 4
CAP = 0.005


def revised_experiment():
    exp = experiment(True)
    price = exp.spec.pricing.model_copy(
        update={"version": "standard-2026-11-05", "verified_date": "2026-11-05"}
    )
    exp.spec = exp.spec.model_copy(
        update={"pricing": price, "max_output_tokens": 1024, "max_spend_usd": 0.05}
    )
    return exp


def freeze():
    exp = revised_experiment()
    plan = proposal(exp)
    plan.update(
        protocol="crossref-phase3e-v1",
        executable_prefix=PREFIX,
        prefix_cap_usd=CAP,
        prefix_reserve_usd=sum(r["reserve_usd"] for r in plan["requests"][:PREFIX]),
    )
    return plan


def readiness():
    plan = freeze()
    if (
        plan != load("phase3e_requests.json")
        or plan["request_limit"] != 38
        or plan["prefix_reserve_usd"] > CAP
    ):
        raise ValueError("Frozen readiness check failed")
    return plan


class GuardedTransport(httpx.BaseTransport):
    """Check the actual serialized SDK request at the last boundary before sending."""

    def __init__(self, inner, entries, path):
        self.inner, self.entries, self.path = inner, entries, path
        self.sent = 0
        self.charged = 0.0
        self.pending = None

    def handle_request(self, request):
        if self.sent >= len(self.entries) or self.pending is not None:
            raise ValueError("Attempt already made or request count exhausted")
        row = self.entries[self.sent]
        body = json.loads(request.content)
        if (
            request.method != "POST"
            or str(request.url) != ENDPOINT
            or digest(body) != row["body_sha256"]
            or self.charged + row["reserve_usd"] > CAP
        ):
            raise ValueError("Wire body, destination or budget mismatch")
        self.pending = row
        write_once(
            self.path / f"attempt-{row['case_id']}.json",
            dict(
                run_id=RUN_ID,
                body=body,
                body_sha256=digest(body),
                wire_bytes_sha256=hashlib.sha256(request.content).hexdigest(),
                reserved_usd=row["reserve_usd"],
            ),
        )
        self.sent += 1
        return self.inner.handle_request(request)

    def close(self):
        self.inner.close()


class FrozenProvider(OpenAIProvider):
    def __init__(self, client, guard):
        super().__init__(live=True, client=client)
        self.guard = guard

    def payload(self, request):
        row = self.guard.entries[self.guard.sent]
        if digest(request) != row["request_sha256"]:
            raise ValueError("Logical request mismatch")
        return row["body"]


def verdict(record, row, pricing):
    raw = record.response.raw
    report = assess(row["body"], raw, pricing, row["body_sha256"], text_only=True)
    reason = report.get("stop_reason")
    usage = raw.get("usage") or {}
    if not reason:
        counts = [usage.get(k) for k in ("input_tokens", "output_tokens", "total_tokens")]
        cache = usage.get("input_tokens_details") or {}
        details = usage.get("output_tokens_details") or {}
        if (
            any(type(n) is not int for n in counts)
            or counts[0] + counts[1] != counts[2]
            or counts[0] > row["input_token_reserve"]
            or any(type(cache.get(k)) is not int for k in ("cached_tokens", "cache_write_tokens"))
            or not 0 <= (details.get("reasoning_tokens") or 0) <= counts[1]
        ):
            reason = "inconsistent_token_accounting"
        elif (
            record.response.model != "gpt-6-luna"
            or raw.get("max_output_tokens") not in (None, 1024)
            or raw.get("store") not in (None, False)
        ):
            reason = "unexpected_returned_model_or_settings"
        elif raw.get("tools") or any(
            o.get("type") not in ("message", "reasoning") for o in raw.get("output", [])
        ):
            reason = "unexpected_output_type"
        elif any(
            c.get("type") != "output_text"
            for o in raw.get("output", [])
            if o.get("type") == "message"
            for c in o.get("content", [])
        ):
            reason = "unexpected_message_content"
        elif record.status not in ("passed", "task_failed"):
            reason = "invalid_response_or_grade"
    if reason:
        report.update(continue_eligible=False, stop_reason=reason)
        if reason in {
            "inconsistent_token_accounting",
            "unexpected_returned_model_or_settings",
            "observed_service_tier_violation",
            "observed_cache_policy_violation",
        }:
            report.update(usage_priced_estimate_usd=None, policy_estimate_usd=None)
    return report


def _dispatch(plan, review, results, *, mock_transport=None):
    """Internal acquisition. The production entry point fixes the results directory."""
    exp = revised_experiment()
    entries = plan["requests"][:PREFIX]
    cases = {c.id: c for c in exp.load_cases()}
    exp.cases = [cases[r["case_id"]] for r in entries]
    exp.spec = exp.spec.model_copy(update={"max_requests": PREFIX, "max_spend_usd": CAP})
    root = results / RUN_ID
    guard = GuardedTransport(
        mock_transport if mock_transport is not None else httpx.HTTPTransport(retries=0),
        entries,
        root,
    )
    receipts = {}

    def after(record):
        row = entries[len(receipts)]
        report = verdict(record, row, exp.spec.pricing)
        if (
            guard.pending != row
            or row["case_id"] != record.case_id
            or record.request_hash != row["request_sha256"]
        ):
            report.update(continue_eligible=False, stop_reason="attempt_record_mismatch")
        charge = report["spending_charge_usd"]
        guard.charged += charge
        if guard.charged > CAP:
            report.update(continue_eligible=False, stop_reason="cap_exceeded")
        write_once(root / f"accounting-{record.case_id}.json", report)
        receipts[record.case_id] = report
        guard.pending = None
        return charge, report.get("stop_reason")

    with httpx.Client(transport=guard, follow_redirects=False, trust_env=False) as http:

        def provider():
            write_once(
                root / "authorization.json",
                dict(
                    plan_sha256=digest(plan),
                    review_sha256=review,
                    execution="offline_sdk_simulation"
                    if mock_transport is not None
                    else "owner_approved_live",
                    max_requests=PREFIX,
                    cap_usd=CAP,
                ),
            )
            client = openai.OpenAI(
                api_key="local-test-only" if mock_transport is not None else None,
                base_url="https://api.openai.com/v1",
                http_client=http,
                max_retries=0,
                timeout=60.0,
            )
            return FrozenProvider(client, guard)

        result = run(
            exp,
            results=results,
            mode="live",
            live=True,
            run_id=RUN_ID,
            provider_factory=provider,
            trial_order=[(c.id, "acquire", 0) for c in exp.cases],
            live_record_policy=after,
        )
    records, warnings = read_records(root)
    wires = {
        r.case_id: json.loads(p.read_text(encoding="utf8"))
        for r in records
        if (p := root / f"attempt-{r.case_id}.json").exists()
    }

    def total(field):
        values = [r[field] for r in receipts.values()]
        return sum(values) if len(values) == guard.sent and None not in values else None

    summary = dict(
        attempts=guard.sent,
        run_status=result["run_status"],
        usage_based_usd=total("usage_priced_estimate_usd"),
        policy_based_usd=total("policy_estimate_usd"),
        provider_billed_usd=None,
        conservative_charge_usd=guard.charged
        + sum(
            row["reserve_usd"] for row in entries[: guard.sent] if row["case_id"] not in receipts
        ),
        warnings=warnings,
        policies=replay(
            exp,
            records,
            exp.spec.conditions[0].variables["calibration"],
            proposal=plan,
            wire_receipts=wires,
        )
        if result["run_status"] == "completed"
        else None,
    )
    write_once(root / "pilot-report.json", summary)
    return summary


def execute(approval, worksheet, *, test_transport=None, test_results=None):
    plan = readiness()
    if approval != digest(plan) or not worksheet:
        raise ValueError("Explicit approval of this exact plan and a completed worksheet required")
    review = check_review(worksheet)
    if test_transport is not None:
        if not isinstance(test_transport, httpx.MockTransport) or test_results is None:
            raise ValueError("Expected an offline SDK mock")
        return _dispatch(plan, review, test_results, mock_transport=test_transport)
    shared = Path(
        subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            text=True,
        ).strip()
    )
    write_once(shared / (RUN_ID + ".json"), dict(plan_sha256=approval, review_sha256=review))
    return _dispatch(plan, review, ROOT / "results")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--approve-plan")
    parser.add_argument("--review", type=Path)
    args = parser.parse_args()
    plan = readiness()
    if not args.live:
        print(
            canonical(
                dict(
                    plan_sha256=digest(plan),
                    requests=PREFIX,
                    prefix_reserve=plan["prefix_reserve_usd"],
                    full_reserve=plan["reserve_usd"],
                    provider_calls=0,
                )
            )
        )
        return
    result = execute(args.approve_plan, args.review)
    print(canonical({k: v for k, v in result.items() if k != "policies"}))
    if result["run_status"] != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
