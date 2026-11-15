# Experiment 006 · Can a cheaper model with good context match an expensive model?

*Design and acquisition protocol. Owner decisions recorded November 15, 2026. No inference is authorized by this document.*

## Decision

A team building a finance SQL assistant can spend on a larger model or on business context. Experiment 005 showed that curated definitions lifted `gpt-6-luna` from 1 to 18 correct decisions out of 36 on the Meridian warehouse. It did not test whether a larger model would have closed that gap without the context, or whether the larger model also benefits from it. The decision this study supports is where the next dollar should go: model tier or context.

## Owner decisions

| Choice | Decision | Alternatives considered |
|---|---|---|
| Expensive model | `gpt-6.1-sol` | `gpt-6.1-terra` (smaller price gap), `gpt-6-astra` (about 5× Sol's price) |
| Cheap model | `gpt-6-luna`, unchanged from Experiment 005 | none |
| Context levels | A · schema only, B · curated definitions | Adding C · expanded context |
| Draws | Three independent requests per question and cell | One or five |

Self-discovery (005 arm D) is excluded. It is multi-turn, was the weakest condition, and would make model cost depend on how many lookups each model chooses.

## Design

A 2 × 2 grid on the 36 accepted Meridian evaluation questions:

| Cell | Model | Context |
|---|---|---|
| Luna · A | `gpt-6-luna` | schema |
| Luna · B | `gpt-6-luna` | curated |
| Sol · A | `gpt-6.1-sol` | schema |
| Sol · B | `gpt-6.1-sol` | curated |

Each cell receives each question three times: 432 single-turn requests. Within a draw, the question order is shuffled with a fixed seed and the four cells rotate per question. All 144 requests of draw 1 precede draw 2, and draw 2 precedes draw 3, so a budget stop leaves complete earlier draws.

**Held constant.** Request bodies are the accepted Experiment 005 v3 evaluation bodies for arms A and B: the same reporting conventions, instructions, context packages, question wording, report fields, `max_output_tokens` of 25,000, medium reasoning effort, 30-minute prompt cache lifetime and standard service tier. Luna bodies must be byte-identical to the frozen 005 evaluation bodies. Sol bodies differ only in the `model` field. Tests enforce both.

**Model generation.** Sol is a 6.1 release and Luna is a 6.0 release. The comparison is between models a team could buy on the pricing date, not between sizes within one release.

## Outcomes

Primary, per cell: correct business decisions out of 36 for each draw, graded exactly as in Experiment 005. SQL must pass the admission grammar and return the expected typed result on both evaluation snapshots in the isolated DuckDB worker. The four ambiguous questions need the required clarification dimensions and an adequate question, judged on a masked worksheet that hides model, context and draw.

Reported alongside:

- **Mean and range across draws** for each cell.
- **Stability per question:** correct in 3 of 3, in 1–2 of 3, or in 0 of 3 draws.
- **Paired transitions** per draw on the same question. The headline pair is Luna · B against Sol · A (cheap model with context against expensive model without). Also reported: Sol · B against Luna · B, Sol · A against Luna · A, and context gain within each model.
- **Usage-priced cost** per cell, per correct decision and per draw, plus observed API time.
- **Output exhaustion** counted as an acquired failure, as in 005.

Each draw is one model sample. Three draws estimate within-cell variation on this workload. They are not a population sample, and no significance test is planned. The interpretation stays descriptive.

## What would change the decision

- **Luna · B matches or beats Sol · A at a fraction of the cost:** context is the better first investment.
- **Sol · A matches Luna · B:** a larger model can substitute for curation on this workload, and the choice becomes cost against curation effort.
- **Sol · B clearly exceeds Luna · B:** both levers add value. The size of the gap prices the upgrade.
- **Large draw-to-draw variation:** single-draw results such as 005's need wider caveats, whatever the cell means.

## Budget and spending guard

Prices on the pricing date, standard tier, short context, USD per million tokens, from the OpenAI pricing page:

| Model | Input | Cached input | 30-minute cache write | Output |
|---|---:|---:|---:|---:|
| `gpt-6-luna` | 0.10 | 0.01 | 0.125 | 0.50 |
| `gpt-6.1-sol` | 2.00 | 0.10 | 2.50 | 10.00 |

**Expected spend.** In the 005 run, Luna's A and B requests used at most 2,472 input and 3,877 output tokens, for about $0.038 across both arms. At 20× those rates, one Sol draw of both arms would be about $0.76 if Sol used similar tokens. Three draws of both models would be about $2.4. Sol may reason for longer, so the realistic range is $3–6.

**Worst case.** Each request may produce 25,000 output tokens. At Sol's rate that is $0.25 per request before input, so a worst-case reserve over all 432 requests is about $62. Holding that full reserve, as earlier experiments did, would require confirming about $62 of available credit for a run expected to cost a tenth of that.

**Proposed guard.** The dispatcher refuses to send any request unless the accounted spend plus that request's worst-case cost stays within the approved cap. Spend therefore cannot exceed the cap. If the cap is reached, the run stops, seals and reports the unsent remainder. The proposed cap is **$15**, about 2.5× the high end of the expected range. The manifest records both the guard and the full worst-case reserve.

## Run protocol

1. **Freeze.** Build the 432 request bodies and the manifest, and record the manifest digest, bodies digest and source hashes.
2. **Approve.** The owner approves the exact digest, reviewed revision and cap, and confirms current rates, credit and project limits for both models.
3. **Run once.** Run sequentially with no SDK retries, no resumption and no reruns. Verify each response's model (the requested alias or its dated snapshot), tier, settings, usage and response ID before accounting. Any failure other than output exhaustion stops the run globally.
4. **Seal.** Hash every file in the result directory into a seal on completion or failure.
5. **Audit.** Replay the ledger against the frozen bodies offline. Grade SQL in the isolated worker on both evaluation snapshots. The owner reviews the masked clarification worksheet before any score is reported.

## Limitations accepted in advance

- The 36 questions were inspected during Experiment 005, so they are development-exposed. Both models face the same questions, which keeps the comparison fair, but scores are not a fresh holdout.
- The warehouse is synthetic. The reference answers share accounting assumptions.
- There is one model family and one reasoning setting. Results do not transfer to other providers or effort levels.
- Clarification adequacy remains an AI-assisted, owner-accepted judgment on four questions.
- Costs are usage multiplied by list price, not invoices. Engineering, curation and review effort are not measured.
- Prompt caching lowers repeated-draw cost. Reported cost reflects this run's cache behavior, not a cold-start deployment.

## Files

- `experiments/model_context/`: proposal, accounting, analysis and protocol
- `experiments/model_context/proposals/r1/`: frozen manifest and request bodies
- `scripts/acquire_model_context.py`: one-time dispatcher
- `tests/test_model_context.py`: offline tests
