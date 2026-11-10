"""Checkpoint-one contracts, independent of local snapshots and Docker availability."""

import pytest

from experiments.finops_sql.compare import normalize
from experiments.finops_sql.controls import (
    CLARIFICATIONS,
    DENIED,
    DEVELOPMENT,
    INTEGRITY,
    MUTATIONS,
)
from experiments.finops_sql.discovery import catalog, describe, entries, paths
from experiments.finops_sql.references import QUERIES
from experiments.finops_sql.worker import TABLES, validate


def test_reference_and_control_contracts():
    assert set(QUERIES) == set(range(1, 33))
    assert set(CLARIFICATIONS) == set(range(33, 37))
    assert len(DEVELOPMENT) == 8
    queries = [*QUERIES.values(), *INTEGRITY.values(), *(q for _, q in MUTATIONS.values())]
    queries.extend(q for _, q in DEVELOPMENT.values() if q)
    for _, left, right in CLARIFICATIONS.values():
        queries.extend((left, right))
    for query in queries:
        assert validate(query)


@pytest.mark.parametrize("name", sorted(set(DENIED) - {"rows"}))
def test_static_boundary(name):
    with pytest.raises(ValueError):
        validate(DENIED[name])


def test_accounting_precision_order_and_multiplicity():
    assert normalize(7, [[-1e-14]]) == normalize(7, [[0]])
    assert normalize(9, [[0.1234567]]) != normalize(9, [[0.1234557]])
    assert normalize(2, [(1, 2), (2, 3)]) != normalize(2, [(2, 3), (1, 2)])
    assert normalize(5, [(1, 2)] * 2) != normalize(5, [(1, 2)])
    with pytest.raises(ValueError):
        normalize(3, [[0.3]])


def test_discovery_paths_replay_from_public_responses():
    objects = entries()
    assert set(catalog("", objects)) == TABLES
    for trace in paths().values():
        _, query = trace[0]
        known = set(catalog(query, objects))
        for op, batch in trace[1:]:
            assert op == "describe" and set(batch) <= known
            for entry in describe(batch, objects).values():
                known.update(entry.get("glossary", ()))
    assert len(paths()) == 32 and max(map(len, paths().values())) == 5
