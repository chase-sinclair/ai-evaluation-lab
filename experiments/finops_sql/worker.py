"""Container entry point. One disposable child per candidate query."""

import json
import multiprocessing
import sys
import time

import duckdb
import sqlglot
from sqlglot import exp

TABLES = set(
    (
        "provider account project region service_class service sku resource team "
        "cost_center resource_owner resource_tag fiscal_period invoice usage_day "
        "charge_revision price_schedule commitment commitment_application "
        "shared_split monthly_budget output_day"
    ).split()
)
NODES = set(
    (
        "Select Having JSONPath JSONPathRoot JSONPathKey Union With CTE Table "
        "TableAlias Identifier Column From Join Where Group Order Ordered Limit "
        "Alias Literal Star Distinct Subquery Paren And Or Not EQ NEQ GT GTE LT "
        "LTE Is Null In Between Add Sub Mul Div Neg Case If Window WindowSpec "
        "Partition Tuple DataType Cast Interval Boolean Var"
    ).split()
)
FUNCTIONS = set(
    (
        "SUM COUNT MAX MIN ROUND COALESCE NULLIF LOWER TRIM EXTRACT ROW_NUMBER "
        "JSON_EXTRACT_SCALAR ABS"
    ).split()
)


def validate(sql):
    if len(sql.encode()) > 65536:
        raise ValueError("query size")
    trees = sqlglot.parse(sql, read="duckdb")
    if len(trees) != 1 or not isinstance(trees[0], (exp.Select, exp.Union)):
        raise ValueError("one query required")
    tree = trees[0]
    names = TABLES | {cte.alias.lower() for cte in tree.find_all(exp.CTE)}
    for n in tree.walk():
        if isinstance(n, exp.Column) and n.name.lower() == "rowid":
            raise ValueError("internal row identifier")
        if isinstance(n, exp.Table):
            if (
                not isinstance(n.this, exp.Identifier)
                or n.db
                or n.catalog
                or n.name.lower() not in names
            ):
                raise ValueError("relation")
        if isinstance(n, exp.With) and n.args.get("recursive"):
            raise ValueError("recursive query")
        if type(n).__name__ in NODES:
            continue
        if isinstance(n, exp.Func) and n.sql_name() in FUNCTIONS:
            continue
        raise ValueError(f"unapproved node {type(n).__name__}")
    # Execute the validated tree's rendering, never the original token stream.
    return tree.sql(dialect="duckdb")


def execute(sql, pipe):
    import resource

    start = time.perf_counter()
    try:
        sql = validate(sql)
        db = duckdb.connect(
            "/warehouse.db",
            read_only=True,
            config={
                "enable_external_access": "false",
                "autoload_known_extensions": "false",
                "autoinstall_known_extensions": "false",
                "threads": "1",
                "memory_limit": "300MB",
                "max_temp_directory_size": "0B",
                "lock_configuration": "true",
            },
        )
        cur = db.execute(sql)
        rows = cur.fetchmany(1001)
        if len(rows) > 1000:
            raise ValueError("row limit")
        result = {"columns": [c[0] for c in cur.description], "rows": rows}
        if len(json.dumps(result, default=str).encode()) > 1048576:
            raise ValueError("byte limit")
        result["rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except Exception as e:
        result = {"error": str(e)}
    result["seconds"] = time.perf_counter() - start
    pipe.send(result)


def batch(queries):
    results = {}
    for name, sql in queries.items():
        reader, writer = multiprocessing.Pipe(False)
        child = multiprocessing.Process(target=execute, args=(sql, writer))
        child.start()
        writer.close()
        try:
            results[name] = reader.recv() if reader.poll(5) else {"error": "timeout"}
        except EOFError:
            results[name] = {"error": "worker exited"}
        finally:
            child.kill()
            child.join()
            reader.close()
    return results


if __name__ == "__main__":
    print(json.dumps(batch(json.load(sys.stdin)), default=str))
