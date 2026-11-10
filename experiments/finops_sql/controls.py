"""Offline calibration tasks, accounting controls and deliberately wrong analytical choices."""

from .references import CTES, QUERIES


def with_tables(names, sql):
    return "WITH " + ", ".join(f"{n} AS ({CTES[n]})" for n in names.split()) + " " + sql


LEDGER = "ranked charges ledger"
ALLOC = LEDGER + " allocated"
# The D-series belongs exclusively to the development snapshot.
DEVELOPMENT = {
    "D01": (
        "How much was billed on January invoices?",
        with_tables(LEDGER, "SELECT sum(billed) AS cost FROM ledger WHERE post=1"),
    ),
    "D02": (
        "How many extra delivery rows did February invoices contain?",
        with_tables(
            "ranked",
            (
                "SELECT count(*) AS repeats FROM ranked JOIN invoice ON "
                "invoice_id=id WHERE posting_month=2 AND rn>1"
            ),
        ),
    ),
    "D03": (
        "What were January 2026 postings for 2025 usage?",
        with_tables(LEDGER, "SELECT sum(billed) AS cost FROM ledger WHERE post=13"),
    ),
    "D04": (
        "Allocate the February network pool to its recipients.",
        QUERIES[20].replace("=8", "=2"),
    ),
    "D05": (
        "Which teams owned R17 on January 1?",
        (
            "SELECT team_id,share FROM resource_owner WHERE resource_id=17 AND "
            "first_day<=DATE '2025-01-01' AND end_day>DATE '2025-01-01'"
        ),
    ),
    "D06": (
        "What was the July change in SKU X contracted rate in West from June?",
        with_tables(
            LEDGER + " rates",
            (
                "SELECT b.rate-a.rate AS change FROM rates a JOIN rates b ON "
                "a.region_id=b.region_id WHERE a.region_id=1 AND a.m=6 AND b.m=7"
            ),
        ),
    ),
    "D07": (
        "Which resources had conflicting environment tags on January 31?",
        (
            "SELECT resource_id FROM resource_tag WHERE "
            "lower(trim(tag_key))='environment' AND first_day<=DATE '2025-01-31' "
            "AND end_day>DATE '2025-01-31' AND trim(tag_value)<>'' GROUP BY 1 "
            "HAVING count(distinct lower(trim(tag_value)))>1"
        ),
    ),
    "D08": ("What did Finance spend in February?", None),
}
# Each control returns zero violations.
INTEGRITY = {
    "invoice": with_tables(
        "ranked charges",
        (
            "SELECT count(*) FROM (SELECT i.id FROM invoice i LEFT JOIN charges "
            "ON i.id=invoice_id GROUP BY i.id,i.control HAVING sum(billed) IS "
            "NULL OR sum(billed)<>i.control) x"
        ),
    ),
    "amort": with_tables(
        LEDGER,
        (
            "SELECT count(*) FROM (SELECT contract_id,m,sum(value) AS v FROM "
            "(SELECT a.contract_id,m,applied AS value FROM ledger JOIN "
            "commitment_application a USING(charge_id) UNION ALL SELECT "
            "contract_id,m,effective FROM ledger WHERE category='unused') x GROUP "
            "BY 1,2) y JOIN commitment k ON k.id=y.contract_id WHERE v<>monthly"
        ),
    ),
    "alloc": with_tables(
        ALLOC,
        (
            "SELECT count(*) FROM (SELECT m,sum(value) AS actual FROM allocated "
            "GROUP BY 1) a JOIN (SELECT m,sum(effective) AS total FROM ledger "
            "GROUP BY 1) b USING(m) WHERE actual<>total"
        ),
    ),
    "shares": (
        "SELECT count(*) FROM (SELECT resource_id,first_day,end_day FROM "
        "resource_owner GROUP BY 1,2,3 HAVING sum(share)<>1 OR min(share)<=0) x"
    ),
    "weights": (
        "SELECT count(*) FROM (SELECT month_id,pool FROM shared_split GROUP BY "
        "1,2 HAVING sum(weight)<>1 OR min(weight)<=0) x"
    ),
    "rate": with_tables(
        LEDGER,
        (
            "SELECT count(*) FROM (SELECT charge_id FROM ledger l LEFT JOIN "
            "price_schedule p ON p.sku_id=l.sku_id AND p.region_id=l.region_id "
            "AND l.day>=p.first_day AND l.day<p.end_day WHERE category='usage' "
            "GROUP BY 1 HAVING count(p.sku_id)<>1) x"
        ),
    ),
    "origin": with_tables(
        "ranked charges",
        (
            "SELECT count(*) FROM charges c LEFT JOIN charges o ON "
            "c.origin_id=o.charge_id WHERE c.category='credit' AND (o.category IS "
            "NULL OR o.category<>'usage' OR c.billed>=0)"
        ),
    ),
    "coverage": with_tables(
        "ranked charges",
        (
            "SELECT count(*) FROM (SELECT charge_id,sum(covered) AS covered FROM "
            "commitment_application GROUP BY 1) a JOIN charges USING(charge_id) "
            "JOIN usage_day u ON u.id=meter_id WHERE covered>units"
        ),
    ),
    "intervals": (
        "SELECT count(*) FROM resource_owner a JOIN resource_owner b ON "
        "a.resource_id=b.resource_id AND a.first_day<b.first_day AND "
        "a.end_day>b.first_day"
    ),
    "calendar": (
        "SELECT count(*) FROM fiscal_period a JOIN fiscal_period b ON b.id=a.id+1 "
        "WHERE a.end_day<>b.first_day"
    ),
}
MUTATIONS = {
    "raw": (1, QUERIES[1].replace("rn=1", "rn>=1")),
    "basis": (2, QUERIES[2].replace("sum(effective)", "sum(list_cost)")),
    "join": (20, QUERIES[20].replace("effective*weight", "effective")),
    "ownership": (
        23,
        QUERIES[23].replace(
            "l.day>=first_day AND l.day<end_day",
            "DATE '2025-12-31'>=first_day AND DATE '2025-12-31'<end_day",
        ),
    ),
    "clock": (1, QUERIES[1].replace("post=3", "m=3")),
    "ratio": (
        12,
        QUERIES[12]
        .replace(
            "sum(case when m<7 then cost else 0 end)/sum(case when m<7 then qty else 0 end)",
            "sum(case when m<7 then cost/qty else 0 end)/3",
        )
        .replace(
            "sum(case when m>=7 then cost else 0 end)/sum(case when m>=7 then qty else 0 end)",
            "sum(case when m>=7 then cost/qty else 0 end)/3",
        ),
    ),
}
DENIED = {
    "mutation": "DELETE FROM project",
    "external": "SELECT * FROM read_csv('elsewhere.csv')",
    "extension": "INSTALL json",
    "config": "SET threads=2",
    "catalog": "SELECT * FROM information_schema.tables",
    "function": "SELECT random()",
    "rows": "SELECT id FROM resource",
    "multiple": "SELECT 1; SELECT 2",
}


