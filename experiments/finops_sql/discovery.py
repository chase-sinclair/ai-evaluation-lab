"""Reviewer-only coverage audit of the neutral catalog and describe contracts."""

import json
import re
from pathlib import Path

# Each glossary entry describes a reusable warehouse convention.
POLICY = {
    "closing": (
        "charge_revision",
        (
            "Keep one delivery per charge_id, highest revision then arrived then "
            "export_id. For an as-of close, first keep arrivals up to and "
            "including cutoff UTC date. Signed credit and purchase postings are "
            "included in net billed. Join invoice on invoice_id for posting "
            "clock. Charge day is the economic usage clock. Month 13 is January "
            "2026."
        ),
    ),
    "costs": (
        "charge_revision",
        (
            "Amounts in USD. Billed is invoiced cash, effective recognizes "
            "amortized expense, contracted is eligible on-demand price times "
            "quantity, list is undiscounted. Usage comparisons use category "
            "usage. Effective includes all categories unless explicitly limited "
            "to usage."
        ),
    ),
    "codes": (
        "sku resource commitment",
        (
            "X denotes SKU 0, R-number denotes resource id, K-number denotes "
            "commitment id. Named projects, regions, classes and centers resolve "
            "via their name fields."
        ),
    ),
    "variance": (
        "usage_day invoice",
        (
            "SKU changes use realized contracted usage dollars per metered unit. "
            "Bridge volume at base mix and price, then mix at base regional "
            "prices, then prices at current regional units. Credits' contribution "
            "to a billed change uses signed credit change divided by signed total "
            "change."
        ),
    ),
    "output": (
        "output_day",
        (
            "Completed transactions are project-day outputs. Aggregate numerator "
            "and denominator independently before dividing. Missing daily output "
            "is zero when assessing activity. Undefined division returns NULL. "
            "Quarter comparisons use ratios of sums."
        ),
    ),
    "allocation": (
        "resource_owner shared_split",
        (
            "Use usage day and half-open owner intervals. Split direct effective "
            "cost by team share then center, unmatched goes to Unassigned (-1). "
            "Shared rows are removed from direct cost and distributed by calendar "
            "usage month and pool. Preserve all dollars including resource-less "
            "direct expense."
        ),
    ),
    "fiscal": (
        "fiscal_period monthly_budget",
        (
            "Budget is approved per fiscal period and center. Actuals are "
            "allocated effective cost mapped by usage day to half-open fiscal "
            "periods. Fiscal Q3 is periods 7–9. Variance percentage is 100 "
            "times (actual minus budget) divided by budget. Other quarterly "
            "reports use calendar quarters."
        ),
    ),
    "commitments": (
        "commitment commitment_application price_schedule",
        (
            "Eligibility uses contract account, SKU and term. Applications are "
            "contract-charge allocations. Savings equals covered units at dated "
            "SKU-region contracted rate less applied amortization. Service "
            "expense is applied plus unused; purchase cash uses billed purchase "
            "rows."
        ),
    ),
    "labels": (
        "resource resource_tag",
        (
            "Use date-active tag intervals, trim/lower keys and values, discard "
            "blanks. Usable means exactly one distinct normalized value. Active "
            "resources have metered usage in the period. JSON lifecycle is "
            "resource metadata; missing path is unknown."
        ),
    ),
}
NEEDS = [
    "charge_revision invoice @closing",
    "charge_revision sku service @closing @costs",
    "usage_day resource region sku service service_class",
    "charge_revision sku service service_class @closing @costs",
    "charge_revision invoice @closing",
    "charge_revision sku @closing @costs",
    "charge_revision resource region sku usage_day @closing @variance @codes",
    "charge_revision resource usage_day @closing @variance @codes",
    "charge_revision invoice @closing @variance",
    "charge_revision project resource output_day @closing @output @costs",
    "charge_revision resource output_day @closing @output @costs",
    "charge_revision project resource output_day @closing @output @costs",
    *[
        (
            "charge_revision resource_owner team shared_split fiscal_period "
            "monthly_budget @closing @allocation @fiscal"
        )
    ]
    * 3,
    "charge_revision invoice @closing",
    "charge_revision invoice @closing",
    "charge_revision invoice @closing",
    "charge_revision invoice @closing",
    "charge_revision shared_split @closing @allocation",
    (
        "charge_revision resource_owner team cost_center shared_split "
        "fiscal_period @closing @allocation @fiscal"
    ),
    "charge_revision resource_owner @closing @allocation",
    "charge_revision resource_owner @closing @allocation @codes",
    "charge_revision resource_owner team @closing @allocation",
    (
        "charge_revision invoice usage_day commitment commitment_application "
        "@closing @commitments @codes"
    ),
    "charge_revision resource commitment_application price_schedule @closing @commitments @codes",
    "charge_revision commitment commitment_application @closing @commitments @codes",
    "charge_revision commitment_application @closing @commitments",
    "usage_day resource_tag @labels",
    "resource_tag resource @labels",
    "charge_revision resource sku service service_class @closing @labels @costs",
    "charge_revision invoice @closing",
]


# An ID is declared sufficient only if its schema or metric has actually been described.
def entries():
    ddl = Path(__file__).with_name("schema.sql").read_text()
    objects = {}
    for name, body in re.findall(r"CREATE TABLE (\w+) \(([\s\S]*?)\);", ddl):
        grain = re.search(r"PRIMARY KEY \(([^)]+)\)", body)[1]
        links = ["@" + p for p, (tables, _) in POLICY.items() if name in tables.split()]
        objects[name] = {
            "ddl": " ".join(("CREATE TABLE " + name + " (" + body + ");").split()),
            "grain": grain,
            "glossary": links,
        }
    objects.update({"@" + p: {"definition": v} for p, (_, v) in POLICY.items()})
    return objects


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


def describe(ids, objects):
    if len(ids) > 3 or len(set(ids)) != len(ids):
        raise ValueError("invalid describe batch")
    return {k: objects[k] for k in ids}


def paths():
    objects = entries()
    traces = {}
    for number, spec in enumerate(NEEDS, 1):
        if number == 14:
            spec += " cost_center"
        query = " ".join(spec.replace("@", "").replace("_", " ").split())
        # A reviewer may enter free-text search words; subsequent describe IDs
        # must have actually appeared in a catalog or glossary cross-reference.
        if not {k for k in spec.split() if not k.startswith("@")} <= set(catalog(query, objects)):
            query = ""
        known = set(catalog(query, objects))
        missing = set(spec.split())
        events = [["catalog", query]]
        while missing:
            choices = sorted(missing & known, key=lambda k: (k.startswith("@"), k))
            if not choices:
                raise ValueError((number, missing))
            batch = choices[:3]
            response = describe(batch, objects)
            events.append(["describe", batch])
            for entry in response.values():
                known.update(entry.get("glossary", ()))
            missing.difference_update(batch)
        # At least one discovery call and ceil(n/3) full descriptions are required
        # when IDs cannot be guessed. This witness attains that bound.
        assert len(events) == 1 + (len(spec.split()) + 2) // 3, (number, events)
        traces[number] = events
    return traces


def sizes(encode):
    objects = entries()

    def encode_json(v):
        return len(encode(json.dumps(v, separators=(",", ":"))))

    return {
        i: max(
            encode_json(catalog(arg, objects) if op == "catalog" else describe(arg, objects))
            for op, arg in steps
        )
        for i, steps in paths().items()
    }
