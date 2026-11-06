# Preregistration v1 · equal-budget escalation for funder resolution

**Question.** At a fixed 25% escalation rate, does prioritizing the smallest top-two retrieval margin improve end-to-end correct decisions over the frozen uncertainty rule? The estimand is challenger minus reference on the same adjudicated families, equally weighted, at the specified 150-positive/50-no-match mix. The protocol is recorded before cohort draw, retrieval, ranking, adjudication or acquisition. No dispatch authority is attached.

## Freeze and endpoint

- Require 200 independent families, one query each, with both strata complete. Otherwise stop before evaluation and version any revised design. The custodian freezes the independently reviewed answers separately from query inputs. Use the Phase 3F reference revision, ROR v2.6 lexical retriever, ordered top five, prompt, parsing and baseline fallback. No target insertion. Keep every retained family, including missing targets and ties. Confirm request and body hashes, ordering and parser on offline transport before a separately approved dispatch. [Reference revision and frame](phase3g_sampling_manifest.json)
- Let `t` be the top score, `g` the top-minus-second margin rounded to eight decimals, with missing scores padded by zero as in the frozen implementation. The baseline links to the first candidate if present and both `t ≥ .75` and `g ≥ .03`, otherwise abstains. Reference order is ascending `abs(round(min(t − .75, g − .03), 8))`. Challenger order is ascending `g`. Ties in either use lexical original case ID (`cr-<seq_no>`). Each escalates the first floor(N/4) cases. Compute lists on all blinded queries once, before opening gold labels or collecting responses. Record list hashes and overlap. Avoid changing cutoffs or breaking ties from observed overlap.
- Use one fixed response per acquired query in all arms. On selected queries use the frozen parser and the baseline fallback on a recorded acquisition failure or invalid output. Distinguish completed fallbacks from never-attempted cases when a safety stop truncates collection. A required but unattempted case leaves the full comparison incomplete. Always record attempted, completed, failed, invalid, fallback and missing counts. No optional stopping on performance.
- For each family score 1 for its exact adjudicated active ID or the correct no-match abstention, else 0. Compute `Dᵢ = correct(challenger) − correct(reference)`. Report challenger-only correct count W, reference-only correct count L, net correct decisions W−L and primary accuracy difference (W−L)/200. Count a baseline repair as +1 and regression as −1 in the corresponding policy. Identical correct outputs, identical incorrect outputs and different outputs that are both incorrect contribute zero difference. Publish the entire paired transition table when the acquisition scope identifies it.

## How many responses?

Let A and B be the reference and challenger prefixes, each of size k=50, and h their observed intersection. Baseline predictions are known for all rows. A shared escalation uses precisely the same response in both policies. No outcome assumption is needed for cancellation.

| Intended result | Sufficient distinct acquisitions | At N=200 |
|---|---|---:|
| Primary paired difference, W and L only | Symmetric difference of A and B: 2(k−h) | 0–100 |
| Absolute accuracy, total repairs/regressions, usage and cost for each 25% policy | Union of A and B: 2k−h | 50–100 |
| Absolute 50% policies | Union of both top-100 prefixes; reuse any acquired responses | 100–200 total |
| Absolute 100% performance or unrestricted replay over all families | All families, once each | 200 total |

For example, h=40 requires 20 unique responses for the primary difference or 60 to also measure each policy's totals. At h=50 the contrast is identically zero on the frozen cohort. At any overlap the largest possible absolute shift is 2(50−h)/200. Report this structural limit before acquisition. For difference-only comparisons at 50%, use the analogous symmetric difference at k=100, subtracting already acquired IDs. Replaying random allocations or a bootstrap that **reranks** families can select cases outside the acquired union; do not impute those responses. At 0% all decisions are already known.

**Recommended acquisition scope if approved later:** use the 25% union to measure operational quality and cost as well as the primary endpoint. Hold 50% and 100% analyses outside the primary authorization. If the two lists are identical or the maximum difference is below the practical threshold, report the pre-outcome bound and return for review before any acquisition. For very high overlap a difference-only study is cheaper, but it cannot identify shared escalations' effects, absolute accuracy or total cost. Choose scope at freeze time without outcomes.

