"""Only files explicitly listed here can enter the public interface."""

import json
import re
from functools import lru_cache
from pathlib import Path

import tiktoken

from eval_lab.core.hashes import canonical

ROOT = Path(__file__).parent
PUBLIC = ROOT / "public" / "v1"
FILES = {
    "A": ["schema.sql"],
    "B": ["dictionary.curated.json", "metrics.md", "joins.md", "policy.md"],
    "C": ["dictionary.full.json", "lineage.md", "operations.md", "registry.json"],
}
QUESTIONS = json.loads((PUBLIC / "questions.json").read_bytes())
OBJECTS = json.loads((PUBLIC / "dictionary.full.json").read_bytes())
SAMPLES = json.loads((PUBLIC / "registry.json").read_bytes())


def source(name):
    return (
        ((ROOT if name == "schema.sql" else PUBLIC) / name)
        .read_text(encoding="utf8")
        .replace("\r\n", "\n")
    )


def package(arm):
    if arm == "D":
        return ""
    names = []
    for level in "ABC":
        names += FILES[level]
        if level == arm:
            break
    else:
        raise ValueError("unknown arm")
    return "".join(f"\n--- {name} ---\n{source(name)}" for name in names)


@lru_cache(maxsize=1)
def encoder():
    return tiktoken.get_encoding("cl100k_base")


def tokens(obj):
    return len(encoder().encode_ordinary(obj if isinstance(obj, str) else canonical(obj)))


def catalog(query, objects):
    if not query.strip():
        return {k: v["grain"] for k, v in sorted(objects.items()) if "grain" in v}
    words = set(re.findall(r"[a-z0-9]+", query.lower()))
    ranked = []
    for k, v in objects.items():
        fields = k + " " + v.get("ddl", "")
        score = len(words.intersection(re.findall(r"[a-z0-9]+", fields.lower())))
        if score:
            ranked.append((-score, k))
    return [k for _, k in sorted(ranked)[:8]]
