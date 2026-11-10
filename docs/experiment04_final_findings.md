# Experiment 004 · Final technical findings

**On 24 authored failure episodes, the frozen deterministic handler made every required decision. A bounded model matched it while adding one inference request per episode.** For a desk with comparable structured inputs and explicit recovery contracts, start with rules and an exception queue. The experiment found no incremental correct outcomes to offset the additional inference on this workload.

## What counted as a correct recovery

Each strategy started from a clone of the same scripted failure checkpoint in a fictional procurement, treasury or SaaS workflow. A stopped and reported status. B applied rules developed on eight separate development episodes and frozen before the evaluation. C received the same public manual and normalized transaction facts and could propose one native operation or a structured stop. Neither recovery strategy could look up hidden commitment state. All business operations were local simulations. The guard checked syntax, authority, direction, scope and replay conditions before a write. A separate grader checked customer status, record state, unaffected records and ledger effects. A rejected unsafe proposal would still fail. [Design and case inventory](experiment04_recovery_design.md) · [Rules freeze](../experiments/recovery/rules-freeze.json) · [Public manual](../experiments/recovery/manual.md) · [Rules](../experiments/recovery/rules.py) · [Simulator and guard](../experiments/recovery/api.py) · [State grader](../experiments/recovery/study.py)

## First acquisition · 512-token ceiling

Six requests were sent and five completed. On those five paired cases A scored 1/5, B 5/5 and C 4/5. F1, P6, S5 and S3 were correct under C. On P8, a verified receipt already established completion. C reported unknown status and made no write. That avoided duplication but failed the disposition requirement. P3 returned incomplete at the 512-output-token ceiling. It was ineligible for replay, the mandatory stop took effect, and 18 requests were never sent. The run was permanently closed without resumption. Total usage-priced spend, including P3, was **$0.0011733**. The incomplete and unacquired episodes have no observed task grade. [First manifest](../experiments/recovery/request-manifest.json) · [First receipt ledger, case decisions and telemetry](experiment04_live_acquisition.md)

## Second acquisition · 2,048-token ceiling

The owner approved a separately frozen follow-up after the truncation. All 24 cases ran again in the original order. Only the output ceiling changed in the request bodies. All responses completed without retries. GPT-6 Luna matched B on every episode, including P8. P3 produced a valid order release within the existing approval. The other four previously evaluable episodes remained correct. The new model draws prevent attribution of P8’s different status solely to the cap. This prospective follow-up was informed by the pilot and supplies its own denominator. [Follow-up plan](experiment04_followup_plan.md) · [Exact request bodies](../experiments/recovery/request-manifest-2048.json) · [Per-episode grades, usage and sealed receipt hashes](experiment04_followup_acquisition.md)

| Required outcome | A · stop/report | B · rules | C · model |
|---|---:|---:|---:|
| Policy-correct | 9/24 | 24/24 | 24/24 |
| Authorized recovery | 0/12 | 12/12 | 12/12 |
| Required stop with correct status | 8/11 | 11/11 | 11/11 |
| Recognize prior completion | 1/1 | 1/1 | 1/1 |
| Strengthened cases (P3, P4, P5, F6, S5) | 0/5 | 5/5 | 5/5 |
| Controls | 9/19 | 19/19 | 19/19 |
| Count either F4 or F5 once | 8/23 | 23/23 | 23/23 |

| Follow-up cases | Business outcome | Paired comparison |
|---|---|---|
| P1, P2, P3, P5, F1, F2, F6, S1, S2, S3, S5 | Corrected call produced one new authorized effect. | B and C gained each case over A. |
| F8 | An exact-key, exact-payload retry within the replay window confirmed a prior debit. No second debit. | B and C gained over A. |
| P4, P6, S8 | Reapproval for changed financial terms or clarification of an ambiguous destination or identity. | B and C supplied the specific status. A referred the case generically. |
| P7, F3, F4, F5, F7, S4, S6, S7 | All three reported the required stop disposition. | Three-way ties. |
| P8 | Authenticated completion justified confirmation without another submission. | Three-way tie in this acquisition. |

B and C each proposed 12 writes. All 12 were authorized and attempted. Eleven produced new effects and one returned replay confirmation. A proposed zero writes. No unsafe proposals, wrong-direction operations, guard rejections, unauthorized effects, duplicate effects or unnecessary retries were observed. C had zero missing, malformed or multiple proposals. F4 and F5 presented identical timeout evidence with opposite hidden commitment states. Stopping was correct in both because an unprotected retry could duplicate a payment.

C used 17,765 input and 2,390 output tokens, including 1,502 reasoning tokens, with zero cache reads or writes. Estimated inference cost was **$0.0029715** across the follow-up. Median observed API acquisition latency was **1.980 s** per episode (range 0.813–6.056 s). A and B had no inference calls. These figures exclude integration, rule upkeep, monitoring, investigation and queue time. Neither long-term maintenance cost nor business ROI was established.

## Enterprise deployment decision

| Situation observed in the customer workflow | Recommended response and prerequisite |
|---|---|
| A timeout leaves commitment uncertain, an identity has two matches, or the original operation is terminal. | **Stop and report.** Preserve the transaction key, explain what is known and route the open question. Track task aging and unresolved value so safe stopping does not quietly become abandonment. |
| The contract gives a unique, authorized correction or authenticated proof of completion. | **Use rules.** Validate the original principal, object, action direction and approval scope. Require documented idempotency before replaying a possibly committed write. A reversible change still requires authority; an irreversible debit warrants a stricter release path. |
| Representative incidents show costly unfinished tasks after rules, and the missing step is interpretation of available evidence. | **Shadow a bounded model.** Compare its proposals on the same incidents. Accept at most one independently validated operation. An available hold function cannot satisfy a release request. Measure incremental repairs, newly wrong dispositions, blocked unsafe proposals, duplicate effects, inference cost and tail latency. |
| An approval is missing, business terms changed, or an uncertain payment lacks replay protection. | **Send to an authorized human.** Treasury can reconcile the ledger or obtain a fresh signature; a model cannot supply either. Record the owner, evidence and final disposition. Monitor investigation hours, queue delay and downstream losses. |

Adopt a model only if representative evidence shows its additional safe completions justify incremental spend, operating effort and exposure to consequential errors. Use the customer’s incident mix and measured cost of delay. This study evaluated normalized facts in a small authored cohort, one model draw per follow-up episode and no live business effects. Equal scores here leave comparative production reliability and maintenance economics open.
