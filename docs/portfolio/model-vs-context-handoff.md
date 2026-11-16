# Website handoff · model tier against context

Place this sixth study after financial SQL context in **Applied AI decisions**. Do this only after owner acceptance and a separate approval for website integration. Use the [case study](model-vs-context.md) as the editorial source. It covers Experiments 006 and 007 as one study, because 007 is a pre-registered replication of 006.

**Card headline**: Should a Finance SQL Assistant Buy a Bigger Model or Better Context?

**Card copy**: A low-cost model with curated financial definitions beat a model costing 20 times more per token without them, in every draw on both GPT and Claude models, for roughly a quarter of the cost. On one question, every schema-only answer from the expensive model flipped the sign of a credit.

**Primary action**: Read the case study. Use the [006 scored results](../experiment06_scored_results.md) and [007 scored results](../experiment07_scored_results.md) as secondary actions.

## Article and assets

Keep the six article sections in order. Lead with the budget choice. Follow the four-configuration table with the means chart, and the paired-transition paragraph with the paired chart. Keep the format-sensitivity paragraph next to the provider difference it explains. Keep the Q17 trace and the recommendation after the results.

| Figure | Caption and text alternative | Files |
|---|---|---|
| Context before model tier | Mean correct of 36 over three draws, with each draw marked. Cheap with schema: GPT 3.7, Claude 1.3. Cheap with curated context: GPT 15.3, Claude 17.0. Expensive with schema: GPT 6.7, Claude 8.7. Expensive with curated context: GPT 24.0, Claude 18.0. | [Wide](assets/context-tier-means.svg) · [Compact](assets/context-tier-means-compact.svg) |
| Same question, same draw | Cheap model with curated context against expensive model with schema only, 108 paired outcomes per provider. GPT: 30 gained, 4 lost, 74 tied. Claude: 32 gained, 7 lost, 69 tied. | [Wide](assets/context-tier-paired.svg) · [Compact](assets/context-tier-paired-compact.svg) |

Keep the article's picture markup, alt text and semantic table headers. Use proportional images with max-width 100% and height auto. Switch to compact below 760 px or in a narrow article column. Give the results table its own horizontally scrollable, labelled region on small screens and keep the units in its headers. The figure labels also express every value in text.

The [renderer](render_context_tier.py) reads the two locally preserved, digest-checked machine reports. Regenerate from the repository root with `python docs/portfolio/render_context_tier.py`. The checked-in SVGs need no runtime dependencies on the website.

## Claims to keep intact

- Strict scores are the official result. The format-lenient Claude scores were chosen after the run and must stay labelled post-hoc.
- The two provider columns do not rank GPT against Claude. Settings were not calibrated across providers, and the prompts were developed on GPT models.
- Costs are usage-priced and exclude the effort of writing the curated package, which already existed from Experiment 005.
- The questions were seen in Experiment 005, and the warehouse is synthetic.
- Three draws describe variation. Do not add significance language.
- Keep the attribution of clarification review: AI-drafted and owner-accepted in 006, owner-reviewed item by item in 007.
