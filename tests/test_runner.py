import json

import pytest
from test_budget import live_spec

from eval_lab.contracts import ModelResponse, Usage
from eval_lab.core.result_store import read_records
from eval_lab.core.runner import run
from eval_lab.providers.mock import MockProvider


def test_interrupt_preserves_partial_run(experiment, tmp_path):
    class Interrupting(MockProvider):
        count = 0

        def generate(self, request):
            self.count += 1
            if self.count == 3:
                raise KeyboardInterrupt
            return super().generate(request)

    result = run(
        experiment, results=tmp_path, run_id="interrupt", provider_factory=lambda: Interrupting(42)
    )
    records, _ = read_records(tmp_path / "interrupt")
    assert len(records) == 3 and records[-1].status == "interrupted"
    assert result["run_status"] == "interrupted" and result["unattempted"] == 12
    assert (tmp_path / "interrupt" / "manifest.json").exists()
    original = (tmp_path / "interrupt" / "records.jsonl").read_bytes()
    with pytest.raises(FileExistsError):
        run(experiment, results=tmp_path, run_id="interrupt")
    assert (tmp_path / "interrupt" / "records.jsonl").read_bytes() == original


def test_provider_and_grader_failures_are_distinct(experiment, tmp_path, monkeypatch):
    class Broken:
        def generate(self, request):
            raise TimeoutError("secret-must-not-be-recorded")

    result = run(experiment, results=tmp_path, run_id="provider", provider_factory=Broken)
    assert result["status_counts"] == {"provider_error": 15}
    assert result["end_to_end_success_rate"] == 0
    assert "secret-must-not" not in (tmp_path / "provider" / "records.jsonl").read_text()

    def broken_grade(*args):
        raise RuntimeError("bad grader")

    monkeypatch.setattr(experiment, "grade", broken_grade)
    result = run(experiment, results=tmp_path, run_id="grader")
    assert result["status_counts"] == {"grader_error": 15}


def test_provider_initialization_failure_preserves_plan(experiment, tmp_path):
    def broken():
        raise RuntimeError("construction failed")

    result = run(experiment, results=tmp_path, run_id="failed", provider_factory=broken)
    assert result["run_status"] == "failed" and result["unattempted"] == 15
    assert (tmp_path / "failed" / "plan.json").exists()


@pytest.mark.parametrize(
    "usage,expected",
    [(None, "failed"), (Usage(input_tokens=20_000_000, output_tokens=0), "budget_stopped")],
)
def test_live_unknown_usage_and_spend_stop(experiment, tmp_path, usage, expected):
    experiment.spec = live_spec(experiment)

    class FakeLive:
        def generate(self, request):
            return ModelResponse(parsed={"tool_calls": []}, usage=usage)

    result = run(experiment, results=tmp_path, mode="live", live=True, provider_factory=FakeLive)
    assert result["run_status"] == expected and result["recorded"] == 1
    if usage is None:
        assert result["estimated_cost_usd"] is None


def test_incomplete_no_call_is_not_success(experiment, tmp_path):
    class Incomplete:
        def generate(self, request):
            return ModelResponse(parsed={"tool_calls": []}, finish_status="incomplete")

    result = run(experiment, results=tmp_path, provider_factory=Incomplete)
    assert result["status_counts"] == {"invalid_output": 15}


def test_torn_last_line_is_reported(experiment, tmp_path):
    run(experiment, results=tmp_path, run_id="torn")
    with (tmp_path / "torn" / "records.jsonl").open("ab") as stream:
        stream.write(b'{"run_id":')
    records, warnings = read_records(tmp_path / "torn")
    assert len(records) == 15 and warnings
    with (tmp_path / "torn" / "records.jsonl").open("ab") as stream:
        stream.write(b"\n")
    with pytest.raises(ValueError):
        read_records(tmp_path / "torn")


def test_second_experiment_without_runner_changes(experiment, tmp_path):
    class TextExperiment:
        spec = experiment.spec.model_copy(update={"id": "text", "grader_version": "text-v1"})
        directory = experiment.directory

        def load_cases(self):
            return experiment.load_cases()[:1]

        def validate(self, cases):
            pass

        def build_request(self, case, condition):
            from eval_lab.contracts import ModelRequest

            return ModelRequest(
                model=condition.model,
                messages=[{"role": "user", "content": "ping"}],
                output_format="text",
            )

        def grade(self, case, response):
            from eval_lab.contracts import GradeResult

            passed = response.parsed == "pong"
            return GradeResult(passed=passed, score=float(passed), grader_version="text-v1")

    class TextProvider:
        def generate(self, request):
            return ModelResponse(parsed="pong")

    result = run(TextExperiment(), results=tmp_path, provider_factory=TextProvider)
    assert result["correct"] == 3
    manifest = json.loads((tmp_path / result["run_id"] / "manifest.json").read_text())
    assert manifest["experiment"]["id"] == "text"
