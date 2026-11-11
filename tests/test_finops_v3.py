import gzip
import json
import os
from decimal import Decimal
from pathlib import Path

import httpx
import openai
import pytest

from eval_lab.core.hashes import canonical, digest
from experiments.finops_sql.controls import DENIED
from experiments.finops_sql.episode import Discovery
from experiments.finops_sql.episode import body as historical_body
from experiments.finops_sql.packages import QUESTIONS, ROOT
from experiments.finops_sql.v3.accounting import charge
from experiments.finops_sql.v3.development import rehearse, run
from experiments.finops_sql.v3.grading import sandbox
from experiments.finops_sql.v3.proposal import (
    DEV_QUESTIONS,
    OUTPUT,
    REPORTING,
    body,
    build,
    reserve,
    turn_bounds,
)
from experiments.finops_sql.v3.worker import validate


@pytest.mark.parametrize(
    "scope,episodes,turns,tools",
    [
        ("development", 5, 11, 6),
        ("evaluation", 144, 360, 216),
    ],
)
def test_exact_archive_and_reserve(scope, episodes, turns, tools):
    folder = ROOT / "proposals/v3" / scope
    plan, bodies = build(scope)
    assert json.loads((folder / "manifest.json").read_bytes()) == plan | {
        "proposal_digest": digest(plan)
    }
    assert json.loads(gzip.decompress((folder / "bodies.json.gz").read_bytes())) == bodies
    assert (len(bodies), plan["request_ceiling"], plan["tool_ceiling"]) == (episodes, turns, tools)
    total = Decimal(0)
    for row, payload in zip(plan["requests"], bodies, strict=True):
        arm = row["arm"]
        if scope == "development":
            q = DEV_QUESTIONS[row["question"]]
        else:
            q = next(q for q in QUESTIONS if q["id"] == row["question"])
        old = historical_body(arm, q)
        assert old["max_output_tokens"] == 2048
        old["max_output_tokens"] = OUTPUT
        old["input"][0]["content"] = REPORTING + old["input"][0]["content"]
        assert payload == old and digest(payload) == row["body_hash"]
        bounds = row["turn_input_bounds"]
        assert len(bounds) == (7 if arm == "D" else 1)
        total += reserve(sum(bounds), len(bounds))
    assert total == Decimal(plan["reserve_usd"]) <= Decimal(plan["proposed_cap_usd"])


def test_dynamic_history_bound_and_final_turn():
    q = DEV_QUESTIONS["D06"]
    state = Discovery()
    bounds = turn_bounds("D", q, body("D", q))
    for turn, limit in enumerate(bounds):
        payload = body("D", q, state.history)
        assert payload["max_output_tokens"] == 25000
        assert len(canonical(payload).encode()) + 256 <= limit
        assert ("tools" in payload) == (turn < 6)
        if turn < 6:
            state.select("catalog", canonical({"query": ""}))
    with pytest.raises(ValueError):
        body("D", q, [{"result": '"' * 2048}])


