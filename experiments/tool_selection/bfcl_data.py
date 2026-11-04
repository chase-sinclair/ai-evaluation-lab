"""Bounded, offline importer for the audited BFCL development subset only."""

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from eval_lab.contracts import TestCase as Case
from eval_lab.core.hashes import canonical, digest

REVISION = "f7cf7359b7ac615a0b294831c5ba2bc95ee4a000"
BASE_URL = (
    f"https://github.com/ShishirPatil/gorilla/blob/{REVISION}/berkeley-function-call-leaderboard/"
)
DATASET_ID = "bfcl-development"
VERSION = "0.2.0"
DIRECTORY = Path(__file__).resolve().parent / "bfcl"
INPUT_PATH = "bfcl_eval/data/BFCL_v4_simple_python.json"
NO_CALL_PATH = "bfcl_eval/data/BFCL_v4_irrelevance.json"
ANSWER_PATH = "bfcl_eval/data/possible_answer/BFCL_v4_simple_python.json"
CHECKER_PATH = "bfcl_eval/eval_checker/ast_eval/ast_checker.py"
EXCLUDED = {
    "simple_python_5": "All roots vs default real-only root_type is ambiguous.",
    "simple_python_14": "Symbolic derivative vs default evaluation at x=0 is ambiguous.",
}
POSITIVE_IDS = tuple(f"simple_python_{i}" for i in range(16) if i not in (5, 14))
NO_CALL_IDS = tuple(f"irrelevance_{i}" for i in range(4))
SELECTED_IDS = POSITIVE_IDS + NO_CALL_IDS
MAX_SOURCE_BYTES = 400_000


def wire_name(name: str) -> str:
    converted = name.replace(".", "_")
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", converted):
        raise ValueError("Unsupported function name")
    return converted


def convert_schema(schema: dict[str, Any], *, root: bool = True) -> dict[str, Any]:
    """Fail closed outside this subset's shallow Python schema vocabulary."""
    kind = schema.get("type")
    permitted = {"type", "description", "default", "enum"}
    if root:
        if kind != "dict":
            raise ValueError("Expected BFCL dict parameters")
        permitted |= {"properties", "required"}
    elif kind == "array":
        permitted.add("items")
        if schema["items"].get("type") not in {"float", "integer", "string", "boolean"}:
            raise ValueError("Only primitive array elements are supported")
    elif kind not in {"integer", "float", "string", "boolean"}:
        raise ValueError("Unsupported BFCL parameter type")
    if set(schema) - permitted:
        raise ValueError("Unsupported BFCL schema keywords")
    result = copy.deepcopy(schema)
    result["type"] = {"dict": "object", "float": "number"}.get(kind, kind)
    if root:
        properties, required = schema["properties"], schema["required"]
        if not set(required) <= set(properties) or len(set(required)) != len(required):
            raise ValueError("Invalid required parameters")
        result["properties"] = {
            name: convert_schema(value, root=False) for name, value in properties.items()
        }
        result["additionalProperties"] = False
    elif kind == "array":
        result["items"] = convert_schema(schema["items"], root=False)
    Draft202012Validator.check_schema(result)
    return result


def convert_tool(function: dict[str, Any]) -> dict[str, Any]:
    if set(function) != {"name", "description", "parameters"}:
        raise ValueError("Unsupported function fields")
    return {
        "type": "function",
        "name": wire_name(function["name"]),
        "description": function["description"],
        "parameters": convert_schema(function["parameters"]),
        "strict": False,  # Responses otherwise normalizes optional fields into required ones.
    }


def index_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {}
    for row in rows:
        if row["id"] in result:
            raise ValueError(f"Duplicate source ID: {row['id']}")
        result[row["id"]] = row
    return result


