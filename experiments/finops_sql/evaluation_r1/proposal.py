"""Prospective evaluation-only extension of the accepted v3 evaluation plan."""

from pathlib import Path

from eval_lab.core.hashes import digest

from ..packages import ROOT
from ..proposal import sha
from ..v3.proposal import build as original


def build():
    plan, bodies = original("evaluation")
    parent = digest(plan)
    if parent != "1b3a5529069e19c9d219a58d4891c39c4fb51676a7ef548a482bd59ddddb61b1":
        raise ValueError("accepted evaluation changed")
    name = "meridian-v3-evaluation-r1-once"
    plan.update(version=name, result_directory="results/" + name, parent_evaluation_digest=parent)
    for file in ("proposal.py", "../pilot_v3_1/accounting.py", "protocol.md", "analysis.py"):
        path = (Path(__file__).parent / file).resolve()
        plan["source_sha256"][path.relative_to(ROOT).as_posix()] = sha(
            path.read_text(encoding="utf8").encode()
        )
    return plan, bodies
