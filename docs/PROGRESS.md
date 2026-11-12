# Progress — November 11, 2026

## Experiment 005 · scored offline, pending architecture review

At sealed checkpoint ff9d0036192a4630c450c8ab451f985efe315120, validated both worksheets, the complete ledger, snapshots and grader image. Ran the frozen evaluation_r1.analysis command with the completed review and both evaluation snapshots. The 144 case grades and per-arm metrics are in the ignored .verification/evaluation-report.json. Its SHA-256 is d6986bcf9d2f5b509e4f36af1c29d9c745ed3e5c7348117f238a61d6168399f4. All 399 fixture-enabled offline tests and Ruff lint/format passed. Only analytical documentation changed. Next step is owner architectural review before any publication. [Comparative report and case ledger](experiment05_scored_results.md)


## Experiment 005 · full evaluation sealed, blinded review pending

Executed once at approved clean revision `46c15339f9dcbe767ae7e3dba6cd986ee2099205` with owner-confirmed credit and project settings. All 144 planned episodes produced terminal decisions. There were 350 model requests, 206 local discovery calls, zero retries, output exhaustions, interruptions, unsent episodes or unaccounted attempts. Usage-estimated cost was $0.103640710 under the $5.50 ceiling.

Verified all 1,751 sealed files, frozen and dynamic wire bodies, discovery histories, unique response IDs, settings, receipt usage partitions and individual charges. Input was 576,292 tokens including 390,766 cache reads and 51,318 short-cache writes. Output was 159,795 including 128,367 reasoning tokens. The ledger digest is `ba05d8c60ce0dd58043c044d7a39e276a76f5a1b8668f891c0355237188b3c4b`. Seal SHA-256 is `5f136beda3c3cdd97d3daa55e4e174b746594b5b2492a1f56099ae5f5d5bec79`.

The frozen replay generated 11 distinct masked worksheet entries in the ignored local file `.verification/evaluation-clarifications.json`, SHA-256 `affd0375b0f3da89e2873aa9722ff628e69add15623a24852fc5a8826ef4982e`. Give the reviewer only the worksheet. Return a copy with each adequate field set to true or false, preserving identifiers and wording. Final scoring awaits that review. The live directory is consumed. All 399 local tests passed, including warehouse fixtures. No model-quality results are reported at this checkpoint.


## Experiment 005 · full evaluation dispatcher awaiting owner review

Based on accepted pilot audit `a145d01d326a2d9242a3e1b7071fb9ac07fedede`, added the separate evaluation-r1 proposal, dispatcher, fail-stop and exhaustion tests, and sealed two-snapshot analysis with masked clarification review. Raw evidence and original manifests remain untouched. Maximum-depth, early-terminal and exhaustion mocks cover all 144 episodes. The evaluation reserve remains $5.008329. Next step is separate owner review of the exact commit, digest and $5.50 cap before any inference. [Review packet, identities, mocked evidence and commands](finops_evaluation_dispatch.md)


The final fixture-enabled local suite passed 399 tests in 178.44 s. Ruff lint and format, staged whitespace, archive identity, historical seals and extension scope passed. No live result directory exists.

## Experiment 005 · development pilot sealed and independently audited

The one-time development pilot from approved revision `b2e15eb3610455e15e634836b439b80bff193203` completed all five episodes, 11 requests and six discovery calls. All 56 covered files, the ledger, wire bodies and $0.003635530 usage estimate reconciled. Two SQL outputs matched financial references, one executed incorrectly, one expected SQL answer was a clarification and the required clarification omitted scope. Owner review is next. Full evaluation implementation and acquisition are outstanding. [Case-level results, hashes and readiness](finops_pilot_audit.md)


Verification passed all 379 offline tests with FINOPS_VERIFIED_ROOT set, Ruff lint/format and whitespace checks. Only the audit and continuity documents changed.

## Experiment 005 · development pilot dispatcher, revision 1

From accepted checkpoint `5caa79e50fe2d07787bfbd043ad31eaf25c9f904`, added the pilot-only dispatcher, accounting and protocol extension, separately bound manifest and transport tests. Both original v3 archives remain intact. Rehashed all 188 sealed v2 entries against the original seal SHA-256. No historical candidate was executed. Verified identical five initial request bodies and regenerated dynamic bounds. Next step is owner review of the exact revision, account limits and credit before any paid execution. [Identity, command, mocked evidence and remaining risks](finops_pilot_dispatch.md)


