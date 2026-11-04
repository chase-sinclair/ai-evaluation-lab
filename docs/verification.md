# Phase 0 / Phase 1 verification

Date: November 3, 2026. Host: Windows, CPython 3.13.0, uv 0.13.7.

## Phase 3A — November 4, 2026

Completed a bounded, source-based feasibility audit, not a new experiment. Exactly
40 previously unreviewed multiple-function records, unchanged schemas/keys and
provenance are retained with licensing. AI-assisted ledger: 12 label-eligible,
28 excluded, 11 eligible families, six business-function domains, zero no-call and
zero independently human-verified cases. Source-function catalogs range 3–19 tools;
none meets the old 15/30 near/adjacent quotas. Recommendations and limits are in
[the feasibility report](phase3a_feasibility.md).

Added only offline scripts/tests and evidence/documents. The cache proposal is a
pure calculator/validator, not live adapter/runner integration. It keeps actual
provider USD unknown, separates reported-usage pricing from a requested-30m-policy
estimate, and reserves at the highest reviewed write rate/full output bound. Tests
reject body/hash/size, breakpoint/history/hosted-tool, tier, TTL, prewarming, output
limit and usage violations. No historical record is retrospectively repriced.

Final verification commands, all passed:

```text
py -3.13 -m uv sync --locked --offline
py -3.13 -m uv run --offline pytest -q
py -3.13 -m uv run --offline ruff check .
py -3.13 -m uv run --offline ruff format --check .
py -3.13 -m uv run --offline python -m scripts.audit_phase3a --source-dir datasets/cache/bfcl/bfcl_eval/data
py -3.13 -m uv run --offline python -m experiments.tool_selection.prepare_bfcl --check
git diff --check
```

**136 tests passed in 28.97 seconds**; Ruff passed with 58 formatted Python files.
Locked sync checked 36 packages. The audit deterministically reproduces IDs, counts,
native-tool membership, seeded nested ordering, schema sizes and hashes; 41 gold
argument variants pass JSON Schema and the existing strict subset grader in an
audit-only view. Semantic uniqueness is not proven by those tests. Fresh CI does
not need the ignored upstream cache: committed bounded evidence supplies its inputs.

Pinned upstream input/answer files were fetched within a 400,000-byte-per-file
limit. Existing cache files have one extra final LF; parsed contents match and
upstream byte hashes are recorded explicitly. The optional source-cache check
accepts exactly that known EOF difference and rejects other hash drift. Source
schemas with unsupported optional metadata remain unsupported; no silent migration.

Read-only SHA-256 comparisons confirm all four original smoke artifacts still
match the Phase 2.6 preservation hashes. Frozen 54-request validation passed with
zero provider calls; no matrix or smoke execution occurred. Original experiment
interfaces, engine files, dataset and grades were not changed. No paid requests,
new raw results, credentials, large archives or benchmark dependencies.

Delivery CI verification is pending push. Remaining gates are independent human
review, further source feasibility for held-out/no-call cases, acceptance of the
reduced design/accounting policy, and separate integration/execution authorization.
The current pool does not justify the substantive enterprise study.

## Phase 2.6 — November 4, 2026

Implemented typed cache usage/pricing, component costs and provenance, strict
accounting validation, unknown-cost stopping and maximum-write-rate reserves.
Added prospective BFCL diagnostics without changing primary grading or answer
keys. Generic summaries include diagnostic denominators/versions and cache
partition coverage. Historical smoke files and frozen requests are preserved.
See [accounting and diagnostic details](phase2_6_hardening.md).

Commands run from the repository root (all passed):

```text
py -3.13 -m uv sync --locked --offline
py -3.13 -m uv run --offline pytest -q
py -3.13 -m uv run --offline ruff check .
py -3.13 -m uv run --offline ruff format --check .
py -3.13 -m uv run --offline python -m experiments.tool_selection.prepare_bfcl --check
git diff --check
```

Results: **114 tests passed in 34.01 seconds**, including the existing 388 official
checker decisions and fake SDK/runner flows. Ruff checks passed; 52 Python files
already formatted. Locked install checked 36 packages. Frozen manifest check
validated all 54 requests with zero provider/network calls; it did not execute
the development matrix. Test sockets are blocked and API credentials removed.

