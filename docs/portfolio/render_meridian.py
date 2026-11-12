"""Render the Meridian publication figures from the approved local scoring report."""

import hashlib
import json
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

PORTFOLIO = Path(__file__).resolve().parent
REPORT = PORTFOLIO.parents[1] / ".verification/evaluation-report.json"
DIGEST = "d6986bcf9d2f5b509e4f36af1c29d9c745ed3e5c7348117f238a61d6168399f4"


def chart(name, title, unit, rows, footer):
    """Use a common zero baseline and a full 36-question scale."""
    for width, suffix in [(720, ""), (330, "-compact")]:
        track = width - 48
        height = 115 + 49 * len(rows)
        description = ". ".join(f"{label}: {value} of 36" for label, value in rows)

        def label(y, content, size, bold=False):
            weight = "700" if bold else "400"
            return (
                f'<text x="24" y="{y}" font-size="{size}" font-weight="{weight}">'
                f"{escape(content)}</text>"
            )

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(description + ". " + footer)}</desc>',
            '<rect width="100%" height="100%" fill="white"/>',
            '<g font-family="Arial, sans-serif" fill="#17394b">',
            label(31, title, 21, True),
            label(55, unit, 15),
        ]
        for index, (caption, value) in enumerate(rows):
            y = 86 + 49 * index
            svg.extend(
                [
                    label(y, f"{caption}   {value}/36", 17, True),
                    f'<rect x="24" y="{y + 7}" width="{track}" height="10" fill="#e4ecee"/>',
                    f'<rect x="24" y="{y + 7}" width="{track * value / 36:.2f}" '
                    'height="10" fill="#176c70"/>',
                ]
            )
        svg.extend([label(height - 15, footer, 14), "</g></svg>"])
        (PORTFOLIO / "assets" / f"meridian-{name}{suffix}.svg").write_text(
            "\n".join(svg) + "\n", encoding="utf-8", newline="\n"
        )


def main():
    data = REPORT.read_bytes()
    if hashlib.sha256(data).hexdigest() != DIGEST:
        raise ValueError("Unexpected machine report digest")
    report = json.loads(data)
    names = ["A · Schema", "B · Curated", "C · Expanded", "D · Discovery"]
    arms = report["arms"]
    chart(
        "decisions",
        "Correct business decisions",
        "Same 36 questions per condition",
        [(name, arms[name[0]]["policy"][0]) for name in names],
        "32 financial tasks · 4 required clarifications",
    )
    cases = report["cases"]
    pairs = Counter(
        (cases[f"Q{i:02}B"]["business_correct"], cases[f"Q{i:02}C"]["business_correct"])
        for i in range(1, 37)
    )
    chart(
        "overlap",
        "Where the two sets overlap",
        "Curated (B) and expanded (C) context",
        [
            (label, pairs[key])
            for key, label in [
                ((True, True), "Both correct"),
                ((True, False), "Only curated correct"),
                ((False, True), "Only expanded correct"),
                ((False, False), "Neither correct"),
            ]
        ],
        "One paired comparison per question",
    )
    depths = Counter(report["discovery_depth"].values())
    usage = arms["D"]["telemetry"]
    chart(
        "discovery",
        "How far discovery went",
        f"{usage['tools']} local metadata calls across 36 episodes",
        [(f"{depth} of 6 calls used", depths[depth]) for depth in sorted(depths)],
        f"{usage['requests']} model requests · ${float(usage['cost']):.5f} estimated",
    )


if __name__ == "__main__":
    main()
