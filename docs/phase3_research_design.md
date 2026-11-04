# Phase 3 proposal: business function selection as tool catalogs expand

November 4, 2026 — **design for owner review; no new experiment implemented or run.**

Recommend a bounded, single-call BFCL-derived study at **5, 15 and 30 tools**.
Keep the hypothesis: expanding choice sets may reduce full-call correctness.
Measure function selection separately to explain failures. Accept null and ceiling
results; do not change cases, tools or the hypothesis to obtain an accuracy drop.
This tests selecting business functions from schemas, not executing enterprise
workflows or producing an official BFCL score.

## Evidence and dataset feasibility

| Source inspected | Labels and relevant evidence | Decision |
|---|---|---|
| BFCL `multiple`, pinned Gorilla `f7cf7359b7ac615a0b294831c5ba2bc95ee4a000` | Existing small cache contains 200 input rows and paired answer keys. Reinspected `multiple_56`: average closing price competes with trading volume and revenue, with similar company/days/source arguments. `multiple_81`: concert versus festival booking; requested artist/backstage option distinguishes the target. | Preferred basis; objective single-function keys and existing compatibility work. Neither example proves availability of 30 appropriate tools or enough independent cases. |
| BFCL `live_multiple` at the same revision | Prior bounded inspection found realistic food/drink edits, but nested defaults and ambiguous schema/description mappings; their keys have not been audited. | Candidate expansion pool only after paired input/key audit. Not yet eligible. |
| API-Bank, Alibaba DAMO-ConvAI `faf754671f5b850e1b4d1ff870db37a6a2480df6` | Published labeled dialogues and callable simulated APIs. Inspected meeting dialogue, `AddMeeting` and `AddAgenda` implementations. The meeting label follows authentication; attendee values are a stringified list in `param_dict` but a list in the result. The checker also uses topic word overlap. | Useful enterprise follow-up; do not casually turn dialogue labels into unique stateless function gold. Requires state/context and representation reconciliation. |
| Sierra current τ-bench 2.0, tau2-bench `033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f` | Official evaluation documentation explicitly says reference actions are usually one valid trajectory, not uniquely required tools. Its airline example task `1` can pass by refusing without the listed read calls. | Strong workflow relevance, unsuitable as direct single-choice labels. Would require a separate stateful design and potentially paid simulators/judges. Defer. |

BFCL evidence: pinned [multiple inputs](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_multiple.json),
[multiple keys](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/possible_answer/BFCL_v4_multiple.json),
[live inputs](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_live_multiple.json),
and [data README/license declaration](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/README.md).
BFCL data is declared Apache-2.0. Preserve original questions, schemas, identifiers,
answer alternatives, revision, hashes, notices and conversion provenance.

