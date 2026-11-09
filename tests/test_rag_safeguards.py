import importlib
import json
import re
from pathlib import Path

import httpx
import pytest
from openai import OpenAI

from eval_lab.core.hashes import digest
from eval_lab.core.result_store import write_once


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    return (
        importlib.import_module("experiments.rag_safeguards.stages"),
        importlib.import_module("experiments.rag_safeguards.report"),
    )


def transport(rows, fault=None):
    sent = []

    def handle(request):
        row = rows[len(sent)]
        body = json.loads(request.content)
        assert body == row["body"] and digest(body) == row["body_hash"]
        sent.append(row)
        stage = row["stage"]
        text = {
            "generator": "Original  response [1].\n",
            "gate": "BLOCK" if row["case"].startswith("I") else "PASS",
            "verifier": "BLOCK" if row["case"].startswith("C") else "PASS",
        }[stage]
        return httpx.Response(
            200,
            json=dict(
                id="resp_" + stage + row["case"],
                object="response",
                created_at=0,
                model="other" if fault == "model" else "gpt-6-luna",
                service_tier="fast" if fault == "tier" else "default",
                status="incomplete" if fault == "incomplete" else "completed",
                usage=None
                if fault == "usage"
                else dict(
                    input_tokens=99999 if fault == "budget" else 60,
                    output_tokens=10,
                    input_tokens_details=dict(cached_tokens=0, cache_write_tokens=0),
                ),
                output=[
                    dict(
                        type="message",
                        role="assistant",
                        id="m",
                        status="completed",
                        content=[dict(type="output_text", text=text, annotations=[])],
                    )
                ],
            ),
        )

    return OpenAI(
        api_key="offline",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handle)),
    ), sent


def test_staged(modules, tmp_path, monkeypatch):
    s, r = modules
    exp, one = s.verified_first(tmp_path)
    cases = {c.id: c for c in exp.load_cases()}
    design = (s.HERE.parents[1] / "docs/experiment03_phase_b_design.md").read_text(encoding="utf8")
    for line in re.findall(r"^\| [RIC]\d\d .*?$", design, re.M):
        label, question, packet, key, risk = [field.strip() for field in line.strip("|").split("|")]
        case = cases[label.split()[0]]
        assert case.task_input == {
            "question": question,
            "excerpts": dict(zip(("1", "2"), packet.split(" / "), strict=True)),
        }
        assert case.ground_truth == {"key": key, "risk": risk}
    assert list(exp.protocol["prompts"].values()) == re.findall(
        r"^\*\*[^\n]+?\*\* “([^”]+)”", design, re.M
    )
    assert len(one["rows"]) == 72 and len(cases) == 36
    for row in one["rows"]:
        assert json.loads(row["body"]["input"][1]["content"]) == cases[row["case"]].task_input
    client, sent = transport(one["rows"])
    with client:
        with pytest.raises(ValueError):
            s.execute(1, "incorrect", tmp_path, client)
        assert not sent
        assert s.execute(1, digest(one), tmp_path, client)["run_status"] == "completed"
        with pytest.raises(FileExistsError):
            s.execute(1, digest(one), tmp_path, client)
    _, two = s.build(2, tmp_path)
    with monkeypatch.context() as m:
        # A prior acquisition alone can consume the remaining cumulative allowance.
        m.setattr(s, "verified_first", lambda root: (exp, one))
        m.setattr(s, "CAP", two["stage_one_spend"] + 0.000001)
        with pytest.raises(ValueError):
            s.build(2, tmp_path)
    assert two == s.build(2, tmp_path)[1] and len(two["rows"]) == 36
    for row in two["rows"]:
        data = json.loads(row["body"]["input"][1]["content"])
        assert data == {
            **cases[row["case"]].task_input,
            "candidate_reply": "Original  response [1].\n",
        }
        assert row["source"]["response_id"] == "resp_generator" + row["case"]
    assert two["stage_one_spend"] + two["reserve"] <= s.CAP
    path = s.manifest_path(tmp_path, 2)
    write_once(path, two)
    client, sent = transport(two["rows"])
    with client:
        with pytest.raises(ValueError):
            s.execute(2, digest(one), tmp_path, client)
        modified = json.loads(path.read_bytes())
        modified["rows"][0]["body_hash"] = "bad"
        path.write_text(json.dumps(modified))
        with pytest.raises(ValueError):
            s.execute(2, digest(two), tmp_path, client)
        path.write_text(json.dumps(two))
        assert not sent
        assert s.execute(2, digest(two), tmp_path, client)["run_status"] == "completed"
        with pytest.raises(FileExistsError):
            s.execute(2, digest(two), tmp_path, client)
    sheetpath = tmp_path / "worksheet.json"
    report = r.report(tmp_path, sheetpath)
    sheet = json.loads(sheetpath.read_bytes())
    for q in report["outcomes"]:
        for arm, c in q["arms"].items():
            blocked = (arm, q["group"]) in (("B", "I"), ("C", "C"))
            assert sheet[c["review_id"]]["reply"] == (
                exp.protocol["referral"] if blocked else "Original  response [1].\n"
            )
    for entry in sheet.values():
        bad = entry["reply"].startswith("Original")
        entry["review"] = dict(
            reviewer="mock",
            rationale="scripted",
            correct=not bad,
            behavior="other",
            claims=[
                dict(
                    span="Original",
                    evidence="fixture",
                    supported=False,
                    citation_links={"1": False},
                    authority_correct=False,
                )
            ]
            if bad
            else [],
        )
    sheetpath.write_text(json.dumps(sheet))
    graded = r.report(tmp_path, sheetpath, True)
    assert graded["comparisons"]["all/A-B"]["counts"]["unsupported_answers_prevented"] == 12
    assert graded["comparisons"]["all/A-C"]["counts"]["unsupported_answers_prevented"] == 12
    assert graded["comparisons"]["all/B-C"]["counts"]["unsupported_claims_introduced"] == 12
    assert graded["architectures"]["all/C"]["authority_assessments"] == 24
    receipts = s.run_dir(tmp_path, 1) / "records.jsonl"
    with receipts.open("ab") as f:
        f.write(b" ")
    with pytest.raises(ValueError):
        s.build(2, tmp_path)


@pytest.mark.parametrize("fault", ["model", "tier", "incomplete", "usage", "budget"])
def test_failure_stops(modules, tmp_path, fault):
    s, r = modules
    _, one = s.verified_first(tmp_path)
    client, sent = transport(one["rows"], fault)
    with client:
        assert s.execute(1, digest(one), tmp_path, client)["run_status"] == "failed"
    assert len(sent) == 1
    result = r.report(tmp_path, tmp_path / "sheet")
    assert all(m["evaluable"] == 0 for m in result["architectures"].values())
    with pytest.raises(FileNotFoundError):
        s.build(2, tmp_path)
