# Website handoff · financial context for SQL

Place this fifth study after tool recovery in **Applied AI decisions**, following owner acceptance and separate website integration approval. Use the [case study](finops-sql.md) as the editorial source.

**Card headline** — How Much Business Context Does an AI SQL Assistant Need?

**Card copy** — The schema let an assistant write SQL for March spending, but it counted the wrong charges. Curated and expanded financial context each raised the score from 1 to 18 correct decisions on 36 questions. They succeeded on different cases.

**Primary action** — Read the case study. Use the [scored evidence](../experiment05_scored_results.md) as the secondary action.

## Article and assets

Keep the six article sections in order. Lead with the two March clocks. Follow the comparison table with the decision chart, the Q20/Q07 examples with the overlap chart, and the separate discovery comparison with the depth chart. Keep the Q01 trace and the recommendation for a controlled analyst workflow after the results.

| Figure | Caption and text alternative | Files |
|---|---|---|
| Correct business decisions | Same 36 questions per condition. Schema passed 1, curated 18, expanded 18 and discovery 5. | [Wide](assets/meridian-decisions.svg) · [Compact](assets/meridian-decisions-compact.svg) |
| Paired overlap | Fourteen questions passed both preloaded business-context conditions, four only curated, four only expanded and fourteen neither. | [Wide](assets/meridian-overlap.svg) · [Compact](assets/meridian-overlap-compact.svg) |
| Discovery depth | Of 36 episodes, one each used one, two and five metadata calls. The other 33 used six. The 242 model requests cost an estimated $0.04544. | [Wide](assets/meridian-discovery.svg) · [Compact](assets/meridian-discovery-compact.svg) |

Keep the article’s picture markup, alt text and semantic table headers. Use proportional images with max-width 100% and height auto. Switch to compact below 760 px or in a narrow article column. Give the comparison table its own horizontally scrollable, labelled region on small screens and keep the units in its headers. The figure labels also express every value in text.

The [renderer](render_meridian.py) reads the locally preserved, digest-checked machine report. Regenerate from repository root with `python docs/portfolio/render_meridian.py`. The checked-in SVGs require no runtime dependencies on the website.

Retain the Q16 sensitivity, shared reference assumptions, historical question reuse, single draw per condition, AI-assisted wording review and small clarification denominator. Keep estimates and cumulative API times labelled. The proposed analyst controls were outside the evaluated conditions.
