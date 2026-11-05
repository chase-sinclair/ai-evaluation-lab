"""Rebuild only the 24 development candidates from two owner-approved, pinned inputs."""

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from itertools import combinations
from pathlib import Path

SOURCE = "7c5c4bae3b71d029082a1337299f5a4c21014ddd2012064be38893fda4b5c0c8"
ROR = "526e175ec445002cf6129d862aa59f13a1e95916f81b38b3221ae1163654f052"
ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/audits/phase3c/candidates.json"
CACHE = ROOT / "datasets/cache/phase3c"


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold()))


def grams(name: str) -> set[str]:
    padded = " " + normalize(name) + " "
    return {padded[i : i + 3] for i in range(len(padded) - 2)}


def edges(row: dict) -> dict[str, list[str]]:
    links = {}
    for part in filter(None, row["relationships"].split("; ")):
        kind, targets = part.split(": ", 1)
        links[kind] = targets.split(", ")
    return links


def ancestors(org: str, registry: dict) -> set[str]:
    seen = set()
    stack = list(registry[org]["edges"].get("parent", []))
    while stack:
        current = stack.pop()
        if current not in seen:
            seen.add(current)
            stack.extend(registry[current]["edges"].get("parent", []))
    return seen


def read_registry(path: Path) -> dict:
    registry = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            display = row["names.types.ror_display"]
            names = {normalize(display)}
            for field in ("label", "alias", "acronym"):
                # Same-language values can contain commas, including inside one name.
                # Use complete language groups for the eligibility filter.
                for name in filter(None, row["names.types." + field].split("; ")):
                    names.add(normalize(name.partition(": ")[2] or name))
            registry[row["id"]] = dict(
                display=display,
                country=row["locations.geonames_details.country_code"],
                status=row["status"],
                names=names,
                edges=edges(row),
                acronyms=row["names.types.acronym"],
            )
    return registry


def audit(cache: Path) -> dict:
    source, ror = cache / "crossref.jsonl", cache / "ror.csv"
    for path, wanted in ((source, SOURCE), (ror, ROR)):
        with path.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != wanted:
                raise ValueError(f"Changed source file: {path.name}")
    lines = source.read_bytes().splitlines()
    rows = list(map(json.loads, lines))
    row_hashes = {
        r["seq_no"]: hashlib.sha256(line).hexdigest() for r, line in zip(rows, lines, strict=True)
    }
    registry = read_registry(ror)
    labels = defaultdict(set)
    for r in rows:
        labels[normalize(r["input"])].add((tuple(r["output"]), bool(r["alternates"])))
    eligible = []
    for r in rows:
        orgs = r["output"]
        name = normalize(r["input"])
        if (
            r["seq_no"] < 20
            or len(orgs) != 1
            or r["alternates"]
            or len(labels[name]) != 1
            or orgs[0] not in registry
            or registry[orgs[0]]["status"] != "active"
        ):
            continue
        org = orgs[0]
        eligible.append(
            dict(
                seq_no=r["seq_no"],
                name=r["input"],
                ror=org,
                output=orgs,
                alternates=r["alternates"],
                row_sha256=row_hashes[r["seq_no"]],
                complete_registry_field=name in registry[org]["names"],
            )
        )
    features = {r["seq_no"]: grams(r["name"]) for r in eligible}
    normalized = {r["seq_no"]: normalize(r["name"]) for r in eligible}
    buckets = defaultdict(list)
    for a, b in combinations(eligible, 2):
        positive = a["ror"] == b["ror"]
        if normalized[a["seq_no"]] == normalized[b["seq_no"]]:
            continue
        if positive and not (a["complete_registry_field"] or b["complete_registry_field"]):
            continue
        if not positive and not all(
            r["complete_registry_field"] and len(normalized[r["seq_no"]].split()) >= 2
            for r in (a, b)
        ):
            continue
        x, y = (features[r["seq_no"]] for r in (a, b))
        score = round(2 * len(x & y) / (len(x) + len(y)), 6)
        cuts = (0, 0.45, 0.72, 0.97) if positive else (0.50, 0.65, 0.80, 0.97)
        for band, (lo, hi) in enumerate(zip(cuts[:-1], cuts[1:], strict=True)):
            if lo <= score < hi:
                seed = f"phase3c-v1/{a['seq_no']}/{b['seq_no']}".encode()
                buckets[positive, band].append((hashlib.sha256(seed).hexdigest(), score, a, b))
                break
    chosen = []
    used = set()
    for positive in (True, False):
        for band in range(3):
            count = 0
            for _, score, a, b in sorted(buckets[positive, band]):
                ids = {a["ror"], b["ror"]}
                if ids & used:
                    continue
                used.update(ids)
                for r in (a, b):
                    entry = registry[r["ror"]]
                    r.update(
                        display=entry["display"],
                        country=entry["country"],
                        status=entry["status"],
                        registry_acronyms=entry["acronyms"],
                        parents=entry["edges"].get("parent", []),
                    )
                left, right = a["ror"], b["ror"]
                comparison = None
                if not positive:
                    direct = {
                        side: [k for k, targets in registry[i]["edges"].items() if j in targets]
                        for side, i, j in (("left", left, right), ("right", right, left))
                    }
                    lpath, rpath = ancestors(left, registry), ancestors(right, registry)
                    comparison = dict(
                        direct=direct,
                        ancestor=left in rpath or right in lpath,
                        common_ancestors=sorted(lpath & rpath),
                    )
                chosen.append(
                    dict(
                        pair=f"{'P' if positive else 'N'}{band * 4 + count + 1:02}",
                        proposed="same" if positive else "different",
                        left=a,
                        right=b,
                        similarity=score,
                        relationship_check=comparison,
                    )
                )
                count += 1
                if count == 4:
                    break
            if count != 4:
                raise ValueError("Insufficient candidates in frozen band")
    return {
        "crossref_sha256": SOURCE,
        "ror_csv_sha256": ROR,
        "split": "development-only",
        "selection": "phase3c-v1",
        "candidates": chosen,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=CACHE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = audit(args.cache)
    if args.check:
        if result != json.loads(AUDIT.read_text(encoding="utf8")):
            raise SystemExit("Candidate receipt differs")
        print("24 candidate rows reproduced")
    else:
        AUDIT.parent.mkdir(exist_ok=True, parents=True)
        with AUDIT.open("x", encoding="utf8", newline="\n") as out:
            json.dump(result, out, ensure_ascii=False, indent=2)
            out.write("\n")
