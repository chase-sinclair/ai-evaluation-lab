"""Exercise both accounting implementations and collect private verification evidence."""

import argparse
import hashlib
import json
from pathlib import Path

from .audit import sandbox
from .compare import normalize
from .controls import CLARIFICATIONS, DENIED, DEVELOPMENT, INTEGRITY, MUTATIONS
from .oracle import answers
from .references import QUERIES

SNAPSHOTS = {
    "development": "43db891725b1f1a58aeb4f9a606d62caa8e816e87db1db6eca9ca0ed2002e369",
    "evaluation_a": "3e484882533f9bb72a0b0d4ef829fbe8a51e197f6b233342b7f02e641dfb4d1c",
    "evaluation_b": "585f34eb81530cbf55dd77f2cd9830c2a477988c57799201c371073d0175f835",
}


def verify_sources(folder):
    manifest = json.loads((folder / "manifest.json").read_text())
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(canonical).hexdigest() != SNAPSHOTS[folder.name]:
        raise ValueError("snapshot manifest changed")
    hashes = {**manifest["table_csv_sha256"], "economic": manifest["economic_sha256"]}
    for name, expected in hashes.items():
        with (folder / (name + ".csv")).open("rb") as source:
            if hashlib.file_digest(source, "sha256").hexdigest() != expected:
                raise ValueError(f"{name} differs from its frozen source")
    with (folder / "warehouse.db").open("rb") as db:
        return hashlib.file_digest(db, "sha256").hexdigest()


def check(folder):
    original_db = verify_sources(folder)
    queries = {f"check_{k}": v for k, v in INTEGRITY.items()}
    queries.update({f"deny_{k}": v for k, v in DENIED.items()})
    dev = folder.name == "development"
    if dev:
        queries.update({k: v for k, (_, v) in DEVELOPMENT.items() if v})
    else:
        queries.update({str(k): v for k, v in QUERIES.items()})
        queries.update({f"wrong_{k}": q for k, (_, q) in MUTATIONS.items()})
        for i, (_, left, right) in CLARIFICATIONS.items():
            queries[f"{i}a"] = left
            queries[f"{i}b"] = right
    data = sandbox(folder, queries)
    (folder / "checkpoint.json").write_text(json.dumps(data, sort_keys=True, indent=2))
    if verify_sources(folder) != original_db:
        raise ValueError("database changed during audit")
    errors = []
    for k, r in data.items():
        if k.startswith("deny_"):
            if "error" not in r:
                errors.append(k)
        elif "error" in r or (k.startswith("check_") and r["rows"] != [[0]]):
            errors.append((k, r))
    if not dev and not errors:
        oracle = answers(folder)
        for i, rows in oracle.items():
            if normalize(i, data[str(i)]["rows"]) != normalize(i, rows):
                errors.append((i, "oracle"))
        for k, (i, _) in MUTATIONS.items():
            if normalize(i, data[f"wrong_{k}"]["rows"]) == normalize(i, oracle[i]):
                errors.append((k, "undetected mutation"))
        for i in CLARIFICATIONS:
            if data[f"{i}a"]["rows"] == data[f"{i}b"]["rows"]:
                errors.append((i, "equal interpretations"))
    print(folder.name, errors, flush=True)
    return not errors


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    root = p.parse_args().root
    ok = [check(root / name) for name in ("development", "evaluation_a", "evaluation_b")]
    raise SystemExit(0 if all(ok) else 1)
