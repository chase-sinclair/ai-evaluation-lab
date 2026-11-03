import json
from pathlib import Path

from typer.testing import CliRunner

from eval_lab.cli import app
from eval_lab.core.hashes import digest
from eval_lab.core.result_store import read_records
from eval_lab.core.runner import run

ROOT = Path(__file__).resolve().parents[1]


def test_exact_cli_flow(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    runner = CliRunner()
    assert runner.invoke(app, ["--help"]).exit_code == 0
    assert "tool_selection" in runner.invoke(app, ["list"]).stdout
    validation = runner.invoke(app, ["validate", "tool_selection"])
    assert validation.exit_code == 0 and json.loads(validation.stdout)["trials"] == 15
    arguments = ["run", "tool_selection", "--results", str(tmp_path)]
    dry = runner.invoke(app, [*arguments, "--dry-run"])
    assert dry.exit_code == 0 and json.loads(dry.stdout)["provider_calls"] == 0
    assert not list(tmp_path.iterdir())
    result = runner.invoke(app, [*arguments, "--mode", "mock"])
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert data["recorded"] == 15 and data["correct"] == 10
    assert data["estimated_cost_usd"] == 0 and data["usage_records"] == 0
    records, warnings = read_records(tmp_path / data["run_id"])
    assert not warnings
    assert len({r.trial_id for r in records}) == 15
    assert all(r.grade.passed for r in records if r.case_id == "no_call")
    assert all(not r.grade.passed for r in records if r.case_id == "ticket")
    for record in records:
        assert record.request_hash == digest(record.request)
        assert record.response.latency_ms >= 0 and record.ground_truth_ref
        assert len(record.offered_tool_ids) == int(record.condition_id.split("_")[1])
    summary = runner.invoke(app, ["summarize", data["run_id"], "--results", str(tmp_path)])
    assert summary.exit_code == 0
    assert json.loads(summary.stdout)["correct"] == 10
    assert runner.invoke(app, [*arguments, "--mode", "live"]).exit_code != 0
    assert runner.invoke(app, ["summarize", "../escape", "--results", str(tmp_path)]).exit_code != 0


def test_reproducible_predictions_and_order(experiment, tmp_path):
    results = [run(experiment, results=tmp_path, run_id=name) for name in ("one", "two")]
    records = [read_records(tmp_path / result["run_id"])[0] for result in results]
    for left, right in zip(*records, strict=True):
        assert left.trial_id == right.trial_id
        assert left.request_hash == right.request_hash
        assert left.response.parsed == right.response.parsed
        assert left.grade == right.grade


def test_mock_never_initializes_live_adapter(experiment, tmp_path, monkeypatch):
    from eval_lab.providers import openai_adapter

    def forbidden(*args, **kwargs):
        raise AssertionError("Mock called live adapter")

    monkeypatch.setattr(openai_adapter, "OpenAIProvider", forbidden)
    assert run(experiment, results=tmp_path)["recorded"] == 15
