import importlib
import json
from pathlib import Path

import httpx
import pytest

from eval_lab.core.hashes import digest
from eval_lab.core.result_store import read_records


@pytest.fixture
def pilot(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    return importlib.import_module("experiments.entity_matching.ror.dispatch")


@pytest.fixture
def worksheet(pilot, tmp_path):
    # Simulation-only form lives under pytest's temporary directory.
    form = importlib.import_module("experiments.entity_matching.ror.human_review").FORM.read_text(
        encoding="utf8"
    )
    for key, value in {
        "Decision": "NO_SUPPORTED_MATCH",
        "Evidence and search terms": "SIMULATED input for gate test",
        "Reviewer": "TEST FIXTURE",
        "Date": "2026-01-01",
        "Offered-set result": "NONE",
    }.items():
        form = form.replace(key + ":\n", key + ": " + value + "\n")
    p = tmp_path / "test-only.md"
    p.write_text(form, encoding="utf8")
    return p


def mock_response():
    return dict(
        id="resp_test",
        object="response",
        created_at=0,
        model="gpt-6-luna",
        status="completed",
        service_tier="default",
        max_output_tokens=1024,
        output=[
            dict(
                id="msg_test",
                type="message",
                role="assistant",
                status="completed",
                content=[dict(type="output_text", text="ABSTAIN", annotations=[])],
            )
        ],
        usage=dict(
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            input_tokens_details=dict(cached_tokens=10, cache_write_tokens=30),
        ),
    )


def test_entire_sdk_prefix_and_rerun(pilot, worksheet, tmp_path):
    plan = pilot.readiness()
    sent = []

    def handler(req):
        idx = len(sent)
        expected = plan["requests"][idx]
        assert json.loads(req.content) == expected["body"]
        assert digest(json.loads(req.content)) == expected["body_sha256"]
        assert (tmp_path / pilot.RUN_ID / f"attempt-{expected['case_id']}.json").exists()
        sent.append(expected["case_id"])
        raw = mock_response()
        if idx % 2 == 0:
            raw["usage"]["input_tokens_details"]["cache_write_tokens_details"] = {
                "ttl_30m_tokens": 30,
                "ttl_12h_tokens": 0,
            }
        if idx == 3:
            raw["output"][0]["content"][0]["text"] = json.loads(
                expected["body"]["input"][1]["content"]
            )["candidates"][0]["id"]
        return httpx.Response(200, json=raw)

    def run():
        return pilot.execute(
            digest(plan),
            worksheet,
            test_transport=httpx.MockTransport(handler),
            test_results=tmp_path,
        )

    report = run()
    assert report["run_status"] == "completed" and len(sent) == report["attempts"] == 4
    assert report["usage_based_usd"] is None and report["provider_billed_usd"] is None
    assert report["policy_based_usd"] == pytest.approx(0.0000794)
    assert report["conservative_charge_usd"] == pytest.approx(plan["prefix_reserve_usd"])
    assert [len(p["selected_ids"]) for p in report["policies"]] == [0, 1, 2, 4]
    records, warnings = read_records(tmp_path / pilot.RUN_ID)
    assert not warnings and [r.case_id for r in records] == sent
    assert all(
        r.response.effective_options["sent"]["prompt_cache_options"]["ttl"] == "30m"
        for r in records
    )
    with pytest.raises(FileExistsError):
        run()
    assert len(sent) == 4


@pytest.mark.parametrize(
    "fault",
    [
        "http429",
        "network",
        "model",
        "store",
        "tier",
        "missing",
        "partition",
        "total",
        "output",
        "cache",
        "invalid",
        "incomplete",
        "refusal",
    ],
)
def test_abort_once_retain_record(pilot, worksheet, tmp_path, fault):
    calls = []

    def handler(req):
        calls.append(req)
        raw = mock_response()
        if fault == "http429":
            return httpx.Response(429, json={"error": {"message": "offline throttle"}})
        if fault == "network":
            raise httpx.ConnectError("offline", request=req)
        if fault == "model":
            raw["model"] = "another-model"
        if fault == "store":
            raw["store"] = True
        if fault == "tier":
            raw["service_tier"] = "fast"
        if fault == "missing":
            raw.pop("usage")
        if fault == "partition":
            raw["usage"]["input_tokens_details"]["cached_tokens"] = 200
        if fault == "total":
            raw["usage"]["total_tokens"] = 999
        if fault == "output":
            raw["usage"].update(output_tokens=1025, total_tokens=1125)
        if fault == "cache":
            raw["prompt_cache_options"] = {"ttl": "12h", "mode": "implicit"}
        if fault == "invalid":
            raw["output"][0]["content"][0]["text"] = "unknown"
        if fault == "incomplete":
            raw["status"] = "incomplete"
        if fault == "refusal":
            raw["output"][0]["content"] = [{"type": "refusal", "refusal": "no"}]
        return httpx.Response(200, json=raw)

    result = pilot.execute(
        digest(pilot.readiness()),
        worksheet,
        test_transport=httpx.MockTransport(handler),
        test_results=tmp_path,
    )
    assert result["run_status"] == "failed" and result["attempts"] == len(calls) == 1
    records, _ = read_records(tmp_path / pilot.RUN_ID)
    assert len(records) == 1
    assert result["conservative_charge_usd"] > 0 and result["policies"] is None


def test_review_and_approval_before_transport(pilot, worksheet, tmp_path):
    opts = dict(
        test_transport=httpx.MockTransport(lambda r: pytest.fail("unexpected send")),
        test_results=tmp_path,
    )
    frozen = digest(pilot.readiness())
    with pytest.raises(ValueError, match="approval"):
        pilot.execute("wrong", worksheet, **opts)
    module = importlib.import_module("experiments.entity_matching.ror.human_review")
    with pytest.raises(ValueError, match="incomplete"):
        pilot.execute(frozen, module.FORM, **opts)
    worksheet.write_text(
        worksheet.read_text(encoding="utf8").replace(
            "Decision: NO_SUPPORTED_MATCH", "Decision: INSUFFICIENT", 1
        ),
        encoding="utf8",
    )
    with pytest.raises(ValueError, match="recalibrate"):
        pilot.execute(frozen, worksheet, **opts)
    assert not (tmp_path / pilot.RUN_ID).exists()


@pytest.mark.parametrize("fault", ["endpoint", "body", "budget", "count", "retry"])
def test_wire_guard_blocks_before_network(pilot, tmp_path, fault):
    entries = pilot.readiness()["requests"][:4]
    guard = pilot.GuardedTransport(
        httpx.MockTransport(lambda r: pytest.fail("wire escape")), entries, tmp_path
    )
    body = entries[0]["body"].copy()
    url = pilot.ENDPOINT
    if fault == "body":
        body["prompt_cache_options"] = {"ttl": "12h"}
    if fault == "endpoint":
        url = "https://example.org/v1/responses"
    if fault == "budget":
        guard.charged = pilot.CAP
    if fault == "count":
        guard.sent = 4
    if fault == "retry":
        guard.pending = entries[0]
    with pytest.raises(ValueError):
        guard.handle_request(httpx.Request("POST", url, json=body))
    assert not list(tmp_path.glob("attempt-*.json"))
