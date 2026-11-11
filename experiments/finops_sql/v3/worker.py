"""Prospective grammar. The original process worker is reused only inside the v3 image."""

import json
import sys

import sqlglot
from sqlglot import exp
from sqlglot.optimizer.normalize_identifiers import normalize_identifiers
from sqlglot.optimizer.scope import traverse_scope

from experiments.finops_sql import worker

NODES = worker.NODES | {"Exists", "Filter", "Qualify", "NullSafeEQ", "NullSafeNEQ"}
FUNCTIONS = worker.FUNCTIONS | {
    "AVG",
    "COUNT_IF",
    "DENSE_RANK",
    "RANK",
    "LAG",
    "LEAD",
    "TIMESTAMP_TRUNC",
    "DATE_TRUNC",
    "DATEDIFF",
    "GREATEST",
    "LEAST",
    "UPPER",
    "FLOOR",
    "CEIL",
}


def validate(sql: str) -> str:
    if len(sql.encode()) > 65536:
        raise ValueError("query size")
    trees = sqlglot.parse(sql, read="duckdb")
    if len(trees) != 1 or not isinstance(trees[0], (exp.Select, exp.Union)):
        raise ValueError("one query required")
    tree = trees[0]
    for node in tree.walk():
        if isinstance(node, exp.Column) and node.name.lower() == "rowid":
            raise ValueError("internal row identifier")
        if isinstance(node, exp.Table) and (
            not isinstance(node.this, exp.Identifier) or node.db or node.catalog
        ):
            raise ValueError("relation")
        if isinstance(node, exp.With) and node.args.get("recursive"):
            raise ValueError("recursive query")
        if type(node).__name__ in NODES or (
            isinstance(node, exp.Func) and node.sql_name() in FUNCTIONS
        ):
            continue
        raise ValueError(f"unapproved node {type(node).__name__}")
    # A CTE name is a permitted relation only where it resolves in SQL scope.
    for scope in traverse_scope(normalize_identifiers(tree.copy(), dialect="duckdb")):
        for table in scope.tables:
            if table.name not in worker.TABLES and table.name not in scope.cte_sources:
                raise ValueError("relation")
    return tree.sql(dialect="duckdb", unsupported_level=sqlglot.ErrorLevel.RAISE)


if __name__ == "__main__":
    worker.validate = validate
    print(json.dumps(worker.batch(json.load(sys.stdin)), default=str))
