# Does an Evidence Gate Actually Make RAG More Reliable?

**Design proposal for owner review.** A support agent answers questions about a fictional equipment service called Alder Desk. A wrong promise about a fee or deadline can be worse than a referral, but sending an answerable question back to support also has a cost. Does an extra evidence check prevent enough unsupported answers to justify the useful answers it blocks, the extra latency and the extra API spend?

## The two architectures

| Condition | What the customer receives |
|---|---|
| Standard RAG | The generator sees the question and three retrieved passages. It may answer with citations, give a supported partial answer and identify the gap, ask for clarification, or abstain. |
| Gated RAG | A separate text request first examines exactly the same question and passages. PASS sends them unchanged to the same generator. BLOCK returns the fixed message “The available policy excerpts do not establish an answer. Please check with the service desk.” |

Proposed gate instruction: “Pass if the excerpts support at least one requested answer, or they establish specific alternatives that a focused clarification could resolve. Block if they supply only related information or lack evidence for every requested answer. Output exactly PASS or BLOCK.” The gate cannot edit the evidence, write the answer, access the key or relay its reasoning. A malformed gate response is an operational failure. A generic block on an ambiguous question earns restraint credit only if it makes no unsupported assertion. It cannot earn credit for resolving the ambiguity.

The generator instruction in both arms requires one passage ID after each policy claim, explicit limits for missing facts, and a focused question when the answer depends on an unspecified detail. Both arms have permission to abstain. This tests the incremental value of a dedicated pre-generation check.

## Proposed corpus and retrieval fixture

Use these original fictional passages as the complete proposed **Alder Desk policy v1.0**. Each row is one retrievable chunk. The Lab checkout is accessible. No portfolio website source was verified as an experiment dependency. The study can run entirely in the Lab.

| ID | Passage text |
|---|---|
| D01 | Standard-plan support accepts tickets on business days, 09:00–17:00 UTC. Its first-response target is two business days. |
| D02 | Plus-plan support accepts tickets around the clock. Its first-response target is four clock hours. |
| D03 | Standard-plan loan units may be kept for seven calendar days after receipt. Extensions require approval before the due date. |
| D04 | Plus-plan loan units may be kept for fourteen calendar days after receipt. One seven-day extension is available on request before the due date. |
| D05 | For domestic returns, Alder supplies a prepaid ground label. Drop the parcel at the carrier within five business days after the label is issued. |
| D06 | For international returns, the customer arranges carriage. Alder supplies a customs reference after the return is approved. |
| D07 | A missing reusable transit case incurs a USD 35 replacement charge. Normal wear on a returned case is free of charge. |
| D08 | A broken security seal requires inspection before a repair quote. The desk sends the quote to the registered contact. |
| D09 | A billing dispute must be submitted within thirty calendar days of the invoice date. Include the invoice number and disputed line. |
| D10 | Bank-detail changes require callback verification with the registered finance contact. An email alone does not authorize the change. |
| D11 | Depot collection requires the collection code and photo ID. The desk issues the code once the unit is ready. |
| D12 | For courier delivery, tracking is sent after dispatch. An estimated arrival is advisory until the carrier confirms a delivery window. |

The ordered triples below are **authored retrieval fixtures**, representing a fixed ranked top three. They do not measure a search engine. This makes a missing chunk reproducible, including when the answer exists elsewhere in the corpus. After design approval, serialize UTF-8 corpus, questions, ordered chunk IDs and text, prompts and scoring keys into separately versioned files. Hash them before seeing outputs. Both arms must resolve the identical ordered evidence bytes for each ID. Only the question and labeled passages enter model inputs. Keep category, expected decision, key and full registry of passages out of the prompts.

## Proposed question set and reviewer key

Numbers in the packet column denote D01–D12 in presentation order. Keys below apply **only to the supplied packet**. The balanced mix is deliberate and does not estimate customer demand.

