"""Print the offline plan or exercise it with scripted tool calls."""

import argparse
import json
from collections import Counter
from dataclasses import asdict

from eval_lab.core.hashes import canonical

from .pilot import (
    CONDITIONS,
    MAX_CALLS,
    MAX_OUTPUT_TOKENS,
    MAX_TRANSCRIPT_BYTES,
    PROVIDERS,
    Complete,
    Episode,
    Outcome,
    identity,
    load,
    run_episode,
    schedule,
)


def scripted_fixture(episode: Episode) -> Complete:
    lookup = episode.case.id.split("-")[0]
    steps = iter(
        (
            {"action": "search", "query": lookup},
            {"action": "open", "id": episode.case.source},
            {"action": "answer", "answer": episode.case.answer, "source": episode.case.source},
        )
    )

    def next_reply(*_):
        return canonical(next(steps))

    return next_reply


def summarize(
    rows: list[tuple[Episode, Outcome]], expected: tuple[Episode, ...], source_kinds: dict[str, str]
) -> dict:
    if len(rows) != len(expected) or {episode for episode, _ in rows} != set(expected):
        raise ValueError("Expected exactly one row per scheduled episode")
    report = {}
    for provider in PROVIDERS:
        arms = {
            condition: {
                episode.case.id: outcome
                for episode, outcome in rows
                if episode.provider == provider and episode.condition == condition
            }
            for condition in CONDITIONS
        }
        baseline, mapped = (arms[condition] for condition in CONDITIONS)
        report[provider] = {
            "pairs": len(baseline),
            "gains": sum(mapped[c].correct and not baseline[c].correct for c in baseline),
            "losses": sum(baseline[c].correct and not mapped[c].correct for c in baseline),
            "arms": {},
        }
        for condition, by_case in arms.items():
            outcomes = list(by_case.values())
            correct = sum(row.correct for row in outcomes)
            calls = sum(row.calls for row in outcomes)
            report[provider]["arms"][condition] = {
                "correct": correct,
                "scheduled": len(outcomes),
                "statuses": dict(Counter(row.status for row in outcomes)),
                "model_calls": calls,
                "model_calls_per_correct": calls / correct if correct else None,
                "search_calls": sum(len(row.queries) for row in outcomes),
                "document_opens": sum(len(row.opened) for row in outcomes),
                "reached_authority": sum(row.searches_to_authority is not None for row in outcomes),
                "first_search_query": dict(
                    Counter(row.queries[0] if row.queries else "" for row in outcomes)
                ),
                "first_result": dict(Counter(row.first_returned or "" for row in outcomes)),
                "first_opened": dict(
                    Counter(row.opened[0] if row.opened else "" for row in outcomes)
                ),
                "first_opened_kind": dict(
                    Counter(source_kinds[row.opened[0]] if row.opened else "" for row in outcomes)
                ),
                "first_cited": dict(Counter(row.cited or "" for row in outcomes)),
            }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["plan", "smoke"])
    parser.add_argument("--traces", action="store_true", help="Include all scripted action traces.")
    args = parser.parse_args()
    documents, cases = load()
    episodes = schedule(cases)
    result = {
        "mode": "offline plan",
        "plan_sha256": identity(documents, episodes),
        "documents": len(documents),
        "questions": len(cases),
        "provider_families": PROVIDERS,
        "conditions": CONDITIONS,
        "episodes": len(episodes),
        "max_model_requests": len(episodes) * MAX_CALLS,
        "max_output_tokens_per_request": MAX_OUTPUT_TOKENS,
        "max_local_transcript_bytes_per_request": MAX_TRANSCRIPT_BYTES,
    }
    if args.mode == "smoke":
        rows = [
            (episode, run_episode(episode, documents, scripted_fixture(episode)))
            for episode in episodes
        ]
        result.update(
            mode="scripted software check only",
            completed=len(rows),
            scripted_model_calls=sum(row.calls for _, row in rows),
            summary=summarize(rows, episodes, {doc.id: doc.kind for doc in documents}),
        )
        if args.traces:
            result["traces"] = [
                {
                    "case": episode.case.id,
                    "provider": episode.provider,
                    "condition": episode.condition,
                    **asdict(outcome),
                }
                for episode, outcome in rows
            ]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