Local verification passed all 379 tests with FINOPS_VERIFIED_ROOT set (114.63 s), including 19 pilot dispatcher tests. Ruff lint and format and staged whitespace checks passed. Full- and early-depth mocked acquisitions completed 5/5 episodes in 11 and 6 requests respectively. No provider inference or model-quality measurement occurred.

## Experiment 005 · v2 accepted, prospective v3 ready for owner review

The permanent historical checkpoint is `c6fb697d359778260fb9f6dcfb5745b18ad0077d`. Its 188 receipt files and ledger matched the published seal. The read-only response diagnosis, common reporting-year convention, separately versioned DuckDB worker, development rehearsal and exact archives are complete. The v3 files are under `experiments/finops_sql/v3`, `experiments/finops_sql/proposals/v3` and `tests/test_finops_v3.py`. The two-snapshot numeric and ambiguity keys carry forward. The owner packet identifies all 17 clarification replies and the three operational/grammar failures. [Findings, differences and budgets](experiment05_prospective_v3.md) · [Verification](verification.md)

All 32 scripted development episodes completed. Seven distinct SQL results matched the existing development keys, and the eighth task retained material ambiguity. The locally verified proposal commit is `4098197b86253fc5bdb55f9c7b8a67f024987a5a`. All 360 local tests passed with both Docker images, and both Ruff checks passed. The subsequent CI change adds the v3 Docker build and development fixture test to the existing warehouse job. It preserves the proposal digests. Hosted checks comprise the portable Python 3.12/3.13 matrix and a separate clean warehouse build. [Warehouse CI](https://github.com/chase-sinclair/ai-evaluation-lab/actions/workflows/finops-checkpoint.yml)

**Next step is owner review of the separate five-episode development pilot**, reserve $0.153159625, proposed cap $0.17. Full evaluation reserves $5.008329 under a proposed $5.50 cap. Live execution integration, review of its exact revision, cohort-specific authorization, current API credit and applicable project limits are outstanding. At resumption, read the owner packet and protocol and check the frozen hashes. No inference is authorized by this checkpoint.

## Experiment 005 · interrupted live acquisition sealed

The approved one-time run stopped on Q23C at the output limit. Verified all receipts, reconciled usage and graded all 21 completed episodes offline. No retry or resume. The full offline suite passed 329 tests and both Ruff checks passed. Next step is owner review. [Case-level audit and integrity evidence](finops_acquisition_audit.md)

## Experiment 005 · dispatcher review

The v2 dispatcher and mocked acquisition are ready for owner review. The next decision is separate authorization against the exact digest, reviewed extension SHA and confirmed spend allowance. [Dispatch checkpoint](finops_dispatch.md)

## Experiment 005 · pre-acquisition v2 awaiting owner review

Following the accepted infrastructure at `0e35794`, Q07 now spans the July rate change, Q14 uses percent-of-budget terminology and Q16 is classified as a balanced-ledger output task. The stateless discovery workflow remains the secondary architecture. The separately frozen v2 proposal reserves $0.8432640 under a proposed $1.00 cap. Next step is owner review before live acquisition. [Case-level changes, hashes and verification](experiment05_preacquisition_v2.md) · [Reviewer packet](experiment05_oracle_review_v2.md)

## Experiment 005 · checkpoint 2 pending owner review

The accepted checkpoint-1 revision was `df74a10321df6697f89849c915bdcae4b828d8f3`. The four context conditions, provenance-enforced discovery, typed two-snapshot grading, masked clarification checkpoint, reviewer packet and offline SDK workflow are implemented. The proposal freezes 144 initial bodies and the deterministic construction of up to 216 later D bodies. The proposed reserve is $0.842857750. Review the oracle packet, budget, tokenization limitation and exact digest before considering a live dispatcher or granting execution authority. [Checkpoint and artifact index](experiment05_checkpoint2.md) · [Verification](verification.md)

## Experiment 005 · checkpoint 1 ready for owner review

Implemented the offline 22-table warehouse, 32 paired Python/SQL keys, four clarification witnesses and eight development tasks. The sealed source-manifest bindings reproduced across two builds. The bounded Docker worker handled every reference query. The discovery audit supports raising the tool budget and reserving more output for reasoning. The current decision is owner review of the evidence and proposed limits before context-package work. Prior verified design commit `7d4771cd98db01493adfedcc49bf9ca134d7040f`. [Checkpoint, budgets and reproduction](experiment05_checkpoint1.md) · [Verification](verification.md)

## Experiment 005 · FinOps SQL design awaiting review

Following the completed Experiment 004 checkpoint at `ab58549`, the [Experiment 005 proposal](experiment05_sql_context_design.md) specifies a fictional 22-table warehouse, 36 paired questions, three preloaded-context conditions and a separate bounded discovery workflow. Next decision is owner review before warehouse or experiment implementation. [Verification](verification.md)

## Experiment 004 · publication package complete

Final review approved the package at `d1c1347` subject to three editorial edits. The article now opens in the simulation, the handoff uses the shorter listing title, and the root README lists the study. The next owner decision is whether the Lab needs Experiment 005. Website integration remains deferred. [Verification](verification.md)

## Experiment 004 · publication materials ready for editorial and design review

The owner accepted the technical findings at `b4054a1`. The [final findings](experiment04_final_findings.md), [case study](portfolio/recovery.md), three responsive figures and [website handoff](portfolio/recovery-handoff.md) are ready for review. The recommendation favors rules for comparable normalized inputs and documented recoveries. Maintenance costs remain unmeasured. The next decision is owner approval of the presentation. Website integration remains deferred until the Lab is declared complete. [Verification](verification.md)

## Experiment 004 · completed follow-up awaiting owner review

The approved 2,048-token acquisition at `8a4074b` completed all 24 requests once. The live model and frozen rules each scored 24/24, against 9/24 for stop-and-report. Estimated follow-up spend was $0.0029715. Both acquisitions retain separate seals, receipts and denominators. [Case results and receipt ledger](experiment04_followup_acquisition.md). The next decision is owner review of the technical findings.

## Experiment 004 · separately configured follow-up awaiting owner decision

The first acquisition at `ae4c116` is permanently closed. Its six receipts and seal reverified. The [new approval checkpoint](experiment04_followup_plan.md) freezes the same 24 requests in order with the output cap raised to 2,048. Estimated reserve $0.038285, proposed cap $0.05. Next decision is separate owner approval or rejection. No paid follow-up requests have been sent. [Verification](verification.md)

## Experiment 004 · live acquisition sealed at mandatory stop

From approved freeze `b8a6fca` and clean dispatcher `8ee89e7`, six of 24 requests were sent once. P3 reached the 512-token limit and returned incomplete. Five completed proposals were replayed offline; C scored 4/5 evaluable, with four verified successes against 24 planned. P8 missed confirmed completion. Total usage-priced spend was $0.0011733. [Partial paired results and receipt audit](experiment04_live_acquisition.md) · [Verification](verification.md). Next step is owner review. The run cannot resume.

## Experiment 004 · offline implementation and request freeze

The [implementation checkpoint](../experiments/recovery/README.md) covers the 24 evaluation episodes, eight development episodes, immutable mock traces and exact acquisition proposal. Rules freeze `491abff` preceded final evaluation. A scored 9/24 and B scored 24/24. C has only scripted transport evidence. The next decision is whether to authorize the 24 frozen requests for a descriptive safety and parity comparison. Account access and live dispatch controls must be checked separately before execution. [Verification](verification.md)

## Experiment 004 · revised design awaiting approval

Following review of `3652d0a`, the [revised proposal](experiment04_recovery_design.md) strengthens five business-context episodes and defines eight offline development cases, a pre-evaluation rules freeze and independent syntax, authorization and outcome checks. A possible 24/24 rules ceiling is explicit. The 24-case evaluation and provisional budget remain unchanged in size. Next decision: owner review before implementation. [Verification](verification.md)

## Experiment 004 · recovery design awaiting owner review

The owner approved the Experiment 03 publication package at `c41025d`. Portfolio website integration is deferred until the owner explicitly declares the Lab complete. The [Experiment 004 design](experiment04_recovery_design.md) proposes 24 paired mock failure episodes across procurement, financial operations and SaaS administration. The next decision is approval of the proposed scenarios, recovery authority and scoring before any implementation. A later live run requires a separate frozen-manifest approval. [Verification](verification.md)

## Experiment 03 · final publication-preparation pass

Following design review of `1005df3`, the [article](portfolio/rag-safeguards.md) and [website handoff](portfolio/rag-safeguards-handoff.md) explicitly scope the comparison to preselected evidence. The workflow and Annex B figures now have wide and compact layouts. The accepted findings and FDE guidance carry forward. The package is ready for website integration as a separate activity. [Rendering and offline checks](verification.md)

## Experiment 03 · publication package ready for final design review

The owner accepted the grading and technical findings at `7532f34` and approved the FDE playbook as engineering guidance. The [article](portfolio/rag-safeguards.md), three accessible figures and [website handoff](portfolio/rag-safeguards-handoff.md) are ready for design review. The C12 quotations match the source packet, generator receipt and application referral. The package passed the full offline suite, Ruff and responsive figure checks. The next decision is owner approval of the presentation. [Verification](verification.md)

## Experiment 03 · paired analysis ready for owner adjudication

From acquisition checkpoint `2627169`, validated the supplied 40-entry AI-assisted review, replayed both sealed stages offline, and reconciled 32/36, 32/36 and 28/36 fully correct decisions. The [grading audit](experiment03_phase_b_review.md), [technical draft](experiment03_paired_findings.md), [deployment playbook](fde_deployment_playbook.md) and [portfolio draft](portfolio/rag-safeguards.md) await owner review. Priority decisions concern I03 referral sufficiency and I04 scope/citation treatment. No new acquisition or website changes. [Verification](verification.md)

## Experiment 03 Phase B · acquisition complete; masked review pending

At approved revision `6fd092f`, the verifier completed 36 requests once. Four replies were blocked. The local blank worksheet at `.verification/enterprise-phase-b-blank-review.json` covers all 108 derived arm outcomes in 40 distinct entries. Review a copy before interpreting quality or recommending an architecture. [Acquisition audit](verification.md#experiment-03-phase-b--stage-2-live-checkpoint)

## Experiment 03 Phase B · Stage 1 complete; Stage 2 awaiting approval

The authorized run at `d027aeb` completed all 72 requests once. Each gate returned PASS. Total acquisition cost was an estimated $0.00427860. The private 36-body verifier manifest is materialized and verified offline. Next decision: review the [exact Stage 2 digest, limits and receipt audit](verification.md#experiment-03-phase-b--stage-1-live-checkpoint). No verifier inference or quality grading has occurred.

## Experiment 03 Phase B · Stage 1 freeze awaiting approval

Built the isolated [staged experiment](../experiments/rag_safeguards/README.md) from accepted design revision `963cade`. The frozen first stage has 72 bodies, a $0.03754650 reserve and no live receipts. Mock-only tests cover the separate verifier materialization, dispatch and human-reviewed paired reporting. All 203 offline tests and both Ruff checks passed. Next decision: review the Stage 1 digest, settings and funding limit. Stage 2 requires a new manifest and separate approval after Stage 1. [Verification](verification.md)

## Experiment 03 · Phase A accepted, revised Phase B design awaiting review

From reviewed revision `9ad5dd3`, recorded Phase A acceptance as AI-assisted, owner-reviewed findings with the P4 judgment retained. Updated [seven scenarios and the staged approval procedure](experiment03_phase_b_design.md) and added a [deployment decision matrix and customer advisories](fde_deployment_playbook.md). Phase B remains design-only. Next decision is owner review of these revisions before implementation. [Verification](verification.md)

## Experiment 03 · Phase A draft graded and Phase B proposed

From verified checkpoint `1a60818`, validated the supplied AI-assisted worksheet and reproduced the [paired review report](experiment03_phase_a_review.md). The [36-question design](experiment03_phase_b_design.md) and [deployment playbook](fde_deployment_playbook.md) are ready for review. No Phase B implementation or acquisition. Next decisions are final approval of Phase A grades and approval or revision of Phase B before implementation. [Offline checks](verification.md)

## Experiment 03 · live acquisition complete, awaiting human review

The authorized run at `134ce15` completed all 48 requests. All 24 gate decisions matched their packet-relative keys. The private worksheet at `.verification/alder-review.json` contains 30 distinct question/answer entries with all judgment fields blank. Review a copy using the [review guide](../experiments/evidence_gate/review.md). Answer quality and adoption remain undecided. [Receipt audit and telemetry](verification.md#experiment-03--live-acquisition)

## Experiment 03 · offline implementation complete

Starting from approved design `a1d9445`, the [Alder Desk implementation and frozen plan](../experiments/evidence_gate/README.md) add paired replay, human review and a 48-request one-shot dispatcher. The runner now permits a stage to use a tighter output limit than the experiment maximum. The 512/256 stage limits and reserve of $0.02433150 reproduce offline. All 197 tests and both Ruff checks passed. Next decision is owner review of this exact freeze before any paid use. Human grading and observed outcomes remain pending.

## Experiment 03 · evidence-gate design awaiting review

Starting from the approved portfolio revision `95579b7`, the [design proposal](experiment03_design.md) defines a synthetic service-desk corpus, 24 keyed questions, paired replay, human grading and a provisional execution budget. Scope is documentation only. The next decision is whether to approve the dataset, gate behavior and adoption criterion for offline implementation. Live execution requires separate approval. [Verification](verification.md)

## Experiment 02 · evaluation closed and portfolio article ready

The owner accepted the findings at `0352f51`. The [final case study](portfolio/tool-catalog.md) and [website handoff](portfolio/tool-catalog-handoff.md) cover both runs, the C06 decision trace and the recommended write check. Three figures accompany the article. The earlier outline now directs readers to the completed work. Next step is portfolio editorial review. [Publication checks](verification.md)

## Experiment 02 V2 · live run complete and audited

The November 6 run at verified revision `19329ab` completed the approved 216 requests. All primary and control scenarios passed. C06 at 10B proposed an unsafe substitution. The [findings](experiment02_v2_live_findings.md) include the unsupported-reply review, paired outcomes, telemetry and architecture recommendation. Published the report and README link after 193 passing offline tests, both Ruff checks and frozen-manifest reproduction. Raw receipts remain local. Next step is owner review of the findings. Any further execution requires separate authorization.

## Experiment 02 V2 · offline implementation complete, awaiting live approval

The [V2 plan](../experiments/catalog_scope_v2/README.md) freezes all 216
requests, including the revised N03 and N05 and all six capability cases.
The 12 controls, 18 primary scenarios and six secondary scenarios have
separate reports. Final conservative reserve $0.33637350; proposed cap
$0.36. Starting revision `9cb5f7c`. All 193 offline tests and both Ruff
checks passed. Next decision is separate owner approval of this exact
manifest, model, request count and cap. No live execution has occurred.

## Experiment 02 V2 · scenario design awaiting owner review

The [design and complete 24-scenario review packet](experiment02_v2_design.md)
keeps the 12 original scenarios as a distinct control group. It proposes
18 common-task challenges and six optional capability cases, two paired
layouts per catalog. The proposed primary-plus-controls scope is 180
requests; including the optional block would bring the total to 216.
No V2 fixtures, implementation, live manifest or model calls were created.
The next decision is approval or revision of the actual prompts, keys,
catalog eligibility and scope. Live approval would be separate.
Starting verified revision: `268f41d`. [Design checks](verification.md)

## Experiment 02 · approved live run complete and closed

Executed the frozen digest once at approved revision `92a8ae98566a97c1646d18f9021c753c68b255f6`.
All 36 requests completed sequentially with zero retries or tool execution.
Each catalog scored 12/12. Estimated total API cost was $0.0024521.
The [findings](experiment02_live_findings.md) give the paired scenario
outcomes, observed latency, tokens, costs, recommendation and receipt hashes.
Historical development records and raw live receipts are preserved.
All 190 offline tests and both Ruff checks passed. Stop for owner review.
No further calls, retries or expansion are authorized.

## Experiment 02 · offline implementation complete, live approval pending

Added the `catalog_scope` experiment and its [frozen live proposal](../experiments/catalog_scope/README.md).
Twelve authored freight-desk scenarios (eight calls, four no-calls) are paired
across 5, 10 and 20 tools. One seeded order, 36 requests, 1,024 output tokens
each, $0.05571150 conservative reserve, $0.07 proposed estimated-spend cap.
The experiment uses the shared runner, summaries, immutable storage, budget
checks and Responses adapter. The exact-wire-path check uses local SDK mock
transport. No paid calls, external dataset, or new entity-matching work.

Starting verified revision: `54bbc8f`. The [case-study outline](portfolio/tool-catalog-outline.md)
leaves model findings open. Next decision is owner review of the canonical
manifest digest, model/settings, request limit and cap. Only after explicit
approval may the one-shot dispatcher be used. [Verification](verification.md)

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
