"""Inspectable DuckDB reference calculations. Expand only the required CTEs."""

CTES = {
    "ranked": (
        "SELECT c.*, row_number() over(partition by charge_id order by revision "
        "desc, arrived desc, export_id desc) AS rn FROM charge_revision c"
    ),
    "charges": "SELECT * FROM ranked WHERE rn=1",
    "ledger": """SELECT c.*, i.account_id, i.posting_month AS post, extract(month from c.day) AS m,
 r.project_id,r.region_id,r.metadata,s.service_id,sv.class_id
 FROM charges c JOIN invoice i ON c.invoice_id=i.id
 LEFT JOIN resource r ON c.resource_id=r.id JOIN sku s ON c.sku_id=s.id
 JOIN service sv ON s.service_id=sv.id""",
    "allocated": (
        "SELECT l.day,l.m,f.id AS period,coalesce(t.center_id,-1) AS center, "
        "l.effective*coalesce(o.share,1) AS value,'direct' AS kind FROM ledger l "
        "JOIN fiscal_period f ON l.day>=f.first_day AND l.day<f.end_day LEFT JOIN "
        "resource_owner o ON l.resource_id=o.resource_id AND l.day>=o.first_day "
        "AND l.day<o.end_day LEFT JOIN team t ON o.team_id=t.id WHERE l.pool IS "
        "NULL UNION ALL SELECT "
        "l.day,l.m,f.id,w.center_id,l.effective*w.weight,'pool' FROM ledger l "
        "JOIN fiscal_period f ON l.day>=f.first_day AND l.day<f.end_day JOIN "
        "shared_split w ON l.pool=w.pool AND l.m=w.month_id"
    ),
    "rates": """SELECT l.m,l.region_id,sum(u.units) AS q,sum(l.contracted)/sum(u.units) AS rate
 FROM ledger l JOIN usage_day u ON l.meter_id=u.id WHERE l.sku_id=0 GROUP BY 1,2""",
    "tags": """SELECT resource_id,count(distinct lower(trim(tag_value))) AS n FROM resource_tag
 WHERE lower(trim(tag_key))='environment' AND trim(tag_value)<>'' AND first_day<=DATE '2025-08-31'
 AND end_day>DATE '2025-08-31' GROUP BY 1""",
    "costs": (
        "SELECT project_id,m,sum(effective) AS cost FROM ledger WHERE project_id "
        "IS NOT NULL GROUP BY 1,2"
    ),
    "outputs": (
        "SELECT project_id,extract(month from day) AS m,sum(transactions) AS qty "
        "FROM output_day GROUP BY 1,2"
    ),
}
QUERIES = {}


def add(num, parts, sql, extra=""):
    deps = [f"{n} AS ({CTES[n]})" for n in parts.split()]
    if extra:
        deps.append(extra)
    QUERIES[num] = ("WITH " + ",\n".join(deps) + "\n" if deps else "") + sql


