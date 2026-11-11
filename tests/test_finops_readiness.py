import csv
import gzip
import itertools
import json
import os
import re
from pathlib import Path

import httpx
import pytest

from eval_lab.core.hashes import canonical, digest
from experiments.finops_sql.discovery import paths
from experiments.finops_sql.episode import Discovery, body, mock_episode
from experiments.finops_sql.grading import grade, matches
from experiments.finops_sql.packages import OBJECTS, QUESTIONS, ROOT, SAMPLES, package, tokens
from experiments.finops_sql.proposal import build
from experiments.finops_sql.references import QUERIES


def call(name="catalog", args=None):
    return {
        "type": "function_call",
        "call_id": "call_1",
        "name": name,
        "arguments": canonical(args if args is not None else {"query": ""}),
    }


def message(text):
    return {
        "type": "message",
        "role": "assistant",
        "content": [{"type": "output_text", "text": text}],
    }


def scenario(tmp_path, turns, arm="D", number=1):
    pending = iter(turns)
    bodies = []

    def handle(request):
        bodies.append(json.loads(request.content))
        assert request.url.host == "offline.invalid"
        status, items = next(pending)
        if status == "error":
            return httpx.Response(503, json={"error": {"message": "scripted"}})
        return httpx.Response(200, json={"id": "resp_mock", "status": status, "output": items})

    result = mock_episode(arm, QUESTIONS[number - 1], handle, tmp_path / "receipts")
    assert list(pending) == []
    for turn, observed in enumerate(bodies, 1):
        frozen = json.loads((tmp_path / "receipts" / f"{turn:02}.request").read_bytes())
        assert observed == frozen
    return result, bodies


@pytest.mark.parametrize(
    "turns,kind",
    [
        ([("completed", [message("invalid")])], "malformed"),
        ([("completed", [])], "missing"),
        ([("completed", [call(), call()])], "invalid_proposals"),
        ([("incomplete", [message("{}")])], "incomplete"),
        ([("error", [])], "provider_error"),
        ([("completed", [call("describe", {"ids": ["invoice"]})]), ("completed", [])], "missing"),
        ([("completed", [call()])] * 7, "invalid_proposals"),
        (
            [("completed", [call()])] * 6
            + [("completed", [message('{"kind":"sql","query":"SELECT 1"}')])],
            "sql",
        ),
    ],
)
def test_episode_failure_and_exhaustion(tmp_path, turns, kind):
    result, bodies = scenario(tmp_path, turns)
    assert result["kind"] == kind
    assert all(b.get("max_output_tokens") == 2048 for b in bodies)
    assert len(list((tmp_path / "receipts").glob("*.json"))) == len(turns)
    if len(turns) == 7:
        assert "tools" not in bodies[-1]
    if len(turns) == 2:
        assert "Invalid or oversized" in bodies[-1]["input"][-1]["content"]


@pytest.mark.parametrize("dimension,expected", [("scope", None), ("period", False)])
def test_clarification_review(tmp_path, dimension, expected):
    reply = {"kind": "clarify", "dimensions": [dimension], "question": "Which reporting center?"}
    result, bodies = scenario(tmp_path, [("completed", [message(canonical(reply))])], number=34)
    assert len(bodies) == 1 and grade(34, result, tmp_path)["business_correct"] is expected


def test_public_scope_and_reachability():
    assert package("C").startswith(package("B")) and package("B").startswith(package("A"))
    for trace in paths().values():
        state = Discovery()
        for op, arg in trace:
            rec = state.select(op, canonical({"query" if op == "catalog" else "ids": arg}))
            assert "error" not in rec and tokens(rec["result"]) <= 800
    state = Discovery()
    assert "error" in state.select("examples", '{"table":"invoice"}')
    state.select("catalog", '{"query":""}')
    assert len(state.select("examples", '{"table":"invoice"}')["result"]) == 3
    # Check the 800-token cap for every three-ID combination of legitimate descriptions.
    for ids in itertools.combinations(OBJECTS, 3):
        assert tokens({k: OBJECTS[k] for k in ids}) <= 800