New coverage: mixed 30m/12h writes, read/ordinary-input separation, no reasoning
double charge, missing/malformed counters, totals inconsistency, tier mismatch,
missing prices, unknown lifetime, conservative preflight and durable stop on cost
uncertainty. Grading tests distinguish integer versus float lists, schema-valid
wrong values, malformed/unoffered calls, no-call and incomplete output; reporting
tests retain primary results and explicitly count unmeasured diagnostics.

The first expanded run exposed an overly strict test assertion about SDK-added
null cache-mode metadata; the assertion now checks the relevant reported TTL.
No production behavior was weakened. The final suite above passes without skips.

Read-only SHA-256 checks before and after changes match all four original smoke
files; exact hashes are in the hardening document. No original grades, stored
estimates, raw records or frozen dataset/configuration were rewritten. No paid
requests or benchmark archives were downloaded. No new raw output is committed.

Documentation research inspected pinned BFCL multiple examples and keys, API-Bank
meeting labels and checker code/license, and current Sierra evaluation rules/license.
The [Phase 3 proposal](phase3_research_design.md) specifies selection, split isolation,
controls, paired analysis, sample quotas, estimated costs, abort rules and approval
gates. It does not claim that enough eligible cases or distractors have been audited.
The held-out experiment is neither implemented nor executed.

Implementation commit `991c963d9c57ef30c66dd0a30bc30757dc508b8b` was pushed to origin/main.
[GitHub Actions run 41918593399](https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41918593399)
passed on Python 3.12 and 3.13 with locked install, offline pytest, Ruff lint and
format checks. This documentation-only follow-up records verified CI evidence.
No implementation blockers remain. Live work still needs a reviewed accounting policy for absent write
lifetime detail, eligible source/gold audits, a frozen protocol and owner approval.

## Approved Phase 2.5 execution — November 4, 2026

The owner explicitly approved the six frozen requests and their existing limits.
Reran the frozen-manifest/readiness checks and spending preflight, then invoked
`py -3.13 -m uv run --offline python -m experiments.tool_selection.smoke_bfcl --live`
exactly once from clean commit `ca06c7c428dc47e2588c8d4b2d8b92bb84f09e68`.
Run bfcl-smoke-v1 recorded six completed responses and no retries or additional runs.

Reviewed every response against actual offered tools and original keys; reproduced
all grades offline and verified request hashes/order, JSON Schema validity and usage.
Result: 4 passes, 2 invalid outputs caused by the frozen BFCL float-list rule. All four
function calls chose offered targets and were valid JSON/schema; both no-call outputs
were correct. API integration succeeded for these payloads, but the grading mismatch
and omitted cache-write premiums prevent claiming unconditional validation success.

Returned model was gpt-6-luna throughout. Reported defaults: temperature 1.0, top_p 0.98,
medium reasoning effort, standard reasoning mode, default service tier; output cap 4096
and parallel calls false. Detailed per-request arguments, usage, latency, settings and
cost estimates are documented in [the findings](bfcl_smoke_findings.md).
Totals: 5784 input, 226 output (63 reasoning), 4599 cache-write tokens. Stored estimate
$0.0006914; short-cache rate scenario $0.000806375, not an invoice. Raw responses report
unrequested 24h cache retention; the applicable write price is unresolved. No missing usage,
refusals, incomplete outputs, API/schema rejections or parsing errors. Raw immutable
artifacts remain local/ignored; no code, data, protocol or grades changed.

Post-run checks: **85 pytest tests passed**, Ruff lint passed, Ruff format check
passed (47 files), and diff whitespace check passed. Git confirms raw records are
ignored; only these verification/progress notes and the derived findings are staged.
Documentation-delivery [CI run 41904991694](https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41904991694)
passed for commit `016e2b006dafa6ee89cba4cdcf77234051ebfda7` on the configured
Python 3.12/3.13 matrix. A documentation-only follow-up records this result.
No further paid execution is authorized; stop for review of the findings.

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
configuration. GitHub Actions [run 41869541258](https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41869541258)
passed for implementation commit `dcc2203f183031c71906bcd25726007dd1605674`.
Both Python 3.12 and 3.13 jobs passed locked installation, offline pytest, Ruff lint
and formatting. Phase 2.5 preparation acceptance is complete; a documentation-only
checkpoint records this result. Paid execution remains pending explicit owner approval.

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