## Precision and interpretation

Prespecify **3 percentage points** (six net decisions per 200) as the smallest difference of practical interest for this study, pending owner acceptance before sampling. Let d=W+L be the number of families with *discordant correctness*, at most 2(50−h). Allocation differences alone do not imply discordant correctness. Near a balanced split of wins and losses, a planning approximation to the standard error in percentage points is `100 × sqrt(d) / N`. These are scenario calculations with independent-family assumptions; no development effect rate was imported.

| Discordant families d | Approx. 95% half-width near zero | Net effect for ~80% power, two-sided 5%, normal planning approximation |
|---:|---:|---:|
| 5 | 2.2 pp | 3.1 pp |
| 10 | 3.1 pp | 4.4 pp |
| 20 | 4.4 pp | 6.3 pp |
| 40 | 6.2 pp | 8.9 pp |

Discrete counts matter. With five discordances, even five wins gives only 2.5 pp and a two-sided exact sign-test p-value of .0625. With ten discordances, 8 wins and 2 losses deliver +3 pp, but the two-sided exact p-value is .1094. At a 10% discordance rate, a nominal 80%-power design for 3 pp would need roughly 872 independent families at the same mix and rankings (normal approximation). Independence, rate and stable policy overlap are unverified. **200 is reasonable for estimating a first effect and detecting larger changes; it cannot promise a decisive 3 pp comparison.**

Report the exact observed paired difference for the frozen cohort. For uncertainty, use 20,000 paired family bootstrap draws, seed 31007, sampling within the two adjudicated strata at their original sizes, and report the percentile 95% interval for the mean of the observed Dᵢ. Keep frozen policy membership in each draw. This conditional analysis can be done from the symmetric difference plus structural zeros. It differs from Phase 3F's proposed reranking bootstrap: it measures variability of paired contributions at this realized allocation and omits uncertainty from re-estimating rank cutoffs on a new cohort. Report W, L and a two-sided exact sign test conditional on d as a sensitivity analysis (d=0 has no sign information). With sparse or zero discordances identify degenerate intervals explicitly; do not infer equivalence or generalization from them. Retain the reference unless the estimated benefit reaches 3 pp, the interval excludes zero in the challenger's favor and error/cost breakdowns support the operational use case. Results confined to this curated class mix need external replication.

## Separate retrieval, selection and cost

Report positive-target Recall@5 over all adjudicated positives, correct links conditional on retrieval and end-to-end accuracy including all misses. An absent true target makes exact resolution impossible under either policy. An abstention there still misses a positive. Report false links on reviewed no-matches, incorrect abstentions, wrong-ID assertions, link precision/recall/F1, asserted links and abstentions by stratum. Break down baseline repairs and regressions by offered-target status. Separate predictive outcomes from invalid output or transport failure. With a difference-only acquisition, report only identifiable quantities and mark all others unmeasured.

Before any future live authorization, freeze a new one-shot manifest limited to the unique required IDs. Recheck available model, approved standard tier, prompt, body hashes, explicit 30-minute cache policy and dated prices. Proposed controls mirror Phase 3E: GPT-6 Luna, no tools, 1,024 output tokens, sequential, zero retries, immutable receipts. Under Phase 3F's *historical planning assumptions* of ≤8,000 body bytes plus 256 framing tokens, the reserve is ≤$0.002576 per unique request; at most **$0.25760** for the 25% union. Proposed ceiling **$0.26**, subject to exact preflight, separate approval and the returned tier/usage guards. Stage the first min(20, required) attempts for integrity checks only, inside the same total. Stop on hash, model, tier, price, duplicate, reserve, provider, parsing, or cache/accounting violations. Report measured latency, reported tokens and usage-priced estimate separately from the reserve and any actual provider bill. No automatic expansion to optional arms.
