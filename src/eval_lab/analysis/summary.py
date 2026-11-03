from collections import Counter
from itertools import combinations
from statistics import mean

from eval_lab.contracts import RunRecord


def _aggregate(records: list[RunRecord], planned: int) -> dict:
    correct = sum(r.status == "passed" for r in records)
    costs = [r.estimated_cost_usd for r in records if r.estimated_cost_usd is not None]
    usages = [r.response.usage for r in records if r.response.usage is not None]
    cost_complete = len(costs) == len(records)
    return {
        "planned": planned,
        "recorded": len(records),
        "unattempted": planned - len(records),
        "correct": correct,
        "end_to_end_success_rate": correct / planned if planned else None,
        "attempted_success_rate": correct / len(records) if records else None,
        "status_counts": dict(sorted(Counter(r.status for r in records).items())),
        "diagnostic_counts": dict(
            sorted(Counter(d for r in records if r.grade for d in r.grade.diagnostics).items())
        ),
        "latency_ms_mean": mean(r.response.latency_ms for r in records) if records else None,
        "known_estimated_cost_usd": sum(costs),
        "estimated_cost_usd": sum(costs) if cost_complete else None,
        "unknown_cost_records": len(records) - len(costs),
        "cost_per_correct_task_usd": sum(costs) / correct if correct and cost_complete else None,
        "usage_records": len(usages),
        "known_input_tokens": sum(u.input_tokens for u in usages) if usages else None,
        "known_output_tokens": sum(u.output_tokens for u in usages) if usages else None,
    }


def summarize(records: list[RunRecord], planned: int, planned_by_condition=None) -> dict:
    """Descriptive case-paired comparisons; repeated calls are not independent cases."""
    result = _aggregate(records, planned)
    groups = {name: [] for name in (planned_by_condition or {})}
    seen = set()
    for record in records:
        key = (
            record.dataset_id,
            record.dataset_version,
            record.case_id,
            record.condition_id,
            record.repeat,
        )
        if key in seen:
            raise ValueError("Duplicate case/condition/repeat record")
        seen.add(key)
        groups.setdefault(record.condition_id, []).append(record)
    conditions, indexed = {}, {}
    for name, rows in sorted(groups.items()):
        count = planned_by_condition[name] if planned_by_condition else len(rows)
        metrics = _aggregate(rows, count)
        cases = {}
        for row in rows:
            key = (row.dataset_id, row.dataset_version, row.case_id)
            cases.setdefault(key, {})[row.repeat] = row
        indexed[name] = cases
        metrics.update(
            {
                "unique_cases_recorded": len(cases),
                "repetitions_per_case_recorded": sorted({len(r) for r in cases.values()}),
                "accuracy": metrics["end_to_end_success_rate"],
                "denominator_basis": "planned" if planned_by_condition else "recorded_only",
            }
        )
        for status in ("task_failed", "invalid_output", "provider_error", "grader_error"):
            n = sum(r.status == status for r in rows)
            metrics[status + "_count"] = n
            metrics[status + "_rate"] = n / count if count else None
        conditions[name] = metrics
    pairs = []
    for left, right in combinations(sorted(indexed), 2):
        a, b = indexed[left], indexed[right]
        shared = set(a) & set(b)
        deltas, latency, costs, matched_ids = [], [], [], []
        for key in sorted(shared):
            # Compare only identical repetition sets, averaging within case first.
            if set(a[key]) != set(b[key]):
                continue
            ids = sorted(a[key])
            deltas.append(
                mean(
                    int(b[key][i].status == "passed") - int(a[key][i].status == "passed")
                    for i in ids
                )
            )
            latency.append(
                mean(b[key][i].response.latency_ms - a[key][i].response.latency_ms for i in ids)
            )
            if all(
                a[key][i].estimated_cost_usd is not None
                and b[key][i].estimated_cost_usd is not None
                for i in ids
            ):
                costs.append(
                    mean(b[key][i].estimated_cost_usd - a[key][i].estimated_cost_usd for i in ids)
                )
            matched_ids.append(
                {
                    "dataset_id": key[0],
                    "dataset_version": key[1],
                    "case_id": key[2],
                    "repetitions": len(ids),
                }
            )
        pairs.append(
            {
                "left": left,
                "right": right,
                "direction": "right_minus_left",
                "matched_cases": len(deltas),
                "matched_case_ids": matched_ids,
                "excluded_cases": len(set(a) | set(b)) - len(deltas),
                "accuracy_difference": mean(deltas) if deltas else None,
                "latency_ms_difference": mean(latency) if latency else None,
                "cost_usd_difference": mean(costs) if costs else None,
                "cost_paired_cases": len(costs),
            }
        )
    result.update(
        {
            "conditions": conditions,
            "paired_comparisons": pairs,
            "comparison_note": "Descriptive only; case means weight cases equally. "
            "Repetitions are not independent cases. No significance claim. "
            "Pairs exclude absent cases or unequal recorded repetition sets; "
            "partial-run comparisons may be biased.",
        }
    )
    return result
