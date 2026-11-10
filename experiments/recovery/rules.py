"""Frozen public-input recovery strategies. No simulator or grader dependency."""

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from eval_lab.core.hashes import canonical, digest

MANUAL = Path(__file__).with_name("manual.md").read_text(encoding="utf8")
STATUSES = ("confirmed", "denied", "approval", "clarify", "terminal", "unknown", "escalate")
PUBLIC_FIELDS = ("request", "original", "error", "facts", "catalog")


def project(envelope):
    """Serialize only trusted public fields, with no shared references."""
    return json.loads(canonical({field: envelope[field] for field in PUBLIC_FIELDS}))


def payload(call):
    return json.loads(call["arguments"]["payload"])


def corrected(call, field, value):
    data = payload(call)
    data[field] = value
    return {**call, "arguments": {**call["arguments"], "payload": canonical(data)}}


def stop(status):
    return {"name": "stop", "arguments": {"status": status}}


def receipt_matches(view):
    call = view["original"]
    args = call["arguments"]
    receipt = view["facts"].get("receipt", {})
    return receipt == {
        "authenticated": True,
        "status": "completed",
        "tenant": args["tenant"],
        "key": args["key"],
        "endpoint": call["name"],
        "payload_hash": digest(args["payload"]),
    }


def status(view):
    error = view["error"]
    if error == "duplicate":
        return "confirmed" if receipt_matches(view) else "unknown"
    return {
        "timeout": "unknown",
        "denied": "denied",
        "prerequisite": "approval",
        "ambiguous": "clarify",
        "terminal": "terminal",
    }.get(error, "escalate")


def may_replay(view):
    facts = view["facts"]
    return view["error"] == "busy_no_commit" or (
        view["error"] == "timeout"
        and facts.get("atomic_replay") is True
        and facts["clock"] < facts["expires"]
    )


def within_approval(facts):
    if facts.get("protected_changes"):
        return False
    if "goods" not in facts:
        return True
    charge = facts["charge"]
    refundable = facts.get("signed_rider_refundable", facts["vendor_refundable"])
    excluded = min(charge, facts["deposit_limit"]) if refundable else 0
    return facts["goods"] + charge - excluded <= facts["approval_limit"]


def rights(group, graph):
    pending, visited, grants = [group], set(), set()
    while pending:
        node = pending.pop()
        if node not in visited:
            visited.add(node)
            grants.update(graph[node]["grants"])
            pending.extend(graph[node]["parents"])
    return grants


def eligible(option, facts):
    req = facts["requirements"]
    if any(option.get(k) != v for k, v in req.get("equals", {}).items()):
        return False
    if "window" in option:
        lo, hi = option["window"]
        if not lo <= facts["clock"] < hi:
            return False
    if option.get("booking_required"):
        booking = facts.get("booking", {})
        if not (
            booking.get("confirmed")
            and booking["site"] == option["id"]
            and booking["start"] <= facts["clock"] < booking["end"]
        ):
            return False
    if "deadline_days" in req:
        settlement = option["days"] + int(facts["clock"] >= option["cutoff"])
        if settlement > req["deadline_days"] or option["fee"] > req["fee_limit"]:
            return False
    if "graph" in facts:
        grants = rights(option["id"], facts["graph"])
        if set(req["required"]) - grants or set(req["forbidden"]) & grants:
            return False
    return True


def decide(view):
    original, error, facts = view["original"], view["error"], view["facts"]
    if may_replay(view):
        return original
    if error == "version":
        if within_approval(facts):
            return corrected(original, "version", facts["version"])
        return stop("approval")
    if error == "format":
        source = payload(original)[facts["field"]]
        if "aliases" in facts:
            value = facts["aliases"].get(source)
            if value is None:
                return stop("clarify")
        else:
            try:
                converted = Decimal(str(source)) * Decimal(str(facts["multiplier"]))
                if not converted.is_finite() or converted != converted.to_integral_value():
                    return stop("escalate")
                value = int(converted)
            except InvalidOperation:
                return stop("escalate")
        return corrected(original, facts["field"], value)
    if error == "obsolete":
        matches = [o["id"] for o in facts["options"] if eligible(o, facts)]
        if len(matches) == 1:
            return corrected(original, facts["field"], matches[0])
        return stop("clarify")
    return stop(status(view))
