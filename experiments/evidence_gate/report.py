"""Create a blinded review packet or summarize completed reviewer judgments."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Literal

from pydantic import StrictBool

from eval_lab.contracts import Contract
from eval_lab.core.hashes import digest
from eval_lab.core.result_store import read_records, write_once

from .experiment import REFERRAL
from .plan import verify


class Claim(Contract):
    span: str
    support: Literal["supported", "unsupported", "contradicted"]
    evidence: str
    citations: dict[str, StrictBool]


class Judgment(Contract):
    claims: list[Claim]
    useful_correct: StrictBool
    appropriate_abstention: StrictBool
    over_refusal: StrictBool
    partial_handling: Literal["complete", "incomplete", "not_applicable"]
    clarification: Literal["focused", "conditional", "missed", "not_applicable"]
    reviewer: str
    rationale: str


def total(rows, field):
    values = [getattr(r, field) for r in rows]
    return None if None in values else sum(values)


def replay(records, cases):
    index = {(r.case_id, r.condition_id): r for r in records}
    if len(index) != len(records):
        raise ValueError("Duplicate stage receipt")
    worksheet = {}
    pairs = []
    gate_counts = Counter()
    for c in cases:
        gen = index.get((c.id, "generator"))
        gate = index.get((c.id, "gate"))
        if (
            not gen
            or not gate
            or any(r.status not in ("passed", "task_failed") for r in (gen, gate))
        ):
            continue
        verdict = gate.response.parsed
        if verdict not in ("PASS", "BLOCK"):
            continue
        standard = gen.response.parsed
        gated = standard if verdict == "PASS" else REFERRAL
        ids = []
        for answer in (standard, gated):
            key = digest([c.id, answer])
            ids.append(key)
            offered = {p["id"] for p in c.task_input["excerpts"]}
            worksheet[key] = dict(
                **c.task_input,
                answer=answer,
                rubric=c.ground_truth["key"],
                outside_packet_ids=sorted(set(re.findall(r"\[(D\d+)\]", answer)) - offered),
                judgment=dict.fromkeys(Judgment.model_fields),
            )
        stages = [gate, gen] if verdict == "PASS" else [gate]
        gate_counts[f"{c.ground_truth['expected_gate']}/{verdict}"] += 1
        pairs.append(
            dict(
                question=c.id,
                gap=c.ground_truth["gap"],
                verdict=verdict,
                standard=ids[0],
                gated=ids[1],
                standard_usd=gen.estimated_cost_usd,
                gated_usd=total(stages, "estimated_cost_usd"),
                standard_ms=gen.response.latency_ms,
                modeled_serial_ms=sum(r.response.latency_ms for r in stages),
            )
        )
    return pairs, dict(sorted(worksheet.items())), gate_counts


def outcomes(pairs, reviews):
    metrics = {arm: Counter() for arm in ("standard", "gated")}
    changes = Counter(
        dict(
            unsupported_prevented=0,
            unsupported_introduced=0,
            lost_useful_A=0,
            lost_useful_P=0,
            lost_clarifications=0,
            already_abstained_blocks=0,
        )
    )
    for pair in pairs:
        family = pair["question"][0]
        a, b = (reviews[pair[arm]] for arm in ("standard", "gated"))
        unsupported = []
        for arm, j in zip(metrics, (a, b), strict=True):
            m = metrics[arm]
            bad = any(c.support != "supported" for c in j.claims)
            unsupported.append(bad)
            m["questions"] += 1
            m["unsupported_answers"] += bad
            m[f"{family}_useful_correct"] += j.useful_correct
            m[f"{family}_over_refusal"] += j.over_refusal
            m[f"{family}_appropriate_abstention"] += j.appropriate_abstention
            m[f"partial_{j.partial_handling}"] += 1
            m[f"clarification_{j.clarification}"] += 1
            for claim in j.claims:
                m["claims"] += 1
                m["supported_claims"] += claim.support == "supported"
                m["supported_claims_with_entailing_citation"] += (
                    claim.support == "supported" and any(claim.citations.values())
                )
                m["claims_with_entailing_citation"] += any(claim.citations.values())
                m["citation_links"] += len(claim.citations)
                m["correct_links"] += sum(claim.citations.values())
        changes["unsupported_prevented"] += unsupported == [True, False]
        changes["unsupported_introduced"] += unsupported == [False, True]
        if family in ("A", "P"):
            changes[f"lost_useful_{family}"] += a.useful_correct and not b.useful_correct
        if family == "M":
            good = ("focused", "conditional")
            changes["lost_clarifications"] += (
                a.clarification in good and b.clarification not in good
            )
        changes["already_abstained_blocks"] += (
            a.appropriate_abstention and pair["verdict"] == "BLOCK"
        )
    return dict(arms=metrics, paired=changes)


def report(path, worksheet_path, reviewed=False):
    exp, plan = verify()
    records, warnings = read_records(path)
    for r, row in zip(records, plan["rows"], strict=False):
        if (r.case_id, r.condition_id, r.request_hash, digest(r.request)) != (
            row["case"],
            row["stage"],
            row["request_hash"],
            row["request_hash"],
        ):
            raise ValueError("Receipt differs from approved order or request")
    if len(records) > 48:
        raise ValueError("Too many receipts")
    pairs, sheet, gates = replay(records, exp.load_cases())
    result = dict(
        planned_pairs=24,
        evaluable_pairs=len(pairs),
        attempted=len(records),
        warnings=warnings,
        statuses=Counter(r.status for r in records),
        gate_expected_observed=gates,
        pairs=pairs,
        study_usage_usd=total(records, "estimated_cost_usd"),
        tokens_by_stage={},
    )
    for stage in ("generator", "gate"):
        usage = [r.response.usage for r in records if r.condition_id == stage]
        result["tokens_by_stage"][stage] = {
            k: sum(getattr(u, k) for u in usage) if usage and all(usage) else None
            for k in ("input_tokens", "output_tokens")
        }
    if pairs:
        result["median_modeled_serial_ms"] = median(p["modeled_serial_ms"] for p in pairs)
        result["median_standard_ms"] = median(p["standard_ms"] for p in pairs)
        result["median_added_ms"] = median(p["modeled_serial_ms"] - p["standard_ms"] for p in pairs)
        result["additional_estimated_usd"] = (
            sum(p["gated_usd"] - p["standard_usd"] for p in pairs)
            if all(p["gated_usd"] is not None and p["standard_usd"] is not None for p in pairs)
            else None
        )
    if reviewed:
        submitted = json.loads(worksheet_path.read_bytes())
        judgments = {}
        if submitted.keys() != sheet.keys():
            raise ValueError("Review set mismatch")
        for key, entry in submitted.items():
            judgments[key] = Judgment.model_validate(entry.pop("judgment"))
            if entry != {k: v for k, v in sheet[key].items() if k != "judgment"}:
                raise ValueError("Review text changed")
        result.update(outcomes(pairs, judgments))
    else:
        write_once(worksheet_path, sheet)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("worksheet", type=Path)
    parser.add_argument("--reviewed", action="store_true")
    args = parser.parse_args()
    print(json.dumps(report(args.run, args.worksheet, args.reviewed), indent=2))
