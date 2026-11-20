from collections import Counter
from itertools import pairwise

import pytest

from eval_lab.core.hashes import canonical
from experiments.source_routing.__main__ import scripted_fixture, summarize
from experiments.source_routing.pilot import (
    CONDITIONS,
    MAX_CALLS,
    PROVIDERS,
    SOURCE_MAP,
    SYSTEM,
    Episode,
    identity,
    load,
    run_episode,
    schedule,
)


def test_frozen_matrix_and_counterbalance():
    documents, cases = load()
    episodes = schedule(cases)
    assert episodes == schedule(cases)
    assert len(episodes) == len(set(episodes)) == 72
    assert len(documents) == len(cases) == 12
    assert len(identity(documents, episodes)) == 64
    assert identity(documents, episodes) != identity(documents, episodes[::-1])
    kinds = {doc.id: doc.kind for doc in documents}
    assert Counter(kinds[case.source] for case in cases) == {
        "filing": 4,
        "transcript": 4,
        "commentary": 4,
    }
    first = Counter()
    for left, right in pairwise(episodes):
        if left.case == right.case and left.provider == right.provider:
            assert left.condition != right.condition
            first[left.provider, kinds[left.case.source], left.condition] += 1
    assert first == {
        (provider, kind, arm): 2
        for provider in PROVIDERS
        for kind in set(kinds.values())
        for arm in CONDITIONS
    }


def test_only_source_map_differs_and_search_does_not_leak_answer():
    documents, (case, *_) = load()
    transcripts = {}
    for arm in CONDITIONS:
        episode = Episode("gpt", arm, case)
        fixture = scripted_fixture(episode)
        transcripts[arm] = []

        def complete(provider, messages, record=transcripts[arm], reply=fixture):
            record.append(messages)
            return reply(provider, messages)

        assert run_episode(episode, documents, complete).correct
    baseline = transcripts["baseline"]
    mapped = transcripts["source_map"]
    assert baseline[0][0].content == SYSTEM
    assert mapped[0][0].content == f"{SYSTEM}\n\n{SOURCE_MAP}"
    assert [messages[1:] for messages in baseline] == [messages[1:] for messages in mapped]
    assert case.answer not in baseline[1][-1].content
    assert case.answer in baseline[2][-1].content


@pytest.mark.parametrize(
    ("actions", "status"),
    [
        (['{"action":"search","action":"search","query":"arbor"}'], "invalid_action"),
        (['{"action":"open","id":"arbor-filing"}'], "invalid_action"),
        (['{"action":"answer","answer":"184","source":"arbor-filing"}'], "unopened_citation"),
        (['{"action":"search","query":"arbor"}'] * MAX_CALLS, "call_limit"),
        (["x" * 1025], "reply_limit"),
    ],
)
def test_unsupported_action_or_exhaustion_cannot_pass(actions, status):
    documents, (case, *_) = load()
    script = iter(actions)
    outcome = run_episode(Episode("claude", "baseline", case), documents, lambda *_: next(script))
    assert outcome.status == status
    assert not outcome.correct
    assert outcome.calls == len(actions)


@pytest.mark.parametrize(
    ("source", "answer", "status"),
    [
        ("arbor-brief", "184", "wrong_source"),
        ("arbor-filing", "192", "wrong_answer"),
        ("arbor-filing", "184", "correct"),
    ],
)
def test_correctness_requires_authority_and_answer(source, answer, status):
    documents, (case, *_) = load()
    script = iter(
        (
            {"action": "search", "query": "arbor"},
            {"action": "open", "id": source},
            {"action": "answer", "answer": answer, "source": source},
        )
    )
    result = run_episode(
        Episode("gemini", "source_map", case), documents, lambda *_: canonical(next(script))
    )
    assert result.status == status
    assert result.correct == (status == "correct")
    assert result.queries == ("arbor",)
    assert result.first_returned is not None
    assert result.opened == (source,)
    assert result.cited == source
    assert result.searches_to_authority == (1 if source == case.source else None)


def test_paired_summary_includes_failures_and_rejects_missing_rows():
    documents, cases = load()
    episodes = schedule(cases)
    by_kind = {doc.id: doc.kind for doc in documents}
    rows = [(episode, run_episode(episode, documents, lambda *_: "{}")) for episode in episodes]
    episode = next(e for e in episodes if e.provider == "gpt" and e.condition == "source_map")
    rows[episodes.index(episode)] = (
        episode,
        run_episode(episode, documents, scripted_fixture(episode)),
    )
    summary = summarize(rows, episodes, by_kind)
    row = summary["gpt"]
    assert row["pairs"] == 12
    assert row["gains"] == 1
    assert row["losses"] == 0
    assert row["arms"]["source_map"]["scheduled"] == 12
    assert row["arms"]["source_map"]["correct"] == 1
    assert row["arms"]["baseline"]["model_calls_per_correct"] is None
    with pytest.raises(ValueError, match="one row per scheduled episode"):
        summarize(rows[:-1], episodes, by_kind)
