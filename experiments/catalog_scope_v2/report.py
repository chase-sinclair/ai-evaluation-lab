"""Read immutable V2 run records. Keep coverage, controls and primary results separate."""

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import median

from eval_lab.analysis.summary import summarize
from eval_lab.core.result_store import read_records


def report(path):
    plan = json.loads((path / "plan.json").read_bytes())
    if plan["manifest"]["experiment"]["id"] != "catalog_scope_v2":
        raise ValueError("Expected a V2 run")
    records, warnings = read_records(path)
    index = {(r.case_id, r.condition_id): r for r in records}
    groups = {}
    for cohort in ("control", "primary", "capability"):
        cases = {t["case"]["id"]: t["case"] for t in plan["trials"] if t["case"]["split"] == cohort}
        group = {
            "scenario_count": len(cases),
            "catalogs": {},
            "scenarios": {},
            "paired_changes": {},
        }
        groups[cohort] = group
        for n in (5, 10, 20):
            layouts = {}
            rows = []
            disagreements = 0
            for layout in "AB":
                cond = f"tools_{n:02}_{layout}"
                subset = []
                for cid in cases:
                    row = index.get((cid, cond))
                    cell = group["scenarios"].setdefault(cid, {}).setdefault(n, {})
                    cell[layout] = row.status if row else "unattempted"
                    if row:
                        subset.append(row)
                rows.extend(subset)
                layouts[layout] = summarize(subset, len(cases))["end_to_end_success_rate"]
            for cells in group["scenarios"].values():
                a, b = cells[n].values()
                disagreements += "unattempted" not in (a, b) and (
                    (a == "passed") != (b == "passed")
                )
            totals = summarize(rows, len(cases) * 2)
            for key in ("paired_comparisons", "conditions", "comparison_note"):
                totals.pop(key, None)
            totals.update(
                layout_accuracy=layouts,
                layout_success_disagreements=disagreements,
                median_latency_ms=median(r.response.latency_ms for r in rows) if rows else None,
            )
            if cohort == "capability":
                group.setdefault("coverage_by_scenario", {})
                offered = {
                    t["name"]
                    for t in next(
                        trial
                        for trial in plan["trials"]
                        if trial["condition_id"] == f"tools_{n:02}_A"
                    )["request"]["tools"]
                }
                eligible = {
                    cid
                    for cid, c in cases.items()
                    if c["ground_truth"]["tool_calls"][0]["name"] in offered
                }
                coverage = Counter()
                for cid in cases:
                    cell = group["coverage_by_scenario"].setdefault(cid, {}).setdefault(n, {})
                    for layout in "AB":
                        r = index.get((cid, f"tools_{n:02}_{layout}"))
                        if r is None:
                            outcome = "unattempted"
                        elif cid in eligible:
                            outcome = "fulfilled" if r.status == "passed" else "supported_failed"
                        elif r.status == "passed":
                            outcome = "safe_abstention"
                        elif r.grade and r.grade.submetrics.get("unsafe_substitution"):
                            outcome = "unsafe_substitution"
                        else:
                            outcome = "unsupported_other_failure"
                        cell[layout] = outcome
                        coverage[outcome] += 1
                totals["coverage"] = {
                    "supported_planned": 2 * len(eligible),
                    "unsupported_planned": 2 * (len(cases) - len(eligible)),
                    "outcomes": dict(coverage),
                }
            group["catalogs"][n] = totals
        for n in (10, 20):
            changes = Counter()
            for cells in group["scenarios"].values():
                for layout in "AB":
                    a, b = cells[5][layout], cells[n][layout]
                    if "unattempted" in (a, b):
                        changes["unpaired"] += 1
                    elif (a == "passed") == (b == "passed"):
                        changes["unchanged"] += 1
                    else:
                        changes["gain" if b == "passed" else "regression"] += 1
            group["paired_changes"][f"5_to_{n}"] = dict(changes)
    return {"mode": plan["manifest"]["mode"], "warnings": warnings, "cohorts": groups}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    print(json.dumps(report(parser.parse_args().run), indent=2))
