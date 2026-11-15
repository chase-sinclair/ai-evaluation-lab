# Experiment 006 · scored results

*Scored offline from the sealed one-time run. On November 15 the owner accepted the AI-assisted clarification adjudication without amendment.*

## Answer

**A cheaper model with curated context beat a more expensive model without it, by a wide margin and at about a third of the cost.** Across three draws, `gpt-6-luna` with curated definitions averaged 15.3 correct business decisions out of 36, against 6.7 for `gpt-6.1-sol` with the schema alone. Paired on the same question and draw, the cheaper configuration gained 30 decisions and lost 4.

**The expensive model also benefited from the context, and the two together scored highest.** Sol with curated context averaged 24.0 of 36. That is the best result in either experiment, at 5.7× Luna's cost for the same context.

## Results

Correct business decisions out of 36, three draws per cell, same 36 questions:

| Model | Context | Draw 1 | Draw 2 | Draw 3 | Mean | Usage-priced cost, 108 requests | Cost per correct |
|---|---|---:|---:|---:|---:|---:|---:|
| `gpt-6-luna` | schema | 4 | 4 | 3 | 3.7 | $0.0366 | $0.0033 |
| `gpt-6-luna` | curated | 20 | 14 | 12 | 15.3 | $0.0776 | $0.0017 |
| `gpt-6.1-sol` | schema | 8 | 6 | 6 | 6.7 | $0.2677 | $0.0134 |
| `gpt-6.1-sol` | curated | 26 | 23 | 23 | 24.0 | $0.4433 | $0.0062 |

The same scores split into financial SQL (/32) and required clarifications (/4):

| Cell | SQL by draw (/32) | Clarification by draw (/4) |
|---|---|---|
| Luna · schema | 4, 4, 3 | 0, 0, 0 |
| Luna · curated | 18, 14, 12 | 2, 0, 0 |
| Sol · schema | 6, 5, 5 | 2, 1, 1 |
| Sol · curated | 24, 21, 21 | 2, 2, 2 |

**Paired transitions** compare the same question in the same draw, 108 pairs per comparison:

| Comparison | Gains | Losses | Ties |
|---|---:|---:|---:|
| Luna · curated against Sol · schema | 30 | 4 | 74 |
| Sol · curated against Luna · curated | 32 | 6 | 70 |
| Sol · schema against Luna · schema | 11 | 2 | 95 |
| Context gain within Luna | 36 | 1 | 71 |
| Context gain within Sol | 52 | 0 | 56 |

**Stability across draws** counts the 36 questions by how many of the three draws each cell answered correctly:

| Cell | Correct in all 3 | Correct in 1–2 | Correct in none |
|---|---:|---:|---:|
| Luna · schema | 2 | 4 | 30 |
| Luna · curated | 8 | 14 | 14 |
| Sol · schema | 6 | 2 | 28 |
| Sol · curated | 19 | 9 | 8 |

## What the results show

- **Context mattered more than model tier on this workload.** Adding curated definitions raised each model by more than switching models raised either context level: +11.7 mean for Luna and +17.3 for Sol, against +3.0 (schema) and +8.7 (curated) for switching to Sol.
- **The context gain was nearly one-directional.** Context gained 52 decisions and lost none for Sol. It gained 36 and lost 1 for Luna.
- **Luna with curated context was unstable.** Its draws ranged from 12 to 20. Only 8 questions were correct in all three draws, and 14 were correct in one or two. Experiment 005's single draw for the same configuration (18 of 36) sits near the top of this range. Sol with curated context was steadier, with a range of 23–26 and 19 questions correct in every draw.
- **Cost per correct answer favored context.** Luna with context was the cheapest per correct decision ($0.0017). Sol without context was the most expensive ($0.0134).
- **Sol reasoned far more briefly than Luna.** Its output totaled 23,884 tokens (schema) and 39,937 tokens (curated), against 68,781 and 148,191 for Luna. Total spend was therefore $0.825, well below the $3–6 planning estimate.

## Robustness to the clarification adjudication

Required clarifications contribute at most 4 per draw, and observed credit was 0–2. On financial SQL alone, every ordering above holds. Luna with curated context scored 12–18 of 32 against 5–6 for Sol with schema only. Sol with curated context scored 21–24. Reversing every drafted clarification judgment could not change the headline comparison.

## Method notes

- The acquisition, seal and replay are described in [verification](verification.md). Proposal digest `f9fd35762130871a80c4a24d28dae47a3bf9f500c5d4f7185cb77fe21ba458f0`, seal SHA-256 `54a0290a8aea3b1712e0ff8670e1b16d95b266016051a7640a55c0850d5707c7`.
- SQL ran in the `meridian-worker:v3` sandbox and had to match the typed key on both evaluation snapshots, the same grading as Experiment 005.
- **Clarification adjudication.** Claude drafted judgments on the 17 distinct masked wordings, seeing only question and wording. Nine were judged adequate, and the owner accepted all 17 judgments without amendment. The rubric came from the owner-accepted 005 precedents. Q33 needs both period and cost basis. Q34 needs cost center or scope. Q35 needs both the list-minus-contracted discount and commitment savings named as the alternative. The judgments and a rationale for each are in the ignored files `.verification/model-context-reviewed.json` (SHA-256 `c3cd39772f04bba5c9b8ec7727c870f163948c32bf8422fcf5aa1edb0c1353f4`) and `.verification/model-context-review-notes.json`. The drafter also designed and implemented the study, so this is not an independent adjudication.
- The machine report is `.verification/model-context-report.json`, SHA-256 `4fcf8385ff23ed143b085624704b3964fc66b71e8557d44dbfd12b92b734764e`. Per-request grades are in `.verification/model-context-cases.json`.

## Limitations

These are the limitations accepted in the [design](experiment06_model_context_design.md), plus what the results add:

- The questions were inspected during Experiment 005, so they are not a fresh holdout.
- The warehouse is synthetic.
- The study covers one model family and one reasoning setting. Sol and Luna are different releases (6.1 and 6.0).
- Costs are usage-priced and include this run's caching.
- Three draws describe variation on this workload. They do not support significance claims.
- Luna's curated-context variance means any single-draw figure for that configuration, including Experiment 005's 18, should be read as one sample from roughly 12–20.
