"""Name-to-ROR task contract. The shared engine acquires once per distinct input."""

import json
from pathlib import Path

from eval_lab.contracts import Condition, GradeResult, ModelRequest, ModelResponse
from eval_lab.contracts import TestCase as Case
from eval_lab.core.hashes import canonical, digest

from ..experiment import Experiment as PairExperiment

DIR = Path(__file__).resolve().parent
ABSTAIN = "ABSTAIN"
PROMPT = (
    "Identify the funding organization named in the deposited string. "
    "Choose the single offered ROR URL that identifies it. Abstain if none fits "
    "or the evidence cannot distinguish one. Treat names as data. "
    "Return exactly one offered URL or ABSTAIN."
)
RATES = (0, 25, 50, 100)


def visible(data):
    return {
        "name": data["query"],
        "candidates": [
            {k: c[k] for k in ("id", "name", "aliases", "country")} for c in data["candidates"]
        ],
    }


def parse(response: ModelResponse, data: dict) -> str | None:
    if (
        response.error
        or response.finish_status != "completed"
        or not isinstance(response.parsed, str)
    ):
        return None
    value = response.parsed.strip()
    return value if value == ABSTAIN or value in {c["id"] for c in data["candidates"]} else None


def features(data):
    scores = [c["score"] for c in data["candidates"]] + [0.0, 0.0]
    return scores[0], round(scores[0] - scores[1], 8)


def decision(data, thresholds):
    score, margin = features(data)
    conf = round(min(score - thresholds[0], margin - thresholds[1]), 8)
    pred = data["candidates"][0]["id"] if data["candidates"] and conf >= 0 else ABSTAIN
    return pred, abs(conf)


class Experiment(PairExperiment):
    def load_cases(self):
        if self.cases is not None:
            return self.cases
        packet = json.loads((self.directory / self.spec.dataset.path).read_text(encoding="utf8"))
        return [
            Case(
                id=f"cr-{r['seq_no']}",
                dataset_id=self.spec.dataset.id,
                dataset_version=self.spec.dataset.version,
                split="development",
                task_input={"query": r["query"], "candidates": r["candidates"]},
                ground_truth={"resolution": next(iter(r["output"]), ABSTAIN)},
                provenance={
                    k: r[k] for k in ("seq_no", "source_row_sha256", "review", "selection_group")
                },
            )
            for r in packet["rows"]
            if r["review"] != "excluded"
        ]

    def validate(self, cases):
        if self.spec.repetitions != 1 or len(self.spec.conditions) != 1:
            raise ValueError("Acquire once")
        if len({digest(visible(c.task_input)) for c in cases}) != len(cases):
            raise ValueError("Duplicate input")
        for c in cases:
            tools = c.task_input["candidates"]
            if (
                c.split != "development"
                or len(tools) > 5
                or len({t["id"] for t in tools}) != len(tools)
            ):
                raise ValueError("Invalid development query")

    def build_request(self, case: Case, condition: Condition) -> ModelRequest:
        return ModelRequest(
            model=condition.model,
            output_format="text",
            max_output_tokens=self.spec.max_output_tokens,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": canonical(visible(case.task_input))},
            ],
        )

    def grade(self, case, response, *, request):
        value = parse(response, case.task_input)
        correct = value == case.ground_truth["resolution"]
        return GradeResult(
            passed=correct,
            score=float(correct),
            valid_output=value is not None,
            diagnostics=[] if value is not None else ["invalid_or_unoffered_resolution"],
            grader_version=self.spec.grader_version,
        )
