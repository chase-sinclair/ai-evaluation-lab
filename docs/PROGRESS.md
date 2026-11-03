# Progress — November 3, 2026

Current phase: Phase 1.5 implementation and local verification complete; remote CI pending.

Completed: per-condition reporting, case-paired descriptive comparisons, text/tool-call
normalization, SDK transport tests, offline CI matrix, pinned BFCL pilot methodology.
Preserved shared runner/experiment isolation, sequential execution, live opt-in, budgets,
immutable records and raw output. No frontend/additional experiment or paid calls.

Files: summary, runner, CLI, contracts, providers; comparison/adapter tests;
`.github/workflows/ci.yml`; README; comparative reporting, BFCL protocol and verification docs.
Local checks: 54 pytest tests pass; Ruff lint/format and diff checks pass.
Latest locally tested implementation commit: `7571d3b` (remote user guidance merged afterward).

Outstanding: push merged checkpoint and inspect both Python CI jobs. Then record CI URL,
commit and outcome here and in verification. No live execution before owner approval.
Pilot blockers: exact model/prices, case ambiguities, importer/checker compatibility,
rendered 60-request review, source handling and spending/request ceiling approval.

Decisions: preserve aggregate keys; compare equal-weight case means, not independent
repetitions; disclose incomplete pairs and unknown costs. BFCL development subset is
purposeful and correlated, with easy business-record distractors; no official benchmark
comparability or model-performance claims.