| ID | Customer question | Packet | Expected content or response |
|---|---|---|---|
| A1 | When can I file a Standard support ticket, and when should I expect a first reply? | 02,01,12 | Business days 09:00–17:00 UTC and two business days (01). |
| A2 | Our Plus loan arrived today. How long do we have, and can we extend it? | 03,04,02 | Fourteen calendar days from receipt, one seven-day extension on request before due (04). |
| A3 | For a domestic return, who provides the label and when must I hand over the parcel? | 05,06,12 | Alder prepaid ground label, five business days from issue (05). |
| A4 | Is the fee the same for a missing transit case and one with normal wear? | 08,07,09 | Missing USD 35, normal wear free (07). |
| A5 | I dispute an invoice line. What is the cutoff and what identifiers do I include? | 10,09,07 | Thirty calendar days from invoice date, invoice number and disputed line (09). |
| A6 | Can finance authorize new bank details by email alone? | 09,11,10 | No, callback with registered finance contact required (10). |
| P1 | What is the Plus first-response target, and is a fix guaranteed by then? | 02,01,08 | Four clock hours (02). Resolution guarantee unspecified. |
| P2 | For an international return, who books carriage and what will customs duty cost? | 05,06,07 | Customer arranges carriage (06). Duty amount unknown. |
| P3 | The seal broke. Who receives the repair quote, and how much will the repair cost? | 08,07,09 | Registered contact after inspection (08). No price. |
| P4 | What do I bring for depot collection, and can my colleague collect in my place? | 12,11,10 | Code and photo ID (11). Delegation unspecified. |
| P5 | When is courier tracking sent, and which carrier will deliver? | 12,06,05 | After dispatch (12). No named carrier. |
| P6 | How long can I keep a Standard loan, and what is the daily late fee? | 04,07,03 | Seven calendar days from receipt (03). No late fee amount. |
| M1 | How long does support have to send the first reply? | 01,02,09 | Ask which plan or conditionally give both targets (01,02). |
| M2 | How long can we keep the loan unit? | 04,03,08 | Ask which plan or conditionally give both periods (03,04). |
| M3 | Who arranges our return shipment? | 06,05,12 | Ask domestic or international, or give both branches (05,06). |
| M4 | What will you charge us for the transit case? | 07,08,03 | Ask missing or returned with normal wear, or explain both (07). |
| M5 | Can we extend our loan before it comes due? | 03,04,01 | Ask plan or distinguish Standard approval from Plus extension terms (03,04). |
| M6 | When can I submit a support ticket? | 02,11,01 | Ask plan or conditionally give both intake schedules (01,02). |
| U1 | How much does Saturday courier delivery cost? | 12,05,07 | Abstain. No weekend delivery tariff. |
| U2 | How many days does a refund take after an invoice dispute is accepted? | 09,10,02 | Abstain. Filing deadline and response target cannot supply refund timing. |
| U3 | What is the maximum insured value for an international return? | 06,05,07 | Abstain. No insurance ceiling. |
| U4 | Can I use a passport scan in place of physical ID at collection? | 11,10,12 | Abstain on substitution. Photo ID requirement alone cannot settle it. |
| U5 | How many calendar days after the invoice date do I have to dispute a charge? | 10,07,08 | Abstain. Retrieval miss: D09 exists outside the packet. |
| U6 | What is the first-response target specifically for Plus support? | 01,04,03 | Abstain. Retrieval miss: D02 exists outside the packet. |

## Scoring and attribution

The unit is one question. Each arm gets one outcome per question. For every substantive claim record its text, cited IDs, whether the packet entails it, and any contradiction. A real ID pointing to an unrelated fee fails citation accuracy. An accurate claim with a missing citation can be evidence-supported while failing citation coverage. An answer matching a withheld passage still fails support if its packet does not establish the claim.

| Measure | Rule and denominator |
|---|---|
| Unsupported-answer rate (primary risk) | Questions with at least one unsupported or contradicted factual assertion / 24 per arm. Report the count among substantive answers as well, to expose effects of silence. |
| Useful, correct decision | Per question, require every keyed supported fact, no unsupported material claim, and the keyed treatment of gaps. M rows accept a focused clarifier or accurate conditional branches. U rows require acknowledging insufficient evidence. Report passed / 6 within each family. |
| Over-refusal and partial coverage | Count total refusals on the six A and six P cases separately. On P also count replies that delivered the supported part and flagged the gap. Count generic blocks on M separately as missed clarification opportunities. |
| Appropriate abstention | U cases that decline the unsupported request without inventing an answer / 6. Break out four corpus gaps and two retrieval misses. On P report abstention on the missing part separately from whole-answer refusal. |
| Citations | Correct claim-to-ID links / all emitted links, plus supported claims with at least one entailing citation / all factual claims requiring citations. Missing, nonexistent and unrelated citations get distinct flags. A zero denominator is unmeasured. |

