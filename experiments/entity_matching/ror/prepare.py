"""Reproduce the offline development freeze and a non-executable live proposal."""

import argparse
import hashlib
import json
from time import perf_counter

import yaml

from eval_lab.contracts import ExperimentSpec
from eval_lab.core.budgets import preflight
from eval_lab.core.hashes import canonical, digest
from eval_lab.core.runner import validate
from eval_lab.providers.openai_adapter import request_payload
from scripts.audit_crossref_pairs import CACHE, ROR, SOURCE, read_registry
from scripts.cache_policy_proposal import request_policy_valid

from .cohort import nominate, quarantine, sources
from .core import ABSTAIN, DIR, Experiment, decision
from .report import calibrate, metrics
from .retrieval import VERSION, Registry


def load(name):
    return json.loads((DIR / name).read_text(encoding="utf8"))


def experiment(pilot=False):
    spec = ExperimentSpec.model_validate(
        yaml.safe_load((DIR / ("pilot.yaml" if pilot else "experiment.yaml")).read_text())
    )
    return Experiment(spec, DIR.parent)


def save(name, packet, check):
    if check:
        if load(name) != packet:
            raise ValueError("Frozen artifact differs: " + name)
    else:
        with (DIR / name).open("x", encoding="utf8", newline="\n") as stream:
            json.dump(packet, stream, indent=2, ensure_ascii=False)
            stream.write("\n")


def proposal():
    exp = experiment(True)
    if (
        exp.spec.conditions[0].variables["calibration"]
        != load("baseline.json")["calibration"]["thresholds"]
    ):
        raise ValueError("Frozen calibration differs from the proposal config")
    _, trials = validate(exp)
    requests = [r for *_, r in trials]
    engine_reserve = preflight(exp.spec, requests, "live", True)
    manifest = []
    pricing = exp.spec.pricing
    for case, _, _, request in trials:
        body = {
            **request_payload(request),
            "prompt_cache_options": {"mode": "implicit", "ttl": "30m"},
        }
        sha = digest(body)
        if not request_policy_valid(body, sha, pricing, text_only=True):
            raise ValueError("Cache policy")
        tokens = len(canonical(body).encode()) + 256
        usd = (
            tokens * max(pricing.cache.write_usd_per_million.values())
            + body["max_output_tokens"] * pricing.output_usd_per_million
        ) / 1e6
        manifest.append(
            dict(
                case_id=case.id,
                request=request.model_dump(),
                request_sha256=digest(request),
                body=body,
                body_sha256=sha,
                input_token_reserve=tokens,
                reserve_usd=usd,
            )
        )
    reserve = max(engine_reserve, sum(r["reserve_usd"] for r in manifest))
    if reserve > exp.spec.max_spend_usd:
        raise ValueError("Wire reserve exceeds cap")
    return dict(
        status="review_required",
        model=exp.spec.conditions[0].model,
        config_sha256=digest(exp.spec),
        dataset_sha256=digest(load("dataset.json")),
        calibration_sha256=digest(load("baseline.json")),
        retrieval_version=VERSION,
        grader_version=exp.spec.grader_version,
        pricing=pricing.model_dump(),
        request_limit=len(manifest),
        cap_usd=exp.spec.max_spend_usd,
        engine_preflight_usd=engine_reserve,
        reserve_usd=reserve,
        requests=manifest,
    )


def build(check):
    rows = sources()
    records = read_registry(CACHE / "ror.csv")
    selected = nominate(rows, records)
    review = load("review.json")
    start = perf_counter()
    registry = Registry(CACHE / "ror.csv")
    indexed = perf_counter()
    for row in selected:
        key = str(row["seq_no"])
        if key in review["excluded"]:
            status, reason = "excluded", review["excluded"][key]
        elif not row["output"]:
            status, reason = "pending_independent_nil", review["pending"][key]
        else:
            status = "source_supported"
            reason = (
                review["variant_evidence"][key]
                if row["selection_group"] == "variant"
                else "Registry field and single Crossref annotation agree."
            )
        candidates, ranks = registry.retrieve(row["query"])
        org = next(iter(row["output"]), None)
        row.update(
            review=status,
            review_reason=reason,
            candidates=candidates,
            full_registry_target_rank=ranks[org][0] if org in ranks else None,
            unrestricted_top_two=[dict(id=i, score=ranks[i][1]) for i in list(ranks)[:2]],
            target_display=records[org]["display"] if org else None,
        )
    elapsed = perf_counter() - indexed
    split = quarantine(rows, selected, records)
    save("quarantine.json", split, check)
    packet = dict(
        source_sha256=SOURCE,
        ror_csv_sha256=ROR,
        registry_version="2.6",
        crossref_record="19699937",
        retrieval=VERSION,
        active_ids=len(registry.orgs),
        split="development-only",
        independent_nil_reviews=0,
        rows=selected,
    )
    save("dataset.json", packet, check)
    save(
        "blind_review.json",
        [
            {"seq_no": r["seq_no"], "query": r["query"]}
            for r in sorted(
                selected, key=lambda r: hashlib.sha256(f"blind/{r['seq_no']}".encode()).digest()
            )
        ],
        check,
    )
    eligible = [r for r in selected if r["review"] != "excluded"]
    calibration = calibrate(eligible)
    trials = []
    for r in eligible:
        y = next(iter(r["output"]), ABSTAIN)
        pred, _ = decision(r, calibration["thresholds"])
        trials.append(
            dict(
                id=r["seq_no"],
                target=y,
                prediction=pred,
                available=y in {c["id"] for c in r["candidates"]},
                full_registry_prediction=decision(
                    {"candidates": r["unrestricted_top_two"]}, calibration["thresholds"]
                )[0],
            )
        )
    save(
        "baseline.json",
        dict(
            calibration=calibration,
            source_label_metrics=metrics(trials),
            full_registry_correct=sum(t["full_registry_prediction"] == t["target"] for t in trials),
            retrieval_misses=[
                t["id"] for t in trials if t["target"] != ABSTAIN and not t["available"]
            ],
            query_decisions=trials,
        ),
        check,
    )
    live = proposal()
    save("proposal.json", live, check)
    print(
        json.dumps(
            dict(
                nominated=len(selected),
                eligible=len(eligible),
                baseline=metrics(trials),
                thresholds=calibration["thresholds"],
                reserve=live["reserve_usd"],
                excluded_future_rows=len(split["development_only_seq_nos"]),
                indexing_ms=round((indexed - start) * 1000),
                retrieval_batch_ms=round(elapsed * 1000),
            )
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    build(parser.parse_args().check)
