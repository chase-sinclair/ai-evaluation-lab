"""Offline tests for Experiment 007. No provider request leaves the process."""

import gzip
import hashlib
import json
from collections import Counter
from decimal import Decimal

import anthropic
import httpx2
import pytest

from experiments.claude_context import analysis
from experiments.claude_context.accounting import charge, terminal
from experiments.claude_context.proposal import CAP, COUNTERPART, MODELS, OUTPUT
from experiments.finops_sql.references import QUERIES
from experiments.model_context.proposal import FROZEN as PARENT_FROZEN
from experiments.model_context.proposal import cell_id
from experiments.model_context.replay import replay
from scripts import acquire_claude_context as run


@pytest.fixture(scope="module")
def frozen():
    return run.preflight(run.APPROVAL)


@pytest.fixture(autouse=True)
def reuse_frozen_build(monkeypatch, frozen):
    monkeypatch.setattr(run, "build", lambda: frozen)


def test_bodies_derive_from_006_with_identical_text(frozen):
    plan, bodies = frozen
    parent = json.loads((PARENT_FROZEN / "manifest.json").read_bytes())
    parent_bodies = json.loads(gzip.decompress((PARENT_FROZEN / "bodies.json.gz").read_bytes()))
    rows = plan["requests"]
    assert len(rows) == len(bodies) == plan["request_ceiling"] == 432
    assert Counter((r["model"], r["arm"]) for r in rows) == {
        (m, a): 108 for m in MODELS for a in ("A", "B")
    }
    for row, body, prow, pbody in zip(rows, bodies, parent["requests"], parent_bodies, strict=True):
        # Same position, question, arm and draw as 006; the counterpart model.
        assert (row["question"], row["arm"], row["draw"]) == (
            prow["question"],
            prow["arm"],
            prow["draw"],
        )
        assert row["model"] == COUNTERPART[prow["model"]] and row["parent_id"] == prow["id"]
        assert row["parent_body_hash"] == prow["body_hash"] == run.digest(pbody)
        developer, user = (m["content"] for m in pbody["input"])
        assert body == {
            "model": MODELS[row["model"]],
            "max_tokens": 25000,
            "system": [{"type": "text", "text": developer, "cache_control": {"type": "ephemeral"}}],
            "messages": [{"role": "user", "content": user}],
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": "medium"},
            "inference_geo": "global",
        }
        assert run.digest(body) == row["body_hash"]
        assert len(run.canonical(body).encode()) + 256 == row["input_bound"]


def test_reserve_and_cap(frozen):
    plan, _ = frozen
    worst = sum(Decimal(r["worst_case_usd"]) for r in plan["requests"])
    assert Decimal(plan["worst_case_reserve_usd"]) == worst
    assert Decimal("60") < worst < Decimal("65")
    assert Decimal(plan["proposed_cap_usd"]) == CAP == Decimal("15.00")


def usage(i=100, o=15, read=10, write=5, **extra):
    return (
        dict(
            input_tokens=i,
            output_tokens=o,
            cache_read_input_tokens=read,
            cache_creation_input_tokens=write,
            cache_creation={"ephemeral_5m_input_tokens": write, "ephemeral_1h_input_tokens": 0},
            output_tokens_details={"thinking_tokens": 2},
            service_tier="standard",
            inference_geo="global",
        )
        | extra
    )


def receipt(model, answer=None, **fields):
    text = run.canonical(answer or {"kind": "clarify", "dimensions": ["period"], "question": "?"})
    return (
        dict(
            id="msg_1",
            type="message",
            role="assistant",
            model=model,
            content=[
                {"type": "thinking", "thinking": "", "signature": "sig"},
                {"type": "text", "text": text},
            ],
            stop_reason="end_turn",
            stop_sequence=None,
            usage=usage(),
        )
        | fields
    )


