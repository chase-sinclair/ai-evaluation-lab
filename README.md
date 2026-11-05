# AI Evaluation Lab

A small Python framework for controlled, objectively graded reliability and cost studies.
The first working experiment is a **fully offline software fixture**, not research evidence.
No paid model calls or third-party dataset ingestion are needed.

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

Current research status: the substantive BFCL study is deferred and WDC
development is paused. The [Crossref feasibility audit](docs/phase3c_crossref_feasibility.md)
recommends name-to-ROR resolution for owner review. See also the
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
