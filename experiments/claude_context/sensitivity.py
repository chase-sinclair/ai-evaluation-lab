"""POST-HOC sensitivity analysis for Experiment 007. Not part of the frozen protocol.

The pre-registered scores count any answer that breaks the output contract ("exactly one JSON
object") as incorrect. This module re-scores only those malformed answers by extracting the
first JSON object that the frozen 005 parser accepts, separating format compliance from
financial correctness. Its results are reported beside the official scores and never replace
them. It reads the sealed run through the same verified replay.
"""

import argparse
import json
from pathlib import Path

from experiments.finops_sql.episode import final
from experiments.model_context.analysis import score

from .analysis import load, replay, summarize

DECODER = json.JSONDecoder()


def lenient(text: str) -> dict:
    """The first decodable JSON object in the text that the frozen parser accepts."""
    for start, char in enumerate(text):
        if char != "{":
            continue
        try:
            _, end = DECODER.raw_decode(text, start)
        except ValueError:
            continue
        answer = final(text[start:end])
        if answer["kind"] in ("sql", "clarify"):
            return answer
    return {"kind": "malformed"}


def recover(ends: dict, folder: Path, plan_rows: list[dict]) -> tuple[dict, dict]:
    """Replace only malformed terminal answers with their lenient reading."""
    out, changed = dict(ends), {}
    for i, row in enumerate(plan_rows, start=1):
        key = row["id"]
        if ends[key]["kind"] != "malformed":
            continue
        raw = load(folder / f"{i:03}.response-body")
        text = "".join(b.get("text", "") for b in raw["content"] if b.get("type") == "text")
        out[key] = lenient(text)
        changed[key] = out[key]["kind"]
    return out, changed


if __name__ == "__main__":
    from scripts.acquire_claude_context import APPROVAL, preflight

    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--sensitivity-review", type=Path, required=True)
    parser.add_argument("--snapshots", type=Path, required=True)
    args = parser.parse_args()
    plan, _ = preflight(APPROVAL)
    ends, stats, _ = replay(args.folder)
    recovered, changed = recover(ends, args.folder, plan["requests"])
    review = load(args.review) | load(args.sensitivity_review)
    cases = score(recovered, args.snapshots, review)
    result = summarize(cases, recovered, stats)
    result["post_hoc"] = "format-lenient sensitivity; not the pre-registered result"
    result["recovered_kinds"] = {k: list(changed.values()).count(k) for k in set(changed.values())}
    print(json.dumps(result, indent=2, default=str))
