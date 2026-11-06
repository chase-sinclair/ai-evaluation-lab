# Website handoff · When Should Entity Matching Escalate to an LLM?

Place the study under **Applied AI decisions**, beside the engineering projects. Use the portfolio card to open the case study. Give readers the technical evidence link after the recommendation.

## Final listing copy

**Title:** When Should Entity Matching Escalate to an LLM?

**Card description:** A deterministic matcher got 32 of 38 development decisions right. Four live requests produced one repair. I examined why the routing rule put that name last and where a human should review a correction.

**Card action:** Read the case study

**Search and share description:** An exploratory study of funder-name matching compares a deterministic baseline with selective LLM review on accuracy, latency and estimated API cost.

## Article copy and section order

Use the [published Markdown article](entity-matching.md) as the final body copy, including captions, the first-person contribution statement, limitations and evidence links. Preserve the headline metrics with their denominators and labels.

| Placement | Copy or component |
|---|---|
| 1. Opening | Use the title, implementation question and recommendation verbatim. Display **32/38 decisions correct** (development baseline), **1 missed link corrected** (observed LLM repairs), **4 distinct names, one call each** (live requests). Stack the metrics on narrow screens. |
| 2. The implementation decision | Use the three-row alternatives table. Keep the consequences of a false attribution and a missed link visible. |
| 3. How I evaluated the choice | Place the workflow diagram above the cohort and replay description. Keep its implemented/proposed caption adjacent. |
| 4. What the baseline could resolve | Keep the 32/38 development result separate from the four-name pilot. Retain the Hoffmann-La Roche retrieval miss. |
| 5. Four live requests, four ways to use them | Render the article’s four policy rows as an HTML table with column headers and a caption: “Accuracy, summed API latency and usage-priced cost on the same four names.” Preserve all dollar decimals. On phones allow horizontal scrolling within the table. |
| 6. Why the only repair came last | Use the CNPq diagram, then the comparison of routing rules. Keep 30th of 38 labeled as escalation rank and second of five as candidate rank. |
| 7. My contribution | Use the three sourced bullets covering design and implementation direction, human evaluation, and analysis and recommendation. |
| 8. What I would implement | Close with the advisory workflow and the limits paragraph. Keep the stopped holdout and unmeasured ROI visible in the article. |

## Figures and evidence

| File | Display and accessibility |
|---|---|
| [Workflow SVG](assets/entity-matching-workflow.svg) | Intrinsic size 590 × 564. Solid boxes show the evaluation; a dashed, explicitly labeled box marks proposed human review. Use the article’s alt text. |
| [CNPq SVG](assets/cnpq-decision.svg) | Intrinsic size 590 × 447. The ordered shortlist leads into the baseline decision, queue position and observed repair. Use the article’s alt text. |

Keep the figures in their original aspect ratios; allow full-size viewing on small screens. The surrounding article explains both figures in text. Use the policy table as the numerical reference. The rows are alternative replays; summing their costs would count some responses more than once. For the secondary action, use **Inspect the pilot results**. [Pilot results](../phase3e_live_findings.md)

For future pages, reuse the [case-study outline](study-format.md#reusable-page-outline).