def make_cases(
    inputs: list[dict[str, Any]], answers: list[dict[str, Any]], lock: dict[str, Any]
) -> list[Case]:
    """Join by ID, retain original rows, and separate labels from task inputs."""
    if lock["revision"] != REVISION:
        raise ValueError("Unpinned BFCL revision")
    source, gold = index_rows(inputs), index_rows(answers)
    if not set(SELECTED_IDS) <= source.keys() or not set(POSITIVE_IDS) <= gold.keys():
        raise ValueError("Missing selected input or answer")
    cases = []
    for identifier in SELECTED_IDS:
        row = source[identifier]
        if set(row) != {"id", "question", "function"} or len(row["function"]) != 1:
            raise ValueError("Only audited single-function rows are supported")
        if len(row["question"]) != 1 or len(row["question"][0]) != 1:
            raise ValueError("Only audited single-turn rows are supported")
        message = row["question"][0][0]
        if set(message) != {"role", "content"} or message["role"] != "user":
            raise ValueError("Expected user message")
        if not isinstance(message["content"], str) or not message["content"]:
            raise ValueError("Expected nonempty question")
        original = row["function"][0]
        converted = convert_tool(original)
        no_call = identifier in NO_CALL_IDS
        answer = None if no_call else gold[identifier]
        receipt = lock["selected_rows"][identifier]
        if digest(row) != receipt["input"] or digest(answer) != receipt["answer"]:
            raise ValueError("Selected row differs from pinned source")
        if not no_call:
            alternatives = answer["ground_truth"]
            if len(alternatives) != 1 or set(alternatives[0]) != {original["name"]}:
                raise ValueError("Expected a single matching answer function")
            params = alternatives[0][original["name"]]
            if set(params) != set(original["parameters"]["properties"]):
                raise ValueError("Answer/schema parameters differ")
            if any(not isinstance(v, list) or not v for v in params.values()):
                raise ValueError("Expected nonempty answer alternatives")
        path = NO_CALL_PATH if no_call else INPUT_PATH
        cases.append(
            Case(
                id=identifier,
                dataset_id=DATASET_ID,
                dataset_version=VERSION,
                split="development",
                task_input={"messages": row["question"][0], "function": original},
                ground_truth={"bfcl": [] if no_call else answer["ground_truth"]},
                provenance={
                    "source_revision": REVISION,
                    "source_id": identifier,
                    "source_url": BASE_URL + path,
                    "source_file_sha256": lock["files"][path],
                    "source_row_sha256": digest(row),
                    "original_row": row,
                    "original_answer": answer,
                    "answer_row_sha256": digest(answer),
                    "answer_source_url": BASE_URL
                    + ("bfcl_eval/eval_checker/eval_runner.py" if no_call else ANSWER_PATH),
                    "answer_file_sha256": None if no_call else lock["files"][ANSWER_PATH],
                    "answer_rule": "category-zero-calls" if no_call else "official-alternatives",
                    "name_map": {original["name"]: converted["name"]},
                    "license": "Apache-2.0",
                    "attribution": "Berkeley Function Calling Leaderboard, Gorilla contributors",
                    "semantic_review": "docs/bfcl_phase2_design.md; audited 29 record-only tools",
                    "no_call_review": no_call,
                    "transform_version": VERSION,
                },
            )
        )
    return cases


def import_cache(source_directory: Path) -> list[Case]:
    lock = json.loads((DIRECTORY / "sources.lock.json").read_text(encoding="utf-8"))
    rows = {}
    for path in (INPUT_PATH, NO_CALL_PATH, ANSWER_PATH):
        source = source_directory / path
        if source.stat().st_size > MAX_SOURCE_BYTES:
            raise ValueError("Source exceeds bounded importer size")
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != lock["files"][path]:
            raise ValueError(f"Source hash mismatch: {path}")
        rows[path] = [json.loads(line) for line in data.decode("utf-8").splitlines()]
    return make_cases(rows[INPUT_PATH] + rows[NO_CALL_PATH], rows[ANSWER_PATH], lock)


def serialize_cases(cases: list[Case]) -> str:
    return "".join(canonical(case) + "\n" for case in cases)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = import_cache(args.source_dir)
    with args.output.open("x", encoding="utf-8", newline="\n") as output:
        output.write(serialize_cases(cases))
    print(f"Imported {len(cases)} development cases; zero network/model calls.")


if __name__ == "__main__":
    main()
