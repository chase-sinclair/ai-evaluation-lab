import pytest

from eval_lab.contracts import ExperimentSpec, Usage
from eval_lab.core.budgets import cost, preflight
from eval_lab.core.runner import run, validate


def live_spec(experiment, spend=10):
    data = experiment.spec.model_dump()
    for condition in data["conditions"]:
        condition.update(provider="openai", model="test-exact-model")
    data.update(
        max_spend_usd=spend,
        pricing={
            "version": "test-only",
            "verified_date": "2026-11-03",
            "source_url": "https://example.test",
            "model": "test-exact-model",
            "input_usd_per_million": 1,
            "output_usd_per_million": 2,
        },
    )
    return ExperimentSpec.model_validate(data)


def test_opt_in_spend_and_model_gates(experiment):
    experiment.spec = live_spec(experiment)
    requests = [t[3] for t in validate(experiment)[1]]
    with pytest.raises(ValueError, match="opt-in"):
        preflight(experiment.spec, requests, "live", False)
    with pytest.raises(ValueError, match="positive"):
        preflight(experiment.spec.model_copy(update={"max_spend_usd": 0}), requests, "live", True)
    with pytest.raises(ValueError, match="Projected"):
        preflight(
            experiment.spec.model_copy(update={"max_spend_usd": 1e-9}), requests, "live", True
        )
    assert preflight(experiment.spec, requests, "live", True) > 0
    assert cost(Usage(input_tokens=1000, output_tokens=500), experiment.spec.pricing) == 0.002
    requests[0] = requests[0].model_copy(update={"model": "different"})
    with pytest.raises(ValueError, match="exact model"):
        preflight(experiment.spec, requests, "live", True)


def test_request_cap(experiment, tmp_path):
    experiment.spec = experiment.spec.model_copy(update={"max_requests": 14})
    with pytest.raises(ValueError, match="max_requests"):
        run(experiment, results=tmp_path)
    assert not list(tmp_path.iterdir())


def test_dry_run_never_constructs_provider(experiment, tmp_path):
    def forbidden():
        raise AssertionError("Dry run created a provider")

    for mode in ("mock", "live"):
        if mode == "live":
            experiment.spec = live_spec(experiment)
        outcome = run(
            experiment,
            results=tmp_path,
            dry_run=True,
            mode=mode,
            live=mode == "live",
            provider_factory=forbidden,
        )
        assert outcome["provider_calls"] == 0
        assert outcome["planned_trials"] == 15
    assert not list(tmp_path.iterdir())
