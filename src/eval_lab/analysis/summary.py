from collections import Counter
from statistics import mean

from eval_lab.contracts import RunRecord


def summarize(records: list[RunRecord], planned: int) -> dict:
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