def team_leader(m, basis):
    return with_tables(
        LEDGER,
        "SELECT team_id FROM ledger l JOIN resource_owner o ON l.resource_id=o.resource_id "
        f"AND l.day>=first_day AND l.day<end_day WHERE m={m} GROUP BY team_id "
        f"ORDER BY sum({basis}*share) DESC,team_id LIMIT 1",
    )


CLARIFICATIONS = {
    33: ("period and cost basis", team_leader(1, "billed"), team_leader(10, "effective")),
    34: (
        "reporting center or scope",
        *[
            with_tables(
                ALLOC,
                "SELECT sum(value)-budget FROM allocated JOIN monthly_budget "
                f"ON center_id=center AND period_id=period WHERE center={cc} "
                "AND period=6 GROUP BY budget",
            )
            for cc in (0, 1)
        ],
    ),
    35: (
        "list-to-contract discount or commitment saving",
        with_tables(LEDGER, "SELECT sum(list_cost-contracted) FROM ledger WHERE m=7"),
        QUERIES[26].replace("a.contract_id=2 AND ", ""),
    ),
    36: (
        "output unit and SKU for a metered denominator",
        with_tables(
            LEDGER + " costs outputs",
            (
                "SELECT sum(cost)/sum(qty) FROM costs JOIN outputs "
                "USING(project_id,m) WHERE project_id=0 AND m>=10"
            ),
        ),
        with_tables(
            LEDGER,
            (
                "SELECT sum(effective)/sum(units) FROM ledger JOIN usage_day ON "
                "meter_id=id WHERE m>=10 AND project_id=0 AND sku_id=0"
            ),
        ),
    ),
}
