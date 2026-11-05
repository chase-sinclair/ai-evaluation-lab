"""Freeze source-first nominations and reserve exposed organization/name families."""

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from scripts.audit_crossref_pairs import AUDIT, CACHE, ROR, SOURCE, read_registry

from ..experiment import norm
from .retrieval import unsafe_name

DIR = Path(__file__).resolve().parent


def sources():
    for file, sha in (("crossref.jsonl", SOURCE), ("ror.csv", ROR)):
        with (CACHE / file).open("rb") as f:
            if hashlib.file_digest(f, "sha256").hexdigest() != sha:
                raise ValueError("Changed source")
    lines = (CACHE / "crossref.jsonl").read_bytes().splitlines()
    rows = []
    for line in lines:
        r = json.loads(line)
        r["row_sha256"] = hashlib.sha256(line).hexdigest()
        rows.append(r)
    return rows


def nominate(rows, registry):
    labels = defaultdict(set)
    for r in rows:
        labels[norm(r["input"])].add((tuple(r["output"]), bool(r["alternates"])))
    quotas = {"registry_form": 18, "variant": 18, "empty": 12}
    used = set()
    chosen = []
    for r in sorted(
        rows, key=lambda r: hashlib.sha256(f"phase3d-v1/{r['seq_no']}".encode()).digest()
    ):
        name = r["input"]
        key = norm(name)
        ids = r["output"]
        if (
            r["seq_no"] < 20
            or r["alternates"]
            or len(ids) > 1
            or len(labels[key]) != 1
            or unsafe_name(name)
            or not 8 <= len(name) <= 140
            or len(key.split()) < 2
            or re.search(
                r"\b(?:project|award|grant|fellowship|programme|program|scholarship)\b", key
            )
        ):
            continue
        if ids:
            rec = registry.get(ids[0])
            if not rec or rec["status"] != "active" or ids[0] in used:
                continue
            group = "registry_form" if key in rec["names"] else "variant"
        else:
            if not re.search(
                r"\b(?:university|agency|foundation|institute|association|society|council|laboratory|fund|center|centre)\b",
                key,
            ):
                continue
            group = "empty"
        if not quotas[group] or key in used:
            continue
        chosen.append(
            dict(
                seq_no=r["seq_no"],
                query=name,
                output=ids,
                alternates=r["alternates"],
                source_row_sha256=r["row_sha256"],
                selection_group=group,
            )
        )
        quotas[group] -= 1
        used.update([key, *ids])
        if not any(quotas.values()):
            break
    if any(quotas.values()):
        raise ValueError(quotas)
    return sorted(chosen, key=lambda r: r["seq_no"])


def family_keys(r):
    ids = [
        *r["output"],
        *(v for pair in r["alternates"] for v in pair if v.startswith("https://ror.org/")),
    ]
    name = norm(r["input"])
    stripped = re.sub(
        r"\b(?:grant|project|programme|program|scholarship|fellowship|award|funding)\b", " ", name
    )
    keys = {"name:" + name, "family:" + " ".join(sorted(set(stripped.split()))), *ids}
    for tag in re.findall(r"\(([A-Z][A-Z0-9-]{2,12})\)", r["input"]):
        keys.add("name:" + norm(tag))
    return keys


def quarantine(rows, chosen, registry):
    """Transitive exposure closure. Remaining identities require manual family clearance."""
    prior = json.loads(AUDIT.read_text(encoding="utf8"))["candidates"]
    ids = {p[k]["seq_no"] for p in prior for k in ("left", "right")}
    ids.update(range(20))
    ids.update(r["seq_no"] for r in chosen)
    keyed = {r["seq_no"]: family_keys(r) for r in rows}
    exposed = set().union(*(keyed[i] for i in ids))
    exposed.update(c["id"] for r in chosen for c in r["candidates"])
    for org in list(exposed):
        if org in registry:
            for relatives in registry[org]["edges"].values():
                exposed.update(relatives)
    while True:
        before = len(exposed)
        for org in list(exposed):
            if org in registry:
                exposed.update("name:" + n for n in registry[org]["names"] if n)
        for keys in keyed.values():
            if keys & exposed:
                exposed.update(keys)
        if before == len(exposed):
            break
    return dict(
        development_only_seq_nos=sorted(i for i, k in keyed.items() if k & exposed),
        blocked_keys=sorted(exposed),
        future_split_status="closed_pending_manual_family_audit",
    )


if __name__ == "__main__":
    reg = read_registry(CACHE / "ror.csv")
    for r in nominate(sources(), reg):
        print(
            r["seq_no"],
            r["selection_group"],
            r["query"],
            " / ",
            reg[r["output"][0]]["display"] if r["output"] else "EMPTY",
        )
