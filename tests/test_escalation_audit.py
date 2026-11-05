import importlib
from pathlib import Path

import pytest


@pytest.fixture
def analysis(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    return importlib.import_module("scripts.analyze_crossref_escalation")


def test_acquisition_opportunities_and_retrieval_ceiling(analysis):
    rows, labels, pilot = analysis.read_inputs()
    order = analysis.orders(rows)["Frozen distance"]
    assert len(set(order)) == 38
    assert analysis.counts(order, labels) == (6, 5)
    assert analysis.counts(order[:9], labels) == analysis.counts(order[:19], labels) == (4, 4)
    assert order[29] == "cr-2775"
    assert [i for i in order if i in pilot] == ["cr-2819", "cr-830", "cr-744", "cr-2775"]
    assert labels["cr-2775"]["rank"] == 2
    assert labels["cr-970"]["rank"] == 8
    assert not labels["cr-970"]["correctable"]


def test_allocation_appendix_reproduces(analysis):
    path = analysis.ROOT / "docs/phase3f_allocation_audit.md"
    assert path.read_text(encoding="utf8") == analysis.appendix()
