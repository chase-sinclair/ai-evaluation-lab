"""Aggregate feasibility only. Never retrieves candidates, draws a cohort or reads outcomes."""

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict

from experiments.entity_matching.experiment import norm
from experiments.entity_matching.ror.cohort import DIR, family_keys, sources
from experiments.entity_matching.ror.retrieval import unsafe_name
from scripts.audit_crossref_pairs import AUDIT, CACHE, ROR, SOURCE, edges

PROGRAM = re.compile(r"\b(project|award|grant|fellowship|programme|program|scholarship)\b")
ORG = re.compile(
    r"\b(university|agency|foundation|institute|association|society|council|laboratory|"
    r"fund|center|centre)\b"
)
RELATIONS = {"parent", "child", "predecessor", "successor"}
# Public registry IDs cited in the signed Phase 3E worksheet beyond the 3D quarantine.
# The private worksheet itself stays local; its provenance is recorded in the receipt.
REVIEW_SUPPLEMENT = (
    "00dhpdx54",
    "00djwmt25",
    "00t30yz20",
    "01n1pt995",
    "030enq015",
    "036bzjr85",
    "039g7tm38",
    "03c94dv58",
    "03kt66j61",
)


class Families:
    def __init__(self):
        self.parent = {}

    def root(self, key):
        path = []
        while key in self.parent:
            path.append(key)
            key = self.parent[key]
        for node in path:
            self.parent[node] = key
        return key

    def join(self, a, b):
        a, b = sorted((self.root(a), self.root(b)))
        if a != b:
            self.parent[b] = a


def folded(s):
    decomposed = unicodedata.normalize("NFKD", s)
    return norm("".join(c for c in decomposed if not unicodedata.combining(c)))


def variants(name, places):
    full = folded(name)
    keys = {full}
    # Retain the original; geographic removal only creates a collision flag.
    words = full.split()
    for n in range(1, min(7, len(words) - 1)):
        if " ".join(words[-n:]) in places:
            stem = words[:-n]
            if stem[-1] in {"in", "of", "de"}:
                stem = stem[:-1]
            if len(stem) >= 2:
                keys.add(" ".join(stem))
        if " ".join(words[:n]) in places:
            keys.add(" ".join(words[n:]))
    keys.update(folded(a) for a in re.findall(r"\(([A-Z][A-Z0-9-]{2,12})\)", name))
    return {k for k in keys if k}


def registry_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream)


def name_forms(row):
    yield row["names.types.ror_display"]
    for kind in ("alias", "label", "acronym"):
        for block in row["names.types." + kind].split("; "):
            value = block.partition(": ")[2] or block
            if value:
                yield value
                # Comma pieces are deliberately over-inclusive for leakage screening only.
                if "," in value:
                    yield from value.split(", ")


def eligibility(r, labels, active):
    name, targets = r["input"], r["output"]
    key = norm(name)
    if r["alternates"] or len(targets) > 1 or len(labels[key]) != 1:
        return "annotation"
    if (
        unsafe_name(name)
        or not 8 <= len(name) <= 140
        or len(key.split()) < 2
        or PROGRAM.search(key)
    ):
        return "name"
    if targets:
        return "positive" if targets[0] in active else "inactive"
    return "empty" if ORG.search(key) else "empty_without_org_term"


