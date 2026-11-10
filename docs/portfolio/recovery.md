# When Should an Enterprise AI Agent Recover Automatically—and When Should It Stop?

*AI Evaluation Lab · Experiment 004*

A purchasing desk submits an order and the API reports a duplicate. Trying again could order the goods twice. Sending the buyer to investigate could also waste time if the desk already has a receipt proving the first submission succeeded. What should the assistant tell the buyer, and should it touch the order again?

**For workflows like the ones I tested, I would automate documented corrections with rules and give the desk a clear path for exceptions.** In the completed study, frozen rules and a model each made the correct decision on **24 of 24** episodes. Stopping and reporting the failure scored **9 of 24**. Calling the model added a median **1.980 seconds** per episode and recovered no additional task over rules.

## Three ways to handle a failed operation

I compared three responses to the same failure. The first reported what the system knew and escalated when necessary. The second applied a documented rule, such as converting an approved payout from dollars to integer cents. The third let GPT-6 Luna inspect the error and propose one correction or an explicit stop.

<picture>
  <source media="(min-width: 760px)" srcset="assets/recovery-architecture.svg">
  <img src="assets/recovery-architecture-compact.svg" alt="Stop/report returns a status. Rules and the model can propose one correction. An independent guard checks proposed writes before the local API can change state.">
</picture>

*All three paths start after the same scripted failure. Only an authorized proposal reaches the simulated business system.*

The model had the same public rules and normalized business facts as the deterministic handler. It could propose a call but could neither grant itself permission nor declare that a transaction had succeeded. The guard checked whether the caller could take that action on that record. A separate grader checked whether the resulting state and the status shown to the user actually fulfilled the request.

## What the comparison measured

The 24 fictional procurement, treasury and software-administration episodes began with **scripted failures**. I wanted to evaluate the next decision under identical conditions. The experiment did not measure how frequently agents cause these failures. The rules were frozen after development on eight separate examples, before evaluation on the 24 episodes. Every business operation ran against a local simulator with an effect ledger, which let the grader detect a second write even if the final status looked right.

| Follow-up strategy | Policy-correct decisions | Estimated inference cost for 24 | Median API acquisition time |
|---|---:|---:|---:|
| Stop and report | 9/24 | $0 | No API call |
| Deterministic rules | 24/24 | $0 | No API call |
| Bounded model proposal | 24/24 | $0.0029715 | 1.980 s per request |

<picture>
  <source media="(min-width: 760px)" srcset="assets/recovery-outcomes.svg">
  <img src="assets/recovery-outcomes-compact.svg" alt="Stop/report scored 9/24. Rules and the model each scored 24/24. Model inference cost an estimated $0.0029715 across 24 episodes, with median API acquisition time of 1.980 seconds per episode.">
</picture>

*Cost covers inference for the full follow-up. Time measures a single model request. Engineering and exception handling have separate, unmeasured costs.*

Rules and model each recovered all 12 recoverable tasks, gave the required stop status on all 11 stop cases, and recognized one prior completion. Stop-and-report left all 12 recoverable tasks unfinished. It also sent three cases for generic review where a buyer or administrator needed a specific request for clarification or reapproval.

An authorized retry did not always mean a new effect. On one timed-out invoice, the API guaranteed that repeating the **identical payment with its original key** would return the original confirmation. Both recovery strategies used that guarantee. Their 12 attempted writes produced 11 new effects and one confirmation, with zero duplicate payments or observed unsafe proposals.

## One order, two status reports

The purchase-order task asked, “Submit the approved order once.” The duplicate error came with an authenticated receipt for the original order. It identified the operation, transaction key and exact request. The correct desk response was to confirm completion without submitting again.

<picture>
  <source media="(min-width: 760px)" srcset="assets/recovery-p8.svg">
  <img src="assets/recovery-p8-compact.svg" alt="For order PO-48 a verified receipt established completion. The first model draw reported unknown under a 512-token cap. The follow-up reported confirmed under a 2,048-token cap. Neither proposed a write.">
</picture>

*The evidence established one completed order in both runs. Only the status returned to the desk changed.*

In the first pilot the model stopped with status `unknown`. It protected the ledger but left the buyer without an answer the evidence supported. The pilot ended on the next episode, P3, when the response hit its 512-token output limit. Six requests were sent, five completed and four of those five were correct. The run cost an estimated $0.0011733 and was permanently closed.

After that interruption I approved a separately frozen follow-up with a 2,048-token output limit. All 24 requests ran afresh. The model reported `confirmed` on the purchase order, and P3 completed correctly. The cap and the model draw both changed. These two observations cannot tell us why the purchase-order answer changed. [Pilot audit](../experiment04_live_acquisition.md) · [Follow-up case ledger](../experiment04_followup_acquisition.md)

## My contribution

I directed the comparison, required a strong rules baseline and approved the cases before implementation. I required separate checks for a valid call, permission to execute it and a correct business outcome. I accepted the first pilot’s stop, reviewed its loss on the purchase order, and approved a new budget and manifest for the follow-up. Codex implemented the rules, simulator, dispatcher and audit tooling. The frozen grader scored state transitions, effects and statuses programmatically. [Design and scoring protocol](../experiment04_recovery_design.md)

## What I would recommend to a customer

Start with the contract for the failed operation. If it documents a unique, authorized correction, encode it and test the ledger. If a payment may already have committed and the API offers no safe replay guarantee, stop and give treasury the key it needs to reconcile the transaction. If a price increase invalidates an approval, route the order to the approver. A model proposal cannot renew that authority.

I would consider a model for the slice of real incidents where rules leave valuable work unfinished **and the available evidence is sufficient to finish it**. First run it in shadow mode. Count additional authorized completions, wrong-direction proposals, duplicate effects and escalations. Price the time saved at the desk against inference, investigation, monitoring and delay. For irreversible actions, require independent approval or a stronger execution control before releasing a write.

This was a small authored cohort with supplied, normalized facts. A desk interpreting raw contracts or facing a different incident mix needs its own evidence. The study measured neither production reliability nor a long-term maintenance advantage for either handler. [Accepted evidence and deployment criteria](../experiment04_final_findings.md)
