"""Offline tests for Experiment 006. No provider request leaves the process."""

import hashlib
import json
from collections import Counter
from decimal import Decimal

import httpx
import openai
import pytest

from experiments.finops_sql.references import QUERIES
from experiments.model_context import analysis
from experiments.model_context.accounting import charge, served_as
from experiments.model_context.proposal import CAP, CELLS, MODELS, cell_id, parent_bodies
from experiments.model_context.replay import replay
from scripts import acquire_model_context as run


@pytest.fixture(scope="module")
def frozen():
    return run.preflight(run.APPROVAL)


@pytest.fixture(autouse=True)
def reuse_frozen_build(monkeypatch, frozen):
    monkeypatch.setattr(run, "build", lambda: frozen)


def test_frozen_inventory_and_bodies(frozen):
    plan, bodies = frozen
    rows = plan["requests"]
    assert len(rows) == len(bodies) == plan["request_ceiling"] == 432
    assert Counter(r["draw"] for r in rows) == {1: 144, 2: 144, 3: 144}
    # Draw-major order: a guard stop leaves complete earlier draws.
    assert [r["draw"] for r in rows] == sorted(r["draw"] for r in rows)
    assert len({r["id"] for r in rows}) == 432
    assert Counter((r["model"], r["arm"]) for r in rows) == {c: 108 for c in CELLS}
    parents = parent_bodies()
    for row, body in zip(rows, bodies, strict=True):
        parent = parents[(row["question"], row["arm"])]
        assert body["model"] == MODELS[row["model"]]
        # Luna is byte-identical to Experiment 005; Sol differs only in the model.
        assert body == parent | {"model": body["model"]}
        if row["model"] == "luna":
            assert body == parent
        assert run.digest(body) == row["body_hash"]
        assert len(run.canonical(body).encode()) + 256 == row["input_bound"]
        assert body["max_output_tokens"] == 25000
        assert body["reasoning"] == {"effort": "medium"}


def test_reserve_and_cap(frozen):
    plan, _ = frozen
    worst = sum(Decimal(r["worst_case_usd"]) for r in plan["requests"])
    assert Decimal(plan["worst_case_reserve_usd"]) == worst
    assert Decimal("60") < worst < Decimal("65")
    assert Decimal(plan["proposed_cap_usd"]) == CAP == Decimal("15.00")


def usage(i=120, o=15, read=10, write=5):
    return dict(
        input_tokens=i,
        output_tokens=o,
        total_tokens=i + o,
        input_tokens_details=dict(
            cached_tokens=read,
            cache_write_tokens=write,
            cache_write_tokens_details={"ttl_30m_tokens": write, "ttl_12h_tokens": 0},
        ),
        output_tokens_details=dict(reasoning_tokens=2),
    )


def test_charge_prices_each_model():
    luna = dict(model="gpt-6-luna", service_tier="default", usage=usage())
    sol = dict(model="gpt-6.1-sol-2026-10-01", service_tier="default", usage=usage())
    assert charge(luna, "gpt-6-luna", 1000) == Decimal("0.000018725")
    assert charge(sol, "gpt-6.1-sol", 1000) == Decimal("0.0003735")
    assert served_as("gpt-6.1-sol", "gpt-6.1-sol")
    for wrong in ("gpt-6.1-sol-pro", "gpt-6.1-sol-2026-10", "gpt-6-luna", None):
        assert not served_as(wrong, "gpt-6.1-sol")
    with pytest.raises(ValueError):
        charge(luna, "gpt-6.1-sol", 1000)
    with pytest.raises(ValueError):
        charge(luna | {"reasoning": {"effort": "high"}}, "gpt-6-luna", 1000)
    with pytest.raises(ValueError):
        charge(luna, "gpt-6-luna", 100)


def answer_for(question):
    if question == "Q01":
        return {"kind": "sql", "query": QUERIES[1]}
    if question == "Q34":
        return {"kind": "clarify", "dimensions": ["scope"], "question": "Which cost centers?"}
    return {"kind": "clarify", "dimensions": ["period"], "question": "Which period?"}


