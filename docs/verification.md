# Phase 0 / Phase 1 verification

Date: November 3, 2026. Host: Windows, CPython 3.13.0, uv 0.13.7.

## Phase 2.5 — live integration preparation (November 4, 2026)

Implemented keyword-only request context in the generic grading boundary; BFCL grader
0.2.1 now validates against the actual request's offered tools and refuses missing
context. Added an exact-permutation trial-order option to retain the frozen smoke
sequence; default runner ordering is unchanged. A six-request view/configuration
uses the existing runner, provider, immutable store and spending guards. Explicit
standard service tier, fixed endpoint, six-call/$0.05 limits, 4096 output tokens,
zero retries, sequential execution and fixed run ID are preserved/enforced.

Independently re-inspected all six frozen request objects against original pinned
source questions and keys, plus every rendered distractor schema/template. Documented
optional fields, unique outcomes, no-call behavior, lack of label leakage and exact
canonical request hashes in [the audit](bfcl_smoke_audit.md). This was a fresh assistant
review, not an external human review. The dataset and historical request manifest are
unchanged; original source/grader metadata is retained while new runs identify 0.2.1.

Initial local suite: **85 passed**, including all previous 74 tests (updated to pass
actual grading context), all 388 official-checker vectors, and 11 new parameterized
smoke/context tests. Real SDK tests use local HTTP mock transport with sockets blocked;
no credentials or paid calls. Valid offered targets, unoffered tools, malformed
arguments and no-call responses are covered. End-to-end tests prove an unoffered
warehouse call is invalid at 5 tools but a task failure at 30 tools; captured six-call
SDK bodies/order match the audit hashes and repeated run IDs cannot call a provider.

Offline spending preflight: **6 planned requests; 43,740 conservative input tokens;
24,576 output-token ceiling; $0.016662 projected standard cost; zero provider calls**.
The all-input 30-minute cache-write estimate is $0.0177555, below the $0.05 guard.
Published Luna availability and prices rechecked November 4; account-specific access,
actual usage and server acceptance were not probed. Only the alias is published.
Grading still has the documented BFCL float-list/string-normalization limitations.

Final local checks: `uv sync --locked --offline` succeeded (36 packages);
`uv run --offline pytest -q` **85 passed**; Ruff lint and format checks passed
(47 files); the 54-request frozen-manifest check and six-request offline preflight
passed; `git diff --check` passed. Commands used `py -3.13 -m uv` on Windows.
Git diff confirms no changes to the frozen cases/requests/source locks or full-development
configuration. GitHub Actions verification is pending commit/push.

No paid execution authorization is
inferred from preparation acceptance. Explicit owner approval is the remaining gate;
see the audit for the exact command and risks. No new experiment or held-out design change.

## Phase 2 — BFCL integration and experimental preparation

Implemented the audited BFCL development subset inside the existing tool-selection
module. No shared runner/provider/contracts were changed. The default five authored
fixtures remain unchanged. Added bounded offline importer, raw-source/selected-row
hash locks, provenance and original schemas/answers, Apache-2.0 attribution, narrow
Python AST-compatible grading, and a complete frozen 54-request manifest. Excluded
ambiguous simple_python_5 and simple_python_14 before model execution; retained 18
development IDs, including four no-call cases. Added a source-supported validity
assessment and a six-request/$0.05 API smoke proposal; no live invocation activated.

Final local checks (November 3, 2026):

| Check | Observed result |
|---|---|
| `uv sync --locked --offline` | Resolved/checked 36 locked packages; no dependency additions. |
| `uv run --offline pytest -q` | **74 passed**, including all 54 existing tests; no skips. |
| `uv run --offline ruff check .` | All checks passed. |
| `uv run --offline ruff format --check .` | 44 files already formatted. |
| `uv run --offline python -m experiments.tool_selection.prepare_bfcl --check` | Exactly reproduces 54 frozen requests; zero provider calls. |
| Bounded raw-source reimport | Three exact pinned raw files reproduce all 18 committed cases byte-for-byte. |
| Official checker regeneration | 388 decisions reproduced from the pinned, hash-verified checker; local grader agrees with all frozen vectors. |
| `git diff --check` | Passed. |

