"""Offline SDK and bounded DuckDB rehearsal on the eight existing development tasks."""

import argparse
import json
from pathlib import Path

import httpx
from openai import OpenAI

from eval_lab.core.hashes import canonical, digest

from ..checkpoint import verify_sources
from ..episode import Discovery, final
from .accounting import charge, timeout
from .grading import sandbox
from .proposal import DEV_QUESTIONS, OUTPUT, body, turn_bounds

# Private scripted candidates. Only public questions, fields and discovery records go on wire.
LATEST = """WITH latest AS (
 SELECT * FROM charge_revision QUALIFY row_number() OVER (
 PARTITION BY charge_id ORDER BY revision DESC, arrived DESC, export_id DESC)=1) """
SQL = {
    "D01": LATEST
    + """SELECT sum(billed) FILTER (WHERE i.posting_month=1) AS cost
        FROM latest l JOIN invoice i ON l.invoice_id=i.id""",
    "D02": """SELECT count(*) AS repeats FROM (SELECT row_number() OVER (
        PARTITION BY charge_id ORDER BY revision DESC, arrived DESC, export_id DESC) AS n,
        invoice_id FROM charge_revision) r JOIN invoice i ON i.id=r.invoice_id
        WHERE i.posting_month=2 AND n>1""",
    "D03": LATEST
    + """SELECT sum(billed) AS cost FROM latest l WHERE
        day >= DATE '2025-01-01' AND day < DATE '2026-01-01' AND EXISTS
        (SELECT 1 FROM invoice i WHERE i.id=l.invoice_id AND i.posting_month=13)""",
    "D04": LATEST
    + """SELECT center_id, sum(l.effective*s.weight) AS allocated,
        sum(sum(l.effective*s.weight)) OVER () AS total FROM latest l JOIN shared_split s
        ON l.pool=s.pool AND extract(month FROM l.day)=s.month_id
        WHERE l.day>=DATE '2025-02-01' AND l.day<DATE '2025-03-01' AND s.pool='network'
        GROUP BY center_id""",
    "D05": """SELECT team_id, share FROM resource_owner WHERE resource_id=17
        AND first_day<=DATE '2025-01-01' AND DATE '2025-01-01'<end_day""",
    "D06": LATEST
    + """, rates AS (
        SELECT extract(month FROM l.day) AS m, sum(l.contracted)/nullif(sum(u.units),0) AS rate
        FROM latest l JOIN usage_day u ON u.id=l.meter_id JOIN resource r ON r.id=l.resource_id
        JOIN region g ON g.id=r.region_id WHERE g.name='West' AND l.sku_id=0
        AND l.category='usage' AND l.day>=DATE '2025-06-01' AND l.day<DATE '2025-08-01'
        GROUP BY 1)
        SELECT max(rate) FILTER (WHERE m=7) - max(rate) FILTER (WHERE m=6) AS change FROM rates""",
    "D07": """SELECT resource_id FROM resource_tag WHERE lower(trim(tag_key))='environment'
        AND first_day<=DATE '2025-01-31' AND DATE '2025-01-31'<end_day AND trim(tag_value)<>''
        GROUP BY resource_id HAVING count(DISTINCT lower(trim(tag_value)))>1""",
}
CLARIFY = {
    "kind": "clarify",
    "dimensions": ["scope", "cost_basis"],
    "question": "Which reporting entity does Finance refer to, and which cost basis should I use?",
}
# Describe batches follow a neutral catalog list, then any disclosed glossary links.
BATCHES = {
    "D01": ["invoice charge_revision", "@closing @costs"],
    "D02": ["charge_revision invoice", "@closing"],
    "D03": ["invoice charge_revision", "@closing"],
    "D04": ["shared_split charge_revision", "@closing @allocation"],
    "D05": ["resource_owner resource", "@codes @allocation"],
    "D06": ["charge_revision usage_day sku", "resource region", "@closing @variance @codes"],
    "D07": ["resource_tag", "@labels"],
    "D08": ["cost_center team charge_revision", "resource_owner", "@costs @allocation"],
}
DEV_KEY_HASH = "dd27912769d7c62c17a581328cbd618397471d8c5b2b980442a3a21f662be9c5"