API-Bank sources: pinned [README](https://github.com/AlibabaResearch/DAMO-ConvAI/blob/faf754671f5b850e1b4d1ff870db37a6a2480df6/api-bank/README.md),
[meeting dialogue](https://github.com/AlibabaResearch/DAMO-ConvAI/blob/faf754671f5b850e1b4d1ff870db37a6a2480df6/api-bank/lv1-lv2-samples/level-1-given-desc/AddMeeting-level-1-1.jsonl),
[meeting implementation/checker](https://github.com/AlibabaResearch/DAMO-ConvAI/blob/faf754671f5b850e1b4d1ff870db37a6a2480df6/api-bank/apis/add_meeting.py),
[agenda implementation](https://github.com/AlibabaResearch/DAMO-ConvAI/blob/faf754671f5b850e1b4d1ff870db37a6a2480df6/api-bank/apis/add_agenda.py),
and [Apache-2.0 license](https://github.com/AlibabaResearch/DAMO-ConvAI/blob/faf754671f5b850e1b4d1ff870db37a6a2480df6/api-bank/LICENSE).
Only this repository distribution was checked; do not assume every linked hosted
dataset has identical terms. No dialogue content is imported or sent to a provider.

Sierra sources: pinned [current README](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/README.md),
[evaluation rules and worked labeled example](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/docs/evaluation.md),
and [MIT license](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/LICENSE).
The [older repository](https://github.com/sierra-research/tau-bench/blob/59a200c6d575d595120f1cb70fea53cef0632f6b/README.md)
warns its tasks are outdated. Current docs supersede its pointer to τ³-bench naming.
No benchmark stack, archive, simulator or new dataset was installed/downloaded.

## Exact eligibility and selection rules proposed

1. Start with pinned `multiple`; consider `live_multiple` and native `irrelevance` /
   `live_irrelevance` only if their source keys/checker paths pass a bounded audit.
   Use business analytics, bookings/orders, account/record operations and workplace
   scheduling. Exclude pure math, weather trivia, coding and open-ended retrieval.
2. Require one objectively necessary function or an explicit no-call label; retain
   all source alternatives. Every required value must be present in the user
   context or supplied by an unambiguous documented default. Exclude missing IDs,
   unclear transaction authorization, incompatible schema/key pairs, hidden state,
   multiple necessary calls, unspecified timezone/date, and unsupported grading
   types. Never repair ambiguous gold by guessing. Log each exclusion and reason.
3. Retain the complete native catalog, with at most five tools. Each positive
   needs at least two plausible domain neighbors with distinct capabilities.
   Tools added later must come from the pinned source catalog, with unchanged
   names, descriptions and schemas, except documented collision-free wire mapping.
   No generic lookup clones or invented negative-capability disclaimers.
4. Two reviewers independently compare the question with **every tool in the
   30-tool set**, without model outputs. For each distractor record the capability
   boundary that prevents it satisfying the entire request. Examples: trading
   volume cannot provide a closing-price average; a festival booking cannot
   satisfy a specified concert artist/backstage request. A gold label alone does
   not establish uniqueness. Reject disagreement or overlapping capabilities.
5. No-call cases must have no valid tool even in the largest set. Prefer upstream
   business-domain irrelevance labels; do not create negatives by hiding the
   positive target. Exclude underspecified requests when a partial valid call
   would be defensible. Availability of 36 suitable negatives across splits is
   **unverified** and is a feasibility gate, not an assumed dataset property.
6. Cluster near duplicates by normalized intent/template, target capability and
   shared function schema; manually merge paraphrase families. Use at most one
   case per cluster for the planned independent-case analysis. All previously
   inspected families stay development-only: the frozen simple/irrelevance set,
   `multiple_46/55/56/76/81/93`, and the first five previously inspected live rows.
   Cases 76 and 93 remain excluded for ambiguity; exposure does not make them valid.
7. Before prompt tuning or paid execution, a data custodian freezes eligible
   clusters and the exclusion ledger. Within business-domain and call/no-call
   strata, sort unseen cluster IDs by SHA-256 of
   `phase3-v1|20261104|source_revision|cluster_id`. Allocate development first,
   then held-out, with no cluster sharing. Assign the same cluster split to tools
   derived from that family; no held-out cases become development demonstrations.
   Require at least three business domains; cap any domain at 50% of a split.
   If quotas cannot be filled, stop and report counts for a revised owner-approved
   design; never relax eligibility or sample until a desired result appears.

Held-out means unseen by the prompt/implementation developer and unused in model
tuning, not unknown to the label auditors or guaranteed absent from pretraining.
Freeze the held-out IDs/hash with the custodian; audit gold independently of model
results, then reveal it only for the locked evaluation. No held-out set is selected
or implemented in this milestone.

## Treatment construction and controls

Only tool count is manipulated: 5/15/30, nested sets per case, identical query,
target definition, model, output ceiling, instruction and inference settings.
All native tools must fit the smallest set and remain available unchanged.

Reviewers classify distractors before execution as near (same business object and
related operation) or adjacent (same workflow/domain, distinct operation/object).
For positives, use near/adjacent counts **2/2, 7/7, 14/15**; for no-call cases use
**3/2, 8/7, 15/15**. These are construction quotas, not another experimental factor.
Pick within strata by the fixed hash ordering. Exclude a case if its native set
cannot satisfy the quotas or 30 distinct non-substitutable tools are unavailable.
Increasing the absolute number of plausible competitors is part of the treatment.

Before seeing responses, match added batches to the initial catalog: median
description byte length and property count within 20%, required/optional counts
within one, and comparable enum/nesting proportions. Preserve each original
definition across treatments. Reject unmatchable catalogs; do not rewrite a
distractor to make a target stand out or truncate prompts to fit budgets.

Hash-rank the full catalog once per case and restrict that ordering to each nested
set. This preserves pairwise order while randomizing target position. Record exact
index and normalized position, names/order/schema bytes, complete request/prompt
hashes and target-definition hash. Check position balance before freezing; report
residual imbalance without rerolling after results. Balance the six possible
condition execution orders across case blocks (two blocks each in a 12-case pilot).
Shuffle blocks with the frozen seed; keep calls sequential and independent with
no conversation history or tool execution.

Larger catalogs necessarily add context. This study estimates the practical effect
of adding comparable tools **including their context**, not a pure count effect
at constant token length. Do not add padding, which would create a different
intervention. Record input tokens and schema bytes; treat latency/cost associations
as descriptive, with cache state and service load as additional limitations.

## Samples, outcomes and analysis

| Stage | Independent cases | Calls | Purpose |
|---|---:|---:|---|
| Development pool | 24: 18 call + 6 no-call | None automatically | Schema/grader/prompt preparation; exposed families only here |
| Initial pilot | 12 of those: 9 call + 3 no-call | 36 = 12 × 3 × 1 | Integration, accounting, error review; descriptive only |
| Reserved development | Remaining 12 | No calls approved | Fix validation defects without touching held-out cases |
| Proposed held-out | 120: 90 call + 30 no-call | 360 = 120 × 3 × 1 | Locked paired assessment after separate approval |

These are target quotas, **not verified counts of suitable source cases**. Existing
18-case mathematical development data does not satisfy them. The first pilot is
the hash-first eligible 9/3 within development, not cases chosen from performance.
No repeats initially; repeated calls would not create independent observations.

Strict official-compatible BFCL full-call correctness remains the primary benchmark
metric. Predeclare the primary contrast as **30 minus 5 tools** on case-paired full
call success. Report tool-selection accuracy as a distinct explanatory endpoint
for the business question, plus schema validity, exact argument failures, wrong
tool, missed/unnecessary calls, extra calls, incomplete output, provider errors,
latency, token partitions, cost and cost per correct case. Report both call/no-call
strata and fixed 75/25 weighted overall rates. Diagnostic measured-only means must
not be substituted for end-to-end accuracy.

Use all planned cases as the end-to-end denominator. Provider/incomplete/grader
failures count as unsuccessful and retain separate categories; unattempted cases
after an abort are explicitly missing, with bounds and no completed-study claim.
For matched completed cases, report discordant pairs and per-case deltas, with a
95% case-bootstrap interval (10,000 resamples, frozen seed) for the primary contrast.
If residual clustering remains, resample clusters and report the effective count.
15-tool comparisons and diagnostic contrasts are secondary, with no selective
significance claims. At 120 independent pairs, worst-case normal-approximation
half-width for a difference is about 18 percentage points (1.96/sqrt(120)); this
is not a power guarantee for small effects. The 12-case pilot supports no meaningful
significance claim. More precision needs a separately justified larger sample.

## Model, cost assumptions and abort rules

Propose `gpt-6-luna`, Responses API, standard tier, 4,096 maximum output tokens,
one response per request, sequential, zero retries, no hosted tools or execution.
Keep optional inference settings unset and record returned settings/model; do not
assume deterministic outputs. Freeze the final payload/model/settings before any
calls. Current [model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)
and [pricing](https://developers.openai.com/api/docs/pricing) were reviewed November 4.
Rates per million tokens: ordinary input $0.10, cached read $0.01, 30-minute write
$0.125, 12-hour write $0.25, output $0.50. The write rates are supported by the
[cache documentation](https://developers.openai.com/api/docs/guides/prompt-caching).

Illustrative planning assumptions, **not measured usage**: average 6,000 input and
200 output tokens, all input conservatively treated as 30-minute writes. The
36-call pilot would cost about **$0.0306** (12-hour-write scenario **$0.0576**).
No cache read discount is needed for these estimates.

For an approval reserve, require each serialized request to be at most 20,000
UTF-8 bytes plus the existing 256-token framing reserve. At the highest reviewed
write rate and full output ceiling, reserve
`36 × (20,256 × $0.25 + 4,096 × $0.50) / 1,000,000 = $0.256032`.
Propose a **$0.35 / 36-request cap** after actual rendered preflight. The analogous
360-request held-out reserve is $2.56032, with a separately proposed $3 cap.
Byte-based token estimation is deliberately conservative, not guaranteed billing.
If actual frozen requests exceed the byte limit, return for protocol review;
do not shorten schemas or drop difficult cases to meet it.

Abort on access/model/schema rejection, safety/hash drift, missing or inconsistent
usage, unknown lifetime pricing, service-tier mismatch, insufficient remaining
reserve, or incomplete output. Keep the attempted record; no retries, substitution
or automatic resume. Ordinary incorrect answers are outcomes, not abort reasons.
The current runner stops on unknown cost/provider errors; a future protocol-specific
wrapper must also enforce incomplete-output abort and exact matrix authorization.
The smoke did not report write-lifetime detail, so **accounting readiness remains a
live-protocol blocker**: approval must explicitly resolve how missing detail is
handled without fabricating actual cost. No automatic 30-minute inference is proposed.

## Approval gates and risks

Approve this design before any subset implementation. Then authorize bounded
source/key inspection and redistribution with notices; appoint independent label
reviewers/custodian; establish sufficient eligible clusters and distractor pools;
freeze splits, compatibility evidence, payload matrix and exposure ledger. Require
an offline leak test proving that poisoning keys/provenance cannot alter requests.
Any needed multiple-function/schema support belongs in the existing experiment
module; the shared engine stays reusable. These changes are deferred, not implemented.

After that preparation, separately approve the exact model/settings, complete dated
pricing, accounting policy, immutable matrix, request/spend caps and abort behavior.
Review the initial pilot before deciding on held-out execution. The 54-request old
matrix and original smoke are not authorized for rerun by this proposal.

Main risks: unverified eligibility yield, public-data contamination, remaining label
ambiguity, narrow synthetic business coverage, dependent task families, context and
position effects, alias drift, cache/service latency effects, limited precision,
and incomplete cost telemetry. The source examples motivate a better selection
study; they establish neither enterprise reliability nor any new model result.