Commands on this Windows host used `py -3.13 -m uv` for the uv executable. Test socket
connections are blocked and API credentials removed by the existing autouse fixture.
Actual OpenAI SDK calls use `httpx.MockTransport`, never a remote model. Tests cover
correct/incorrect calls, alternative strings, optional omissions, typed arguments,
extra/malformed calls, no-call/refusal/incomplete handling, label-leak resistance,
source tampering/size limits, target/schema/order invariants and frozen smoke budgets.
An injected scripted provider also drives all 54 BFCL trials through the unchanged
runner/store/summary path; these authored outcomes are software checks only.

Source verification corrected a connector-added EOF newline before freezing exact
raw source hashes. No question, schema, or key content changed. Reproduction tools
write exclusively to new files; committed artifacts are the frozen Phase 2 release.

GitHub Actions [run 41765877967](https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41765877967)
passed for implementation commit `b4fbecd199426ca7c4fae374d58ca474236edab1`.
Both Python 3.12 and 3.13 jobs passed locked installation, offline pytest, Ruff lint
and formatting. Phase 2 preparation acceptance is complete. A following documentation
checkpoint records this observed CI result without changing implementation or inputs.

Remaining limits/gates: this easy mathematical set risks ceiling effects and has
correlated families; BFCL string normalization is not symbolic equivalence. No held-out
dataset or new experiment was implemented. No benchmark-wide or real-model performance
claims. No paid calls, large archives, credentials, caches or raw results committed.
Owner approval is required for the six frozen smoke requests, GPT-6 Luna alias/default
settings, dated prices and five-cent cap. The full development config retains a zero
live budget. Account acceptance/actual usage and independent rendered-request review
can only be resolved at the approved smoke stage. See
[research design](bfcl_phase2_design.md) and [smoke protocol](bfcl_smoke_test.md).

## Phase 1.5 — Research engine hardening

Implemented additive condition summaries and case-paired comparisons with explicit
repetition/partial-pair denominators; fixed text versus tool-call normalization without
changing the shared-engine/module design. Added SDK fake-transport text-grading tests,
comparison tests, and a Python 3.12/3.13 GitHub Actions matrix with locked installation,
offline pytest, lint and format checks. No secrets are supplied to CI; socket connections
are blocked by the test fixture. Installation itself requires network access.

Local validation: **54 tests passed**, Ruff lint and format checks passed, diff whitespace
check passed. Run `20261103T221524-68ef3167b8f6` contains 15 trials, with 4/5 passes under
tools_5 and 3/5 under each larger condition. These are software fixture outcomes only.
Paired differences are descriptive and not statistical significance evidence.

Prepared [the BFCL protocol](bfcl_pilot_protocol.md): pinned source/checker inspection,
20 exact development IDs, answer-key compatibility requirements, a fixed easy distractor
pool and semantic audit, controls, and a conditional 60-call/$1 pilot proposal. No
additional experiment or frontend was implemented; no paid calls or large archives used.
Outstanding live-pilot gates: owner approval, exact model/prices, selected-case ambiguity
review, importer/grader compatibility tests and independent rendered-request review.
GitHub Actions [run 41729343742](https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41729343742)
passed for commit `1fc165911f190c989f7ff38fabb2b059000641d6`: both Python 3.12 and
3.13 jobs completed locked installation, pytest, Ruff lint and formatting checks.
Phase 1.5 acceptance is complete; the live-pilot approval and compatibility gates remain.

## Workflow guidance update — November 3, 2026

Synced the owner's Git/GitHub workflow guidance from commit `8652be1` and made
phase verification updates explicit in `AGENTS.md`: record implementation, checks
and outcomes, and unresolved limitations while preserving earlier evidence.
Documentation-only change; no engine behavior changed. Validation: offline pytest
**48 passed**, Ruff lint passed, Ruff format check passed (31 files), and diff
whitespace check passed. No GitHub Actions workflows are currently configured.

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
