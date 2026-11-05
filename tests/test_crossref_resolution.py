import csv
import importlib
import json
from pathlib import Path

import httpx
import openai
import pytest

from eval_lab.contracts import ModelResponse
from eval_lab.core.hashes import digest
from eval_lab.core.result_store import read_records


@pytest.fixture
def ror(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    return importlib.import_module("experiments.entity_matching.ror.__main__")


def test_active_alias_ranking_ties_and_unrestricted_search(tmp_path, ror):
    module = importlib.import_module("experiments.entity_matching.ror.retrieval")
    path = tmp_path / "registry.csv"
    fields = [
        "id",
        "names.types.ror_display",
        "names.types.alias",
        "names.types.label",
        "names.types.acronym",
        "locations.geonames_details.country_code",
        "status",
    ]
    with path.open("w", encoding="utf8", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        for i in reversed(range(7)):
            writer.writerow(
                dict(
                    zip(
                        fields,
                        [
                            f"id-{i}",
                            f"Org {i}",
                            "en: Example Council",
                            "",
                            "",
                            "US",
                            "inactive" if i == 0 else "active",
                        ],
                        strict=True,
                    )
                )
            )
    c, ranks = module.Registry(path).retrieve("Example Council")
    assert [x["id"] for x in c] == [f"id-{i}" for i in range(1, 6)]
    assert ranks["id-6"] == (6, 1.0) and "id-0" not in ranks
    assert all(x["score"] == 1 and "Example Council" in x["aliases"] for x in c)
    core = importlib.import_module("experiments.entity_matching.ror.core")
    assert core.decision({"candidates": c}, (0.75, 0.03))[0] == core.ABSTAIN


def test_frozen_nominations_and_exposure(ror):
    rows = ror.load("dataset.json")["rows"]
    nil = [r for r in rows if not r["output"]]
    assert (len(rows), len(nil), len({r["query"] for r in rows})) == (48, 12, 48)
    assert sum(r["review"] == "excluded" for r in rows) == 10
    assert all(r["review"] in ("excluded", "pending_independent_nil") for r in nil)
    assert len(set(r["output"][0] for r in rows if r["output"])) == 36
    prior = json.loads(Path("docs/audits/phase3c/candidates.json").read_text(encoding="utf8"))
    deny = ror.load("quarantine.json")
    assert {p[k]["seq_no"] for p in prior["candidates"] for k in ("left", "right")} <= set(
        deny["development_only_seq_nos"]
    )
    assert {c["id"] for r in rows for c in r["candidates"]} <= set(deny["blocked_keys"])
    assert {r["seq_no"] for r in rows} <= set(deny["development_only_seq_nos"])
    assert all(set(r) == {"seq_no", "query"} for r in ror.load("blind_review.json"))


def test_proposal_hashes_and_no_label_leak(ror):
    prep = importlib.import_module("experiments.entity_matching.ror.prepare")
    frozen = ror.load("proposal.json")
    assert prep.proposal() == frozen and 0 < frozen["reserve_usd"] < 0.15
    exp = ror.experiment(True)
    condition = exp.spec.conditions[0]
    for c in exp.load_cases():
        req = exp.build_request(c, condition)
        poisoned = c.model_copy(
            update={
                "ground_truth": {"resolution": "CANARY-GOLD"},
                "provenance": {"secret": "HIDDEN"},
                "task_input": {**c.task_input, "target": "CANARY-GOLD"},
            }
        )
        assert exp.build_request(poisoned, condition) == req
        data = json.loads(req.messages[1]["content"])
        assert set(data) == {"name", "candidates"}
        assert all(set(t) == {"id", "name", "aliases", "country"} for t in data["candidates"])
        offered = {t["id"] for t in data["candidates"]}
        assert len(offered) == len(data["candidates"]) == 5
        for response, valid in (
            (ModelResponse(parsed=next(iter(offered))), True),
            (ModelResponse(parsed="ABSTAIN"), True),
            (ModelResponse(parsed="https://ror.org/000000000"), False),
            (ModelResponse(parsed={"id": "ABSTAIN"}), False),
            (ModelResponse(parsed="ABSTAIN", finish_status="incomplete"), False),
        ):
            assert exp.grade(c, response, request=req).valid_output == valid


def test_full_mock_replay_real_labels(ror, tmp_path):
    directory, reports = ror.demo(tmp_path)
    records, warnings = read_records(directory)
    assert len(records) == 38 and not warnings
    policies = reports["policies"]
    assert [len(p["selected_ids"]) for p in policies] == [0, 9, 19, 38]
    for p in policies:
        assert p["selected_ids"] == policies[-1]["selected_ids"][: len(p["selected_ids"])]
        assert p["mock_charge_usd"] == 0 and p["measured_provider_usd"] is None
        assert p["marginal_f1_per_usd"] is None
    m = policies[0]["metrics"]
    assert (
        m["positive"],
        m["retrieved"],
        m["correct_link"],
        m["incorrect_link"],
        m["correct_abstention"],
    ) == (30, 29, 26, 3, 6)
    assert ror.load("baseline.json")["retrieval_misses"] == [970]
    assert policies[-1]["fallbacks"] == {"invalid_output": 8}
    assert policies[-1]["input_tokens"] is None and policies[-1]["output_tokens"] is None
    assert [p["metrics"] for p in ror.analyze(directory)["policies"]] == [
        p["metrics"] for p in policies
    ]
    exp = ror.experiment()
    thresholds = ror.load("baseline.json")["calibration"]["thresholds"]
    absent = ror.replay(exp, records[:-1], thresholds)[-1]
    assert (
        absent["usage_estimated_or_mock_usd"] is None and absent["fallbacks"]["missing_record"] == 1
    )
    with pytest.raises(ValueError, match="Duplicate"):
        ror.replay(exp, records + [records[0]], thresholds)
    exp.cases = [
        c.model_copy(update={"ground_truth": {"resolution": "hidden"}}) for c in exp.load_cases()
    ]
    assert ror.replay(exp, [], thresholds)[-1]["selected_ids"] == policies[-1]["selected_ids"]


def test_frozen_sdk_body_and_unknown_cache_writes(ror):
    from scripts.cache_policy_proposal import assess

    exp = ror.experiment(True)
    sample = ror.load("proposal.json")["requests"][0]
    body = sample["body"]
    raw = {
        "id": "resp_local",
        "object": "response",
        "created_at": 0,
        "model": "gpt-6-luna",
        "status": "completed",
        "output": [],
        "service_tier": "default",
        "prompt_cache_retention": "24h",
        "usage": {
            "input_tokens": 250,
            "output_tokens": 10,
            "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 100},
        },
    }

    def handler(request):
        assert json.loads(request.content) == body
        return httpx.Response(200, json=raw)

    with openai.OpenAI(
        api_key="local-test",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    ) as client:
        observed = client.responses.create(**body).model_dump(mode="json")

    def evaluate(payload, response):
        return assess(payload, response, exp.spec.pricing, sample["body_sha256"], text_only=True)

    estimate = evaluate(body, observed)
    assert estimate["continue_eligible"] and estimate["usage_priced_estimate_usd"] is None
    assert estimate["provider_reported_cost_usd"] is None and estimate[
        "policy_estimate_usd"
    ] == pytest.approx(0.0000325)
    assert estimate["spending_charge_usd"] >= sample["reserve_usd"]
    assert not evaluate(body, {**observed, "service_tier": "fast"})["continue_eligible"]
    assert not evaluate({**body, "prompt_cache_options": {"ttl": "12h"}}, observed)[
        "continue_eligible"
    ]
    assert digest(body) == sample["body_sha256"]
