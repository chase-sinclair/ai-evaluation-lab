# Website handoff · RAG reliability safeguards

Place Experiment 03 alongside the entity-matching and tool-access studies under **Applied AI decisions**. The [case study](rag-safeguards.md) supplies the final article copy, figures and accessible table.

## Project card

**Title** — Which RAG Reliability Safeguards Are Worth Deploying?

**Card copy** — Across 36 synthetic enterprise questions, standard RAG gave 32 fully correct replies. A pre-generation gate preserved all 32. A post-generation verifier withheld four useful replies and roughly doubled estimated inference cost.

**Action** — Read the case study

**Search description** — A paired comparison of three RAG workflows traces a blocked facilities answer and asks when the benefit of another model check justifies its cost.

## Page order and figures

| Placement | Final copy or presentation |
|---|---|
| Opening | Use the article’s synthetic Annex B example and recommendation. Keep the 36-question denominator beside the scores. |
| Architecture | Place the [workflow diagram](assets/rag-workflows.svg) after the implementation decision. Caption — “All three workflows start with the same preselected packet. The pre-gate checks the evidence. The verifier sees the answer as well.” |
| Method | Keep the separate 24-question pilot before the 36-question paired comparison. State that both phases used frozen, preselected packets and excluded live retrieval and ranking. Explain why each generator reply was reused. |
| Results | Keep the HTML table with column headers and exact values. Place the [comparison figure](assets/rag-outcomes.svg) immediately after it. Caption — “Fully correct replies out of 36, estimated inference dollars for all 36 questions, and median modeled serial seconds per question. Each panel has its own zero-based scale.” |
| Decision trace | Use the [C12 trace](assets/rag-c12.svg). Caption — “The signed local closure answered the question. The verifier blocked the scoped reply, and the application returned a referral. A workplace delay is hypothetical.” Retain the original wording inside the figure. |
| Customer recommendation | Use the article’s diagnosis table. Link the [approved FDE playbook](../fde_deployment_playbook.md) as engineering guidance. |
| Contribution, limitations and evidence | Preserve AI-assisted grading and owner-review attribution, I03, I04 and C06 qualifications, and the boundary on customer ROI. End with **Inspect the paired findings**. [Technical findings](../experiment03_paired_findings.md) · [Grading audit](../experiment03_phase_b_review.md) · [Phase A evidence](../experiment03_phase_a_review.md) |

Use the article’s image descriptions as alt text. Use the article’s picture elements for the workflow and C12 diagrams. Their 800-pixel layouts support a wide article column. Below a 760-pixel viewport use the 360-pixel stacked versions. For a narrow embedded column, choose the compact layout whenever the column is under 700 pixels wide. Set image max-width to 100% and height to auto. Keep the outcome chart at its native 384-pixel maximum. Place each caption immediately below its figure. Keep the results table available as text and allow local horizontal scrolling on small screens. Keep the labels “estimated” and “modeled” visible wherever the figures are reused.
