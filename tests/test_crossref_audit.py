"""Validate the public review packet in CI without fetching either registry."""

import hashlib
import json
import re
import unicodedata
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1] / "docs/audits/phase3c"


def test_development_receipt_matches_pair_review():
    packet = json.loads((AUDIT / "candidates.json").read_text(encoding="utf8"))
    assert packet["split"] == "development-only"
    pairs = packet["candidates"]
    assert len(pairs) == 24
    assert len({r["seq_no"] for p in pairs for r in (p["left"], p["right"])}) == 48
    review = (AUDIT / "review.md").read_text(encoding="utf8").splitlines()
    seen = set()
    retained = []
    for index, pair in enumerate(pairs):
        a, b = pair["left"], pair["right"]
        same = index < 12
        assert (a["ror"] == b["ror"]) == same
        assert pair["proposed"] == ("same" if same else "different")
        assert pair["pair"] == f"{'P' if same else 'N'}{index % 12 + 1:02}"
        ids = {a["ror"], b["ror"]}
        assert seen.isdisjoint(ids)
        seen.update(ids)
        (line,) = [line for line in review if line.startswith("| " + pair["pair"] + " |")]
        grams = []
        for row in (a, b):
            assert row["seq_no"] >= 20 and row["output"] == [row["ror"]] and row["alternates"] == []
            assert len(bytes.fromhex(row["row_sha256"])) == hashlib.sha256().digest_size
            assert row["status"] == "active" and row["name"] in line and row["ror"] in line
            name = unicodedata.normalize("NFKC", row["name"]).casefold()
            name = " " + " ".join(re.findall(r"[^\W_]+", name)) + " "
            grams.append(set(zip(name, name[1:], name[2:], strict=False)))
        x, y = grams
        assert pair["similarity"] == round(2 * len(x & y) / (len(x) + len(y)), 6)
        assert f"{pair['similarity']:.6f}" in line
        if " | retain | " in line:
            retained.append(pair["proposed"])
        else:
            assert " | exclude | " in line
        if not same:
            check = pair["relationship_check"]
            assert check["direct"] == {"left": [], "right": []} and not check["ancestor"]
            assert bool(check["common_ancestors"]) == (pair["pair"] == "N12")
    assert retained.count("same") == 4 and retained.count("different") == 11
