"""Generate source events and a read-only export from deterministic business keys."""

import argparse
import csv
import hashlib
import json
import re
from contextlib import ExitStack
from datetime import date, timedelta
from decimal import Decimal as D
from pathlib import Path

import duckdb

HERE = Path(__file__).parent
START = date(2025, 1, 1)
END = date(2026, 1, 1)
SEEDS = {"development": 19, "evaluation_a": 43, "evaluation_b": 71}


def generate(root, seed):
    root.mkdir(parents=True, exist_ok=False)
    db = duckdb.connect(str(root / "warehouse.db"))
    db.execute((HERE / "schema.sql").read_text())
    tables = re.findall(r"CREATE TABLE (\w+)", (HERE / "schema.sql").read_text())
    balances = {}
    used = {}
    economic = [
        "charge_id",
        "day",
        "invoice_id",
        "resource_id",
        "meter_id",
        "sku_id",
        "category",
        "origin_id",
        "pool",
        "contract_id",
        "billed",
        "effective",
        "list_cost",
        "contracted",
        "memo",
    ]
    with ExitStack() as stack:
        writers = {
            t: csv.writer(
                stack.enter_context((root / (t + ".csv")).open("w", newline="", encoding="utf8"))
            )
            for t in [*tables, "economic"]
        }
        for t in tables:
            writers[t].writerow([c[0] for c in db.execute(f"describe {t}").fetchall()])
        writers["economic"].writerow(economic)

        def emit(t, *row):
            writers[t].writerow(row)

        seq = 0

        def charge(cid, day, inv, r, meter, sku, cat, origin, pool, k, b, e, list_amount, c, memo):
            nonlocal seq
            emit(
                "economic",
                cid,
                day,
                inv,
                r,
                meter,
                sku,
                cat,
                origin,
                pool,
                k,
                b,
                e,
                list_amount,
                c,
                memo,
            )
            balances[inv] = balances.get(inv, 0) + b
            revised = cat == "usage" and cid % 41 == 0
            arrival = (
                date(day.year + (day.month == 12), day.month % 12 + 1, 1)
                if cat == "credit"
                else day
            )
            fields = [inv, day, r, meter, sku, cat, origin, pool, k]
            seq += 1
            emit(
                "charge_revision",
                cid,
                1,
                seq,
                arrival,
                *fields,
                b + 1 if revised else b,
                e,
                list_amount,
                c,
                memo,
            )
            if cid % 53 == 0:
                seq += 1
                emit(
                    "charge_revision",
                    cid,
                    1,
                    seq,
                    arrival,
                    *fields,
                    b + 1 if revised else b,
                    e,
                    list_amount,
                    c,
                    memo,
                )
            if revised:
                seq += 1
                emit(
                    "charge_revision",
                    cid,
                    2,
                    seq,
                    day + timedelta(days=12),
                    *fields,
                    b,
                    e,
                    list_amount,
                    c,
                    "meter correction",
                )

        for i in range(2):
            emit("provider", i, ["Nimbus", "Cirrus"][i])
        for i in range(16):
            emit("account", i, i % 2)
            emit("team", i, i % 7)
        for i in range(8):
            emit("cost_center", i, ["Engineering", "Research", *[f"CC{x}" for x in range(2, 8)]][i])
        for i in range(64):
            emit("project", i, i % 16, "Atlas" if i == 0 else f"Project {i}")
        for i in range(4):
            emit("region", i, ["East", "West", "North", "South"][i])
        for i, n in enumerate(["compute", "storage", "network"]):
            emit("service_class", i, n)
        for i in range(10):
            emit("service", i, i % 3)

        def rate(s, g, late):
            return D(10 + s + g * 3 + seed % 9 + late * 4) / 100

        for s in range(40):
            emit("sku", s, s % 10, ["hour", "GB-day", "GB"][(s % 10) % 3])
            for g in range(4):
                for a, b, late in [(START, date(2025, 7, 1), 0), (date(2025, 7, 1), END, 1)]:
                    v = rate(s, g, late)
                    emit("price_schedule", s, g, a, b, v + D(".06"), v)
        for r in range(1200):
            proj = r % 64
            s = r % 40
            g = (r // 40 + seed) % 4
            emit(
                "resource",
                r,
                proj,
                s,
                g,
                json.dumps(
                    {"lifecycle": "ephemeral" if r % 3 == 0 else "stable"} if r % 11 else {}
                ),
            )
            if r % 37:
                handoff = date(2025, 6, 16) if r == 17 else date(2025, 10, 1)
                for a, b, offset in [(START, handoff, 0), (handoff, END, 1)]:
                    team = (r + seed + offset) % 16
                    if r % 13:
                        emit("resource_owner", r, team, a, b, 1)
                    else:
                        emit("resource_owner", r, team, a, b, D(".75"))
                        emit("resource_owner", r, (team + 1) % 16, a, b, D(".25"))
            if (r + seed) % 7:
                emit("resource_tag", r, " Environment ", " Prod " if r % 5 else "", START, END)
            if r % 29 == seed % 29:
                emit("resource_tag", r, "environment", "test", date(2025, 8, 1), END)
        a = START
        for i, weeks in enumerate([4, 4, 5] * 4, 1):
            b = a + timedelta(weeks=weeks) if i < 12 else END
            emit("fiscal_period", i, a, b)
            for center in range(8):
                emit("monthly_budget", i, center, 10000 + center * 200 + seed * i)
            a = b
        # K2 covers SKU 0 on account 0. K3 co-covers a subset of its eligible charges.
        monthly = 2000 + seed
        for k in [2, 3]:
            emit("commitment", k, 0, 0, START, END, monthly * 12, monthly)
        for m in range(1, 13):
            for center, weight in [(0, D(".6")), (1, D(".4"))]:
                emit("shared_split", m, "network", center, weight)
        for t in range(365):
            d = START + timedelta(days=t)
            for p in range(64):
                if p == seed % 63 + 1 and d.month == 7:
                    continue
                emit("output_day", p, d, (t * (p + 7) + seed) % 800 if (p + t) % 17 else 0)
            for r in range(1200):
                if (r + t + seed) % 4 == 0:
                    continue
                s = r % 40
                cid = t * 1200 + r + 1
                noise = hashlib.blake2s(f"{seed}:meter:{cid}".encode(), digest_size=2).digest()
                qty = 1 + (int.from_bytes(noise, "big") + d.month * 3) % 77
                base = rate(s, (r // 40 + seed) % 4, int(d.month >= 7))
                c = qty * base
                inv = d.month * 100 + r % 16
                b = e = c
                if s == 0 and r % 16 == 0:
                    for k, units in [(2, qty // 2), (3, qty // 4)]:
                        if units:
                            applied = D(".04") * units
                            emit("commitment_application", k, cid, units, applied)
                            used[k, d.month] = used.get((k, d.month), 0) + applied
                            b -= units * base
                            e -= units * base - applied
                pool = "network" if s % 10 % 3 == 2 and r % 5 == 2 else None
                emit("usage_day", cid, r, d, qty)
                charge(
                    cid,
                    d,
                    inv,
                    r,
                    cid,
                    s,
                    "usage",
                    None,
                    pool,
                    None,
                    b,
                    e,
                    c + qty * D(".06"),
                    c,
                    "metered service",
                )
                if cid % 389 == 0:
                    credit = -D(seed % 8 + 1)
                    charge(
                        1000000 + cid,
                        d,
                        (d.month + 1) * 100 + r % 16,
                        None,
                        None,
                        s,
                        "credit",
                        cid,
                        None,
                        None,
                        credit,
                        credit,
                        0,
                        0,
                        "service credit; prior usage",
                    )
        for k in [2, 3]:
            charge(
                2000000 + k,
                START,
                100,
                None,
                None,
                0,
                "purchase",
                None,
                None,
                k,
                monthly * 12,
                0,
                0,
                0,
                "annual capacity",
            )
            for m in range(1, 13):
                unused = monthly - used.get((k, m), 0)
                assert unused >= 0
                charge(
                    2100000 + k * 100 + m,
                    date(2025, m, 1),
                    m * 100,
                    None,
                    None,
                    0,
                    "unused",
                    None,
                    None,
                    k,
                    0,
                    unused,
                    0,
                    0,
                    "unused reservation",
                )
        for inv, total in sorted(balances.items()):
            emit("invoice", inv, inv % 100, inv // 100, total)
    volumes = {}
    hashes = {}
    for t in tables:
        file = root / (t + ".csv")
        db.execute(f"COPY {t} FROM ? (HEADER,FORMAT CSV)", [str(file)])
        volumes[t] = db.execute(f"select count(*) from {t}").fetchone()[0]
        hashes[t] = hashlib.sha256(file.read_bytes()).hexdigest()
    db.close()
    info = {
        "seed": seed,
        "volumes": volumes,
        "table_csv_sha256": hashes,
        "economic_sha256": hashlib.sha256((root / "economic.csv").read_bytes()).hexdigest(),
    }
    (root / "manifest.json").write_text(json.dumps(info, sort_keys=True, indent=2))
    return info


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    args = p.parse_args()
    for name, seed in SEEDS.items():
        generate(args.root / name, seed)