FAULTS = ["none", "exhaust", "guard", "http", "model", "duplicate", "tier", "timeout", "status"]


@pytest.mark.parametrize("fault", FAULTS)
def test_acquisition(tmp_path, frozen, fault):
    plan, bodies = frozen
    dest = tmp_path / "once"
    n = 0

    def handler(request):
        nonlocal n
        n += 1
        assert request.extensions["timeout"]["read"] == 900
        assert (dest / f"{n:03}.request-body").read_bytes() == request.content
        actual = json.loads(request.content)
        assert actual == bodies[n - 1]
        row = plan["requests"][n - 1]
        served = actual["model"] + ("-2026-10-01" if row["model"] == "sol" else "")
        raw = dict(
            id=f"resp_{n}",
            status="completed",
            model=served,
            service_tier="default",
            usage=usage(),
            output=[
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {"type": "output_text", "text": run.canonical(answer_for(row["question"]))}
                    ],
                }
            ],
        )
        if fault == "exhaust" and n == 3:
            raw.update(
                status="incomplete", incomplete_details={"reason": "max_output_tokens"}, output=[]
            )
            raw["usage"] = usage(o=25000) | {"output_tokens_details": {"reasoning_tokens": 25000}}
        if n == 2:
            if fault == "http":
                return httpx.Response(503, json={"error": {"message": "mock"}})
            if fault == "timeout":
                raise httpx.ReadTimeout("scripted timeout", request=request)
            if fault == "model":
                raw["model"] = "gpt-6-luna" if row["model"] == "sol" else "gpt-6.1-sol"
            if fault == "duplicate":
                raw["id"] = "resp_1"
            if fault == "tier":
                raw["service_tier"] = "priority"
            if fault == "status":
                raw.update(status="incomplete", incomplete_details={"reason": "content_filter"})
        return httpx.Response(200, json=raw)

    largest = max(Decimal(r["worst_case_usd"]) for r in plan["requests"])
    allowance = largest if fault == "guard" else CAP

    def invoke():
        run.acquire(run.APPROVAL, "mock", allowance, mock=httpx.MockTransport(handler), dest=dest)

    clean = fault in ("none", "exhaust", "guard")
    if clean:
        invoke()
    else:
        with pytest.raises((ValueError, openai.APIError)):
            invoke()
    seal = json.loads((dest / "seal.json").read_bytes())
    hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in dest.iterdir()
        if p.name != "seal.json"
    }
    assert hashes == seal["files"] and run.digest(hashes) == seal["ledger_hash"]
    assert (seal["failure"] is None) == clean
    assert n == seal["requests_attempted"]
    assert seal["unsent"] == 432 - n
    if fault in ("none", "exhaust"):
        assert n == 432 and seal["stop"] is None
        assert seal["finished"] + seal["exhausted"] == 432
        assert seal["exhausted"] == (fault == "exhaust")
    elif fault == "guard":
        assert seal["stop"] == "spending_guard" and 0 < n < 432
        assert Decimal(seal["accounted_usd"]) <= allowance
    else:
        assert n == 2 and seal["stop"] is None

    ends, stats, served = replay(dest, "gpt")
    if fault == "status":
        assert ends[plan["requests"][1]["id"]] == {"kind": "interrupted"}
        assert seal["attempts_without_accounting"] == 0
        assert sum(cell["requests"] for cell in stats.values()) == 2
        assert not (dest / "002.event").exists()
        with pytest.raises(ValueError, match="seal counts"):
            analysis.replay(dest)
        (dest / "seal.json").write_text(json.dumps(seal | {"accounted_usd": "0"}), encoding="utf-8")
        with pytest.raises(ValueError, match="seal counts"):
            replay(dest, "gpt")
    else:
        assert (ends, stats, served) == analysis.replay(dest)
    kinds = Counter(a["kind"] for a in ends.values())
    assert kinds["unsent"] == seal["unsent"]
    assert sum(s["cost"] for s in stats.values()) == Decimal(seal["accounted_usd"])
    if fault == "none":
        assert served == {
            "luna-A": ["gpt-6-luna"],
            "luna-B": ["gpt-6-luna"],
            "sol-A": ["gpt-6.1-sol-2026-10-01"],
            "sol-B": ["gpt-6.1-sol-2026-10-01"],
        }
        assert kinds == {"clarify": 420, "sql": 12}
        # Luna 216 x 0.000018725 + Sol 216 x 0.0003735
        assert Decimal(seal["accounted_usd"]) == Decimal("0.0847206")
        sheet = analysis.worksheet(ends)
        # Q34 is the only exact-dimension clarification; all 12 copies collapse to one item.
        assert len(sheet) == 1
        assert all(set(item) == {"question", "wording", "adequate"} for item in sheet.values())
    if fault == "exhaust":
        assert ends[plan["requests"][2]["id"]] == {"kind": "output_exhaustion"}
    if fault in ("http", "timeout", "model", "duplicate", "tier"):
        assert ends[plan["requests"][1]["id"]] == {"kind": "interrupted"}
    with pytest.raises((ValueError, openai.APIError)):
        invoke()


