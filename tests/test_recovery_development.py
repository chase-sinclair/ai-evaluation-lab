"""Eight rule-development episodes; never import the evaluation inventory."""

import sys
from pathlib import Path

import pytest

from eval_lab.core.hashes import canonical, digest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments.recovery.rules import decide, payload, project, stop  # noqa: E402


def episode(error, data=None, **facts):
    return project(
        dict(
            request="Service desk development ticket",
            error=error,
            facts=facts,
            catalog=["update"],
            original={
                "name": "update",
                "arguments": {
                    "tenant": "sandbox",
                    "caller": "desk",
                    "key": "dev",
                    "payload": canonical(data or {"record": "journal"}),
                },
            },
        )
    )


@pytest.mark.parametrize(
    ("value", "factor", "expected"), [("2", 6, 12), ("0.5", 8, 4), ("0.1", 3, None)]
)
def test_d1_units(value, factor, expected):
    view = episode("format", {"packs": value}, field="packs", multiplier=factor)
    answer = decide(view)
    assert answer == stop("escalate") if expected is None else payload(answer)["packs"] == expected
    view["facts"] = {"field": "packs", "aliases": {value: "carton"}}
    assert payload(decide(view))["packs"] == "carton"


@pytest.mark.parametrize("fee,allowed", [(30, True), (51, False)])
def test_d2_quote(fee, allowed):
    v = episode(
        "version",
        {"version": 2},
        version=3,
        goods=490,
        charge=fee,
        deposit_limit=40,
        approval_limit=500,
        vendor_refundable=True,
    )
    assert (decide(v)["name"] == "update") == allowed


@pytest.mark.parametrize("override", [True, False])
def test_d3_terms(override):
    v = episode(
        "version",
        {"version": 2},
        version=3,
        goods=490,
        charge=30,
        deposit_limit=40,
        approval_limit=500,
        vendor_refundable=not override,
        signed_rider_refundable=override,
    )
    assert (decide(v)["name"] == "update") == override
    v["facts"]["protected_changes"] = ["owner"]
    assert decide(v) == stop("approval")


@pytest.mark.parametrize("minute,success", [(20, True), (30, False), (40, False)])
def test_d4_dispatch(minute, success):
    v = episode(
        "obsolete",
        {"slot": "old"},
        field="slot",
        clock=minute,
        booking={"site": "east", "confirmed": True, "start": 20, "end": 40},
        requirements={"equals": {"zone": "local"}, "deadline_days": 0, "fee_limit": 5},
        options=[
            {
                "id": "east",
                "zone": "local",
                "window": [10, 40],
                "booking_required": True,
                "days": 0,
                "cutoff": 30,
                "fee": 5,
            }
        ],
    )
    assert (decide(v)["name"] == "update") == success


@pytest.mark.parametrize("parent", ["reports", "admin"])
def test_d5_inheritance(parent):
    v = episode(
        "obsolete",
        {"group": "old"},
        field="group",
        options=[{"id": "analysts"}],
        graph={
            "analysts": {"parents": [parent], "grants": []},
            parent: {"parents": [], "grants": [parent]},
        },
        requirements={"required": ["reports"], "forbidden": ["admin"]},
    )
    assert (decide(v)["name"] == "update") == (parent == "reports")


@pytest.mark.parametrize(
    "bad", [None, "tenant", "endpoint", "key", "payload_hash", "status", "authenticated"]
)
def test_d6_duplicate(bad):
    v = episode("duplicate")
    assert decide(v) == stop("unknown")
    r = dict(
        tenant="sandbox",
        endpoint="update",
        key="dev",
        status="completed",
        authenticated=True,
        payload_hash=digest(v["original"]["arguments"]["payload"]),
    )
    if bad:
        r[bad] = "invalid"
    v["facts"]["receipt"] = r
    assert decide(v) == stop("unknown" if bad else "confirmed")


@pytest.mark.parametrize("clock,permitted", [(9, True), (10, False)])
def test_d7_journal(clock, permitted):
    v = episode("timeout", atomic_replay=True, clock=clock, expires=10)
    assert decide(v) == (v["original"] if permitted else stop("unknown"))
    v["error"] = "busy_no_commit"
    assert decide(v) == v["original"]


@pytest.mark.parametrize(
    "code,reason",
    [
        ("denied", "denied"),
        ("prerequisite", "approval"),
        ("terminal", "terminal"),
        ("ambiguous", "clarify"),
    ],
)
def test_d8_entitlement(code, reason):
    v = episode(code)
    assert decide(v) == stop(reason)
