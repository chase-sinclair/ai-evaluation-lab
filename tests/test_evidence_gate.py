import importlib
import json
from pathlib import Path

import httpx
import pytest
from openai import OpenAI

from eval_lab.core.hashes import digest


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    return importlib.import_module("experiments.evidence_gate.plan"), importlib.import_module(
        "experiments.evidence_gate.report"
    )


def test_packets_and_oracles(modules):
    verify = modules[0].verify
    exp, plan = verify()
    cases = exp.load_cases()
    assert len(plan["rows"]) == 48 and plan["reserve"] <= 0.05
    for case in cases:
        assert case.ground_truth["expected_gate"] == (
            "BLOCK" if case.id.startswith("U") else "PASS"
        )
        rows = [r for r in plan["rows"] if r["case"] == case.id]
        assert rows[0]["body"]["input"][1] == rows[1]["body"]["input"][1]
        packet = json.loads(rows[0]["body"]["input"][1]["content"])
        assert packet == case.task_input and set(packet) == {"question", "excerpts"}
        assert len(packet["excerpts"]) == 3
        if case.id in ("U5", "U6"):
            assert case.ground_truth["gap"] == "retrieval_miss"
            assert {"U5": "D09", "U6": "D02"}[case.id] not in {p["id"] for p in packet["excerpts"]}


@pytest.mark.parametrize("broken", [False, True])
def test_dispatch_and_review(tmp_path, broken, modules):
    verify, execute, report = modules[0].verify, modules[0].execute, modules[1].report
    _, plan = verify()
    seen = []

    def transport(req):
        row = plan["rows"][len(seen)]
        assert json.loads(req.content) == row["body"]
        seen.append(row)
        answer = "A scripted statement [D99]."
        if row["stage"] == "gate":
            answer = "BLOCK" if row["case"].startswith("U") else "PASS"
        return httpx.Response(
            200,
            json=dict(
                object="response",
                id=f"resp_{len(seen)}",
                created_at=0,
                model="gpt-6-luna",
                status="completed",
                service_tier="default",
                usage=None
                if broken
                else dict(
                    input_tokens=50,
                    output_tokens=6,
                    total_tokens=56,
                    input_tokens_details=dict(cached_tokens=0, cache_write_tokens=0),
                ),
                output=[
                    dict(
                        type="message",
                        id="msg_test",
                        role="assistant",
                        status="completed",
                        content=[dict(type="output_text", text=answer, annotations=[])],
                    )
                ],
            ),
        )

    with OpenAI(
        api_key="fixture",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(transport)),
    ) as client:
        with pytest.raises(ValueError):
            execute("wrong", tmp_path, client)
        result = execute(digest(plan), tmp_path, client)
        with pytest.raises(FileExistsError):
            execute(digest(plan), tmp_path, client)
    sheet_path = tmp_path / "review.json"
    result_report = report(tmp_path / "alder-v1-once", sheet_path)
    if broken:
        assert (
            len(seen) == 1
            and result["run_status"] == "failed"
            and result_report["evaluable_pairs"] == 0
        )
        return
    sheet = json.loads(sheet_path.read_bytes())
    assert len(sheet) == 30 and len(seen) == 48
    for pair in result_report["pairs"]:
        if pair["verdict"] == "PASS":
            assert pair["standard"] == pair["gated"]
        else:
            assert sheet[pair["gated"]]["answer"] == plan["referral"]
    for entry in sheet.values():
        bad = bool(entry["outside_packet_ids"])
        entry["judgment"] = dict(
            claims=[
                dict(
                    span="A scripted statement",
                    support="unsupported",
                    evidence="No evidence",
                    citations={"D99": False},
                )
            ]
            if bad
            else [],
            useful_correct=not bad,
            appropriate_abstention=not bad,
            over_refusal=False,
            partial_handling="not_applicable",
            clarification="not_applicable",
            reviewer="test fixture",
            rationale="scripted",
        )
    sheet_path.write_text(json.dumps(sheet))
    graded = report(tmp_path / "alder-v1-once", sheet_path, True)
    assert graded["paired"]["unsupported_prevented"] == 6
    assert graded["arms"]["standard"]["correct_links"] == 0
    assert graded["additional_estimated_usd"] > 0


def test_blocks_can_lose_value_without_preventing_any_claim(modules):
    mod = modules[1]
    base = mod.Judgment(
        claims=[],
        useful_correct=True,
        appropriate_abstention=False,
        over_refusal=False,
        partial_handling="not_applicable",
        clarification="focused",
        reviewer="fixture",
        rationale="scripted",
    )
    refusal = base.model_copy(
        update={"useful_correct": False, "over_refusal": True, "clarification": "missed"}
    )
    abstained = base.model_copy(
        update={"appropriate_abstention": True, "clarification": "not_applicable"}
    )
    pairs = [
        dict(question=f + "1", standard="answer", gated="referral", verdict="BLOCK") for f in "APM"
    ]
    pairs.append(dict(question="U1", standard="stop", gated="stop", verdict="BLOCK"))
    counts = mod.outcomes(pairs, {"answer": base, "referral": refusal, "stop": abstained})["paired"]
    assert counts == dict(
        unsupported_prevented=0,
        unsupported_introduced=0,
        lost_useful_A=1,
        lost_useful_P=1,
        lost_clarifications=1,
        already_abstained_blocks=1,
    )