def test_charge_prices_each_model():
    assert charge(receipt("claude-haiku-5-5"), "claude-haiku-5-5", 1000) == Decimal("0.000018225")
    assert charge(receipt("claude-sonnet-5-5"), "claude-sonnet-5-5", 1000) == Decimal("0.0003635")
    bad = [
        receipt("claude-haiku-5-5"),  # wrong model for the request
        receipt("claude-sonnet-5-5", usage=usage(inference_geo="us")),
        receipt("claude-sonnet-5-5", usage=usage(speed="fast")),
        receipt("claude-sonnet-5-5", usage=usage(service_tier="priority")),
        receipt(
            "claude-sonnet-5-5",
            usage=usage()
            | {"cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 5}},
        ),
        receipt("claude-sonnet-5-5", usage=usage(i=2000)),  # above the input bound
        receipt("claude-sonnet-5-5", usage=usage(o=OUTPUT + 1)),
        receipt("claude-sonnet-5-5", usage=usage() | {"input_tokens": None}),
        receipt("claude-sonnet-5-5", type="error"),
    ]
    for raw in bad:
        with pytest.raises(ValueError):
            charge(raw, "claude-sonnet-5-5", 1000)
    with pytest.raises(ValueError):
        charge(receipt("claude-haiku-5-5", usage=usage(i=100_001)), "claude-haiku-5-5", 10**6)


def test_terminal_classification():
    sql = {"kind": "sql", "query": "SELECT 1"}
    assert terminal(receipt("m", sql)) == sql
    assert terminal(receipt("m", stop_reason="max_tokens", usage=usage(o=OUTPUT))) == {
        "kind": "output_exhaustion"
    }
    assert terminal(
        receipt("m", stop_reason="refusal", stop_details={"type": "refusal", "category": "cyber"})
    ) == {"kind": "refusal", "category": "cyber"}
    tool = receipt("m")
    tool["content"].append({"type": "tool_use", "id": "t", "name": "x", "input": {}})
    assert terminal(tool) == {"kind": "invalid_proposals"}
    empty = receipt("m")
    empty["content"] = [{"type": "thinking", "thinking": "", "signature": "s"}]
    assert terminal(empty) == {"kind": "missing"}
    for raw in (
        receipt("m", stop_reason="max_tokens"),  # below the frozen ceiling
        receipt("m", stop_reason="tool_use"),
        receipt("m", stop_reason="pause_turn"),
        receipt("m", content="text"),
    ):
        with pytest.raises(ValueError):
            terminal(raw)


def answer_for(question):
    if question == "Q01":
        return {"kind": "sql", "query": QUERIES[1]}
    if question == "Q34":
        return {"kind": "clarify", "dimensions": ["scope"], "question": "Which cost centers?"}
    return {"kind": "clarify", "dimensions": ["period"], "question": "Which period?"}


FAULTS = [
    "none",
    "exhaust",
    "refusal",
    "guard",
    "http",
    "timeout",
    "model",
    "duplicate",
    "geo",
    "stop",
]


@pytest.mark.parametrize("fault", FAULTS)
def test_acquisition(tmp_path, frozen, fault):
    plan, bodies = frozen
    dest = tmp_path / "once"
    n = 0

    def handler(request):
        nonlocal n
        n += 1
        assert str(request.url) == run.URL
        assert request.extensions["timeout"]["read"] == 900
        assert (dest / f"{n:03}.request-body").read_bytes() == request.content
        actual = json.loads(request.content)
        assert actual == bodies[n - 1]
        assert "x-api-key" not in json.loads((dest / f"{n:03}.request-headers").read_bytes())
        row = plan["requests"][n - 1]
        raw = receipt(actual["model"], answer_for(row["question"]), id=f"msg_{n}")
        if fault == "exhaust" and n == 3:
            raw.update(stop_reason="max_tokens", content=[], usage=usage(o=OUTPUT))
        if fault == "refusal" and n == 3:
            raw.update(
                stop_reason="refusal",
                content=[],
                stop_details={"type": "refusal", "category": None, "explanation": None},
            )
        if n == 2:
            if fault == "http":
                return httpx2.Response(500, json={"type": "error", "error": {"type": "api_error"}})
            if fault == "timeout":
                raise httpx2.ReadTimeout("scripted timeout", request=request)
            if fault == "model":
                other = "claude-haiku-5-5" if row["model"] == "sonnet" else "claude-sonnet-5-5"
                raw["model"] = other
            if fault == "duplicate":
                raw["id"] = "msg_1"
            if fault == "geo":
                raw["usage"]["inference_geo"] = "us"
            if fault == "stop":
                raw["stop_reason"] = "stop_sequence"
        return httpx2.Response(200, json=raw, headers={"request-id": f"req_{n}"})

    largest = max(Decimal(r["worst_case_usd"]) for r in plan["requests"])
    allowance = largest if fault == "guard" else CAP

    def invoke():
        run.acquire(run.APPROVAL, "mock", allowance, mock=httpx2.MockTransport(handler), dest=dest)

    clean = fault in ("none", "exhaust", "refusal", "guard")
    if clean:
        invoke()
    else:
        with pytest.raises((ValueError, anthropic.APIError)):
            invoke()
    seal = json.loads((dest / "seal.json").read_bytes())
    hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in dest.iterdir()
        if p.name != "seal.json"
    }
    assert hashes == seal["files"] and run.digest(hashes) == seal["ledger_hash"]
    assert (seal["failure"] is None) == clean
    assert n == seal["requests_attempted"] and seal["unsent"] == 432 - n
    if fault in ("none", "exhaust", "refusal"):
        assert n == 432 and seal["stop"] is None
        assert seal["finished"] + seal["exhausted"] + seal["refused"] == 432
        assert seal["exhausted"] == (fault == "exhaust") and seal["refused"] == (fault == "refusal")
    elif fault == "guard":
        assert seal["stop"] == "spending_guard" and 0 < n < 432
        assert Decimal(seal["accounted_usd"]) <= allowance
    else:
        assert n == 2 and seal["stop"] is None

    ends, stats, served = replay(dest, "claude")
    if fault == "stop":
        assert ends[plan["requests"][1]["id"]] == {"kind": "interrupted"}
        assert seal["attempts_without_accounting"] == 0
        assert sum(cell["requests"] for cell in stats.values()) == 2
        assert not (dest / "002.event").exists()
        with pytest.raises(ValueError, match="seal counts"):
            analysis.replay(dest)
        (dest / "seal.json").write_text(json.dumps(seal | {"accounted_usd": "0"}), encoding="utf-8")
        with pytest.raises(ValueError, match="seal counts"):
            replay(dest, "claude")
    else:
        assert (ends, stats, served) == analysis.replay(dest)
    kinds = Counter(a["kind"] for a in ends.values())
    assert kinds["unsent"] == seal["unsent"]
    assert sum(s["cost"] for s in stats.values()) == Decimal(seal["accounted_usd"])
    if fault == "none":
        assert served == {f"{m}-{a}": [MODELS[m]] for m in MODELS for a in ("A", "B")}
        assert kinds == {"clarify": 420, "sql": 12}
        # Haiku 216 x 0.000018225 + Sonnet 216 x 0.0003635
        assert Decimal(seal["accounted_usd"]) == Decimal("0.0824526")
    if fault == "exhaust":
        assert ends[plan["requests"][2]["id"]] == {"kind": "output_exhaustion"}
    if fault == "refusal":
        assert ends[plan["requests"][2]["id"]] == {"kind": "refusal", "category": None}
    if fault in ("http", "timeout", "model", "duplicate", "geo"):
        assert ends[plan["requests"][1]["id"]] == {"kind": "interrupted"}
    with pytest.raises((ValueError, anthropic.APIError)):
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
                auth, "mock", amount, mock=httpx2.MockTransport(forbidden), dest=tmp_path / "once"
            )
        assert not (tmp_path / "once").exists()


