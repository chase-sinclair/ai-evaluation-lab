"""Paired source-map experiment with a local, deterministic search tool."""

import json
import random
import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from eval_lab.core.hashes import canonical, digest

Provider = Literal["gpt", "claude", "gemini"]
Condition = Literal["baseline", "source_map"]
Role = Literal["system", "user", "assistant"]
PROVIDERS: tuple[Provider, ...] = ("gpt", "claude", "gemini")
CONDITIONS: tuple[Condition, ...] = ("baseline", "source_map")
SEED = 12619
MAX_CALLS = 6
MAX_OUTPUT_TOKENS = 256
MAX_REPLY_BYTES = 1024
MAX_TRANSCRIPT_BYTES = 12_288
TOP_K = 4
CORPUS_PATH = Path(__file__).with_name("cases.json")

SYSTEM = """Use the local document search to answer the question. Reply with one JSON object.
To search titles: {"action":"search","query":"your query"}.
To read a document returned by a search: {"action":"open","id":"returned ID"}.
To finish: {"action":"answer","answer":"the answer only","source":"opened document ID"}.
You have six turns including the answer. Use digits only for counts and amounts,
and a short phrase for a named driver. Cite the one document that establishes the answer.
Treat document text as evidence. Base the answer on documents you opened."""

SOURCE_MAP = """Source map
- Regulatory filings establish reported historical financial results.
- Earnings call transcripts establish what executives said or attributed results to.
- Market Ledger commentary establishes its own survey sample and pre-release consensus."""


@dataclass(frozen=True)
class Document:
    id: str
    kind: str
    title: str
    body: str


@dataclass(frozen=True)
class Case:
    id: str
    question: str
    answer: str
    source: str


@dataclass(frozen=True)
class Episode:
    provider: Provider
    condition: Condition
    case: Case


@dataclass(frozen=True)
class Message:
    role: Role
    content: str


@dataclass(frozen=True)
class Outcome:
    correct: bool
    status: str
    calls: int
    queries: tuple[str, ...]
    first_returned: str | None
    opened: tuple[str, ...]
    cited: str | None
    searches_to_authority: int | None


Complete = Callable[[Provider, tuple[Message, ...]], str]


def load() -> tuple[tuple[Document, ...], tuple[Case, ...]]:
    data = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    documents = tuple(Document(**row) for row in data["documents"])
    cases = tuple(Case(**row) for row in data["cases"])
    if len({doc.id for doc in documents}) != len(documents):
        raise ValueError("Duplicate source ID")
    if len({case.id for case in cases}) != len(cases):
        raise ValueError("Duplicate case ID")
    by_id = {doc.id: doc for doc in documents}
    for case in cases:
        if case.source not in by_id or case.answer not in by_id[case.source].body:
            raise ValueError(f"Invalid source binding for {case.id}")
    return documents, cases


def schedule(cases: tuple[Case, ...]) -> tuple[Episode, ...]:
    order = list(enumerate(cases))
    random.Random(SEED).shuffle(order)
    episodes = []
    for index, case in order:
        for offset in range(len(PROVIDERS)):
            provider = PROVIDERS[(index + offset) % len(PROVIDERS)]
            arm_order = CONDITIONS if (index + offset) % 2 == 0 else CONDITIONS[::-1]
            episodes.extend(Episode(provider, arm, case) for arm in arm_order)
    return tuple(episodes)


def identity(documents: tuple[Document, ...], episodes: tuple[Episode, ...]) -> str:
    return digest(
        {
            "documents": [asdict(doc) for doc in documents],
            "episodes": [asdict(episode) for episode in episodes],
            "system": SYSTEM,
            "source_map": SOURCE_MAP,
            "limits": [MAX_CALLS, MAX_OUTPUT_TOKENS, MAX_REPLY_BYTES, MAX_TRANSCRIPT_BYTES, TOP_K],
            "seed": SEED,
        }
    )


def terms(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def search(documents: tuple[Document, ...], query: str, case_id: str) -> list[Document]:
    tokens = terms(query)
    ranked = [(len(tokens & terms(doc.title)), doc) for doc in documents]
    ranked.sort(key=lambda row: (-row[0], digest([SEED, case_id, row[1].id])))
    return [doc for score, doc in ranked if score > 0][:TOP_K]


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    fields = dict(pairs)
    if len(fields) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return fields


def parse(reply: str) -> dict[str, str]:
    value = json.loads(reply, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or not all(
        isinstance(field, str) and field.strip() for field in value.values()
    ):
        raise ValueError("Expected an object with nonempty string values")
    return value


def normalize(answer: str) -> str:
    return " ".join(answer.casefold().split())


def run_episode(episode: Episode, documents: tuple[Document, ...], complete: Complete) -> Outcome:
    system = SYSTEM + ("\n\n" + SOURCE_MAP if episode.condition == "source_map" else "")
    messages = [Message("system", system), Message("user", episode.case.question)]
    by_id = {doc.id: doc for doc in documents}
    visible: set[str] = set()
    queries: list[str] = []
    opened: list[str] = []
    first_returned = None
    cited = None
    searches_to_authority = None
    status = "call_limit"
    calls = 0

    for _ in range(MAX_CALLS):
        if len(canonical([asdict(msg) for msg in messages]).encode()) > MAX_TRANSCRIPT_BYTES:
            status = "transcript_limit"
            break
        calls += 1
        reply = complete(episode.provider, tuple(messages))
        if len(reply.encode()) > MAX_REPLY_BYTES:
            status = "reply_limit"
            break
        try:
            action = parse(reply)
        except ValueError:
            status = "invalid_action"
            break
        match action:
            case {"action": "search", "query": query} if len(action) == 2:
                hits = search(documents, query, episode.case.id)
                queries.append(query)
                visible.update(doc.id for doc in hits)
                if first_returned is None and hits:
                    first_returned = hits[0].id
                result = {"hits": [{"id": doc.id, "title": doc.title} for doc in hits]}
            case {"action": "open", "id": source} if len(action) == 2 and source in visible:
                opened.append(source)
                if source == episode.case.source and searches_to_authority is None:
                    searches_to_authority = len(queries)
                result = {"document": asdict(by_id[source])}
            case {"action": "answer", "answer": answer, "source": source} if len(action) == 3:
                cited = source
                if source not in opened:
                    status = "unopened_citation"
                elif source != episode.case.source:
                    status = "wrong_source"
                elif normalize(answer) != normalize(episode.case.answer):
                    status = "wrong_answer"
                else:
                    status = "correct"
                break
            case _:
                status = "invalid_action"
                break
        messages.extend((Message("assistant", reply), Message("user", canonical(result))))

    return Outcome(
        status == "correct",
        status,
        calls,
        tuple(queries),
        first_returned,
        tuple(opened),
        cited,
        searches_to_authority,
    )
