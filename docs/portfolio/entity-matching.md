# When Should Entity Matching Escalate to an LLM?

“CNPq process” is a short label for a Brazilian research funder. A string matcher gave more weight to “process” and ranked a US organization first. It left the record unlinked. An LLM saw the same five candidates and correctly chose the Brazilian agency in second place. Yet the rule for deciding which records to send to the model put this one last in the four-query pilot.

**My recommendation is to keep deterministic matching and abstention as the default.** The pilot showed a reason to offer an LLM a second look at some records. It also showed why I would keep that step advisory until there is evidence that the routing rule finds more mistakes than the model introduces. [Pilot decisions](../phase3e_live_findings.md)

## The implementation decision

A funding analyst wants variant spellings and acronyms to roll up to the same organization. A false link can credit the wrong institution. An abstention leaves a visible gap that someone can review. The useful business question is how many consequential errors a second decision would prevent, given the time, money and risk it adds.

I compared three ways to handle the same incoming name and registry shortlist.

| Alternative | What it buys | What it risks |
|---|---|---|
| Link by string similarity or abstain | Repeatable decisions with no model latency or API charge | Shared wording can favor the wrong organization. Acronyms can leave a real match unresolved. |
| Escalate a fraction of names | Spend model calls where a second reading might matter | A routing mistake can skip the case that needed help or send a correct decision for reconsideration. |
| Send every name to the model | Every offered candidate gets a second reading | Every record incurs model cost and latency. A missing candidate still cannot be selected. |

## How I evaluated the choice

I used 38 development names from Crossref’s annotated funder data. Thirty had a target in the Research Organization Registry (ROR). Eight had no supported active match after one human review with AI-assisted research. For each name, lexical retrieval supplied five candidates from pinned ROR v2.6. The baseline linked the leader if its similarity was at least 0.75 and its lead over the runner-up was at least 0.03. Otherwise it abstained. I calibrated those thresholds on the same 38 names. [Dataset, baseline and grading](../phase3d_crossref_resolution.md) · [No-match review](../phase3e_readiness.md)

For the four-query live pilot, I froze the candidates and prompt. GPT-6 Luna could return one offered ID or abstain. I acquired one response per query, then reused it to compare escalation budgets on identical records. I scored an exact ID or a correct abstention as a correct decision. Separately, I checked whether retrieval had made each true match available in the first place. [Live pilot and replay](../phase3e_live_findings.md)

## What changed the decision

**The baseline got 32 of 38 decisions right.** It got all 18 registry-form names right, compared with 8 of 12 alternative wordings and 6 of 8 no-matches. Five of its six errors could in principle be corrected using the offered choices. The sixth, “Hoffmann - LaRoche Pharmaceuticals,” had its true target at rank eight. Paying for a better selector would still leave that record unresolved. Across the 30 positive cases, retrieval offered the correct ID 29 times. [Baseline error analysis](../phase3f_escalation_analysis.md)

**One repair accounted for the entire live gain.** At 25% escalation the model confirmed the Pakistan Higher Education Commission link. At 50% it also confirmed the Hong Kong abstention. Sending all four added a correct link for CNPq and confirmed the existing La Laguna link. Each row below represents an alternative use of the same four responses. [Per-query receipts summarized in the pilot report](../phase3e_live_findings.md)

| Escalation | Model calls used | Correct decisions | Summed API latency | Estimated API cost from usage |
|---|---:|---:|---:|---:|
| 0% | 0 | 3/4 | 0 s | $0 |
| 25% | 1 | 3/4 | 1.678 s | $0.0000482 |
| 50% | 2 | 3/4 | 6.859 s | $0.0001083 |
| 100% | 4 | 4/4 | 9.643 s | $0.0002111 |

The four calls used **991 input and 224 output tokens**. The dollar figures apply the pilot-date rates to reported usage. The provider supplied no billed amount. The one-shot run reserved $0.00354375 against a $0.005 cap and completed without retries. The last two calls together added $0.0001028 and repaired one decision. Staff time, the downstream cost of a false link and savings from avoided review were outside the pilot. [Usage and spending controls](../phase3e_live_findings.md)

**The routing rules found different errors at different budgets.** Offline, I counted how many of the five correctable baseline errors each rule brought forward. The existing rule prioritized names near the link/abstain thresholds. In the first nine slots it found four errors, compared with three for the rule that prioritized the smallest gap between the top two candidates. By 19 slots the counts were four and five. CNPq alone accounted for the challenger’s extra opportunity. Its two candidates scored 0.522 and 0.500, but the low leading score put it far from the link threshold and 30th in the existing queue. These counts measure opportunities. The other 34 names have no live model response. [Full ranking and equal-budget comparisons](../phase3f_allocation_audit.md)

## What I would implement

I would keep the shortlist, deterministic decision and explicit abstention visible to the operator. For a workflow where false attribution carries a material cost, I would show an LLM’s proposed correction to a reviewer before changing a record. I would log the original decision, proposed ID, final disposition, latency and usage. That would let the team judge repairs **and** regressions against the cost of its current review process. If audits find missing targets, the component to revisit is retrieval. If they find offered targets consistently overlooked, selective escalation is worth reconsidering.

This was an **exploratory development evaluation**. The constructed case mix, thresholds tuned on those names, and four live responses leave deployment accuracy, statistical significance and return on investment unestablished. I stopped the independent holdout plan. Its first 40-family review alone was estimated at 18–32 person-hours. That investment could answer a broader research question, but the available evidence already supports the portfolio decision to retain the baseline and limit the role of the LLM. [Feasibility assessment](../phase3g_holdout_feasibility.md) · [Project decision record](../PROGRESS.md)
