# Progress — November 3, 2026

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
