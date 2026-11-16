"""Render the model-tier-against-context figures from the scored local reports.

Reads the digest-checked Experiment 006 and 007 machine reports and writes wide and
compact SVGs to `assets/`. Run from the repository root:
`python docs/portfolio/render_context_tier.py`.
"""

import hashlib
import json
from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape

PORTFOLIO = Path(__file__).resolve().parent
EVIDENCE = PORTFOLIO.parents[1] / ".verification"
REPORTS = {
    "GPT": (
        "model-context-report.json",
        "4fcf8385ff23ed143b085624704b3964fc66b71e8557d44dbfd12b92b734764e",
        ("luna", "sol"),
    ),
    "Claude": (
        "claude-context-report.json",
        "e69151b3567ea7288ae69ba69e47dbcb14988c893f19c59dc6c0bd3ac9bc6ef5",
        ("haiku", "sonnet"),
    ),
}
CONFIGURATIONS = [
    ("Cheap model, schema", 0, "A"),
    ("Cheap model, curated", 0, "B"),
    ("Expensive model, schema", 1, "A"),
    ("Expensive model, curated", 1, "B"),
]
INK, TRACK, BAR, LOSS, TICK = "#17394b", "#e4ecee", "#176c70", "#b4532a", "#0b2230"
SIZES = [(720, "", 21), (330, "-compact", 18)]


def load():
    reports = {}
    for provider, (name, expected, models) in REPORTS.items():
        data = (EVIDENCE / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Unexpected machine report digest: {name}")
        reports[provider] = (json.loads(data), models)
    return reports


def text(x, y, content, size, bold=False):
    weight = "700" if bold else "400"
    attributes = f'x="{x}" y="{y}" font-size="{size}" font-weight="{weight}"'
    return f"<text {attributes}>{escape(content)}</text>"


def write(name, width, height, title, description, body):
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        f'<desc id="desc">{escape(description)}</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<g font-family="Arial, sans-serif" fill="{INK}">',
        *body,
        "</g></svg>",
    ]
    (PORTFOLIO / "assets" / name).write_text("\n".join(svg) + "\n", encoding="utf-8", newline="\n")


def means_chart(reports):
    """Mean of three draws as a bar, each draw as a tick, on a full 36-question scale."""
    title = "Context before model tier"
    rows = []
    for caption, tier, arm in CONFIGURATIONS:
        for provider, (report, models) in reports.items():
            cell = report["cells"][f"{models[tier]}-{arm}"]
            draws = cell["complete_draw_scores"]
            mean = Decimal(cell["mean_correct"]).quantize(Decimal("0.1"))
            rows.append((caption, provider, mean, draws))
    description = ". ".join(
        f"{caption}, {provider} models: mean {mean} of 36, draws {', '.join(map(str, draws))}"
        for caption, provider, mean, draws in rows
    )
    footer = "Bar = mean of 3 draws · tick = one draw"
    for width, suffix, title_size in SIZES:
        track = width - 48
        height = 75 + 100 * len(CONFIGURATIONS) + 30
        unit = "Correct of 36, same questions"
        body = [text(24, 31, title, title_size, True), text(24, 55, unit, 15)]
        for index, (caption, provider, mean, draws) in enumerate(rows):
            block, slot = divmod(index, 2)
            top = 75 + 100 * block
            if slot == 0:
                body.append(text(24, top + 14, caption, 15, True))
            y = top + 38 + 38 * slot
            body.extend(
                [
                    text(24, y, f"{provider}  {mean}/36  ({', '.join(map(str, draws))})", 14),
                    f'<rect x="24" y="{y + 6}" width="{track}" height="10" fill="{TRACK}"/>',
                    f'<rect x="24" y="{y + 6}" width="{track * float(mean) / 36:.2f}" '
                    f'height="10" fill="{BAR}"/>',
                ]
            )
            for score in draws:
                x = 24 + track * score / 36
                body.append(
                    f'<line x1="{x:.2f}" y1="{y + 3}" x2="{x:.2f}" y2="{y + 19}" '
                    f'stroke="{TICK}" stroke-width="2"/>'
                )
        body.append(text(24, height - 15, footer, 13))
        name = f"context-tier-means{suffix}.svg"
        write(name, width, height, title, f"{description}. {footer}", body)


def paired_chart(reports):
    """Headline pair on the same question and draw: 108 comparisons per provider."""
    title = "Same question, same draw"
    unit = "Cheap + curated against expensive + schema"
    rows = []
    for provider, (report, models) in reports.items():
        key = f"{models[0]}-B_vs_{models[1]}-A"
        counts = report["paired"][key]["counts"]
        rows.append((provider, counts["gain"], counts["loss"], counts["tie"]))
    description = ". ".join(
        f"{provider} models: cheap model with curated context gained {gain}, lost {loss} "
        f"and tied {tie} of 108"
        for provider, gain, loss, tie in rows
    )
    footer = "108 paired outcomes per provider"
    for width, suffix, title_size in SIZES:
        track = width - 48
        height = 75 + 76 * len(rows) + 56
        body = [text(24, 31, title, title_size, True), text(24, 55, unit, 13 if suffix else 15)]
        # Colour key, so the bars read without the count line beneath them.
        key_y = height - 44
        for slot, (label, fill) in enumerate((("Gained", BAR), ("Lost", LOSS), ("Tied", TRACK))):
            x = 24 + 86 * slot
            body.append(
                f'<rect x="{x}" y="{key_y - 10}" width="12" height="12" fill="{fill}" '
                f'stroke="{TICK}" stroke-opacity="0.25" stroke-width="0.75"/>'
            )
            body.append(text(x + 18, key_y, label, 13))
        for index, (provider, gain, loss, tie) in enumerate(rows):
            y = 90 + 76 * index
            gain_w, loss_w = track * gain / 108, track * loss / 108
            body.extend(
                [
                    text(24, y, f"{provider} models", 15, True),
                    f'<rect x="24" y="{y + 8}" width="{track}" height="14" fill="{TRACK}"/>',
                    f'<rect x="24" y="{y + 8}" width="{gain_w:.2f}" height="14" fill="{BAR}"/>',
                    f'<rect x="{24 + gain_w:.2f}" y="{y + 8}" width="{loss_w:.2f}" '
                    f'height="14" fill="{LOSS}"/>',
                    text(24, y + 42, f"{gain} gained · {loss} lost · {tie} tied", 14),
                ]
            )
        body.append(text(24, height - 15, footer, 13))
        name = f"context-tier-paired{suffix}.svg"
        write(name, width, height, title, f"{description}. {footer}", body)


def main():
    reports = load()
    means_chart(reports)
    paired_chart(reports)


if __name__ == "__main__":
    main()
