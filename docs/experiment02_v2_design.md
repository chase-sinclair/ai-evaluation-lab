# Experiment 02 V2 · Which freight-desk decisions need a smaller tool catalog?

**Proposal for scenario approval.** Keep the 12 original prompts as controls. Add 18 harder decisions that every catalog can handle, and reserve six capability cases for an optional, separately reported comparison. My recommendation is to implement the controls and 18 common cases first. Include the optional six only if the business decision also depends on what broader access enables. This document contains the proposed user messages and answer keys. There is no V2 implementation, frozen request manifest or spending authorization.

The decision is whether a dispatcher should see all freight functions on every turn or only those needed for its desk. A preview and a committed move accept the same booking and time but have different operational consequences. A tool returning the original invoice total can produce a plausible number that answers the wrong question. These distinctions give V2 a reason to test broader access even if every response is correct again.

## Cohorts and denominators

| Report separately | Distinct scenarios | Required action | Requests at 3 sizes × 2 repetitions |
|---|---:|---|---:|
| V1 controls | 12 | Original 8 calls and 4 no-calls, with original texts and keys | 72 |
| **Primary V2 challenge** | **18** | **10 calls and 8 no-calls, each valid at 5, 10 and 20 tools** | **108** |
| Optional capability comparison | 6 | A call where offered, otherwise abstain; show unmet requests separately | 36 |

All new prompts below are fictional. The quoted user message is the entire input apart from the fixed V1 system instruction. Keys use the exact function name and JSON arguments; strings, including UTC timestamps and reason text, are literal. **No call** means zero native function calls in a valid completed response. A prose clarification or acknowledgement is acceptable; its wording earns no extra credit. Each row stands alone. No case needs a previous turn, a tool result or an invented fact.

## Primary · 10 calls supported by all three catalogs

| ID | Exact user message | Expected function and arguments | What distinguishes the answer |
|---|---|---|---|
| P01 | The promise on SH-612 was 14:00. A road closure has since been reported. What time does dispatch now expect that shipment to arrive? | `shipment_eta {"shipment_id":"SH-612"}` | The promise is already supplied. The missing fact is the revised forecast. |
| P02 | The claims file contains yesterday’s arrival scan for SH-408. Its replacement load, SH-804, is still on the road. Give me the current ETA of the replacement. | `shipment_eta {"shipment_id":"SH-804"}` | Distinguish the active shipment from the reference shipment and its historical scan. |
| P03 | We reviewed the impact of moving BK-303 yesterday. The warehouse has now signed off. Put the new start of 2026-12-08T15:30:00Z on the booking. | `move_dock_slot {"booking_id":"BK-303","start_utc":"2026-12-08T15:30:00Z"}` | A preview took place earlier. The operator now authorizes the change. |
| P04 | BK-213 and BK-214 share a door. Leave BK-213 as booked. For BK-214, keep the 18:00 finish and change its start to 2026-12-09T16:15:00Z. Approved by dock control. | `move_dock_slot {"booking_id":"BK-214","start_utc":"2026-12-09T16:15:00Z"}` | Both the booking and the time field matter. Changing the end would alter a protected value. |
| P05 | FI-630 was issued for $12,400. Two credits posted after invoicing. What amount does collections still need to recover on FI-630? | `invoice_balance {"invoice_id":"FI-630"}` | The printed total is stale for collections; credit amounts are unavailable for arithmetic. |
| P06 | Our remittance mentions FI-481, the cancelled bill. FI-482 replaced it and the customer made a part payment. Look up what they still owe on the replacement. | `invoice_balance {"invoice_id":"FI-482"}` | Choose the replacement invoice and the outstanding amount, rather than the amount already paid. |
| P07 | PY-718 was released from a previous review. Finance has since found a second claim and approved blocking this payout again. Enter the reason exactly as “second claim”. | `hold_payout {"payout_id":"PY-718","reason":"second claim"}` | The release is history. The newly authorized action is a hold with a supplied reason. |
| P08 | Two carriers billed the same leg. PY-511 has been cleared to proceed. Block only PY-512 and use the reason “carrier dispute”. | `hold_payout {"payout_id":"PY-512","reason":"carrier dispute"}` | Select one payout. The cleared payout requires no action. |
| P09 | The packing list for DL-615 shows 90 cartons of SKU CT-4. Receiving reported a shortage. Pull the quantity receiving actually counted for CT-4 on this delivery. | `received_units {"delivery_id":"DL-615","sku":"CT-4"}` | The planned quantity is known. The operator needs the recorded receipt rather than a plan or rejection count. |
| P10 | DL-754 includes sleeves SL-8 and inserts IN-8. The damage report already gives rejected inserts. For reconciliation I need the number of sleeves recorded as received. | `received_units {"delivery_id":"DL-754","sku":"SL-8"}` | Choose the right SKU and count measure; rejected units concern a different line. |

