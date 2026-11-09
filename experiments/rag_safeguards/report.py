"""Paired customer outcomes and masked human review. No provider calls."""

import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from statistics import median
from typing import Literal

from pydantic import Field, StrictBool

from eval_lab.contracts import Contract
from eval_lab.core.hashes import digest
from eval_lab.core.result_store import read_records, write_once

from .stages import RESULTS, build, ledger, manifest_path, run_dir, verified_first


class Claim(Contract):
    span: str
    supported: StrictBool
    citation_links: dict[str, StrictBool]
    authority_correct: StrictBool | None
    evidence: str


class Review(Contract):
    reviewer: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    claims: list[Claim]
    correct: StrictBool
    behavior: Literal[
        "useful_answer", "useful_partial", "clarification", "appropriate_abstention", "other"
    ]


def acquisition(root):
    exp, first = verified_first(root)
    valid = {}
    stats = {}
    for stage in (1, 2):
        path = run_dir(root, stage)
        if not path.exists():
            continue
        plan = first if stage == 1 else build(2, root)[1]
        if plan != json.loads(manifest_path(root, stage).read_bytes()):
            raise ValueError("Approval manifest differs")
        records, warnings = read_records(path)
        if warnings or len(records) > len(plan["rows"]):
            raise ValueError("Corrupt receipts")
        seal = path / "seal.json"
        if seal.exists() and json.loads(seal.read_bytes()) != {
            "approval": digest(plan),
            "records_sha256": ledger(path),
        }:
            raise ValueError("Changed receipts")
        status = json.loads((path / "manifest.json").read_bytes())["status"]
        if status == "completed" and (not seal.exists() or len(records) != len(plan["rows"])):
            raise ValueError("Incomplete sealed acquisition")
        for n, (r, row) in enumerate(zip(records, plan["rows"], strict=False)):
            if (r.case_id, r.condition_id, r.request_hash, digest(r.request)) != (
                row["case"],
                row["stage"],
                row["request_hash"],
                row["request_hash"],
            ):
                raise ValueError("Receipt mismatch")
            if r.status == "passed" and not (
                status in ("failed", "interrupted") and n == len(records) - 1
            ):
                valid[r.case_id, r.condition_id] = r
        for name in {r["stage"] for r in plan["rows"]}:
            rows = [r for r in records if r.condition_id == name]
            stats[name] = dict(
                planned=36,
                attempted=len(rows),
                valid=sum(s == name for _, s in valid),
                estimated_usd=sum(r.estimated_cost_usd for r in rows)
                if all(r.estimated_cost_usd is not None for r in rows)
                else None,
                median_observed_ms=median(r.response.latency_ms for r in rows) if rows else None,
                input_tokens=sum(r.response.usage.input_tokens for r in rows)
                if all(r.response.usage for r in rows)
                else None,
                output_tokens=sum(r.response.usage.output_tokens for r in rows)
                if all(r.response.usage for r in rows)
                else None,
            )
    return exp, valid, stats


def paired(left, right):
    a, b = left, right
    x = Counter(c.span for c in a.claims if not c.supported)
    y = Counter(c.span for c in b.claims if not c.supported)
    return dict(
        unsupported_answers_prevented=int(bool(x) and not y),
        unsupported_claims_prevented=(x - y).total(),
        unsupported_claims_retained=(x & y).total(),
        unsupported_claims_introduced=(y - x).total(),
        correct_preserved=int(a.correct and b.correct),
        correct_lost=int(a.correct and not b.correct),
        useful_partial_preserved=int(a.behavior == b.behavior == "useful_partial"),
        useful_partial_lost=int(a.behavior == "useful_partial" and b.behavior != "useful_partial"),
        clarifications_lost=int(a.behavior == "clarification" and b.behavior != "clarification"),
    )


