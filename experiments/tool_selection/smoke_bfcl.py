"""Six frozen requests through the shared runner. Default is offline preflight only."""

import argparse
import json

import yaml

from eval_lab.contracts import ExperimentSpec, Pricing
from eval_lab.core.hashes import digest
from eval_lab.core.runner import run, validate
from eval_lab.providers.openai_adapter import OpenAIProvider, request_payload

from .experiment import Experiment
from .prepare_bfcl import DIRECTORY, FROZEN_DIGEST, SMOKE_CASES, load_experiment, verify_frozen

CONFIG = DIRECTORY / "bfcl_smoke.yaml"
RESULTS = DIRECTORY.parents[1] / "results"
RUN_ID = "bfcl-smoke-v1"  # Fixed identity: no implicit retry/resume or second six-call batch.
VERIFIED_DATE = "2026-11-04"


class SmokeExperiment(Experiment):
    """A bounded view of the existing dataset and experiment, not a new study."""

    def __init__(self):
        frozen = verify_frozen()
        reference = load_experiment()
        spec = ExperimentSpec.model_validate(yaml.safe_load(CONFIG.read_text(encoding="utf-8")))
        expected = reference.spec.model_copy(
            update={
                "conditions": [c for c in reference.spec.conditions if c.id != "tools_15"],
                "max_requests": 6,
                "max_spend_usd": 0.05,
                "pricing": Pricing(
                    version="openai-standard-2026-11-04",
                    verified_date=VERIFIED_DATE,
                    source_url="https://developers.openai.com/api/docs/models/gpt-6-luna",
                    model="gpt-6-luna",
                    input_usd_per_million=0.10,
                    output_usd_per_million=0.50,
                ),
            }
        )
        if spec != expected:
            raise ValueError("Smoke configuration differs from audited six-request protocol")
        super().__init__(spec, DIRECTORY)
        self.audited_config_hash = digest(spec)
        self.rows = [row for row in frozen["requests"] if row["smoke_proposal"]]
        self.trial_order = [(r["case_id"], r["condition_id"], r["repeat"]) for r in self.rows]
        self.expected_cases = [c for c in reference.load_cases() if c.id in SMOKE_CASES]

    def load_cases(self):
        return [c for c in super().load_cases() if c.id in SMOKE_CASES]

    def validate(self, cases):
        if digest(self.spec) != self.audited_config_hash:
            raise ValueError("Smoke configuration changed after audit")
        if cases != self.expected_cases:
            raise ValueError("Smoke cases differ from frozen development cases")

    def build_request(self, case, condition):
        request = super().build_request(case, condition)
        frozen = next(
            r for r in self.rows if r["case_id"] == case.id and r["condition_id"] == condition.id
        )
        if digest(request) != frozen["request_hash"] or request.model_dump() != frozen["request"]:
            raise ValueError("Smoke request differs from frozen payload/hash")
        return request


def preflight_report(experiment: SmokeExperiment) -> dict:
    # live=True here acknowledges the live pricing mode, but dry_run guarantees no provider.
    report = run(
        experiment,
        results=RESULTS,
        mode="live",
        live=True,
        dry_run=True,
        trial_order=experiment.trial_order,
    )
    _, trials = validate(experiment)
    requests = {(c.id, condition.id, repeat): request for c, condition, repeat, request in trials}
    report.update(
        {
            "owner_approval_required": True,
            "pricing_verified_date": VERIFIED_DATE,
            "frozen_development_manifest_digest": FROZEN_DIGEST,
            "execution_config_hash": digest(experiment.spec),
            "grader_version": experiment.spec.grader_version,
            "max_spend_usd": experiment.spec.max_spend_usd,
            "cache_write_conservative_cost_usd": (
                report["estimated_input_tokens"] * 0.125 + report["output_token_ceiling"] * 0.50
            )
            / 1_000_000,
            "requests": [
                {
                    "case_id": key[0],
                    "condition_id": key[1],
                    "repeat": key[2],
                    "request_hash": digest(requests[key]),
                    "responses_body_hash": digest(request_payload(requests[key])),
                }
                for key in experiment.trial_order
            ],
        }
    )
    return report


def live_provider() -> OpenAIProvider:
    from openai import OpenAI

    # Don't allow environment base-URL routing to silently change the approved endpoint.
    client = OpenAI(base_url="https://api.openai.com/v1", max_retries=0, timeout=60.0)
    return OpenAIProvider(live=True, client=client)


def verify_readiness(report: dict) -> None:
    audited = json.loads((DIRECTORY / "bfcl/smoke_readiness.json").read_text(encoding="utf-8"))
    if report != audited:
        raise ValueError("Smoke readiness changed; audit before execution")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--preflight", action="store_true", help="Offline (also the default)")
    group.add_argument("--live", action="store_true", help="Only after explicit owner approval")
    args = parser.parse_args()
    experiment = SmokeExperiment()
    report = preflight_report(experiment)
    verify_readiness(report)
    if args.live:
        report = run(
            experiment,
            results=RESULTS,
            mode="live",
            live=True,
            run_id=RUN_ID,
            provider_factory=live_provider,
            trial_order=experiment.trial_order,
        )
    print(json.dumps(report, indent=2))
    if args.live and report["run_status"] != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
