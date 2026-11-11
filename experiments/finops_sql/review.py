"""Rebuild the reviewer-only sample table from verified snapshots and both oracles."""

import argparse
import json
import re
from pathlib import Path

from .checkpoint import verify_sources
from .compare import normalize
from .controls import CLARIFICATIONS
from .grading import matches, units
from .oracle import answers
from .packages import QUESTIONS


def report(root, design):
    descriptions = {
        int(i): (q, definition)
        for i, q, definition in re.findall(r"^\| (\d\d) \| ([^|]+) \| ([^|]+) \|$", design, re.M)
    }
    snapshots = []
    for name in ("evaluation_a", "evaluation_b"):
        folder = root / name
        verify_sources(folder)
        records = json.loads((folder / "checkpoint.json").read_bytes())
        python = answers(folder)
        for i, rows in python.items():
            result = records[str(i)]
            if not matches(i, result, {"columns": QUESTIONS[i - 1]["fields"], "rows": rows}):
                raise ValueError(f"{name} Q{i:02} contract or oracle discrepancy")
        snapshots.append(records)
    lines = [
        "# Meridian reviewer packet · checkpoint 2",
        (
            "Each cell gives one representative row and the total row count. Both Decimal and "
            "DuckDB calculations agreed on **every row of Q01–32 on both snapshots**, "
            "including ranked positions for Q02 and Q06. Unranked examples use reproducible "
            "sorted output. Amounts round once to cents and rates to six places. Numeric "
            "identifiers and counts are exact. NULL means an undefined or absent value "
            "wherever the business key returns NULL. Independent human adjudication is "
            "pending."
        ),
        (
            "Review Q07–09 for signed decomposition, Q10–12 for ratio denominators, "
            "Q13–16 for fiscal and invoice boundaries, Q18–19 for delivery precedence, "
            "Q20–24 for allocation and ownership, and Q25–28 for commitment cash versus "
            "expense. The approved variance_pct implementation reports percentage points. The "
            "shorthand ratio in the Q14 design table omits the ×100 shown in the accepted "
            "fiscal policy."
        ),
        (
            "| Question | Business definition | Output fields and units | Evaluation A | "
            "Evaluation B |"
        ),
        "|---|---|---|---|---|",
    ]
    for i in range(1, 33):
        q, definition = descriptions[i]
        assert QUESTIONS[i - 1]["question"] == q
        samples = []
        for records in snapshots:
            rows = normalize(i, records[str(i)]["rows"])
            sample = ", ".join(str(v) for v in rows[0]) if rows else "empty"
            samples.append(f"{sample} ({len(rows)} {'row' if len(rows) == 1 else 'rows'})")
        cols = ", ".join(f"{c} ({units(i, j)})" for j, c in enumerate(QUESTIONS[i - 1]["fields"]))
        lines.append(f"| Q{i:02} {q} | {definition} | {cols} | " + " | ".join(samples) + " |")
    lines.extend(
        [
            "",
            "## Clarification keys",
            "",
            (
                "The expected disposition is a focused clarification on both snapshots. The "
                "example results below come from two legitimate interpretations in the accepted "
                "checker. A correct dimension set still requires masked review of what the "
                "question actually asks."
            ),
            "",
            (
                "| Question | Required distinction | Evaluation A alternatives | Evaluation B "
                "alternatives |"
            ),
            "|---|---|---|---|",
        ]
    )
    for i, (dimension, _, _) in CLARIFICATIONS.items():
        alternatives = [
            f"{r[f'{i}a']['rows'][0][0]} / {r[f'{i}b']['rows'][0][0]}" for r in snapshots
        ]
        lines.append(
            f"| Q{i} {descriptions[i][0]} | {dimension} | " + " | ".join(alternatives) + " |"
        )
    return "\n\n".join(lines[:3]) + "\n\n" + "\n".join(lines[3:]) + "\n"


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    args.output.write_text(
        report(
            args.root, Path("docs/experiment05_sql_context_design.md").read_text(encoding="utf8")
        ),
        encoding="utf8",
    )
