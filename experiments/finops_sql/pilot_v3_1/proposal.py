"""Prospective pilot-only extension of the accepted v3 development plan."""

from pathlib import Path

from eval_lab.core.hashes import digest

from ..packages import ROOT
from ..proposal import sha
from ..v3.proposal import build as original


def build():
    plan, bodies = original("development")
    parent = digest(plan)
    if parent != "1e89f432dd61667ada0743d42d301142313513bb126438231d49c788b3ac20f8":
        raise ValueError("accepted pilot changed")
    name = "meridian-v3-development-r1-once"
    plan.update(version=name, result_directory="results/" + name, parent_pilot_digest=parent)
    for file in ("proposal.py", "accounting.py", "protocol.md"):
        path = Path(__file__).with_name(file)
        plan["source_sha256"][path.relative_to(ROOT).as_posix()] = sha(
            path.read_text(encoding="utf8").encode()
        )
    return plan, bodies