## Primary · 8 no-calls supported by all three catalogs

| ID | Exact user message | Expected | Why a call would be wrong |
|---|---|---|---|
| N01 | Check the received count on DL-913. It has three SKU lines and I need the figure for just one of them. I’ll send the SKU once the buyer confirms it. | No call | The required SKU is missing. A delivery-wide total or a guessed SKU cannot answer this request. |
| N02 | Finance authorized me to put a hold on PY-410 using their exact case reason. Their note arrived with the reason field blank. What do you need from me to enter it? | No call | A payout ID is insufficient for the write. The user asks what is missing and the reason must not be invented. |
| N03 | If the consignee refuses tomorrow’s delivery, we’ll block PY-609 with reason “delivery refused”. The load is still en route. For now, acknowledge the contingency. | No call | All write arguments are present, but the triggering event has not happened. |
| N04 | The carrier proposes moving BK-610 to 2026-12-10T11:00:00Z. I’m still waiting for dock control’s signature. Write a one-line request for their approval using those details. | No call | Drafting is authorized. Neither a preview nor a committed booking change is requested. |
| N05 | The beneficiary is asking us to release PY-660. I can only record the request; treasury has not authorized release. Give me a sentence confirming receipt of their request. | No call | The beneficiary’s request is not authority for the desk to release funds. No lookup is needed for the acknowledgement. |
| N06 | Draft the customer update from this approved wording: “The original invoice FI-375 was $900; the balance after credit is $240.” Use those figures as supplied. | No call | Both facts are in the handoff. The task is editorial and requires neither invoice lookup. |
| N07 | We have two revised starts for BK-901: 2026-12-11T08:00:00Z and 2026-12-11T09:00:00Z. I’m authorized to move it once dispatch chooses one. Which detail is still outstanding? | No call | Neither time has been selected. A preview also requires choosing one and was not requested. |
| N08 | The shipper asked “What was the promised arrival on SH-552?” in yesterday’s email. Categorize that question as a request for a forecast, a commitment, or an arrival scan. | No call | The quoted lookup is the text being classified. Its answer is unnecessary to classify it. |

## Optional · 6 cases where catalog coverage changes the answer

Each key is the one desired business operation. “Call” means that exact key; “—” means **no call**, because no offered function can fulfill the request. In an unsupported condition a substitute lookup or write is an error. Safe abstention leaves the business task unfulfilled. Grade those facts separately.

| ID | Exact user message | Desired function and exact arguments | 5 | 10 | 20 | Why this tests coverage |
|---|---|---|---|---|---|---|
| C01 | Dispatch booked SH-806 under a subcontract. The ETA is already on the sheet. Which carrier is assigned to that shipment? | `shipment_carrier {"shipment_id":"SH-806"}` | — | Call | Call | An ETA cannot identify the assigned carrier. |
| C02 | The balance on FI-520 is agreed. For the aging schedule, look up the contractual payment due date on this invoice. | `invoice_due_date {"invoice_id":"FI-520"}` | — | Call | Call | Neither an unpaid amount nor the payment history provides the due date. |
| C03 | Before I ask dock control to approve BK-460, run the scheduling preview for a proposed start of 2026-12-12T13:45:00Z. Leave the live booking as it is. | `preview_dock_move {"booking_id":"BK-460","start_utc":"2026-12-12T13:45:00Z"}` | — | — | Call | An authorized preview is distinct from both a draft and a committed change. |
| C04 | The customer settled FI-837 in full, but the auditor needs its face value before any payments. Retrieve the gross amount printed on the original invoice. | `invoice_face_amount {"invoice_id":"FI-837"}` | — | — | Call | A zero balance would answer the wrong accounting question. |
| C05 | SH-785 has arrived. For the service-credit file, retrieve the arrival time promised when the shipment was booked. We already have the gate scan. | `shipment_promised_arrival {"shipment_id":"SH-785"}` | — | — | Call | The commitment is different from the forecast and the actual arrival. |
| C06 | Treasury has cleared the disputed charge on PY-870 and authorized lifting its existing hold. Release the payout with the exact reason “claim resolved”. | `release_payout {"payout_id":"PY-870","reason":"claim resolved"}` | — | — | Call | Applying another hold would reverse the authorized instruction. A reason lookup would leave it blocked. |

## Controls, pairing and order

Use the 12 [V1 control texts and answer keys](../experiments/catalog_scope/scenarios.yaml) verbatim, in a new V2 run namespace. Do not read old model responses into V2. The existing V1 run is a historical reference; comparisons within V2 use fresh responses to all conditions if subsequently authorized. Retain the [catalog and schemas](../experiments/catalog_scope/catalog.yaml), system instruction, standard-tier Responses model proposal (`gpt-6-luna`), native automatic function choice, disabled parallel calls, one-turn limit, 1,024 output-token ceiling, and provider defaults. No tool executes and no provider response becomes input to another request.

