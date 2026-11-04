"""Generate offline conformance evidence using reviewed functions from the pinned checker.

Optional maintenance command, not a test-time download/dependency. No model text is
executed. Only a SHA-256-verified local upstream Python source is compiled, excluding
imports and selecting the Python checker functions/constants explicitly below.
"""

import argparse
import ast
import copy
import hashlib
import json
import re
from enum import Enum
from pathlib import Path
from types import SimpleNamespace

from eval_lab.core.hashes import canonical

from . import bfcl_data as data
from .bfcl_grader import answer_variants
from .prepare_bfcl import load_experiment


class Language(Enum):
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"


def load_oracle(path: Path):
    source = path.read_bytes()
    lock = json.loads((data.DIRECTORY / "sources.lock.json").read_text(encoding="utf-8"))
    if hashlib.sha256(source).hexdigest() != lock["checker_sha256"]:
        raise ValueError("Unpinned checker source")
    tree = ast.parse(source)
    names = {
        "get_possible_answer_type",
        "convert_func_name",
        "type_checker",
        "standardize_string",
        "string_checker",
        "list_checker",
        "dict_checker",
        "list_dict_checker",
        "simple_function_checker",
    }
    tree.body = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names or isinstance(node, ast.Assign)
    ]
    namespace = {
        "re": re,
        "Language": Language,
        "MODEL_CONFIG_MAPPING": {"local-oracle": SimpleNamespace(underscore_to_dot=True)},
    }
    exec(compile(tree, str(path), "exec"), namespace)
    return namespace["simple_function_checker"]


def probes(case) -> list[tuple[str, dict]]:
    variants = answer_variants(case)
    output = [("allowed_variant", variant["tool_calls"][0]) for variant in variants]
    baseline = variants[0]["tool_calls"][0]
    for key in baseline["arguments"]:
        missing = copy.deepcopy(baseline)
        del missing["arguments"][key]
        output.append((f"omit:{key}", missing))
        for value in (None, True, "incorrect", 98765, 1.5, [], [1, 3], [1.0, 3.0]):
            mutation = copy.deepcopy(baseline)
            mutation["arguments"][key] = value
            output.append((f"mutate:{key}", mutation))
    extra = copy.deepcopy(baseline)
    extra["arguments"]["unexpected"] = 1
    output.append(("extra_parameter", extra))
    output.append(("wrong_name", {**baseline, "name": "unknown_function"}))
    for variant in variants:
        normalized = copy.deepcopy(variant["tool_calls"][0])
        normalized["arguments"] = {
            k: v.upper().replace(" ", "  ") if isinstance(v, str) else v
            for k, v in normalized["arguments"].items()
        }
        output.append(("normalized_string", normalized))
    return output


def generate(checker: Path) -> dict:
    oracle = load_oracle(checker)
    vectors = []
    for case in load_experiment().load_cases():
        if not case.ground_truth["bfcl"]:
            continue  # No-call stricter local behavior is tested separately.
        for label, call in probes(case):
            decision = oracle(
                case.task_input["function"],
                {call["name"]: call["arguments"]},
                case.ground_truth["bfcl"][0],
                Language.PYTHON,
                "local-oracle",
            )
            vectors.append(
                {
                    "case_id": case.id,
                    "probe": label,
                    "call": call,
                    "official_passed": decision["valid"],
                }
            )
    return {
        "source_url": data.BASE_URL + data.CHECKER_PATH,
        "source_sha256": hashlib.sha256(checker.read_bytes()).hexdigest(),
        "method": "Pinned official simple_function_checker; Python; dot-to-underscore names",
        "vectors": vectors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = generate(args.checker)
    with args.output.open("x", encoding="utf-8", newline="\n") as output:
        output.write(canonical(evidence) + "\n")
    print(f"Generated {len(evidence['vectors'])} official-checker conformance decisions offline.")


if __name__ == "__main__":
    main()
