"""Independent event-side accounting. All money arithmetic stays in Decimal."""

import csv
import json
from collections import defaultdict
from decimal import Decimal as D


def records(folder, name):
    with (folder / (name + ".csv")).open(encoding="utf8", newline="") as stream:
        yield from csv.DictReader(stream)


def answers(folder):
    def rows(name):
        return records(folder, name)

    def index(name):
        return {int(x["id"]): x for x in rows(name)}

    inv = index("invoice")
    res = index("resource")
    skus = index("sku")
    services = index("service")
    teams = index("team")
    contracts = index("commitment")
    periods = index("fiscal_period")
    meters = {int(x["id"]): int(x["units"]) for x in rows("usage_day")}
    owners = defaultdict(list)
    for x in rows("resource_owner"):
        owners[int(x["resource_id"])].append(x)
    splits = defaultdict(list)
    for x in rows("shared_split"):
        splits[int(x["month_id"]), x["pool"]].append((int(x["center_id"]), D(x["weight"])))
    apps = defaultdict(list)
    for x in rows("commitment_application"):
        apps[int(x["charge_id"])].append(
            (int(x["contract_id"]), int(x["covered"]), D(x["applied"]))
        )
    prices = defaultdict(list)
    for x in rows("price_schedule"):
        prices[int(x["sku_id"]), int(x["region_id"])].append(x)
    budgets = {
        (int(x["period_id"]), int(x["center_id"])): D(x["budget"]) for x in rows("monthly_budget")
    }
    t = defaultdict(D)
    active = set()
    origins = {}
    dated = {}
    for x in rows("output_day"):
        t["out", int(x["day"][5:7]), int(x["project_id"])] += int(x["transactions"])

    def shares(r, day):
        return [
            (int(o["team_id"]), D(o["share"]))
            for o in owners[r]
            if o["first_day"] <= day < o["end_day"]
        ] or [(-1, D(1))]

    def center(team):
        return int(teams[team]["center_id"]) if team >= 0 else -1

    for x in rows("economic"):
        day = x["day"]
        m = int(day[5:7])
        q = (m - 1) // 3 + 1
        if day not in dated:
            dated[day] = next(i for i, v in periods.items() if v["first_day"] <= day < v["end_day"])
        f = dated[day]
        cid = int(x["charge_id"])
        i = int(x["invoice_id"])
        a = int(inv[i]["account_id"])
        post = int(inv[i]["posting_month"])
        s = int(x["sku_id"])
        service = int(skus[s]["service_id"])
        cls = int(services[service]["class_id"])
        cat = x["category"]
        b, e, c = map(D, (x["billed"], x["effective"], x["contracted"]))
        t["inv", i] += b
        t["post", post] += b
        t["acct", post, a] += b
        t["usageclock", m, a] += b
        t["service", m, service] += e
        if cat == "credit":
            t["credit", post] += b
            if post == 10 and origins[int(x["origin_id"])] == 9:
                t[17] += b
        if cat == "purchase":
            t["cash", q] += b
        if cat == "unused":
            t["expense", q] += e
            if m == 8 and x["contract_id"] == "2":
                t["unused"] += e
        r = int(x["resource_id"] or -1)
        if cat == "usage":
            origins[cid] = m
            rr = res[r]
            g = int(rr["region_id"])
            p = int(rr["project_id"])
            units = meters[int(x["meter_id"])]
            t["cost", m, p] += e
            if m == 5 and cls == 0 and g == 0 and skus[s]["unit"] == "hour":
                t[3] += units
            if m == 5 and cls == 1:
                t[4] += D(x["list_cost"]) - c
            if s == 0:
                t["qty", m, g] += units
                t["contracted", m, g] += c
            if (s, a, m) == (int(contracts[2]["sku_id"]), int(contracts[2]["account_id"]), 7):
                t["eligible"] += units
            for k, covered, applied in apps.get(cid, ()):
                t["expense", q] += applied
                if k == 2 and m == 7:
                    rate = next(
                        D(v["contract_rate"])
                        for v in prices[s, g]
                        if v["first_day"] <= day < v["end_day"]
                    )
                    t["covered"] += covered
                    t[26] += covered * rate - applied
                if k == 2 and m == 8:
                    t["applied"] += applied
            if m == 8:
                active.add(r)
            if m == 10 and cls == 0 and json.loads(rr["metadata"]).get("lifecycle") == "ephemeral":
                t[31] += e
        if x["pool"]:
            for cc, w in splits[m, x["pool"]]:
                t["alloc", f, cc] += e * w
                if m == 8:
                    t["pool", cc] += e * w
                if f == 7 and cc == 1:
                    t["shared"] += e * w
        else:
            for team, w in shares(r, day):
                cc = center(team)
                t["alloc", f, cc] += e * w
                if f == 7 and cc == 1:
                    t["direct"] += e * w
                if cc == -1 and m == 7:
                    t[22] += e * w
                if r == 17 and m == 6:
                    t["handoff", int(day >= "2025-06-16"), team] += e * w
                if m == 9:
                    t["move", cc] -= e * w
            if m == 9:
                for team, w in shares(r, "2025-12-31"):
                    t["move", center(team)] += e * w
    asof = {}
    raw = D(0)
    for x in rows("charge_revision"):
        post = int(inv[int(x["invoice_id"])]["posting_month"])
        if post == 6:
            raw += D(x["billed"])
        if post == 4 and x["arrived"] <= "2025-05-01":
            key = int(x["charge_id"])
            version = (int(x["revision"]), x["arrived"], int(x["export_id"]))
            if key not in asof or version > asof[key][0]:
                asof[key] = (version, D(x["billed"]))
    known = sum(v for _, v in asof.values())

    def qty(m, g):
        return t["qty", m, g]

    def rate(m, g):
        return t["contracted", m, g] / qty(m, g)

    regions = list(index("region"))
    accounts = list(index("account"))
    centers = list(index("cost_center"))
    projects = list(index("project"))
    v0 = sum(qty(6, g) for g in regions)
    v1 = sum(qty(7, g) for g in regions)

    def atlas(ms):
        return sum(t["cost", m, 0] for m in ms) / sum(t["out", m, 0] for m in ms)

    u, v = atlas(range(4, 7)), atlas(range(7, 10))

    def tags(date):
        ans = defaultdict(set)
        for x in rows("resource_tag"):
            if (
                x["first_day"] <= date < x["end_day"]
                and x["tag_key"].strip().lower() == "environment"
                and x["tag_value"].strip()
            ):
                ans[int(x["resource_id"])].add(x["tag_value"].strip().lower())
        return ans

    aug = tags("2025-08-31")
    affected = defaultdict(int)
    for r, vals in tags("2025-09-30").items():
        if len(vals) > 1:
            affected[int(res[r]["project_id"])] += 1
    budget = sum(budgets[m, 0] for m in range(1, 9))
    return {
        1: [[t["post", 3]]],
        2: sorted([(s, t["service", 4, s]) for s in services], key=lambda row: (-row[1], row[0]))[
            :3
        ],
        3: [[t[3]]],
        4: [[t[4]]],
        5: [(a, d) for a in accounts if (d := t["acct", 4, a] - t["acct", 3, a]) > 0],
        6: sorted(
            [(s, t["service", 5, s] - t["service", 4, s]) for s in services],
            key=lambda row: (-row[1], row[0]),
        )[:1],
        7: [[(qty(6, 0) - qty(5, 0)) * rate(5, 0), qty(6, 0) * (rate(6, 0) - rate(5, 0))]],
        8: [
            [
                (v1 - v0) * sum(t["contracted", 6, g] for g in regions) / v0,
                sum((qty(7, g) - v1 * qty(6, g) / v0) * rate(6, g) for g in regions),
                sum(qty(7, g) * (rate(7, g) - rate(6, g)) for g in regions),
            ]
        ],
        9: [[(t["credit", 6] - t["credit", 5]) / (t["post", 6] - t["post", 5])]],
        10: [[1000 * t["cost", 6, 0] / t["out", 6, 0]]],
        11: [(p, t["cost", 7, p]) for p in projects if t["cost", 7, p] > 0 and not t["out", 7, p]],
        12: [[u, v, v - u]],
        13: [(cc, d) for cc in centers if (d := t["alloc", 6, cc] - budgets[6, cc]) > 0],
        14: [[(sum(t["alloc", m, 0] for m in range(1, 9)) - budget) * 100 / budget]],
        15: [
            (cc, sum(budgets[m, cc] for m in (7, 8, 9)))
            for cc in centers
            if not sum(t["alloc", m, cc] for m in (7, 8, 9))
        ],
        16: [
            (i, t["inv", i], D(x["control"]), t["inv", i] - D(x["control"]))
            for i, x in inv.items()
            if x["posting_month"] == "9"
        ],
        17: [[t[17]]],
        18: [[known, t["post", 4], t["post", 4] - known]],
        19: [[raw - t["post", 6]]],
        20: [
            (cc, t["pool", cc], sum(t["pool", c] for c in centers))
            for cc in centers
            if t["pool", cc]
        ],
        21: [[t["direct"], t["shared"], t["direct"] + t["shared"]]],
        22: [[t[22]]],
        23: [
            (key[1], key[2], val)
            for key, val in t.items()
            if isinstance(key, tuple) and key[0] == "handoff"
        ],
        24: [(cc, t["move", cc]) for cc in [-1, *centers] if ("move", cc) in t],
        25: [[t["covered"] / t["eligible"]]],
        26: [[t[26]]],
        27: [[t["applied"], t["unused"], t["applied"] + t["unused"], D(contracts[2]["monthly"])]],
        28: [(q, t["cash", q], t["expense", q]) for q in range(1, 5)],
        29: [[D(sum(len(aug[r]) == 1 for r in active)) / len(active)]],
        30: list(affected.items()),
        31: [[t[31]]],
        32: [
            (a, t["usageclock", 12, a], t["acct", 12, a], t["usageclock", 12, a] - t["acct", 12, a])
            for a in accounts
            if t["usageclock", 12, a] != t["acct", 12, a]
        ],
    }
