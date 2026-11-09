# Alder Desk Phase A · AI-assisted owner-reviewed findings

**The gate classified 24/24 packets correctly and prevented zero observed unsupported answers.** Standard RAG already abstained appropriately on every question the gate blocked. On the 18 passed questions, both workflows returned the identical generated answer.

| Outcome on 24 paired questions | Standard RAG | Gated replay |
|---|---:|---:|
| Useful and fully correct decisions | 23/24 | 23/24 |
| Answers with an unsupported assertion | 1/24 | 1/24 |
| Supported claims | 47/48 | 40/41 |
| Correct claim-to-passage citation links | 47/48 | 40/41 |
| Supported claims with an entailing citation | 47/47 | 40/40 |
| Appropriate whole-answer abstentions on U | 6/6 | 6/6 |
| Over-refusals | 0 | 0 |
| Estimated operating cost | $0.0016779 | $0.0021694 |
| Median latency | 1.833 s observed | 2.750 s modeled serial |

A, P, M and U useful-correct counts were 6/6, 5/6, 6/6 and 6/6 respectively in both arms. All six partial answers handled the known fact and the gap. P4 nevertheless said the **depot** issues the collection code; D11 assigns issuance to the **desk**. The owner accepted treating that minor additional claim as unsupported and the answer as short of fully correct. Both arms shared it. On ambiguous cases both gave five focused clarifications and one conditional explanation.

The six fixed referrals replaced six already appropriate abstentions, removing seven supported claims. They prevented no error and introduced none. No useful answer or clarification was suppressed. The gate added $0.0004915 across 24 queries and 0.969 s median paired delay. Gated serial latency sums separately measured gate and generator timings on PASS and uses the gate timing alone on BLOCK. All-stage acquisition cost was $0.0026082. [Execution evidence](verification.md#experiment-03--live-acquisition)

**Recommendation for this workload:** Standard RAG was sufficient in the pilot. Retain it as the default for this service desk: a second call on every question bought no observed reduction in unsupported answers. This judgment is bounded by a small synthetic set, a single generation per question and an owner-reviewed AI-assisted assessment. It does not establish equivalence on real traffic.

**Provenance.** Validated all 30 deduplicated worksheet keys, original questions, answers, evidence packets, rubrics and deterministic fields against the blank worksheet and replay of frozen receipts. All judgments conform to the review schema, claim spans occur in the respective replies and cited passage IDs occur in the packets. Ran the existing offline reviewed-report workflow on a separate byte-identical private copy. Draft and copy SHA-256: `694c6262638f9ae8420317b22b85f4a8715735e853abbb1a98a852bf39528905`. The original blank worksheet and raw receipts remain unchanged. Validation checks provenance and schema; the owner accepted the **AI-assisted findings**, including the conservative P4 judgment. This review did not independently human-adjudicate the 30 entries.
