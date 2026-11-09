import json

from eval_lab.contracts import GradeResult, ModelRequest
from eval_lab.contracts import TestCase as Case
from eval_lab.core.hashes import canonical


class Experiment:
    def __init__(self, spec, directory):
        self.spec = spec
        self.directory = directory
        self.protocol = json.loads((directory / "protocol.json").read_bytes())
        self.answers = {}

    def load_cases(self):
        return [
            Case(
                id=row["id"],
                dataset_id=self.spec.dataset.id,
                dataset_version="1.0",
                task_input={
                    "question": row["question"],
                    "excerpts": dict(zip(("1", "2"), row["packet"], strict=True)),
                },
                ground_truth={"key": row["key"], "risk": row["risk"]},
                split=row["id"][0],
                provenance={"workflow": row["workflow"], "source": "963cade"},
            )
            for row in self.protocol["cases"]
        ]

    def validate(self, cases):
        if {c.id for c in cases} != {f"{g}{n:02}" for g in "RIC" for n in range(1, 13)}:
            raise ValueError("Unexpected cohort")

    def build_request(self, case, condition):
        stage = condition.id
        data = dict(case.task_input)
        if stage == "verifier":
            data["candidate_reply"] = self.answers[case.id]
        prompts = self.protocol["prompts"]
        return ModelRequest(
            model=condition.model,
            output_format="text",
            max_output_tokens=512 if stage == "generator" else 256,
            messages=[
                {"role": "system", "content": prompts["common"] + "\n" + prompts[stage]},
                {"role": "user", "content": canonical(data)},
            ],
        )

    def grade(self, case, response, *, request):
        value = response.parsed
        valid = (
            isinstance(value, str)
            and bool(value.strip())
            and (request.max_output_tokens == 512 or value in ("PASS", "BLOCK"))
        )
        return GradeResult(
            passed=valid, valid_output=valid, score=float(valid), grader_version="1.0"
        )