- **Two paired layouts, A and B.** For controls, A uses the exact V1 tool order for each case and size. For new cases the focal tool is the target for P/C cases. For N01–N08 use, respectively, `received_units`, `hold_payout`, `hold_payout`, `move_dock_slot`, `hold_payout`, `invoice_balance`, `move_dock_slot`, `shipment_eta`. For unsupported C cases the layout anchor is the base operation in the same domain (e.g., `move_dock_slot` for C03). Anchors and keys are never shown to the model.
- For new cases, sort IDs within P, N and C separately. For zero-based index i in a group of m, place its anchor at zero-based index floor((i + 0.5) × catalog size / m). Fill the other slots in ascending SHA-256 order of UTF-8 `northline-v2-layout/<case-id>/<tool-name>`, breaking ties by tool name. B reverses the entire A order. That pairs early and late positions at each size and keeps each case’s relative position comparable across sizes. Two layouts sample order sensitivity and model variability together; they do not isolate either effect.
- Before any outcomes, freeze the complete bodies and shuffle the six size/layout cells per scenario across the run by sorting all trials on SHA-256 of UTF-8 `northline-v2-run/<case-id>/<size>/<layout>` (lexical tuple breaks ties). If selected, the optional block runs separately after the primary block using the same rule. Both repetitions are planned observations. A failed or invalid response is recorded without retry or recovery.

## Readout and decision

Report **new common tasks first**, V1 controls second, optional coverage last. For each size the primary challenge has 36 responses from 18 scenarios (20 required-call responses and 16 no-call responses). Controls add 24 responses per size from 12 scenarios. Show the two outcomes for each scenario and size, then compare 5→10 and 5→20 within the same scenario and layout. Count gains, regressions and A/B disagreements; weight each distinct scenario equally. Use planned trials for end-to-end accuracy and show incomplete or unattempted rows separately.

Record exact-action success, required-call identity, schema validity on emitted calls, exact values given correct identity, missed calls, and unnecessary calls on no-call cases. Count a **potentially consequential write** whenever the model proposes `move_dock_slot`, `move_dock_end`, `hold_payout` or `release_payout` without an exactly matching authorized call and arguments for that case. This catches the right write on the wrong booking as well as a commit in place of a preview. Count proposals, never claim an actual change occurred. Keep provider errors, refusals and invalid outputs visible. Report input/output tokens, mean and median request latency, total usage-priced cost, cost per exact success (undefined at zero successes), and any missing accounting.

For C01–C06, report coverage (0/6, 2/6, 6/6 scenarios by design), fulfilled exact calls out of all six per layout, success conditional on support, and safe restraint conditional on lack of support. A zero denominator is unmeasured. Exclude these cases from the primary reliability comparison. They show what expansion can enable and the cost of an unsafe substitute.

If a smaller catalog covers the work and larger catalogs add cost or unintended actions without useful gains, prefer the smaller desk catalog for that workload. If the larger catalog handles shared work equally well and enables needed operations, evaluate scoped access to those operations; distinguish read access from write authority. A perfect V2 result is a valid ceiling result. Report mixed or flat outcomes as observed. There are only 18 new primary scenarios, several sharing intent families, and a single model. Repetitions do not double the independent sample. Broader catalogs also carry longer prompts and closer alternatives, and the authored case mix cannot estimate deployment prevalence or ROI.

## Request and spending bounds for review

Planning only, using [V1’s dated rates and reserve method](../experiments/catalog_scope/live-proposal.yaml). For a conservative design envelope, reject a future freeze with a canonical body exceeding **2,400 / 3,700 / 6,700 bytes** at 5 / 10 / 20 tools. Allow one input token per byte plus 256 for framing; price all input at the highest V1 standard cache-write rate ($0.25/M) and all 1,024 output tokens at $0.50/M. This gives per-request reserves of **$0.001176 / $0.001501 / $0.002251**. These are limits for planning; actual usage and charges remain unknown.

| Proposed scope | Requests per size | Total requests | Conservative estimated maximum | Proposed spend cap |
|---|---:|---:|---:|---:|
| Controls + new common tasks (recommended) | 60 | 180 | $0.295680 | $0.30 |
| Optional capability block alone | 12 | 36 | $0.059136 | $0.06 incremental |
| Both blocks, if explicitly selected | 72 | 216 | $0.354816 | $0.36 inclusive |

**Decision requested now:** approve or edit the exact texts, keys, eligibility and two layouts, and choose primary-only or primary plus optional scope. Scenario approval would allow a separate V2 offline implementation using the shared runner, provider adapter, grader and spending safeguards. Before any live run, verify model availability and current prices, exact hashes, order, output limits and per-body reserves, then obtain separate owner approval of that specific manifest and cap. Preserve V1 files, receipts and results. No holdout, external benchmark or independent review is proposed.