def audit():
    rows = sources()  # Verifies both pinned source hashes.
    registry = CACHE / "ror.csv"
    qfile = DIR / "quarantine.json"
    q = json.loads(qfile.read_bytes())
    reserved = set(q["development_only_seq_nos"])
    exposed = set(range(20))
    exposed.update(r["seq_no"] for r in json.loads((DIR / "dataset.json").read_bytes())["rows"])
    for pair in json.loads(AUDIT.read_bytes())["candidates"]:
        exposed.update(pair[side]["seq_no"] for side in ("left", "right"))
    if not exposed <= reserved or len(reserved) != 579:
        raise ValueError("Exposure receipt mismatch")
    return {
        "input_sha256": {
            "crossref": SOURCE,
            "ror": ROR,
            "quarantine": hashlib.sha256(qfile.read_bytes()).hexdigest(),
        },
        "documented_exposed_seeds": len(exposed),
        "additional_cited_review_ids": len(REVIEW_SUPPLEMENT),
        **screen_population(
            rows,
            registry,
            reserved,
            q["blocked_keys"] + ["https://ror.org/" + i for i in REVIEW_SUPPLEMENT],
        ),
    }


def screen_population(rows, registry, reserved, blocked_keys):
    graph = Families()
    places, active = set(), set()
    for org in registry_rows(registry):
        if org["status"] == "active":
            active.add(org["id"])
        for kind, others in edges(org).items():
            if kind in RELATIONS:
                for other in others:
                    graph.join(org["id"], other)
        for field in ("country_name", "country_subdivision_name", "name"):
            value = org["locations.geonames_details." + field]
            places.update(folded(s) for s in value.split("; ") if s)

    labels = defaultdict(set)
    for r in rows:
        labels[norm(r["input"])].add((tuple(r["output"]), bool(r["alternates"])))
    groups = {}
    screen = Counter()
    relevant_ids = {key for key in blocked_keys if key.startswith("https://ror.org/")}
    flags = set(blocked_keys)
    vkeys = {}
    for r in rows:
        i = r["seq_no"]
        reason = eligibility(r, labels, active)
        if i not in reserved:
            screen[reason] += 1
        if i not in reserved and reason not in {"positive", "empty"}:
            continue
        node = f"row:{i}"
        if i in reserved:
            flags.add(node)
        else:
            groups[i] = reason
        vkeys[i] = variants(r["input"], places)
        for k in family_keys(r):
            graph.join(node, k)
            if k.startswith("https://ror.org/"):
                relevant_ids.add(k)
        for k in vkeys[i]:
            graph.join(node, "name:" + k)

    def unblocked():
        blocked = {graph.root(k) for k in flags}
        return {i for i in groups if graph.root(f"row:{i}") not in blocked}

    before = unblocked()
    lookup = set().union(*vkeys.values())
    active_hits = set()
    for org in registry_rows(registry):
        relevant = org["id"] in relevant_ids
        for name in set(name_forms(org)):
            keys = variants(name, places)
            hits = lookup & keys
            if org["status"] == "active":
                active_hits.update(hits)
            for k in keys if relevant else hits:
                graph.join(org["id"], "name:" + k)
    after = unblocked()
    families = defaultdict(lambda: defaultdict(list))
    empty_hit = 0
    for i in sorted(after):
        if groups[i] == "empty" and vkeys[i] & active_hits:
            empty_hit += 1
            continue
        families[graph.root(f"row:{i}")][groups[i]].append(i)
    strata = {"positive": [], "empty": []}
    mixed = 0
    for members in families.values():
        if len(members) != 1:
            mixed += 1
            continue
        group, ids = next(iter(members.items()))
        strata[group].append(ids)
    return {
        "source_rows": len(rows),
        "quarantined": len(reserved),
        "remaining_rows": len(rows) - len(reserved),
        "first_exit_after_quarantine": dict(sorted(screen.items())),
        "after_identity_geo_and_relationship_screen": dict(Counter(groups[i] for i in before)),
        "after_registry_name_screen": dict(Counter(groups[i] for i in after)),
        "additional_empty_rows_with_active_name_hit": empty_hit,
        "excluded_mixed_components": mixed,
        "frame": {
            group: {
                "rows": sum(map(len, components)),
                "families": len(components),
                "membership_sha256": hashlib.sha256(
                    json.dumps(sorted(components), separators=(",", ":")).encode()
                ).hexdigest(),
            }
            for group, components in strata.items()
        },
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
