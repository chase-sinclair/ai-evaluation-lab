# Future direction for AI Evaluation Lab

Use the Lab for short implementation decisions. Begin with a choice someone owns, such as whether an operations team should add a model to an existing review queue. Agree what result would justify the added dependency before spending time on evaluation. Use the existing runner when it answers that question.

| Section of each case study | What the reader should learn |
|---|---|
| Decision | Who uses the output? What action follows? What happens when the system is wrong or abstains? |
| Alternatives | What happens today? Compare that baseline with the smallest plausible AI change and the option to defer it. |
| Evidence | State the sample, how answers were verified, and the metric that matters to the decision. Use the same cases for each alternative and distinguish observed outcomes from estimates. |
| Economics and risk | Give the incremental repairs and regressions, latency, usage cost, and human work added or avoided. Leave unmeasured business value explicit. |
| Recommendation | Say what to adopt, limit or decline, who handles exceptions, and what evidence would change the decision. Link the reproducible technical record. |

Stop when the remaining uncertainty would not change the recommendation. Invest in independent validation when a real deployment decision, its consequences and an accountable owner justify the effort.

## Reusable page outline

1. **Decision and answer.** Give the audience, the concrete choice and your recommendation in two sentences. Pair the baseline result and its denominator with the observed change and the number of live observations.
2. **Alternatives and workflow.** Show the existing process, the smallest AI change, and how each handles a mistake. Label each diagram step as implemented or proposed where its status could be mistaken.
3. **Evaluation and results.** Explain the unit of evaluation, ground truth and comparison in plain language. Put quality, latency and cost in one table with units. Identify reused observations and estimated costs.
4. **One decision trace.** Follow a real input through the baseline, routing decision and observed outcome. State what the system could see at the time.
5. **My contribution.** Separate the decisions, implementation requirements and reviews you owned from work done by software, collaborators or research assistants. Cite the project record.
6. **Recommendation and limits.** Describe the exception path, the business measure still missing and what evidence would change the recommendation. Link the technical findings for readers who want the details.

## Placement on the portfolio website

Put the Lab alongside the engineering projects under **Applied AI decisions**. Let the engineering project pages explain what was built. Use a Lab entry to show how the author decided which parts were worth building. Link directly to the case study as the primary action, with the repository as the secondary link for readers who want to inspect the implementation.

**Suggested project card**

**When Should Entity Matching Escalate to an LLM?**

A deterministic matcher got 32 of 38 development decisions right. In a four-query live pilot, an LLM repaired one missed link. I traced why the routing rule put that record last and used the result to decide where automation should stop.

[Read the case study](entity-matching.md) · [Explore the evaluation code](../../experiments/entity_matching/ror)

The [website handoff](entity-matching-handoff.md) contains the final listing copy, section order, figure assets and pilot-table guidance for this study.
