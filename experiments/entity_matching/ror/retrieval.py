"""Exact maximum character-trigram Dice over active ROR v2.6 name forms."""

import csv
import re
from array import array
from collections import Counter, defaultdict
from pathlib import Path

from ..experiment import norm

VERSION = "ror-v2.6-max-trigram-v1"


def trigrams(value: str) -> set[str]:
    value = " " + norm(value) + " "
    return {value[i : i + 3] for i in range(len(value) - 2)}


def forms(row: dict) -> list[str]:
    canonical = row["names.types.ror_display"]
    values = {canonical}
    for field in ("label", "alias", "acronym"):
        for block in row["names.types." + field].split("; "):
            _, _, name = block.partition(": ")
            # Flattened CSV cannot distinguish list commas from literal commas in names.
            if name and "," not in name:
                values.add(name)
    return [canonical, *sorted(values - {canonical})]


class Registry:
    def __init__(self, path: Path):
        self.orgs = {}
        self.names = []
        self.sizes = []
        self.postings = defaultdict(lambda: array("I"))
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if row["status"] != "active":
                    continue
                org = row["id"]
                names = forms(row)
                self.orgs[org] = (names, row["locations.geonames_details.country_code"])
                for name in names:
                    grams = trigrams(name)
                    if not grams:
                        continue
                    index = len(self.names)
                    self.names.append((org, name))
                    self.sizes.append(len(grams))
                    for g in grams:
                        self.postings[g].append(index)

    def retrieve(self, query: str) -> tuple[list[dict], dict]:
        """No label argument. Rank all nonzero-overlap IDs, then apply the offer limit."""
        grams = trigrams(query)
        overlap = Counter()
        for g in grams:
            overlap.update(self.postings.get(g, ()))
        best = {}
        for index, n in overlap.items():
            org, name = self.names[index]
            score = round(2 * n / (len(grams) + self.sizes[index]), 8)
            if org not in best or (-score, name) < (-best[org][0], best[org][1]):
                best[org] = score, name
        ranked = sorted(best, key=lambda org: (-best[org][0], org))
        candidates = []
        for org in ranked[:5]:
            names, country = self.orgs[org]
            score, matched = best[org]
            aliases = list(dict.fromkeys(n for n in (matched, *names[1:]) if n != names[0]))[:2]
            candidates.append(
                dict(
                    id=org,
                    name=names[0],
                    aliases=aliases,
                    country=country,
                    score=score,
                    matched_form=matched,
                )
            )
        return candidates, {org: (i, best[org][0]) for i, org in enumerate(ranked, 1)}


def unsafe_name(value: str) -> bool:
    return bool(
        re.search(
            r"https?://|www\.|\b10\.\d{4,9}/|@|\b(?:ror|orcid|doi)\s*:|\b0[a-z0-9]{6}\d{2}\b",
            value,
            re.I,
        )
    )