def test_prefill_carries_only_exact_prior_judgments():
    q = "What were July’s discount savings?"
    same = {"question": q, "wording": "A?"}
    new = {"question": q, "wording": "B?"}
    sheet = {
        analysis.digest(same): same | {"adequate": None},
        analysis.digest(new): new | {"adequate": None},
    }
    prior = {analysis.digest(same): same | {"adequate": False}}
    out, reused = analysis.prefill(sheet, prior)
    assert reused == [analysis.digest(same)]
    assert out[analysis.digest(same)]["adequate"] is False
    assert out[analysis.digest(new)]["adequate"] is None
    with pytest.raises(ValueError):
        analysis.prefill(sheet, {analysis.digest(same): new | {"adequate": True}})


def test_summarize_and_replication_criteria():
    def build(haiku_b, sonnet_a):
        cases, ends = {}, {}
        for q in analysis.QUESTION_IDS:
            n = int(q[1:])
            for model in MODELS:
                for arm in ("A", "B"):
                    for d in (1, 2, 3):
                        key = cell_id(q, model, arm, d)
                        ends[key] = {"kind": "sql"}
                        score = {
                            ("haiku", "A"): 2,
                            ("haiku", "B"): haiku_b[d - 1],
                            ("sonnet", "A"): sonnet_a[d - 1],
                            ("sonnet", "B"): 24,
                        }[(model, arm)]
                        cases[key] = n <= score
        return analysis.summarize(cases, ends, {})

    held = build([16, 14, 12], [7, 6, 6])["replication"]
    assert held["primary_haiku_curated_beats_sonnet_schema_every_draw"] is True
    assert held["secondary_context_raises_each_model_every_draw"] is True
    assert held["secondary_paired_gains_exceed_losses"] is True
    assert held["paired_counts"] == {"gain": 9 + 8 + 6, "tie": 108 - 23}
    failed = build([16, 6, 12], [7, 6, 6])["replication"]
    assert failed["primary_haiku_curated_beats_sonnet_schema_every_draw"] is False
    assert failed["primary_draws"] == {"haiku_B": [16, 6, 12], "sonnet_A": [7, 6, 6]}


def test_post_hoc_lenient_extraction():
    from experiments.claude_context.sensitivity import lenient

    sql = '{"kind":"sql","query":"SELECT 1"}'
    assert lenient("```json\n" + sql + "\n```") == {"kind": "sql", "query": "SELECT 1"}
    assert lenient("Interpretation: use posting month.\n" + sql)["kind"] == "sql"
    assert lenient(sql + "\nThis uses the invoice clock.")["kind"] == "sql"
    # A non-answer object first, then the answer.
    assert lenient('{"note": 1} then ' + sql)["kind"] == "sql"
    assert lenient("no json here") == {"kind": "malformed"}
    assert lenient('{"kind":"sql","query":""}') == {"kind": "malformed"}