def test_no_authority_or_budget(tmp_path, frozen):
    plan, _ = frozen
    largest = max(Decimal(r["worst_case_usd"]) for r in plan["requests"])

    def forbidden(request):
        pytest.fail("unapproved HTTP")

    for auth, amount in [
        ("wrong", CAP),
        (run.APPROVAL, CAP + Decimal(".01")),
        (run.APPROVAL, largest - Decimal(".000001")),
        (run.APPROVAL, Decimal("Infinity")),
    ]:
        with pytest.raises(ValueError):
            run.acquire(
                auth, "mock", amount, mock=httpx.MockTransport(forbidden), dest=tmp_path / "once"
            )
        assert not (tmp_path / "once").exists()


def test_summarize_pairs_and_stability():
    cases, ends = {}, {}
    for q in analysis.QUESTION_IDS:
        n = int(q[1:])
        for model, arm in CELLS:
            for d in (1, 2, 3):
                key = cell_id(q, model, arm, d)
                ends[key] = {"kind": "sql"}
                if (model, arm) == ("luna", "B"):
                    cases[key] = n <= 18  # 18/36 every draw
                elif (model, arm) == ("sol", "A"):
                    cases[key] = n <= 10 or (n == 11 and d == 1)  # 11, 10, 10
                elif (model, arm) == ("sol", "B"):
                    cases[key] = n <= 20
                else:
                    cases[key] = n == 1
    # One unsent request makes that draw incomplete.
    missing = cell_id("Q36", "luna", "A", 3)
    cases[missing] = None
    ends[missing] = {"kind": "unsent"}
    stats = {"luna-B": Counter(cost=Decimal("0.054"))}
    out = analysis.summarize(cases, ends, stats)
    luna_b = out["cells"]["luna-B"]
    assert luna_b["complete_draw_scores"] == [18, 18, 18]
    assert luna_b["stability"] == {"all_draws": 18, "no_draws": 18}
    assert Decimal(luna_b["usd_per_correct"]) == Decimal("0.001")
    sol_a = out["cells"]["sol-A"]
    assert sol_a["complete_draw_scores"] == [11, 10, 10] and sol_a["range"] == [10, 11]
    assert sol_a["stability"] == {"all_draws": 10, "some_draws": 1, "no_draws": 25}
    assert out["cells"]["luna-A"]["complete_draw_scores"] == [1, 1]
    assert out["cells"]["luna-A"]["stability"]["incomplete"] == 1
    head = out["paired"]["luna-B_vs_sol-A"]
    assert head["baseline"] == "sol-A" and head["comparison"] == "luna-B"
    assert head["counts"] == {"gain": 8 * 3 - 1, "tie": 36 * 3 - 23}
    assert head["counts"]["loss"] == 0
    assert out["paired"]["luna-B_vs_luna-A"]["counts"]["unpaired"] == 1
