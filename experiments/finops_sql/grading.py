"""Private evaluation contracts. SQL is executed without returning feedback to the model."""

import json
from decimal import DecimalException
from pathlib import Path

from eval_lab.core.hashes import digest

from .audit import sandbox
from .compare import IDS, normalize
from .packages import QUESTIONS, ROOT

DIMENSIONS = {
    33: {"period", "cost_basis"},
    34: {"scope"},
    35: {"savings_basis"},
    36: {"denominator", "sku"},
}
INTEGERS = {
    "TINYINT",
    "SMALLINT",
    "INTEGER",
    "BIGINT",
    "HUGEINT",
    "UTINYINT",
    "USMALLINT",
    "UINTEGER",
    "UBIGINT",
    "UHUGEINT",
}
UNITS = {
    3: "hours",
    9: "fraction",
    10: "USD/1,000 transactions",
    12: "USD/transaction",
    14: "% variance relative to budget",
    25: "fraction",
    29: "fraction",
}


def units(number, index):
    if number == 3:
        return "hours"
    if index in IDS.get(number, ()):
        return "count" if number == 30 and index == 1 else "integer ID"
    return UNITS.get(number, "USD")


def matches(number, actual, key):
    columns = QUESTIONS[number - 1]["fields"]
    if actual.get("columns") != columns or key["columns"] != columns:
        return False
    types = actual.get("types", [])
    if len(types) != len(columns):
        return False
    for i, typ in enumerate(types):
        if typ in INTEGERS:
            continue
        if i in IDS.get(number, ()) or (
            not typ.startswith("DECIMAL(") and typ not in {"FLOAT", "DOUBLE"}
        ):
            return False
    rows = actual["rows"]
    if any(len(row) != len(columns) for row in rows):
        return False
    try:
        # Compare null positions as values; ordering is material only for ranked questions.
        return normalize(number, rows) == normalize(number, key["rows"])
    except (TypeError, ValueError, DecimalException):
        return False


def grade(number, reply, root: Path, execute=sandbox):
    result = {
        "kind": reply["kind"],
        "sql_valid": None,
        "execution_success": None,
        "business_correct": False,
    }
    if reply["kind"] == "clarify":
        if number in DIMENSIONS and set(reply["dimensions"]) == DIMENSIONS[number]:
            result.update(business_correct=None, review="masked review of clarification text")
        return result
    if reply["kind"] != "sql":
        return result
    observations = []
    for name in ("evaluation_a", "evaluation_b"):
        folder = root / name
        actual = execute(folder, {"candidate": reply["query"]})["candidate"]
        key = json.loads((folder / "checkpoint-v2.json").read_text()).get(str(number))
        if number <= 32:
            expected = json.loads((ROOT / "oracle-bindings-v2.json").read_bytes())[name][
                str(number)
            ]
            if (
                not key
                or digest({"columns": key["columns"], "rows": normalize(number, key["rows"])})
                != expected
            ):
                raise ValueError("private key does not match checkpoint")
        success = "error" not in actual
        observations.append(
            {
                "snapshot": name,
                "sql_valid": actual.get("sql_valid"),
                "executed": success,
                "reason": actual.get("error"),
                "correct": bool(success and key and matches(number, actual, key)),
            }
        )
    values = [o["sql_valid"] for o in observations]
    return dict(
        result,
        snapshots=observations,
        sql_valid=False if False in values else (True if all(values) else None),
        execution_success=all(o["executed"] for o in observations),
        business_correct=all(o["correct"] for o in observations),
    )