def rehearse(key: str, arm: str) -> tuple[dict, int]:
    question = DEV_QUESTIONS[key]
    state = Discovery()
    steps = (
        [("catalog", {"query": ""})]
        + [("describe", {"ids": batch.split()}) for batch in BATCHES[key]]
        if arm == "D"
        else []
    )
    scripted = CLARIFY if key == "D08" else {"kind": "sql", "query": SQL[key]}
    bounds = turn_bounds(arm, question, body(arm, question))

    def mock(request: httpx.Request) -> httpx.Response:
        turn = len(state.history)
        payload = json.loads(request.content)
        if (
            request.url.host != "offline.invalid"
            or payload != body(arm, question, state.history)
            or len(canonical(payload).encode()) + 256 > bounds[turn]
        ):
            raise ValueError("wire body or bound")
        if turn < len(steps):
            name, args = steps[turn]
            item = {
                "type": "function_call",
                "call_id": f"mock-{turn}",
                "name": name,
                "arguments": canonical(args),
            }
        else:
            item = {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": canonical(scripted)}],
            }
        # Synthetic telemetry deliberately exceeds the historical 2,048-token guard.
        return httpx.Response(
            200,
            json={
                "id": f"mock-{turn}",
                "status": "completed",
                "output": [item],
                "model": payload["model"],
                "service_tier": payload["service_tier"],
                "prompt_cache_options": payload["prompt_cache_options"],
                "reasoning": payload["reasoning"],
                "max_output_tokens": OUTPUT,
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 3000,
                    "total_tokens": 3100,
                    "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                    "output_tokens_details": {"reasoning_tokens": 2500},
                },
            },
        )

    with OpenAI(
        api_key="offline",
        base_url="https://offline.invalid/v1",
        max_retries=0,
        timeout=timeout(),
        http_client=httpx.Client(transport=httpx.MockTransport(mock)),
    ) as client:
        for turn, bound in enumerate(bounds):
            response = client.responses.with_raw_response.create(
                **body(arm, question, state.history)
            )
            raw = response.http_response.json()
            charge(raw, bound)
            if raw["status"] != "completed" or raw.get("incomplete_details") or raw.get("error"):
                raise ValueError("incomplete rehearsal")
            if response.parse().output_text:
                return final(response.parse().output_text), turn
            call = raw["output"][0]
            if "error" in state.select(call["name"], call["arguments"]):
                raise ValueError("discovery did not resolve a public object")
    raise ValueError("missing terminal reply")


def run(folder: Path) -> dict:
    if folder.name != "development":
        raise ValueError("development snapshot required")
    before = verify_sources(folder)
    records = json.loads((folder / "checkpoint-v2.json").read_bytes())
    keys = {key: {f: records[key][f] for f in ("columns", "types", "rows")} for key in SQL}
    if digest(keys) != DEV_KEY_HASH:
        raise ValueError("development key drift")
    queries, depths = {}, {}
    for key in DEV_QUESTIONS:
        for arm in "ABCD":
            reply, depth = rehearse(key, arm)
            if arm == "D":
                depths[key] = depth
            if key == "D08":
                if reply != CLARIFY:
                    raise ValueError("development clarification")
            elif reply != {"kind": "sql", "query": SQL[key]}:
                raise ValueError("scripted SQL did not round trip")
            else:
                queries[key] = reply["query"]
    results = sandbox(folder, queries)
    for key, expected in keys.items():
        actual = results[key]
        if (
            actual.get("columns") != expected["columns"]
            or actual.get("types") != expected["types"]
            or sorted(actual["rows"]) != sorted(expected["rows"])
        ):
            raise ValueError(
                f"{key} development mismatch: {actual.get('error', 'result contract')}"
            )
    if verify_sources(folder) != before:
        raise ValueError("snapshot changed")
    return {
        "scripted_episodes": 32,
        "distinct_sql_results_checked": len(keys),
        "clarification_fixture": "D08",
        "discovery_depths": depths,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("development_snapshot", type=Path)
    print(json.dumps(run(parser.parse_args().development_snapshot), indent=2))
