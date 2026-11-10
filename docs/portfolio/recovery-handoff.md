# Website handoff · bounded tool recovery

Place this study after the RAG safeguards article in the future **Applied AI Decisions** collection once the owner declares the Lab complete and approves integration. Use the [article](recovery.md) for final editorial copy.

**Project-card headline** — When Should an Enterprise AI Agent Recover Automatically—and When Should It Stop?

**Card copy** — A payment timeout can mean the money already moved. Across 24 simulated enterprise failures, deterministic rules and an AI recovery handler both made every required decision. A purchase-order receipt shows why stopping safely still requires reporting the right status.

**Action** — Read the case study.

## Article order

1. Lead with the duplicate order and the architecture decision. Keep the 24-episode follow-up denominator visible.
2. **Three ways to handle a failed operation.** Place the architecture figure between the three strategy descriptions and the guard/grader explanation.
3. **What the comparison measured.** Keep the method, HTML results table, outcomes figure and exact-key payment example together. Show 9/24, 24/24 and 24/24, $0.0029715 estimated follow-up inference cost, and 1.980 seconds median observed API acquisition time.
4. **One order, two status reports.** Place the P8 figure after the authenticated receipt explanation. Keep the 512-token pilot interruption and the separately configured follow-up in separate paragraphs.
5. **My contribution.** Retain owner direction, approvals and review, Codex-assisted implementation and programmatic grading.
6. **What I would recommend to a customer.** End with the proposed shadow pilot, its adoption criteria and the evidence link.

## Figures and accessible copy

**Figure 1** · [Wide SVG](assets/recovery-architecture.svg) · [Compact SVG](assets/recovery-architecture-compact.svg)

Caption — All three paths start after the same scripted failure. Only an authorized proposal reaches the simulated business system.

Alt text — Stop/report returns a status. Rules and the model can propose one correction. An independent guard checks proposed writes before the local API can change state.

**Figure 2** · [Wide SVG](assets/recovery-outcomes.svg) · [Compact SVG](assets/recovery-outcomes-compact.svg)

Caption — Cost covers inference for the full follow-up. Time measures a single model request. Engineering and exception handling have separate, unmeasured costs.

Alt text — Stop/report scored 9/24. Rules and the model each scored 24/24. Model inference cost an estimated $0.0029715 across 24 episodes, with median API acquisition time of 1.980 seconds per episode.

**Figure 3** · [Wide SVG](assets/recovery-p8.svg) · [Compact SVG](assets/recovery-p8-compact.svg)

Caption — The evidence established one completed order in both runs. Only the status returned to the desk changed.

Alt text — For order PO-48 a verified receipt established completion. The first model draw reported unknown under a 512-token cap. The follow-up reported confirmed under a 2,048-token cap. Neither proposed a write.

Use the article’s picture elements, full-width proportional sizing up to the intrinsic width and the stacked assets for narrow columns. Select compact below a 760-pixel viewport or whenever the article column cannot accommodate a wide diagram. Preserve readable table headers and allow local table scrolling on phones.

## Evidence to retain

The initial failures were scripted, inputs normalized, rules frozen before evaluation and business effects simulated locally. Inference cost excludes engineering, maintenance and exception handling. The 24-case comparison does not establish population-level reliability, ROI or a maintenance advantage. Preserve the pilot’s observed P8 loss and P3 truncation; retain separate denominators. Production interventions are engineering recommendations. [Final technical findings](../experiment04_final_findings.md) · [Design](../experiment04_recovery_design.md) · [Pilot audit](../experiment04_live_acquisition.md) · [Follow-up plan](../experiment04_followup_plan.md) · [Follow-up audit](../experiment04_followup_acquisition.md)
