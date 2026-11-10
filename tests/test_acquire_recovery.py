import json
import sys
from decimal import Decimal
from pathlib import Path

import httpx
import openai
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import acquire_recovery as live  # noqa: E402


def receipt(n):
    return dict(
        id=f"resp_{n}",
        status="completed",
        model=live.MODEL,
        service_tier="default",
        output=[],
        usage=dict(
            input_tokens=120,
            output_tokens=15,
            total_tokens=135,
            input_tokens_details=dict(cached_tokens=16, cache_write_tokens=4),
        ),
    )


@pytest.mark.parametrize(
    "fault",
    [
        "ok",
        "http",
        "incomplete",
        "model",
        "tier",
        "cache",
        "usage",
        "allowance",
        "duplicate",
        "interrupt",
    ],
)
def test_dispatch(tmp_path, fault):
    rows = live.preflight(live.APPROVAL)["requests"]
    seen = []

    def transport(req):
        n = len(seen)
        assert json.loads(req.content) == rows[n]["body"]
        seen.append(n)
        raw = receipt(n)
        if n == 2:
            if fault == "http":
                return httpx.Response(500, json={"error": {"message": "synthetic failure"}})
            if fault == "interrupt":
                raise KeyboardInterrupt()
            if fault == "incomplete":
                raw["status"] = "incomplete"
            if fault in ("model", "tier"):
                raw["service_tier" if fault == "tier" else "model"] = "wrong"
            if fault == "usage":
                raw["usage"]["total_tokens"] = 99
            if fault == "allowance":
                raw["usage"]["output_tokens"] = 513
                raw["usage"]["total_tokens"] = 633
            if fault == "cache":
                raw["prompt_cache_options"] = {"ttl": "12h"}
            if fault == "duplicate":
                raw["id"] = "resp_0"
        return httpx.Response(200, json=raw, headers={"x-request-id": f"req-{n}"})

    def run():
        return live.acquire(live.APPROVAL, tmp_path, mock_transport=httpx.MockTransport(transport))

    if fault == "ok":
        run()
        assert len(seen) == 24
    else:
        with pytest.raises((ValueError, openai.APIStatusError, KeyboardInterrupt)):
            run()
        assert len(seen) == 3
    seal = json.loads((tmp_path / live.RUN / "seal.json").read_bytes())
    assert seal["planned"] == 24 and seal["attempts"] == len(seen)
    assert seal["status"] == ("completed" if fault == "ok" else "interrupted")
    for n, h in enumerate(seal["receipts"]):
        r = json.loads((tmp_path / live.RUN / f"receipt-{n:02}.json").read_bytes())
        assert live.digest(r) == h and r["body_hash"] == rows[n]["body_sha256"]
    with pytest.raises(ValueError, match="already used"):
        run()


def test_wire_budget_and_proposals():
    row = live.preflight(live.APPROVAL)["requests"][0]
    guard = live.WireGuard()
    guard.pending = row
    changed = dict(row["body"])
    del changed["prompt_cache_options"]
    with pytest.raises(ValueError, match="wire body"):
        guard.check(httpx.Request("POST", live.URL, json=changed))
    with pytest.raises(ValueError, match="budget"):
        live.within_budget(Decimal(".025"), [row])
    with pytest.raises(ValueError, match="digest"):
        live.preflight("other")
    call = dict(type="function_call", name="stop", arguments="bad")
    assert live.proposal({"output": [call, call]}) is None
    assert live.proposal({"output": []}) is None
    assert live.proposal({"output": [call]})["arguments"] is None