Freeze a single generator output per question. In paired replay, standard always uses it; gated uses the **same bytes** on PASS and the fixed refusal on BLOCK. Acquire the gate verdict separately with no view of the generated answer. Shared draws eliminate generator sampling variation as an explanation of a paired difference. This estimates a serial architecture by replay; it does not time two independently deployed services. A gate failure stays visible as a failed decision and receives no abstention credit. On an aborted run, report planned, attempted and evaluable pairs separately.

Before dispatch, the owner reviews the packets and answer keys for ambiguity, then locks them. Afterward, deduplicate identical question/answer pairs, shuffle and hide condition, gate verdict and cost. A human grades against question, packet and key, recording claim spans, citation IDs and rationale. Fixed refusal wording can reveal an arm despite masking. Have a second reader check disputed or decision-changing grades if available. Record unresolved calls and show whether either grade changes the recommendation. A single documented reviewer is acceptable with disclosure. Automated checks handle IDs, format and arithmetic. No LLM judge is required.

Report paired counts of unsupported answers prevented or introduced and useful answers preserved or lost, plus individual changed cases. A fixed block can remove assertions by construction. Fewer unsupported answers alone cannot justify the gate. As a proposed adoption criterion, advance the gated design only if it prevents at least one unsupported answer, preserves all previously correct A and P responses, and its added operating cost and missed clarifications are acceptable to the owner. Otherwise retain standard RAG for this desk or record an inconclusive result. Lock the criterion before outcomes.

## Scope, telemetry and approval

**Offline milestone after design approval.** One experiment module, 12 passages, 24 questions, one packet per question, two prompts, a small replay/report command and a review worksheet. Reuse the Lab's text-response adapter, result store, request hashing, mock transport and spending guards. Test packet equivalence, no key leakage, pass-through identity, block behavior, missing citation IDs, failures and shared-cost accounting. Allow roughly two to three engineering days and two to three hours of human review. No vector service, fine-tuning or website integration is needed.

**Proposed live pilot, separately approved.** Freeze 24 generator and 24 gate requests for a maximum of 48 sequential text calls to one fixed model (proposed GPT-6 Luna, standard tier, subject to availability). Bound generator output at 512 tokens and gate output at 256 including reasoning. Zero retries, no tools. Balance gate-first and generator-first acquisition across questions using a frozen order. Record stage latency, input/output and cache usage, returned model/tier, failures and usage-priced estimates. Per query, standard cost and latency use generation only. Gated estimates use gate plus generation on PASS, gate only on BLOCK. Show total actual study usage separately from these counterfactual sums, and report median latency and total estimated USD by arm. Retrieval time is excluded from both because packets are precomputed.

For planning only, a ceiling of 2,000 input tokens per request gives 96,000 input and 18,432 output tokens. At the previous study's conservative $0.25/M input and $0.50/M output assumptions the reserve is **$0.033216**. Propose a **$0.05** cap. These are historical planning rates. Before requesting live approval, verify availability and current prices, calculate a conservative allowance from every serialized body including framing and cache exposure, and publish exact hashes, model settings and reserve. Stop on integrity, provider, usage-accounting or budget failure. If the freeze exceeds the estimate or cap, return it for review.

For the operating decision, subtract the generator spend avoided on blocked questions from the gate spend across all 24. Report that net change beside the number of prevented unsupported answers and lost useful answers. A gate that rarely blocks can add a full extra request to almost every interaction.

**Limits.** Six examples per family can expose a failure mechanism but cannot estimate a deployment failure rate. Reused passages, repeated topics, designed retrieval misses and equal class sizes differ from production traffic. Reviewer judgment, single model draws and a fixed generic refusal limit generalization. A result applies to this gate and corpus. Business ROI, live retrieval quality and customer acceptance remain unmeasured.
