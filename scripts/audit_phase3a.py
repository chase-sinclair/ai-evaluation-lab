"""Offline evidence checks only: no model requests, dataset acquisition or experiment.

Semantic decisions are supplied by the AI-assisted review ledger, not inferred here.
"""

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

from jsonschema import Draft202012Validator

from eval_lab.contracts import ModelResponse
from eval_lab.contracts import TestCase as Case
from eval_lab.core.hashes import canonical, digest
from experiments.tool_selection.bfcl_data import REVISION, convert_tool, wire_name
from experiments.tool_selection.bfcl_grader import grade

DIRECTORY = Path(__file__).resolve().parents[1] / "docs/audits/phase3a"
SELECTED = [f"multiple_{n}" for n in range(57, 100) if n not in (76, 81, 93)]


def load(name: str) -> dict:
    return json.loads((DIRECTORY / name).read_text(encoding="utf-8"))


def verify_source_cache(directory: Path) -> None:
    source = load("source_records.json")
    for path, hash_key, row_key in [
        ("BFCL_v4_multiple.json", "source_file_sha256", "original_row"),
        ("possible_answer/BFCL_v4_multiple.json", "answer_file_sha256", "original_answer"),
    ]:
        with (directory / path).open("rb") as stream:
            raw = stream.read(400_001)
        assert len(raw) <= 400_000, "Source exceeds bounded audit size"
        # Recognize exactly one cache-added final LF, not arbitrary source normalization.
        if hashlib.sha256(raw).hexdigest() != source[hash_key] and raw.endswith(b"\n"):
            raw = raw[:-1]
        assert hashlib.sha256(raw).hexdigest() == source[hash_key], "Source hash mismatch"
        indexed = {r["id"]: r for r in map(json.loads, raw.splitlines())}
        assert all(indexed[r["source_id"]] == r[row_key] for r in source["records"])


