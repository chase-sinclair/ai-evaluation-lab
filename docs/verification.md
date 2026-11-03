# Phase 0 / Phase 1 verification

Date: November 3, 2026. Host: Windows, CPython 3.13.0, uv 0.13.7.

## Completed implementation

Installable Python package and lockfile; typed contracts; trusted local discovery;
YAML/case/schema/control validation; sequential deterministic runner; mock provider;
optional Responses adapter; structured-call grader; budgets; durable exclusive result
storage; summaries; CLI; extension/protocol documentation; root working agreements.

Only one experiment is implemented: five authored development fixtures under three
tool-count conditions. The secondary dataset work is documentation-only.

## Acceptance evidence

| Requirement | Verification |
|---|---|
| Installation and CLI help | `uv sync --locked` and `uv run eval-lab --help` succeeded. |
| Discovery | `uv run eval-lab list` prints `tool_selection`. |
| Validation | `uv run eval-lab validate tool_selection` reports 5 cases / 15 trials. |
| Offline run | `uv run eval-lab run tool_selection --mode mock` writes 15 records. |
| Record content | Tests validate unique IDs, prediction/grade, ground-truth reference, matching request hash, schema order and nonnegative measured latency. |
| Deliberate errors / no-call | 10 pass, 3 wrong-argument task failures, 2 invalid wrong-name calls; all 3 no-call trials pass. Software checks only. |
| Summary | `summarize` recomputes the same counts from stored JSONL. Primary denominator is 15. |
| Dry run | Reports 15 planned trials and zero provider calls; test forbids provider construction and checks no artifacts created. |
| Tests / lint | 48 tests pass; Ruff check and format check pass. Network socket connections are blocked and API credentials removed in tests. |
| Partial results | Injected interruption preserves completed records plus interrupted trial, finalizes failure, and rejects reuse of run ID. Startup/provider/grader failures and torn final lines are tested. |
| Reusability | A second text-output experiment with a different deterministic grader runs through the unchanged runner. |
| Live adapter | Actual installed SDK tested using local HTTP fake transport; no real requests. Opt-in, budget, usage uncertainty, malformed JSON, secret redaction, and no retries covered. |

Final-source acceptance run: **`20261103T210917-113f1fe09b93`**, generated from clean engine
commit `6dab98ed578e8960c248c71f3c6bb89888aa6007`. Manifest, plan, 15 JSONL records, and summary
are in `results/20261103T210917-113f1fe09b93/`. `summarize` and an independent artifact check
confirmed the counts and clean revision. The earlier run `20261103T210204-aea8946b1eb5`
is also preserved. Raw artifacts are local and gitignored; no paid cost or token usage
was invented. Measured latency is machine-specific.

A fresh local clone of that commit at `.verification/fresh-checkout` successfully ran
`uv sync --locked --offline` into a new virtual environment using the populated uv cache,
then CLI help/list/validate, all **48 tests**, and Ruff. This verifies fresh-checkout
installation on Windows; an empty dependency cache still needs a first online installation.
The original checkout also ran the exact `uv run pytest` and `uv run ruff check .` commands
with `UV_OFFLINE=1`: **48 passed**, no skips, all lint checks passed.

## Limits and decisions

- Python 3.12+ declared; tested on this host's 3.13. No claim of a multi-OS CI matrix.
- Only single-turn calls; no tool execution, automatic retries, parallelism, or resume.
- `plan.json` freezes inputs before calls; final `manifest.json` is a separate write-once
  completion snapshot. Files resist application overwrites, not external tampering.
- A hard kill can leave a torn final record or no final manifest. Summarization reports
  that condition and keeps all planned trials in the denominator. The unattempted field
  is planned minus durable records; following a hard kill it can include an in-flight call.
- Input tokens are a conservative byte-based heuristic. Live costs remain estimates and
  the spending guard is best-effort. Missing live usage stops new requests.
- Optional inference settings are rejected; default server settings are recorded when
  reported. Live model/account compatibility has not been exercised.
- No findings about real models, no external benchmark import, no public report/charts.
- Git history records the verified source revisions; raw run artifacts remain local and gitignored.

## Research and approval boundary

All five requested sources are covered in `datasets/catalog.yaml` and
`docs/data_source_research.md`. Inspected official documentation/metadata only. WDC data
rights, BIRD HF revision/database digests/sizes, and some external artifact terms remain
explicitly unresolved. No heavy benchmark stacks or data archives were installed.

Before the first real experiment, `CODEX_HANDOFF.md` Phase 3 requires owner approval of
the dataset/subset and permitted use, exact model/provider/settings, dated price assumptions,
finite spending/request ceilings, and protocol. The proposed BFCL pilot is 20 cases × 3
conditions = 60 calls; illustrative cost arithmetic is not a current quote or authorization.
