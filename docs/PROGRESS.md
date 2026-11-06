# Progress — November 6, 2026

## Recruiter-facing presentation ready for owner review

Revised the [case study](portfolio/entity-matching.md) with three headline
metrics, an accessible architecture diagram, a CNPq decision trace, a
sourced contribution statement and the four pilot replay rows. The proposed
human correction review is separate from both the implemented evaluation
and the completed development-label review. Added a [website handoff](portfolio/entity-matching-handoff.md)
and expanded the [reusable page outline](portfolio/study-format.md).
Starting revision was `24f286c`. All 173 offline tests and both Ruff checks
passed. The materials are ready for editorial review before website integration.

## Portfolio pivot · Phase 3G stopped after feasibility

The owner retired both the 40-family independent review and the proposed
200-family holdout. The first review wave alone was estimated at 18–32
person-hours, disproportionate to the goal of demonstrating an applied
architecture decision. The feasibility assessment at `d0740a3` stands as
completed work. Independent adjudication and holdout evaluation did not take
place. The proposals and next steps in earlier entries are historical.

Closed the [wave-1 preparation draft PR #1](https://github.com/chase-sinclair/ai-evaluation-lab/pull/1)
without merging. Its preparation branch and commit `1455060` retain the
templates and review history. No further review wave or model run is planned.

Published the [entity-matching case study](portfolio/entity-matching.md) and
a [future study format and portfolio placement recommendation](portfolio/study-format.md).
The README points readers to the case study first. The next editorial step
is to decide where to feature it on the portfolio website. This checkpoint
changes documentation only. [Offline verification](verification.md)

## Phase 3G — independent holdout feasibility and preregistration

At verified starting revision `aea5a5ab55d70ebabac7223e586923cdc1eccd4a`,
reconstructed the remaining Crossref population from the two pinned local sources.
The 579-row quarantine and supplemental review-cited IDs leave a screened frame
of 416 positive and 335 source-empty families. No family was recruited or
independently adjudicated in this phase. The 150/50 target is conditional.
[Feasibility and aggregate audit](phase3g_holdout_feasibility.md) ·
[Sampling manifest](phase3g_sampling_manifest.json) ·
[Reviewer workflow](phase3g_reviewer_workflow.md) · [Preregistration](phase3g_protocol.md)

Next decision is whether to authorize a blinded 20+20 feasibility review.
Keep large-scale review and any later spend behind separate decisions. The
25% paired contrast needs only the two lists' symmetric difference; obtaining
absolute quality and costs for both requires their union. A small effect may
remain unresolved at 200 families. No dispatch, acquisition, label change or
holdout ranking occurred. The offline checks are recorded in verification.

## Phase 3F — offline escalation analysis complete

Audited all 38 development decisions against the frozen baseline from commit
`019caffe3ba6251210b49156a0e568534cc8bd63`. Five of six errors were correctable
with the offered actions. Frozen distance reached four by slot nine. Margin reached
three by slot nine and five by slot 19. CNPq accounted for the extra opportunity
at slot 19. The other 34 queries still have no live predictions.
[Analysis and holdout proposal](phase3f_escalation_analysis.md) · [38-query appendix](phase3f_allocation_audit.md)

Added a read-only audit script and two offline tests. The pinned source rebuild,
171 tests, lint and format passed. Phase 3E records and pilot report matched
their published hashes. No live calls or runtime policy changes. Next step is
owner review of the proposed comparison, followed, if accepted, by a separate
holdout sampling/adjudication and preregistration milestone before any spending.

## Phase 3E — authorized live prefix completed

Executed the frozen four-query prefix once at revision 1369906. The pricing
and spending preflight, human review, body hashes and one-shot checks passed.
Three correct links and one correct abstention. Replay accuracy was 3/4 at
0%, 25% and 50%, and 4/4 at 100%. Usage-priced estimate $0.0002111. The
[findings](phase3e_live_findings.md) give each query, cost and policy comparison.
All receipts remain local. Stop for owner review. Any further requests require
separate authorization and a protocol accounting for the four existing records.

## Phase 3E — human review validated, ready for owner approval

Chase Sinclair completed a human-conducted review with AI-assisted research.
All eight full-registry decisions and all eight offered-set decisions agree
with the freeze. The local receipt passed the existing validator after the reviewer
confirmed the Q01 date. The cohort has 38 queries. The next step is explicit
owner authorization for the four-request prefix under the $0.005 cap.
The [readiness report](phase3e_readiness.md) contains the exact command and protocol.

## Earlier Phase 3E checkpoint — dispatch verified offline

The [reviewer worksheet](review/funder_identity.md) covers the eight pending
queries and separates full ROR v2.6 identity from candidate coverage. No human
decisions were supplied. The provisional development cohort has 38 queries,
48 nominations and ten documented exclusions. Baseline correct decisions by
group are 18/18 registry forms, 8/12 variants and 6/8 provisional no-matches.

The [pilot and exact command](phase3e_readiness.md) propose four queries in the
original frozen order. The 1,024-output cap gives a $0.00354375 reserve against
$0.005 for this prefix. The revised 38-request planning reserve is $0.03398625
against $0.05. Both freezes are reproducible. Implementation commit
8b211ae0651f44bcaa1efec121a81a714fed694c passed 169 offline tests and
[the GitHub Actions checks](https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/42089244990).

Next: obtain one documented human development review of all eight queries.
Any changed answer or unresolved case requires a versioned cohort, calibration
and complete refreeze. Then seek explicit owner approval for the four calls.
Paid requests and held-out evaluations in this phase: zero.

## Phase 3D — offline resolution implemented, human review pending

The [Crossref experiment](phase3d_crossref_resolution.md) freezes 48 nominations,
including 10 documented exclusions. The development diagnostic uses 30
source-supported singletons and eight pending empty labels. Independent
no-match adjudications completed: zero. The requested 36/12 reviewed cohort
remains open. Retain all 48 nominations and their families on the development side.

The entity-matching module now supports active-registry lexical retrieval,
an abstaining top-one baseline, immutable shared-runner acquisition and four
paired replay policies. Recall@5 was 29/30. On the provisional calibration
set the baseline scored 32/38 correct and asserted-link F1 was .881.
The complete 38-body proposal reserves $0.09235425 against $0.15.
Paid requests and held-out evaluations this phase: zero.

Verified locally with 149 offline tests, lint, format, source reconstruction,
the original Phase 3C receipt and the mock end-to-end run. Implementation
commit 40f58320ec8b93c3754bdc765a12e4e235cebfb8
[passed GitHub Actions](https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/42038565105).
The next step is for two independent reviewers to use the blinded worksheet.
Resolve disputes, version any changed cohort, then review the exact cache-aware
dispatch and spending guard before requesting separate live authorization.

## Phase 3C — Crossref audit complete, experiment pending owner review

The [formulation comparison](phase3c_crossref_feasibility.md) recommends direct
name-to-ROR resolution with abstention. The [24-pair review](audits/phase3c/review.md)
contains 12 same-ID and 12 similar different-ID proposals from 48 deposited
names and 36 organizations. AI-assisted review provisionally retained 4 and 11,
respectively. Independent human adjudications completed: zero. All candidates
and overlapping families are development-exposed, including the exclusions.

Files include the pinned evidence packet, source reconstruction script and
offline receipt test. Locked offline sync, full reconstruction, 144 tests and
Ruff passed locally. Audit commit e4aad76cf311d14274bb7f158c0f1affd74768b4
[passed CI on Python 3.12 and 3.13](https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41967615964).
Next owner decision covers formulation B and a bounded offline development
protocol. Candidate retrieval, independent label review, held-out family counts
and a separate budget approval remain open. Paid calls this phase: zero.
The WDC implementation is paused and the substantive BFCL study is deferred.

## Phase 3B — WDC paused; dataset decision awaits owner review

The substantive BFCL tool-selection study is **deferred**, not completed. Its
four-case probe was not run. Prior phase notes below are historical.

Preserved the local WDC validation baseline, 180-pair metadata receipt, frozen
but unauthorized pilot proposal, and the existing authored runner/replay example
in experiments/entity_matching. No raw records in Git, paid calls, or held-out
evaluation. WDC external transmission rights remain unresolved. See the
[checkpoint and baseline measurements](entity_matching_checkpoint.md).

[Dataset decision](entity_matching_dataset_decision.md): recommend Crossref's
CC0 manually ROR-labeled deposited funder names over registry-only aliases or
OpenAlex machine-linked affiliations. 220 organizations have two or more
normalized variants after initial screening. No new experiment or pairs built.
Next: owner review of the source, organization-identity definition and bounded
24-pair offline audit; independent reviewers, protocol freeze and separate
approval would precede any model calls. No further WDC work is scheduled.

Local verification: 143 offline tests, Ruff lint/format and full WDC receipt
reconstruction passed. Verified implementation: 230a2547127933654ffed7f4c8edddb8dfcf31a2;
[GitHub Actions passed on Python 3.12 and 3.13](https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41965569494).

## Phase 3A — complete, pushed and CI verified

Audited exactly 40 new BFCL multiple records (57–99 except previously reviewed
76/81/93), preserving source schemas/keys/URLs/revision/hashes with Apache-2.0
attribution. All are development-exposed, with no held-out selection. Counts:
12 provisionally label-eligible records, 11 eligible families, six business-function
domains, 28 exclusions and zero no-call cases. Review is AI-assisted; independent
human reviews: zero. The original 12-case/120-case plans are not supported by this pool.

Constructed source-only catalogs for all 12 label-eligible cases (3–19 tools).
None supports 30 tools or the old 15/30 near/adjacent quotas. Only three have enough
tools for the old five-tool quota. Proposed replacement: four development cases
57/86/87/90 at 3/5 tools, eight requests, descriptive only, with unchanged native
tools and two added adjacent functions. Broader enterprise conclusions are a no-go.
Future held-out target is conditionally 24 untouched families (18 positive/6 native
no-call), subject to a separate audit; availability is not established.

Cache policy proposal: explicitly request implicit 30m caching with no explicit
breakpoints. Keep reported-usage estimates, policy-based estimates and conservative
reserves separate; absent lifetime detail stays unknown. Offline calculator/tests
validate actual-body hashes, byte limits, tier/TTL/counter/output violations and
SDK serialization. It has no network calls and is not connected to the live runner.
Existing engine/adapter, smoke artifacts, old grades and frozen requests are unchanged.

Verification: 136 offline tests passed; Ruff lint/format (58 files), locked offline
sync, source-cache audit reproduction, frozen 54-request check and four smoke hash
comparisons passed. Source refetch was bounded to two small category files; the
cache-added final newline was explicitly reconciled and exact upstream hashes kept.
No additional candidate records were semantically reviewed, no paid calls, no
full experiment/held-out implementation, and no raw results or credentials added.

Files: docs/audits/phase3a (source evidence, review ledger, catalog samples, summary,
license/notices); phase3a_feasibility.md and phase3a_cache_policy.md; two offline
scripts, test_phase3a.py, README/design links, progress and verification.
Latest CI-verified audit delivery: 5fb68f331134d7aeeb04ae8c04559c51ee91329d.
GitHub Actions passed on Python 3.12 and 3.13 (locked install, offline tests, Ruff):
https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41933167093
This documentation-only checkpoint records the verified result. Work is STOPPED
for owner review; no further implementation or execution is authorized.
Next approval gates: reduced design/scope; independent human review and another
bounded source audit; prospective accounting assumptions; minimal future integration;
then frozen requests/settings/prices and explicit spending approval. Proposed
eight-request reserve $0.032896, spending cap $0.05; no execution is authorized.

## Phase 2.6 — complete, pushed and CI verified

Workstream A is complete: cache-aware usage partitions and component pricing,
source/version/tier/lifetime metadata, unknown-cost stopping, conservative cache
reserves, and prospective BFCL schema/selection/exact diagnostics. Strict primary
grader 0.2.1 and answer keys remain unchanged; diagnostics are separately versioned.
Legacy pricing serialization preserves frozen configuration/request hashes.

Workstream B is documentation-only: docs/phase3_research_design.md proposes paired
5/15/30-tool business cases, a 12-case / 36-request development pilot, and a separate
120-case held-out study. Pinned BFCL examples, API-Bank dialogue/checkers and current
Sierra evaluation rules were inspected. Eligibility yield and gold uniqueness are
explicit feasibility gates. No new dataset or experiment was implemented.

Verification: locked offline sync (36 packages), 114 offline tests, Ruff lint/format
(52 files), frozen 54-request manifest check and diff checks passed. Existing 388
official-checker decisions still pass. All four original smoke artifact hashes
match the before-edit snapshot; no smoke regrading or rewriting occurred. No paid
calls, 54-request execution, new raw results, credentials or external data commits.

Files: contracts, budgets, adapter, runner, summary, BFCL diagnostic wrapper;
cache/diagnostic tests and explicit cache counters in the fake smoke transport;
README, hardening/design documents, progress and verification.

Official docs distinguish maximum 24h retention from minimum write lifetime.
No 24h price is inferred. Missing lifetime breakdown remains unknown, so a future
response matching the smoke telemetry would stop further calls. See
docs/phase2_6_hardening.md for the accounting boundary and preservation hashes.

Latest CI-verified implementation: 991c963d9c57ef30c66dd0a30bc30757dc508b8b.
CI passed on Python 3.12 and 3.13, including locked install, offline tests and Ruff:
https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41918593399
This documentation-only checkpoint records that result. Work is STOPPED for owner
review. Next work needs approval of the Phase 3
design, bounded source/label audit and redistribution, independent reviewers and
split custodian, then exact frozen requests/settings/prices and an accounting policy
before a separately approved pilot (proposed $0.35 / 36-request cap). Held-out
implementation/execution and all further paid calls remain unauthorized.

## Previous checkpoint — approved smoke findings

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
Findings delivery commit: 016e2b006dafa6ee89cba4cdcf77234051ebfda7.
CI passed: https://github.com/chase-sinclair/ai-evaluation-lab/actions/runs/41904991694
A documentation-only follow-up records this verified result. Work is STOPPED for
owner review; no pending implementation or live execution is being pursued.
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
