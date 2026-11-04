# Progress — November 4, 2026

Current status: the explicitly approved Phase 2.5 smoke was executed once; stopped
after all six requests. No further execution authorized. See docs/bfcl_smoke_findings.md.

Run bfcl-smoke-v1 used clean commit ca06c7c428dc47e2588c8d4b2d8b92bb84f09e68.
Readiness and spending preflight passed immediately before execution. All six API
responses completed, returned gpt-6-luna and supplied usage. Frozen grades: 4 passes,
2 invalid outputs (integration interval integers rejected by BFCL float-list rule).
All emitted calls were offered and passed JSON Schema; no parsing/schema rejection,
provider error or incomplete output. Raw artifacts remain ignored and unchanged.

Usage: 5784 input / 226 output tokens, including 63 reasoning tokens; 4599 cache-write
tokens. Stored estimate $0.0006914 omits cache-write premium; short-cache rate
scenario $0.000806375. All raw responses report unrequested 24h cache retention;
its applicable price and actual invoice are unverified. Integration transport succeeded;
full validation is qualified by the grading mismatch and cost-accounting omission.

All six responses reviewed individually; hashes/order/membership/schema/regrades and
cost arithmetic verified offline. Documentation only is being updated and delivered.
Post-run checks: 85 tests passed; Ruff lint/format (47 files) and diff checks passed.
Next: commit/push documentation, verify CI, then STOP for owner review.
No retries, substitutions, purchases, full pilot or held-out run.
Any fixes to grading diagnostics or usage pricing require separate review before
more spending; do not retroactively alter this run's grades or delete its directory.

## Previous checkpoint — preparation and approval boundary

Current phase: Phase 2.5 live integration preparation complete, pushed and CI verified.
**No paid requests executed or approved. Await explicit owner approval.**

Completed: request-aware grading (BFCL 0.2.1) rejects unoffered tools; generic grading
context passed by the runner; exact validated trial-order option preserves the frozen
six-row order. Six-request configuration, offline preflight, fixed run ID/replay guard,
explicit standard service tier and pinned OpenAI endpoint. Fresh audit of all six
questions/schemas/keys/optional fields/distractors/hashes is in docs/bfcl_smoke_audit.md.

Frozen dataset, 54-request manifest, source locks and original configuration unchanged.
Current run metadata records new source/grader versions separately. No new experiment,
frontend, held-out dataset or hypothesis/design change. Grader retains BFCL numeric-list
and string-normalization limitations, documented in the audit.

Verification so far: 85 offline tests pass, including 388 retained checker comparisons,
six-request SDK fake transport, per-request invalid-vs-task-failure reporting, frozen
ordering, replay prevention, drift rejection and preflight with zero provider calls.
Spending preflight: 6 requests, 43,740 estimated input tokens, 24,576 output ceiling;
$0.016662 standard / $0.0177555 cache-write estimate, below $0.05.
Model/prices rechecked in official documentation November 4; account access untested.

Files: runner/registry grading context; Responses payload helper/standard tier;
BFCL integration/grader/prepare updates; smoke_bfcl.py, bfcl_smoke.yaml,
bfcl/smoke_readiness.json; context/smoke tests; audit/proposal/extension/verification docs.
Latest CI-verified implementation: dcc2203f183031c71906bcd25726007dd1605674.
CI: https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41869541258
Both Python 3.12 and 3.13 passed locked installation, offline pytest and Ruff checks.
A following documentation-only checkpoint records this evidence.
Final local checks passed: locked offline sync (36 packages), 85 tests, Ruff lint/format
(47 files), frozen 54-request check, six-request spending preflight and diff whitespace.
Next: wait for explicit owner approval of the six-call protocol in docs/bfcl_smoke_audit.md.
No preparation blockers remain; account access/server acceptance remain untested live risks.
After approval only: `py -3.13 -m uv run --offline python -m experiments.tool_selection.smoke_bfcl --live`.
This would make paid calls despite uv's dependency-offline flag. Do not execute on
continuation alone; do not delete results/bfcl-smoke-v1 to retry a failed attempt.

## Previous accepted checkpoint — Phase 2

Current phase: Phase 2 preparation complete; implementation pushed and GitHub Actions passed.

Completed: pinned bounded BFCL importer; 18 audited development cases (14 positive,
4 no-call); schema/name conversion; deterministic subset grader; 388 decisions from
the pinned official checker; complete 54-request offline manifest; source-based
research-design assessment; six-request GPT-6 Luna smoke proposal at a $0.05 cap.
No model execution or large archives. Existing shared engine/provider interfaces and
default authored fixture remain intact. Cases 5 and 14 excluded for ambiguity.

Files: experiment-local bfcl_data/grader/integration/conformance/prepare modules,
bfcl_development.yaml and bfcl artifacts/license/attribution; tests/test_bfcl.py;
docs/bfcl_phase2_design.md, docs/bfcl_smoke_test.md, protocol/experiment README updates.

Final local tests: 74 passed, Ruff lint/format (44 files) passed, locked offline sync
passed, frozen 54-request manifest reproduced, raw-source reimport and all 388 official
checker decisions regenerated exactly. GitHub Actions passed on Python 3.12 and 3.13,
including locked install, offline pytest, Ruff lint and formatting. Raw source
hashes were independently checked against bounded raw upstream responses; preserved
original EOF bytes rather than connector-added final newlines. Final manifest was
checked after formatting. Cached sources and raw results remain ignored.

Latest CI-verified implementation: `b4fbecd199426ca7c4fae374d58ca474236edab1`.
CI evidence: https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41765877967
The following documentation checkpoint records that result; no implementation changes.
No Phase 2 preparation blockers remain. Next: owner review of docs/bfcl_phase2_design.md
and docs/bfcl_smoke_test.md. Do not start paid execution on continuation alone.
Live gates: owner approval of six frozen requests, model alias/default settings,
dated prices and $0.05 cap; activate only the approved six-request invocation and
recheck hashes/budget/account availability before any paid request. The full 54-request
configuration has a zero live budget. Held-out study needs a separate audited protocol.

## Previous accepted checkpoint — Phase 1.5

Phase 1.5 complete; local checks and GitHub Actions passed.

Completed: per-condition reporting, case-paired descriptive comparisons, text/tool-call
normalization, SDK transport tests, offline CI matrix, pinned BFCL pilot methodology.
Preserved shared runner/experiment isolation, sequential execution, live opt-in, budgets,
immutable records and raw output. No frontend/additional experiment or paid calls.

Files: summary, runner, CLI, contracts, providers; comparison/adapter tests;
`.github/workflows/ci.yml`; README; comparative reporting, BFCL protocol and verification docs.
Local checks: 54 pytest tests pass; Ruff lint/format and diff checks pass.
Latest CI-verified implementation checkpoint: `1fc165911f190c989f7ff38fabb2b059000641d6`.
GitHub Actions: https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41729343742
Both Python 3.12 and 3.13 jobs passed locked installation, pytest, Ruff lint and format checks.

Next: owner review of docs/bfcl_pilot_protocol.md; after approval implement the bounded
importer and grader compatibility checks, freeze rendered requests, and recheck the budget.
No live execution before owner approval. No Phase 1.5 implementation blockers remain.
Pilot blockers: exact model/prices, case ambiguities, importer/checker compatibility,
rendered 60-request review, source handling and spending/request ceiling approval.

Decisions: preserve aggregate keys; compare equal-weight case means, not independent
repetitions; disclose incomplete pairs and unknown costs. BFCL development subset is
purposeful and correlated, with easy business-record distractors; no official benchmark
comparability or model-performance claims.