def report(root, sheet_path, reviewed=False):
    exp, valid, stats = acquisition(root)
    sheet = {}
    outcomes = []
    for case in exp.load_cases():
        gen = valid.get((case.id, "generator"))
        row = dict(case=case.id, group=case.split, arms={})
        for arm, stage in (("A", "generator"), ("B", "gate"), ("C", "verifier")):
            r = valid.get((case.id, stage))
            if not r:
                continue
            blocked = arm != "A" and r.response.parsed == "BLOCK"
            if not gen and (arm != "B" or not blocked):
                continue
            text = exp.protocol["referral"] if blocked else gen.response.parsed
            stages = [r]
            if arm == "C" or (arm == "B" and not blocked):
                stages.append(gen)
            key = digest([case.id, text])
            sheet[key] = dict(
                **case.task_input,
                key=case.ground_truth["key"],
                reply=text,
                review=dict.fromkeys(Review.model_fields),
            )
            row["arms"][arm] = dict(
                review_id=key,
                blocked=blocked,
                usd=sum(s.estimated_cost_usd for s in stages),
                serial_ms=sum(s.response.latency_ms for s in stages),
            )
        outcomes.append(row)
    reviews = {}
    if reviewed:
        submitted = json.loads(sheet_path.read_bytes())
        if submitted.keys() != sheet.keys():
            raise ValueError("Incomplete review set")
        for key, entry in submitted.items():
            reviews[key] = Review.model_validate(entry.pop("review"))
            if {**entry, "review": sheet[key]["review"]} != sheet[key] or any(
                c.span not in entry["reply"] for c in reviews[key].claims
            ):
                raise ValueError("Review content mismatch")
    else:
        write_once(sheet_path, dict(sorted(sheet.items())))
    comparisons = {}
    arms = {}
    for group in ("all", "R", "I", "C"):
        subset = [q for q in outcomes if group in ("all", q["group"])]
        for arm in "ABC":
            cells = [q["arms"][arm] for q in subset if arm in q["arms"]]
            metrics = dict(
                planned=len(subset),
                evaluable=len(cells),
                unavailable=len(subset) - len(cells),
                modeled_usd=sum(c["usd"] for c in cells),
                median_modeled_serial_ms=median(c["serial_ms"] for c in cells) if cells else None,
            )
            if reviewed:
                claims = [claim for c in cells for claim in reviews[c["review_id"]].claims]
                links = [v for claim in claims for v in claim.citation_links.values()]
                authority = [
                    claim.authority_correct
                    for claim in claims
                    if claim.authority_correct is not None
                ]
                metrics.update(
                    correct_answers=sum(reviews[c["review_id"]].correct for c in cells),
                    unsupported_claims=sum(not claim.supported for claim in claims),
                    correct_links=sum(links),
                    links=len(links),
                    correct_authority=sum(authority),
                    authority_assessments=len(authority),
                    claims_without_citations=sum(not c.citation_links for c in claims),
                )
            arms[group, arm] = metrics
        for a, b in combinations("ABC", 2):
            totals = Counter()
            changes = []
            for q in subset:
                if a not in q["arms"] or b not in q["arms"]:
                    continue
                lft, rgt = (q["arms"][k] for k in (a, b))
                totals["paired"] += 1
                totals["incremental_modeled_usd"] += rgt["usd"] - lft["usd"]
                totals["incremental_modeled_ms"] += rgt["serial_ms"] - lft["serial_ms"]
                changed = lft["review_id"] != rgt["review_id"]
                detail = {}
                if reviewed:
                    x, y = (reviews[c["review_id"]] for c in (lft, rgt))
                    detail = paired(x, y)
                    detail["redundant_block"] = int(
                        rgt["blocked"]
                        and not lft["blocked"]
                        and x.behavior == "appropriate_abstention"
                    )
                    totals.update(detail)
                if changed:
                    changes.append(dict(case=q["case"], **detail))
            comparisons[f"{group}/{a}-{b}"] = dict(
                planned=len(subset), counts=totals, changed=changes
            )
    return dict(
        acquisition=stats,
        outcomes=outcomes,
        architectures={"/".join(k): v for k, v in arms.items()},
        comparisons=comparisons,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--reviewed", action="store_true")
    args = parser.parse_args()
    print(json.dumps(report(RESULTS, args.sheet, args.reviewed), indent=2))
