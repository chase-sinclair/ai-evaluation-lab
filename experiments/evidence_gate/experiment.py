import json

from eval_lab.contracts import GradeResult, ModelRequest
from eval_lab.contracts import TestCase as Case

GATE = (
    "Pass if the excerpts support at least one requested answer, or they establish "
    "specific alternatives that a focused clarification could resolve. Block if they "
    "supply only related information or lack evidence for every requested answer. Output"
    " exactly PASS or BLOCK."
)
GEN = (
    "Answer only from the supplied excerpts. Cite each policy claim with its bracketed "
    "passage ID, e.g. [D01]. Give supported parts and identify missing facts. Ask a "
    "focused question or explain accurate conditional alternatives if a detail is "
    "unspecified. Decline unsupported requests."
)
REFERRAL = (
    "The available policy excerpts do not establish an answer. Please check with the service desk."
)


class Experiment:
    def __init__(self, spec, directory):
        self.spec = spec
        self.directory = directory

    def load_cases(self):
        data = json.loads((self.directory / "fixtures.json").read_bytes())
        return [
            Case(
                id=r["id"],
                dataset_id="alder",
                dataset_version="1.0",
                split="development",
                task_input={
                    "question": r["question"],
                    "excerpts": [{"id": i, "text": data["corpus"][i]} for i in r["packet"]],
                },
                ground_truth={k: r[k] for k in ("key", "expected_gate", "gap")},
                provenance={"source": "original Alder Desk v1.0"},
            )
            for r in data["questions"]
        ]

    def validate(self, cases):
        if {c.id for c in cases} != {f"{family}{n}" for family in "APMU" for n in range(1, 7)}:
            raise ValueError("Expected the approved 24 questions")
        for c in cases:
            if len({x["id"] for x in c.task_input["excerpts"]}) != 3:
                raise ValueError("Expected three distinct passages")

    def build_request(self, case, condition):
        gate = condition.id == "gate"
        return ModelRequest(
            model=condition.model,
            output_format="text",
            max_output_tokens=256 if gate else 512,
            messages=[
                {"role": "system", "content": GATE if gate else GEN},
                {"role": "user", "content": json.dumps(case.task_input, ensure_ascii=False)},
            ],
        )

    def grade(self, case, response, *, request):
        value = response.parsed
        gate = request.messages[0]["content"] == GATE
        valid = (
            isinstance(value, str)
            and bool(value.strip())
            and (not gate or value in ("PASS", "BLOCK"))
        )
        passed = valid and (not gate or value == case.ground_truth["expected_gate"])
        return GradeResult(
            passed=passed, valid_output=valid, score=float(passed), grader_version="1.0"
        )