def audit() -> dict:
    source, review, catalog = (
        load("source_records.json"),
        load("review.json"),
        load("catalogs.json"),
    )
    assert source["source_revision"] == REVISION
    assert [r["source_id"] for r in source["records"]] == SELECTED
    assert [r["source_id"] for r in review["records"]] == SELECTED
    rows = {r["source_id"]: r for r in source["records"]}
    judgments = {r["source_id"]: r for r in review["records"]}
    tools, names, incompatible = {}, defaultdict(list), []
    for identifier, r in rows.items():
        row, answer = r["original_row"], r["original_answer"]
        assert identifier == row["id"] == answer["id"]
        assert len(row["question"]) == len(row["question"][0]) == 1
        assert len(answer["ground_truth"]) == 1
        assert len(answer["ground_truth"][0]) == 1
        for index, function in enumerate(row["function"]):
            ref = f"{identifier.split('_')[1]}:{index}"
            tools[ref] = function
            names[function["name"]].append(ref)
            try:
                convert_tool(function)
            except ValueError:
                incompatible.append(ref)

    cases = []
    assert len({wire_name(name) for name in names}) == len(names), "Wire-name collision"
    for c in catalog["catalogs"]:
        identifier = c["source_id"]
        row, answer = rows[identifier]["original_row"], rows[identifier]["original_answer"]
        target_name, alternatives = next(iter(answer["ground_truth"][0].items()))
        index = next(i for i, t in enumerate(row["function"]) if t["name"] == target_name)
        target_ref = f"{identifier.split('_')[1]}:{index}"
        refs = [target_ref, *c["near"], *c["adjacent"], *c["far_native"]]
        assert len(refs) == len(set(refs))
        native = {f"{identifier.split('_')[1]}:{i}" for i in range(len(row["function"]))}
        assert native <= set(refs)
        wire = [convert_tool(tools[ref]) for ref in refs]
        assert len({t["name"] for t in wire}) == len(wire)
        function = tools[target_ref]
        assert set(alternatives) == set(function["parameters"]["properties"])
        required = function["parameters"]["required"]
        case = Case(
            id=identifier,
            dataset_id="phase3a-audit-only",
            dataset_version="1",
            task_input={"function": function},
            ground_truth={"bfcl": answer["ground_truth"]},
            split="development-exposed",
            provenance={"source_revision": REVISION},
        )
        checked = 0
        for values in itertools.product(*alternatives.values()):
            args = {
                k: v for k, v in zip(alternatives, values, strict=True) if v != "" or k in required
            }
            assert Draft202012Validator(wire[0]["parameters"]).is_valid(args)
            result = grade(
                case,
                ModelResponse(
                    parsed={"tool_calls": [{"name": wire[0]["name"], "arguments": args}]}
                ),
                wire,
            )
            assert result.passed
            checked += 1
        native_far = len(c["far_native"])
        # Necessary count test only; does not certify semantic or length matching.
        quotas = {
            str(n): not native_far and len(c["near"]) >= near and len(c["adjacent"]) >= adjacent
            for n, near, adjacent in [(5, 2, 2), (15, 7, 7), (30, 14, 15)]
        }
        cases.append(
            {
                "source_id": identifier,
                "target": target_name,
                "target_ref": target_ref,
                "domain": judgments[identifier]["domain"],
                "family": judgments[identifier]["family"],
                "catalog_tools": len(refs),
                "near": len(c["near"]),
                "adjacent": len(c["adjacent"]),
                "far_native": native_far,
                "size_possible": {str(n): len(refs) >= n for n in [5, 10, 15, 20, 30]},
                "original_quota_count_possible": quotas,
                "gold_variants_schema_and_subset_grade_checked": checked,
                "input_row_sha256": digest(row),
                "answer_row_sha256": digest(answer),
                "ordered_source_refs": refs,
                "wire_tools_sha256": digest(wire),
                "wire_schema_bytes": len(canonical(wire).encode("utf-8")),
            }
        )
    eligible = [r for r in review["records"] if r["decision"] == "eligible"]
    assert {c["source_id"] for c in cases} == {r["source_id"] for r in eligible}
    examples = []
    for example in catalog["small_pilot_examples"]:
        identifier = example["source_id"]
        row = rows[identifier]["original_row"]
        native = {f"{identifier.split('_')[1]}:{i}" for i in range(len(row["function"]))}
        permitted = next(c for c in cases if c["source_id"] == identifier)["ordered_source_refs"]
        assert example["tools_5"] == sorted(
            example["tools_5"],
            key=lambda ref: hashlib.sha256(
                f"phase3a-order-v1|20261104|{identifier}|{ref}".encode()
            ).hexdigest(),
        )
        assert example["tools_3"] == [r for r in example["tools_5"] if r in example["tools_3"]]
        assert native <= set(example["tools_3"]) < set(example["tools_5"]) <= set(permitted)
        receipts = {"source_id": identifier}
        for n in (3, 5):
            refs = example[f"tools_{n}"]
            assert len(refs) == n
            wire = [convert_tool(tools[ref]) for ref in refs]
            receipts[f"tools_{n}"] = {
                "source_refs": refs,
                "schema_bytes": len(canonical(wire).encode()),
                "sha256": digest(wire),
                "names": [t["name"] for t in wire],
                "description_bytes_median": median(len(t["description"].encode()) for t in wire),
                "property_count_median": median(len(t["parameters"]["properties"]) for t in wire),
                "target_index": [t["name"] for t in wire].index(
                    wire_name(next(iter(rows[identifier]["original_answer"]["ground_truth"][0])))
                ),
            }
        examples.append(receipts)
    return {
        "audit_version": "phase3a-check-v1",
        "evidence_hashes": {
            name: digest(load(name))
            for name in ["source_records.json", "review.json", "catalogs.json"]
        },
        "candidate_count": len(rows),
        "eligible_labels": len(eligible),
        "excluded": len(rows) - len(eligible),
        "decision_counts": dict(Counter(r["decision"] for r in review["records"])),
        "candidate_families": len({r["family"] for r in review["records"]}),
        "eligible_families": len({r["family"] for r in eligible}),
        "eligible_domains": dict(Counter(r["domain"] for r in eligible)),
        "no_call_cases": 0,
        "source_function_occurrences": len(tools),
        "distinct_source_names": len(names),
        "name_repetitions": {name: refs for name, refs in names.items() if len(refs) > 1},
        "conflicting_name_definitions": {
            name: refs
            for name, refs in names.items()
            if len({digest(tools[ref]) for ref in refs}) > 1
        },
        "unsupported_current_converter_refs": incompatible,
        "cases": cases,
        "small_catalog_examples": examples,
        "independent_human_reviews": 0,
        "model_requests": 0,
        "scope": (
            "Automated integrity/schema/count checks; semantic eligibility and "
            "uniqueness are AI-assisted judgments."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create summary.json exclusively")
    parser.add_argument("--source-dir", type=Path, help="Optional existing cache data directory")
    args = parser.parse_args()
    if args.source_dir:
        verify_source_cache(args.source_dir)
    result = audit()
    destination = DIRECTORY / "summary.json"
    if args.write:
        with destination.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    else:
        assert result == load("summary.json"), "Audit evidence drift"
    print(
        json.dumps(
            {
                k: result[k]
                for k in [
                    "candidate_count",
                    "eligible_labels",
                    "excluded",
                    "candidate_families",
                    "eligible_families",
                    "eligible_domains",
                    "decision_counts",
                    "source_function_occurrences",
                    "distinct_source_names",
                    "conflicting_name_definitions",
                    "unsupported_current_converter_refs",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