L = "ranked charges ledger"
A = L + " allocated"
add(1, L, "SELECT sum(billed) AS cost FROM ledger WHERE post=3")
add(
    2,
    L,
    (
        "SELECT service_id,sum(effective) AS cost FROM ledger WHERE m=4 GROUP BY "
        "1 ORDER BY 2 DESC,1 LIMIT 3"
    ),
)
add(
    3,
    "",
    (
        "SELECT sum(units) AS hours FROM usage_day u JOIN resource r ON "
        "u.resource_id=r.id JOIN sku s ON r.sku_id=s.id JOIN service sv ON "
        "s.service_id=sv.id JOIN service_class sc ON sv.class_id=sc.id JOIN "
        "region g ON g.id=r.region_id WHERE sc.name='compute' AND g.name='East' "
        "AND s.unit='hour' AND extract(month from u.day)=5"
    ),
)
add(
    4,
    L,
    (
        "SELECT sum(list_cost-contracted) AS gap FROM ledger WHERE m=5 AND "
        "class_id=1 AND category='usage'"
    ),
)
add(
    5,
    L,
    (
        "SELECT account_id,sum(case when post=4 then billed else -billed end) AS "
        "delta FROM ledger WHERE post IN (3,4) GROUP BY 1 HAVING delta>0"
    ),
)
add(
    6,
    L,
    (
        "SELECT service_id,sum(case when m=5 then effective else -effective end) "
        "AS delta FROM ledger WHERE m IN (4,5) GROUP BY 1 ORDER BY 2 DESC,1 LIMIT "
        "1"
    ),
)
add(
    7,
    L + " rates",
    (
        "SELECT (b.q-a.q)*a.rate AS volume,b.q*(b.rate-a.rate) AS price FROM "
        "rates a JOIN rates b ON a.region_id=b.region_id WHERE a.region_id=0 AND "
        "a.m=5 AND b.m=6"
    ),
)
add(
    8,
    L + " rates",
    (
        "SELECT (v1-v0)*sum(a.q*a.rate)/v0 AS volume,sum((b.q-v1*a.q/v0)*a.rate) "
        "AS mix,sum(b.q*(b.rate-a.rate)) AS price FROM rates a JOIN rates b ON "
        "a.region_id=b.region_id CROSS JOIN totals WHERE a.m=6 AND b.m=7 GROUP BY "
        "v0,v1"
    ),
    (
        "totals AS (SELECT sum(case when m=6 then q else 0 end) AS v0,sum(case "
        "when m=7 then q else 0 end) AS v1 FROM rates)"
    ),
)
add(
    9,
    L,
    (
        "SELECT sum(case when category='credit' then billed*sgn else 0 "
        "end)/nullif(sum(billed*sgn),0) AS fraction FROM (SELECT *,case when "
        "post=6 then 1 else -1 end AS sgn FROM ledger WHERE post IN (5,6)) x"
    ),
)
add(
    10,
    L + " costs outputs",
    (
        "SELECT cost*1000/nullif(qty,0) AS unit_cost FROM costs JOIN outputs "
        "USING(project_id,m) WHERE m=6 AND project_id=0"
    ),
)
add(
    11,
    L + " costs outputs",
    (
        "SELECT c.project_id,c.cost FROM costs c LEFT JOIN outputs o "
        "USING(project_id,m) WHERE c.m=7 AND c.cost>0 AND coalesce(o.qty,0)=0"
    ),
)
add(
    12,
    L + " costs outputs",
    (
        "SELECT a AS q2,b AS q3,b-a AS delta FROM (SELECT sum(case when m<7 then "
        "cost else 0 end)/sum(case when m<7 then qty else 0 end) AS a,sum(case "
        "when m>=7 then cost else 0 end)/sum(case when m>=7 then qty else 0 end) "
        "AS b FROM costs JOIN outputs USING(project_id,m) WHERE project_id=0 AND "
        "m BETWEEN 4 AND 9) x"
    ),
)
add(
    13,
    A,
    (
        "SELECT center,sum(value)-budget AS delta FROM allocated JOIN "
        "monthly_budget ON center=center_id AND period=period_id WHERE period=6 "
        "GROUP BY center,budget HAVING delta>0"
    ),
)
add(
    14,
    A,
    (
        "SELECT (sum(value)-b)/b*100 AS variance_pct FROM allocated CROSS JOIN "
        "(SELECT sum(budget) AS b FROM monthly_budget WHERE center_id=0 AND "
        "period_id<=8) x WHERE center=0 AND period<=8 GROUP BY b"
    ),
)
add(
    15,
    A,
    (
        "SELECT center_id,sum(budget) AS unused FROM monthly_budget WHERE "
        "period_id BETWEEN 7 AND 9 AND center_id NOT IN (SELECT center FROM "
        "allocated WHERE period BETWEEN 7 AND 9 GROUP BY center HAVING "
        "sum(value)<>0) GROUP BY 1"
    ),
)
add(
    16,
    "ranked charges",
    (
        "SELECT i.id,sum(c.billed) AS actual,i.control,sum(c.billed)-i.control AS "
        "residual FROM invoice i JOIN charges c ON c.invoice_id=i.id WHERE "
        "i.posting_month=9 GROUP BY i.id,i.control"
    ),
)
add(
    17,
    L,
    (
        "SELECT sum(c.billed) AS credit FROM ledger c JOIN charges o ON "
        "c.origin_id=o.charge_id WHERE c.post=10 AND c.category='credit' AND "
        "extract(month from o.day)=9"
    ),
)
add(
    18,
    L,
    (
        "SELECT v AS as_of,sum(billed) AS final,sum(billed)-v AS delta FROM "
        "ledger CROSS JOIN (SELECT sum(billed) AS v FROM (SELECT "
        "c.billed,row_number() over(partition by charge_id order by revision "
        "desc,arrived desc,export_id desc) AS pos FROM charge_revision c JOIN "
        "invoice i ON c.invoice_id=i.id WHERE i.posting_month=4 AND arrived<=DATE "
        "'2025-05-01') a WHERE pos=1) x WHERE post=4 GROUP BY v"
    ),
)
add(
    19,
    "ranked",
    (
        "SELECT sum(case when rn>1 then billed else 0 end) AS excess FROM ranked "
        "JOIN invoice i ON invoice_id=i.id WHERE posting_month=6"
    ),
)
add(
    20,
    "ranked charges",
    (
        "SELECT center_id, sum(effective*weight) AS "
        "allocated,sum(sum(effective*weight)) over() AS total FROM charges JOIN "
        "shared_split USING(pool) WHERE month_id=8 AND extract(month from day)=8 "
        "GROUP BY 1"
    ),
)
add(
    21,
    A,
    (
        "SELECT sum(case when kind='direct' then value else 0 end) AS "
        "direct,sum(case when kind='pool' then value else 0 end) AS "
        "shared,sum(value) AS total FROM allocated WHERE period=7 AND center=1"
    ),
)
add(22, A, "SELECT sum(value) AS unknown FROM allocated WHERE m=7 AND center=-1")
add(
    23,
    L,
    (
        "SELECT case when l.day<DATE '2025-06-16' then 0 else 1 end AS "
        "phase,team_id,sum(effective*share) AS cost FROM ledger l JOIN "
        "resource_owner o ON l.resource_id=o.resource_id AND l.day>=first_day AND "
        "l.day<end_day WHERE l.resource_id=17 AND m=6 GROUP BY 1,2"
    ),
)
add(
    24,
    A,
    (
        "SELECT center,sum(value) AS moved FROM (SELECT center,-value AS value "
        "FROM allocated WHERE m=9 AND kind='direct' UNION ALL SELECT "
        "coalesce(t.center_id,-1),l.effective*coalesce(o.share,1) FROM ledger l "
        "LEFT JOIN resource_owner o ON l.resource_id=o.resource_id AND DATE "
        "'2025-12-31'>=o.first_day AND DATE '2025-12-31'<o.end_day LEFT JOIN team "
        "t ON t.id=o.team_id WHERE m=9 AND pool IS NULL) x GROUP BY 1"
    ),
)
add(
    25,
    L,
    (
        "SELECT sum(coalesce(a.covered,0))/sum(u.units) AS fraction FROM ledger l "
        "JOIN usage_day u ON l.meter_id=u.id JOIN commitment k ON "
        "l.account_id=k.account_id AND k.sku_id=l.sku_id LEFT JOIN "
        "commitment_application a ON a.contract_id=k.id AND "
        "l.charge_id=a.charge_id WHERE k.id=2 AND m=7"
    ),
)
add(
    26,
    L,
    (
        "SELECT sum(covered*contract_rate-applied) AS saving FROM ledger l JOIN "
        "commitment_application a ON l.charge_id=a.charge_id JOIN price_schedule "
        "p ON p.sku_id=l.sku_id AND p.region_id=l.region_id AND "
        "l.day>=p.first_day AND l.day<p.end_day WHERE a.contract_id=2 AND m=7"
    ),
)
add(
    27,
    L,
    (
        "SELECT a AS applied,u AS unused,a+u AS total,k.monthly AS schedule FROM "
        "commitment k CROSS JOIN (SELECT sum(applied) AS a FROM "
        "commitment_application x JOIN ledger l ON x.charge_id=l.charge_id WHERE "
        "x.contract_id=2 AND m=8) x CROSS JOIN (SELECT sum(effective) AS u FROM "
        "ledger WHERE contract_id=2 AND category='unused' AND m=8) y WHERE k.id=2"
    ),
)
add(
    28,
    L,
    (
        "SELECT q,sum(cash) AS cash,sum(expense) AS expense FROM (SELECT "
        "extract(quarter from day) AS q,case when category='purchase' then billed "
        "else 0 end AS cash,case when category='unused' then effective else 0 end "
        "AS expense FROM ledger UNION ALL SELECT extract(quarter from "
        "day),0,applied FROM ledger l JOIN commitment_application a ON "
        "l.charge_id=a.charge_id) x GROUP BY 1"
    ),
)
add(
    29,
    "tags",
    (
        "SELECT count(distinct case when n=1 then u.resource_id "
        "end)/count(distinct u.resource_id) AS fraction FROM usage_day u LEFT "
        "JOIN tags t USING(resource_id) WHERE extract(month from day)=8"
    ),
)
add(
    30,
    "",
    (
        "SELECT project_id,count(*) AS affected FROM resource r JOIN (SELECT "
        "resource_id FROM resource_tag WHERE lower(trim(tag_key))='environment' "
        "AND trim(tag_value)<>'' AND first_day<=DATE '2025-09-30' AND "
        "end_day>DATE '2025-09-30' GROUP BY 1 HAVING count(distinct "
        "lower(trim(tag_value)))>1) t ON r.id=t.resource_id GROUP BY 1"
    ),
)
add(
    31,
    L,
    (
        "SELECT sum(effective) AS cost FROM ledger WHERE m=10 AND class_id=0 AND "
        "category='usage' AND metadata->>'lifecycle'='ephemeral'"
    ),
)
add(
    32,
    L,
    (
        "SELECT account_id,sum(case when m=12 then billed else 0 end) AS "
        "usage_total,sum(case when post=12 then billed else 0 end) AS "
        "posted,sum(case when m=12 then billed else 0 end)-sum(case when post=12 "
        "then billed else 0 end) AS delta FROM ledger GROUP BY 1 HAVING delta<>0"
    ),
)
