# Website handoff · freight-desk tool access

Place this card beside Experiment 01 under **Applied AI decisions**. Use the [case study](tool-catalog.md) verbatim for the article body, captions, tables and first-person contribution.

## Listing and share copy

**Title** — Does Giving an AI Agent More Tools Make It Less Reliable?

**Card** — All 18 shared freight-desk challenges passed with 5, 10 and 20 tools. A missing release function exposed a different risk: the agent proposed putting a hold on the very payout it was asked to release.

**Card action** — Read the case study

**Search description** — A freight-desk evaluation compares shared-task accuracy, capability coverage and token cost, then traces a schema-valid payout proposal with the wrong business effect.

## Recommended page order

| Placement | Copy and presentation |
|---|---|
| Opening | Use the article title, finding and recommendation. Show **18/18 shared scenarios** at every size in both layouts, **2.20× primary input tokens** and **82% higher estimated primary cost** for 20 versus 5 tools. |
| Implementation decision and method | Keep the V1 ceiling beside the reason for V2. Identify the 12 controls, 18 shared challenges and six capability cases before introducing results. |
| Accuracy and coverage | Use the [coverage figure](assets/catalog-coverage.svg) and capability table. Keep “none offered” visible at five tools. Coverage uses distinct tasks. Abstentions count responses and leave the task unfulfilled. |
| Operating cost | Use the [cost figure](assets/catalog-cost.svg) and article's primary table with its exact dollar amounts. Both panels start at zero and use separate units. Preserve the 36-response denominator and median latency label. |
| C06 decision trace | Use the [payout diagram](assets/catalog-c06.svg) followed by the exact proposed call. Preserve both layout columns and the no-execution caption. |
| Contribution and recommendation | Use the first-person section, the three implementation recommendations and the limitations paragraph. End with **Inspect the verified results** linking to the [V2 audit](../experiment02_v2_live_findings.md). |

Use the article’s alt text for each figure. Render the tables as HTML with header cells. On narrow screens, stack the headline metrics, allow horizontal scrolling within tables and offer full-size figures. Keep the outcome labels visible in text as well as color. The article and assets are ready for site integration.
