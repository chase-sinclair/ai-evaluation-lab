# AI Evaluation Lab

AI Evaluation Lab documents applied AI implementation decisions. Each case study compares a baseline with an AI alternative and explains what the observed quality, cost and operational risks justify.

**[When Should Entity Matching Escalate to an LLM?](docs/portfolio/entity-matching.md)** follows a funder name from a missed deterministic match to a successful model correction, then asks whether the system could recognize when to pay for that second look. The evidence covers 38 development queries and four live responses.

The Phase 3G independent holdout and its first review wave are retired. The feasibility findings and technical record remain available. [Project status](docs/PROGRESS.md) · [Format for future studies](docs/portfolio/study-format.md)

**[Does Giving an AI Agent More Tools Make It Less Reliable?](docs/portfolio/tool-catalog.md)**
The freight-desk pilot scored 12/12 at each of 5, 10 and 20 functions.
The 20-tool catalog used 2.25× as many input tokens as the 5-tool catalog
on the same tasks. [Live findings and per-scenario results](docs/experiment02_live_findings.md) ·
[Frozen study and budget](experiments/catalog_scope/README.md)

V2 tested 18 harder shared scenarios in two mirrored orders. All passed at each catalog size. A separate capability test exposed an opposite-direction payout write proposal when the release function was missing. [V2 results, costs and reply audit](docs/experiment02_v2_live_findings.md)

**[Which RAG Reliability Safeguards Are Worth Deploying?](docs/portfolio/rag-safeguards.md)** compares three workflows on the same 36 synthetic enterprise questions and traces why a verifier withheld a correct facilities answer.

**[When Should an Enterprise AI Agent Recover Automatically—and When Should It Stop?](docs/portfolio/recovery.md)** compares three responses to 24 simulated failures. Stop-and-report scored 9/24. Deterministic rules and the AI agent each scored 24/24. Model inference cost an estimated $0.0029715 across the follow-up, with a median API latency of 1.980 seconds per request.

**[How Much Business Context Does an AI SQL Assistant Need?](docs/portfolio/finops-sql.md)** follows a March invoice question through four context designs. Curated and expanded context each scored 18/36, with four questions passing only under each design. Bounded discovery scored 5/36. [Five Lab deployment decisions](docs/portfolio/lab-summary.md)

## Quick start

Install Python 3.12+ and [uv](https://docs.astral.sh/uv/), then run from this checkout:

```sh
uv sync --locked
uv run eval-lab --help
uv run eval-lab list
uv run eval-lab validate tool_selection
uv run eval-lab run tool_selection --dry-run
uv run eval-lab run tool_selection --mode mock
uv run eval-lab summarize <run_id>
uv run pytest
uv run ruff check .
```

Dependency installation requires network on an empty cache. After installation,
`uv run --offline pytest` and all mock commands work without network or credentials.
The development group includes the optional OpenAI SDK for local mocked transport
tests. Production installs can omit it using `uv sync --no-dev`. There are no real API calls in tests.
On Windows, `py -3.13 -m uv` is an equivalent launcher when uv is not on PATH.

## What works

The [Phase 3E live findings](docs/phase3e_live_findings.md) document the completed
four-query pilot. The [readiness report](docs/phase3e_readiness.md) records its controls.

Current research status: the substantive BFCL study is deferred and WDC
development is paused. The [offline Crossref resolution experiment](docs/phase3d_crossref_resolution.md)
supports baseline evaluation and paired escalation replay. Run
`uv run --offline python -m experiments.entity_matching.ror demo` from this checkout.
The eight no-match decisions passed the human-review gate. See also the
[dataset decision](docs/entity_matching_dataset_decision.md) and [offline checkpoint](docs/entity_matching_checkpoint.md).

- Typed contracts and YAML validation; automatic trusted local experiment discovery.
- Five synthetic cases × three tool counts = 15 deterministic trials, including no-call.
- Structured tool-call grading with typed arguments and distinct error categories.
- Seeded trial/tool ordering; frozen requests, answer keys, hashes, schemas, and provenance.
- Sequential execution, request/spend guards, durable records, partial-run reporting.
- Optional single-call OpenAI Responses adapter behind explicit live opt-in and budgets.

The fixture deliberately yields 10 passing and 5 failing trials to exercise the software.
It does not measure any AI model's reliability. Usage is unknown (`null`), and offline cost
is explicitly zero. Real estimated costs would use reported usage and an approved snapshot.

## Files and results

```text
src/eval_lab/              contracts, CLI, runner, providers, summary
experiments/tool_selection/ config, fixture, experiment, grader
experiments/_template/     extension checklist
tests/                    offline unit, failure, adapter, and CLI tests
docs/                     architecture, protocols, research, verification
datasets/catalog.yaml     documentation-only dataset feasibility catalog
results/<run_id>/          ignored local run artifacts
```

Each run writes `plan.json` before provider construction, `records.jsonl` after every
attempt, and final `manifest.json`/`summary.json`. Run IDs are never reused. Plan and
final manifest are separate immutable snapshots. A caught interrupt finalizes status
and preserves records; a hard kill leaves a readable plan and partial JSONL. `summarize`
recomputes without modifying files and flags an absent final manifest or torn final line.
Primary success divides correct trials by **all planned trials**. Interrupted/unattempted
trials never disappear. Timing varies; seeded requests, predictions, and grades reproduce.

Read [architecture](docs/architecture.md), [adding an experiment](docs/adding_an_experiment.md),
[fixture rules](experiments/tool_selection/README.md), and
[real pilot approval protocol](docs/experiment_protocol.md).
The approved six-request BFCL smoke completed; see its preserved
[findings and limitations](docs/bfcl_smoke_findings.md).

Phase 1.5 adds [comparative reporting](docs/comparative_reporting.md), offline CI, and
a [specific BFCL pilot protocol for review](docs/bfcl_pilot_protocol.md).

Phase 2.6 adds [cache accounting and prospective grading diagnostics](docs/phase2_6_hardening.md).
The [Phase 3 research design](docs/phase3_research_design.md) proposes a business-tool
study for owner review; no further live execution is authorized.
The [Phase 3A feasibility audit](docs/phase3a_feasibility.md) reviewed 40 new records:
the original catalog/sample targets are unsupported by that pool. A smaller
development probe and [explicit-30m accounting policy](docs/phase3a_cache_policy.md)
are proposed for review; neither is connected to live execution.

## Research boundary

New dataset research is documentation-only. See [the feasibility review](docs/data_source_research.md)
and [catalog](datasets/catalog.yaml). The approved bounded BFCL development subset is
vendored with attribution; raw caches and results are ignored. A new live pilot needs owner
approval of the subset/license, exact model, pricing assumptions, protocol, and spending cap.
See [verification](docs/verification.md) for completed acceptance checks and remaining limits.