def test_result_contract():
    key = {"columns": ["account_id", "delta"], "rows": [[1, "20.00"]]}
    actual = {**key, "types": ["INTEGER", "DECIMAL(18,6)"]}
    assert matches(5, actual, key)
    for override in [
        {"columns": ["delta", "account_id"]},
        {"types": ["VARCHAR", "DOUBLE"]},
        {"rows": [[1, 0.2]]},
        {"rows": [[1, None]]},
        {"rows": [[1, 20, 0]]},
    ]:
        assert not matches(5, actual | override, key)
    ranked = {"columns": ["service_id", "cost"], "rows": [[1, 10], [2, 8]]}
    assert not matches(
        2, ranked | {"types": ["INTEGER", "DOUBLE"], "rows": [[2, 8], [1, 10]]}, ranked
    )


def test_frozen_proposal():
    plan, bodies = build()
    frozen = ROOT / "proposals" / "v2"
    assert json.loads((frozen / "manifest.json").read_bytes()) == plan | {
        "proposal_digest": digest(plan)
    }
    assert json.loads(gzip.decompress((frozen / "bodies.json.gz").read_bytes())) == bodies
    assert len(bodies) == 144
    previous = ROOT / "proposals" / "v1"
    v1 = json.loads((previous / "manifest.json").read_bytes())
    assert v1["context_sha256"] == plan["context_sha256"]
    originals = json.loads(gzip.decompress((previous / "bodies.json.gz").read_bytes()))
    for old, new, before, after in zip(
        originals, bodies, v1["requests"], plan["requests"], strict=True
    ):
        assert (before["question"], before["arm"]) == (after["question"], after["arm"])
        old["input"][0]["content"] = old["input"][0]["content"].replace(
            "percentages in percentage points", "percentages as percent of the stated base", 1
        )
        if before["question"] == "Q07":
            old["input"][1]["content"] = old["input"][1]["content"].replace("May–June", "June–July")
        assert old == new
    assert sum(len(r["turn_input_bounds"]) for r in plan["requests"]) == 360
    assert all(
        b["input"][1] == body("D", q)["input"][1]
        for q in QUESTIONS
        for b in [body(a, q) for a in "ABC"]
    )


@pytest.mark.skipif(
    not os.getenv("FINOPS_VERIFIED_ROOT"), reason="requires verified Docker fixtures"
)
@pytest.mark.parametrize(
    "arm,sql,valid,executed,correct",
    [
        ("A", QUERIES[1], True, True, True),
        ("B", QUERIES[1].replace("post=3", "m=3"), True, True, False),
        ("C", "DELETE FROM invoice", False, False, False),
        ("A", "SELECT absent_field AS cost FROM invoice", True, False, False),
        ("D", QUERIES[1], True, True, True),
    ],
)
def test_sdk_to_two_snapshot_grader(tmp_path, arm, sql, valid, executed, correct):
    turns = [("completed", [call()])] if arm == "D" else []
    turns.append(("completed", [message(canonical({"kind": "sql", "query": sql}))]))
    reply, _ = scenario(tmp_path, turns, arm)
    scored = grade(1, reply, Path(os.environ["FINOPS_VERIFIED_ROOT"]))
    assert (scored["sql_valid"], scored["execution_success"], scored["business_correct"]) == (
        valid,
        executed,
        correct,
    )


def test_question_isolation():
    design = (ROOT.parents[1] / "docs/experiment05_sql_context_design.md").read_text(
        encoding="utf8"
    )
    original = re.findall(r"^\| (\d\d) \| ([^|]+) \|", design, re.M)
    assert [(q["id"], q["question"]) for q in QUESTIONS] == [("Q" + i, q) for i, q in original]
    for q in QUESTIONS:
        for arm in "ABCD":
            request = body(arm, q)
            assert json.loads(request["input"][1]["content"]) == {
                "question": q["question"],
                "sql_report_fields": q["fields"],
            }
            assert not any(
                s in canonical(request)
                for s in (
                    "evaluation_a",
                    "oracle-bindings",
                    "NEEDS",
                    "checkpoint.json",
                    "required_dimensions",
                )
            )


@pytest.mark.skipif(not os.getenv("FINOPS_VERIFIED_ROOT"), reason="requires development snapshot")
def test_public_records_come_only_from_development():
    folder = Path(os.environ["FINOPS_VERIFIED_ROOT"]) / "development"
    for table, expected in SAMPLES.items():
        with (folder / (table + ".csv")).open(encoding="utf8", newline="") as f:
            assert list(itertools.islice(csv.DictReader(f), 3)) == expected
