"""Focused blind form and offline search of the complete pinned ROR CSV."""

import argparse
import csv
import hashlib
import re
from datetime import date
from pathlib import Path

from scripts.audit_crossref_pairs import CACHE, ROOT, ROR, normalize

from .prepare import load

FORM = ROOT / "docs/review/funder_identity.md"
FIELDS = (
    "Decision",
    "Matching ROR ID",
    "Evidence and search terms",
    "Reviewer",
    "Date",
    "Offered-set result",
)


def subjects():
    keys = {
        r["seq_no"]: r
        for r in load("dataset.json")["rows"]
        if r["review"] == "pending_independent_nil"
    }
    return [keys[r["seq_no"]] for r in load("blind_review.json") if r["seq_no"] in keys]


def search(term):
    path = CACHE / "ror.csv"
    with path.open("rb") as f:
        if hashlib.file_digest(f, "sha256").hexdigest() != ROR:
            raise ValueError("Wrong registry snapshot")
    words = normalize(term).split()
    if not words:
        raise ValueError("Enter a name, country qualifier or ROR ID")
    count = 0
    with path.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            names = [
                r[k]
                for k in (
                    "id",
                    "names.types.ror_display",
                    "names.types.label",
                    "names.types.alias",
                    "names.types.acronym",
                    "locations.geonames_details.country_name",
                )
            ]
            text = normalize(" ".join(names))
            if not all(w in text for w in words):
                continue
            count += 1
            if count <= 30:
                print(" | ".join([*names, r["status"], r["relationships"]]))
    print(f"{count} matching records across all statuses. First 30 shown. Refine broad searches.")


def check_review(path: Path):
    """Only an unchanged cohort can use this freeze. Keep the completed copy local."""
    subjects_list = subjects()
    raw = path.read_text(encoding="utf8")
    blocks = re.split(r"^## ", raw, flags=re.M)[1:]
    if len(blocks) != len(subjects_list) or len(blocks) != 8:
        raise ValueError("Need eight decisions")
    for index, (block, row) in enumerate(zip(blocks, subjects_list, strict=True), 1):
        heading, *lines = block.splitlines()
        if heading != f"Q{index:02} · {row['query']}":
            raise ValueError("Review row mismatch")
        entries = {}
        for line in lines:
            key, _, value = line.partition(":")
            if key in FIELDS:
                if key in entries:
                    raise ValueError("Duplicate review field")
                entries[key] = value.strip()
        if set(entries) != set(FIELDS) or not all(
            entries[k] for k in FIELDS if k != "Matching ROR ID"
        ):
            raise ValueError("Human review incomplete")
        if date.fromisoformat(entries["Date"]) > date.today():
            raise ValueError("Future review date")
        if (
            entries["Decision"] != "NO_SUPPORTED_MATCH"
            or entries["Matching ROR ID"]
            or entries["Offered-set result"] != "NONE"
        ):
            raise ValueError(
                "Review changes or disputes this freeze. Version and recalibrate before dispatch."
            )
    return hashlib.sha256(raw.encode()).hexdigest()


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("search_term")
    search(cli.parse_args().search_term)
