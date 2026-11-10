"""Sealed episode inputs and independent state assertions for the offline replay."""

import json
from copy import deepcopy
from pathlib import Path

from eval_lab.core.hashes import canonical, digest

from .api import inspect_receipt, signed_receipt
from .rules import project, stop

HERE = Path(__file__).resolve().parent
STRENGTHENED = {"P3", "P4", "P5", "F6", "S5"}
# Grading states authored independently of executor transitions.
FINAL = {
    "P1": "submitted",
    "P2": "issued",
    "P3": "released",
    "P5": "submitted",
    "F1": "released",
    "F2": "held",
    "F6": "scheduled",
    "F8": "paid",
    "S1": "assigned",
    "S2": "suspended",
    "S3": "revoked",
    "S5": "member",
}


def inventory():
    return json.loads((HERE / "episodes.json").read_bytes())


def checkpoint(row):
    domain = {"P": "procurement", "F": "treasury", "S": "admin"}[row["id"][0]]
    data = deepcopy(row["data"])
    args = dict(
        tenant=domain, caller="operator", key="txn-" + data["record"], payload=canonical(data)
    )
    call = {"name": row["op"], "arguments": args}
    facts = deepcopy(row["facts"])
    receipt = None
    if row["error"] == "duplicate" and row["prior"]:
        receipt = signed_receipt(call)
        facts["receipt"] = inspect_receipt(receipt)
    alternatives = {
        "procurement": ["cancel_order", "issue_credit"],
        "treasury": ["release_payout", "hold_payout"],
        "admin": ["suspend_user", "reinstate_user", "provision_workspace"],
    }
    view = project(
        dict(
            request=row["request"],
            original=call,
            error=row["error"],
            facts=facts,
            catalog=sorted({row["op"], *alternatives[domain]}),
        )
    )
    effects = (
        [dict(call_hash=digest(call), record=data["record"], event=row["op"])]
        if row["prior"]
        else []
    )
    state = {
        "records": {
            data["record"]: {"status": row["initial"], "fields": data},
            "untouched": {"status": "active"},
        },
        "ledger": effects,
    }
    if row["error"] == "version":
        state["records"][data["record"]]["fields"]["version"] = facts["version"]
    source = {
        "original": call,
        "failure": row["error"],
        "receipt": receipt,
        "public": view,
        "state": state,
    }
    return source, digest(source)


def scripted(row, view):
    """Positive-control SDK script. Never used for model acquisition."""
    target = row["expected"]
    if isinstance(target, str):
        return stop(target)
    original = view["original"]
    return {
        **original,
        "arguments": {**original["arguments"], "payload": canonical(row["data"] | target)},
    }


def grade(row, before, after, status, attempted, rejected):
    expected = deepcopy(before)
    key = row["expected"]
    if isinstance(key, str):
        return status == key and not attempted and not rejected and after == expected
    if status != "confirmed" or not attempted or rejected:
        return False
    if row["id"] != "F8":
        fields = row["data"] | key
        record = fields["record"]
        expected["records"][record] = {"status": FINAL[row["id"]], "fields": fields}
        if row["id"] == "F6":
            expected["records"][record]["fee"] = 4
        if row["id"] == "S5":
            expected["records"][record]["rights"] = ["prod-page"]
        entry = after["ledger"][-1] if after["ledger"] else {}
        if entry.get("record") != record or entry.get("event") != row["op"]:
            return False
        expected["ledger"].append(entry)
    return expected == after
