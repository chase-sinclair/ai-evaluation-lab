# Which RAG reliability safeguards were worth their cost? · accepted technical findings

**Decision for the tested workloads:** keep grounded standard RAG as the reference architecture. It allowed citations, clarification and abstention. Neither additional check prevented an observed unsupported answer under the submitted Phase B grades. Post-generation verification withheld four appropriate original replies. These results guide a local architecture decision; customer adoption requires evidence from representative traffic.

## Phase A · support policy lookup

On 24 fictional Alder Desk queries the pre-gate classified all packets as expected. Standard RAG already abstained on the six cases it blocked. Both arms scored 23/24, sharing P4’s minor unsupported attribution of code issuance to the depot. The gate added $0.0004915 to the standard workload estimate of $0.0016779 and 0.969 s median paired modeled delay. These findings were AI-assisted and owner-reviewed. Phase A had no post-generation verifier. [Accepted Phase A report](experiment03_phase_a_review.md)

## Phase B · 36 enterprise questions

A generated once per question. B checked the packet before forwarding the same reply or a fixed referral. C checked the actual reply against the packet, then forwarded the reply unchanged or substituted that referral. The gate passed all 36. The verifier passed 32 and blocked four. Every architecture was evaluable on all 36 paired units. The 108 acquired stage responses and 108 derived arm outcomes yield 40 distinct question/reply pairs for review. The owner accepted the AI-assisted grades and documented sensitivities. There was no independent human adjudication.

| Workload | A · standard | B · pre-gate | C · post-check |
|---|---:|---:|---:|
| Routine | 12/12 | 12/12 | 11/12 |
| Incomplete or ambiguous evidence | 11/12 | 11/12 | 9/12 |
| Conflict, outdated or misleading evidence | 9/12 | 9/12 | 8/12 |
| **Fully correct** | **32/36** | **32/36** | **28/36** |
| Unsupported annotated claims | 0/91 | 0/91 | 0/83 |
| Correct citation links | 81/83 | 81/83 | 74/76 |
| Claims with no citation link | 12 | 12 | 11 |
| Correct authority assessments where applicable | 36/36 | 36/36 | 34/34 |

Unsupported *answers* were 0/36 in each arm under the supplied reading. Citation links count annotated claim-to-ID relationships. Uncited spans include statements that the packet lacks a fact. The two invalid references on I04 appear in every arm. C's lower authority denominator reflects withheld content. Four safe but incomplete shared replies (I11, C04, C10 and C11) account for A's and B's misses. C retains all four, plus the four changed cases.

| Paired comparison | Correct preserved / lost / gained | Changed replies | Unsupported answers prevented; claims prevented / missed / introduced | Useful partials preserved / lost | Clarifications lost | Redundant blocks |
|---|---|---|---|---|---:|---:|
| A → B | 32 / 0 / 0 | None | 0; 0 / 0 / 0 | 8 / 0 | 0 | 0 |
| A → C | 28 / 4 / 0 | R11, I03, I10, C12 | 0; 0 / 0 / 0 | 8 / 0 | 1 | 1 |
| B → C | 28 / 4 / 0 | R11, I03, I10, C12 | 0; 0 / 0 / 0 | 8 / 0 | 1 | 1 |

R11 and C12 each lost a scoped policy answer. I10 lost a campus clarification. I03 replaced an informative abstention with a generic one. Thus C lost 4/36 fully correct responses (11.1 percentage points). If I03's generic referral is sufficient, the loss is 3/36 (8.3 points). The draft contains no unsupported baseline spans for either safeguard to catch; sensitivity to actual hallucinations cannot be estimated from a zero denominator. [Case audit, disputes and sensitivity analysis](experiment03_phase_b_review.md)

## Operating cost and time

| Architecture | Usage-priced USD per 36 | Change vs A | Median modeled serial latency | Change vs A |
|---|---:|---:|---:|---:|
| A | $0.0024700 | — | 1.522 s | — |
| B | $0.0042786 | +73.2% | 2.767 s | +81.8% |
| C | $0.0049961 | +102.3% | 3.025 s | +98.8% |

Sealed receipts recorded 6,590 input / 3,622 output tokens for generation, 6,086 / 2,400 for gating, and 9,231 / 3,206 for verification. Observed median stage times were 1.522, 1.125 and 1.479 s respectively. Estimated total acquisition spend was $0.0068047. Workflow medians sum the applicable measured stages *per query* before taking the median. Percentages compare arm medians. B added $0.0018086 versus A, C added $0.0025261 versus A and $0.0007175 versus B. No generation was avoidable under the observed pre-gate decisions. Deployment queueing, retrieval time, invoice charges and labor cost were unmeasured. [Receipt audit](verification.md#experiment-03-phase-b--stage-2-live-checkpoint)

## Interpretation and boundary

The baseline already knew to withhold missing facts and treat dated or scoped sources carefully. The pre-gate explicitly allowed supported partial replies and focused clarifications, which helps explain why it passed even incomplete packets. A binary verifier could release a good answer or replace it wholesale; it had no correction step. These are plausible mechanisms. The verdicts do not reveal the verifier’s reasoning.

The cohort was small, synthetic and deliberately balanced across workloads. Each question had one generator draw, reused across arms. All stages used the same model family, so checks may share the generator’s blind spots. The source packets were fixed, and evidence links and authority judgments are reviewer-dependent. No deployment prevalence, realized harm, return on investment or general verifier sensitivity follows from these data. Do not pool Phase A and B accuracy. The customer decision should turn on actual failures observed in the intended workflow and what it costs to prevent them. [FDE deployment playbook](fde_deployment_playbook.md)