# Synthetic compatibility corpus independent of response SQL and evaluation keys.
VALID = {
    "semi": (
        "SELECT count(*) FROM project p WHERE EXISTS (SELECT 1 FROM "
        "resource r WHERE r.project_id=p.id)"
    ),
    "anti": (
        "SELECT count(*) FROM project p WHERE NOT EXISTS (SELECT 1 FROM "
        "resource r WHERE r.project_id=p.id)"
    ),
    "conditional": "SELECT avg(units) FILTER (WHERE units>0), count_if(units=0) FROM usage_day",
    "nested": (
        "WITH X AS (SELECT id FROM project) SELECT count(*) FILTER (WHERE "
        "EXISTS (SELECT 1 FROM x WHERE x.id=r.project_id)) FROM resource r"
    ),
    "window": (
        "SELECT id, rank() OVER (ORDER BY id) AS r, lag(id) OVER (ORDER "
        "BY id) FROM project QUALIFY r<=2"
    ),
    "ties": (
        "SELECT dense_rank() OVER (ORDER BY region_id), lead(id) OVER "
        "(ORDER BY id) FROM resource LIMIT 4"
    ),
    "dates": (
        "SELECT date_trunc('month', first_day), "
        "datediff('day',first_day,end_day) FROM fiscal_period"
    ),
    "nulls": "SELECT greatest(0,least(1,id)), id IS DISTINCT FROM NULL FROM project",
    "strings": "SELECT upper(trim(name)), floor(id/2), ceil(id/2) FROM region",
    "union": "SELECT id FROM project UNION ALL SELECT id FROM region",
}
DENIALS = {
    **{k: v for k, v in DENIED.items() if k != "rows"},
    "unknown": "SELECT * FROM missing_table",
    "nested_table": "SELECT id FROM project WHERE EXISTS (SELECT 1 FROM missing_table)",
    "nested_function": "SELECT count(*) FILTER (WHERE random()>0) FROM invoice",
    "qualified": "SELECT * FROM main.invoice",
    "recursive": "WITH RECURSIVE t AS (SELECT 1) SELECT * FROM t",
    "rowid": "SELECT rowid FROM project",
    "oversized": "SELECT 1" + " " * 65536,
}


@pytest.mark.parametrize("name", VALID)
def test_analytical_grammar(name):
    assert validate(VALID[name])


@pytest.mark.parametrize("name", DENIALS)
def test_recursive_validation(name):
    with pytest.raises(ValueError):
        validate(DENIALS[name])


@pytest.mark.skipif(not os.getenv("FINOPS_VERIFIED_ROOT"), reason="requires v3 Docker fixture")
def test_isolated_development():
    folder = Path(os.environ["FINOPS_VERIFIED_ROOT"]) / "development"
    report = run(folder)
    assert report["distinct_sql_results_checked"] == 7 and report["scripted_episodes"] == 32
    results = sandbox(folder, VALID | DENIALS | {"rows": DENIED["rows"]})
    assert all("error" not in results[k] for k in VALID)
    assert all(results[k].get("sql_valid") is False for k in DENIALS)
    assert results["rows"]["error"] == "row limit" and results["rows"]["sql_valid"]


def receipt(o=OUTPUT, reasoning=OUTPUT):
    return {
        "model": "gpt-6-luna",
        "service_tier": "default",
        "max_output_tokens": OUTPUT,
        "reasoning": {"effort": "medium"},
        "prompt_cache_options": {"ttl": "30m"},
        "usage": {
            "input_tokens": 20,
            "output_tokens": o,
            "total_tokens": 20 + o,
            "input_tokens_details": {"cached_tokens": 5, "cache_write_tokens": 10},
            "output_tokens_details": {"reasoning_tokens": reasoning},
        },
    }


def test_reasoning_and_output_share_one_ceiling():
    assert charge(receipt(), 20) == Decimal(".012501800")
    for raw, bound in [
        (receipt(25001), 20),
        (receipt(100, 101), 20),
        (receipt(), 19),
        (receipt() | {"max_output_tokens": 2048}, 20),
        (receipt() | {"prompt_cache_options": {"ttl": "12h"}}, 20),
    ]:
        with pytest.raises(ValueError):
            charge(raw, bound)


@pytest.mark.parametrize("fault", ["incomplete", "timeout"])
def test_interruption_ends_rehearsal(monkeypatch, fault):
    calls = 0

    def fail_once(self, request):
        nonlocal calls
        calls += 1
        assert request.extensions["timeout"] == {
            "read": 900,
            "write": 30,
            "connect": 10,
            "pool": 10,
        }
        if fault == "timeout":
            raise httpx.ReadTimeout("mock", request=request)
        return httpx.Response(
            200,
            json=receipt()
            | {
                "status": "incomplete",
                "incomplete_details": {"reason": "max_output_tokens"},
                "output": [],
            },
        )

    monkeypatch.setattr(httpx.MockTransport, "handle_request", fail_once)
    with pytest.raises((ValueError, openai.APITimeoutError)):
        rehearse("D06", "D")
    assert calls == 1
