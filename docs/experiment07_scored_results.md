# Experiment 007 · scored results

*Scored offline from the sealed one-time run. The owner reviewed all clarification wordings, masked, item by item. Claude drafted none of them.*

## Answer

**The finding replicated on Claude models. Every pre-registered criterion held.** `claude-haiku-5-5` with curated definitions beat `claude-sonnet-5-5` with the schema alone in all three draws: 16, 17 and 18 against 8, 8 and 10. It did so at 23% of Sonnet's usage-priced cost. Curated context raised each model in every draw. Paired on the same question and draw, the cheaper configuration gained 32 decisions and lost 7.

**Where the providers differed was the expensive model with context.** On GPT models, Sol with curated context clearly led (24.0 against Luna's 15.3). On Claude models, Sonnet with curated context finished nearly level with Haiku: 18.0 against 17.0, with 22 paired gains and 19 losses. Part of that gap is output format. Sonnet broke the required answer format on 18 of its 108 curated-context answers, and the frozen rules score those as incorrect.

## Pre-registered criteria

| Criterion | Result |
|---|---|
| Primary: Haiku · curated outscores Sonnet · schema in every draw | **Held**: 16 > 8, 17 > 8, 18 > 10 |
| Secondary: context raises each model in every draw | **Held**: Haiku 1→16, 1→17, 2→18. Sonnet 8→19, 8→18, 10→17 |
| Secondary: paired gains exceed losses, Haiku · curated against Sonnet · schema | **Held**: 32 gains, 7 losses, 69 ties |

## Results

Correct business decisions out of 36, three draws per cell, with the same questions and order as Experiment 006:

| Model | Context | Draw 1 | Draw 2 | Draw 3 | Mean | Usage-priced cost, 108 requests | Cost per correct |
|---|---|---:|---:|---:|---:|---:|---:|
| `claude-haiku-5-5` | schema | 1 | 1 | 2 | 1.3 | $0.0415 | $0.0104 |
| `claude-haiku-5-5` | curated | 16 | 17 | 18 | 17.0 | $0.1231 | $0.0024 |
| `claude-sonnet-5-5` | schema | 8 | 8 | 10 | 8.7 | $0.5390 | $0.0207 |
| `claude-sonnet-5-5` | curated | 19 | 18 | 17 | 18.0 | $0.9055 | $0.0168 |

The same scores split into financial SQL (/32) and required clarifications (/4), with malformed answers counted across all three draws:

| Cell | SQL by draw (/32) | Clarification by draw (/4) | Malformed answers (/108) |
|---|---|---|---:|
| Haiku · schema | 0, 0, 1 | 1, 1, 1 | 6 |
| Haiku · curated | 15, 16, 18 | 1, 1, 0 | 11 |
| Sonnet · schema | 8, 8, 10 | 0, 0, 0 | 9 |
| Sonnet · curated | 18, 17, 16 | 1, 1, 1 | 18 |

**Paired transitions** compare the same question in the same draw, 108 pairs per comparison:

| Comparison | Gains | Losses | Ties |
|---|---:|---:|---:|
| Haiku · curated against Sonnet · schema | 32 | 7 | 69 |
| Sonnet · curated against Haiku · curated | 22 | 19 | 67 |
| Sonnet · schema against Haiku · schema | 25 | 3 | 80 |
| Context gain within Haiku | 49 | 2 | 57 |
| Context gain within Sonnet | 35 | 7 | 66 |

**Stability across draws** counts the 36 questions by how many of the three draws each cell answered correctly:

| Cell | Correct in all 3 | Correct in 1–2 | Correct in none |
|---|---:|---:|---:|
| Haiku · schema | 1 | 1 | 34 |
| Haiku · curated | 8 | 16 | 12 |
| Sonnet · schema | 8 | 2 | 26 |
| Sonnet · curated | 13 | 9 | 14 |

## Across both providers

The four price-matched pairs on the same questions, as mean correct out of 36 over three draws:

| Configuration | GPT models (006) | Claude models (007) |
|---|---:|---:|
| Cheap model, schema | 3.7 | 1.3 |
| Cheap model, curated | 15.3 | 17.0 |
| Expensive model, schema | 6.7 | 8.7 |
| Expensive model, curated | 24.0 | 18.0 |
| **Cheap + curated beat expensive + schema in every draw** | **Yes** | **Yes** |
| Total usage-priced cost, 432 requests | $0.825 | $1.609 |

This table is descriptive. Effort settings, tokenizers and caching lifetimes are not calibrated across providers, and the prompts were developed on GPT models. Differences between the columns are not a ranking of providers. What the table shows is that the decision-relevant pattern, context before model tier, held on both.

## Post-hoc sensitivity: output format

*This analysis was added after the run and is not pre-registered. It does not replace the results above.*

The instructions require exactly one JSON object. Claude broke that contract in 44 of 432 answers: 17 wrapped the JSON in a markdown code block, 16 put an explanation before it, and 11 added text after it. GPT models were scored under the same rule in 006. To separate format compliance from financial correctness, `experiments/claude_context/sensitivity.py` re-scored only those 44 answers, reading the first JSON object the frozen parser accepts. That recovered 26 SQL answers and 18 clarifications, which added three wordings. The owner reviewed those too and judged all three adequate.

| Cell | Official mean | Format-lenient mean | Format-lenient draws |
|---|---:|---:|---|
| Haiku · schema | 1.3 | 2.3 | 2, 2, 3 |
| Haiku · curated | 17.0 | 19.0 | 20, 19, 18 |
| Sonnet · schema | 8.7 | 8.7 | 8, 8, 10 |
| Sonnet · curated | 18.0 | 22.7 | 24, 22, 22 |

Under lenient extraction the primary criterion still holds in every draw: 36 gains and 5 losses for Haiku · curated against Sonnet · schema. Sonnet with curated context would then lead Haiku by 3.7, closer to the GPT pattern. The format failures cost Sonnet about 4.7 correct decisions per draw with curated context. For a deployment, that argues for structured outputs or a tolerant parser on Claude models. It is not evidence about financial reasoning.

## Method notes

- The acquisition, seal and replay are described in [verification](verification.md). Proposal digest `1d0f60453140362f1f0ddc50a089066d80b093ccac14e2c063d3074447affdef`, seal SHA-256 `001c7e32205a1d8e1938223fd80fae69d37d8d52425413e59f456248c55c9012`.
- SQL ran in the `meridian-worker:v3` sandbox and had to match the typed key on both evaluation snapshots, the same grading as 005 and 006.
- **Clarification adjudication.** The owner reviewed 11 masked wordings for the official score: 8 adequate and 3 not adequate. Each of the 3 offered list minus contracted but did not explicitly name commitment savings, and the owner noted that a commitment-applied amount is not necessarily equivalent to commitment savings. The owner also reviewed 3 wordings for the sensitivity score, all adequate. No 006 judgment carried over, because no wording matched exactly.
- Ignored local evidence:
  - Report: `.verification/claude-context-report.json`, SHA-256 `e69151b3567ea7288ae69ba69e47dbcb14988c893f19c59dc6c0bd3ac9bc6ef5`
  - Sensitivity: `.verification/claude-context-sensitivity.json`, SHA-256 `af208cec22652eedd12320f7df289f9a99cacf9d212d7e3537983193cce70611`
  - Reviewed worksheets: `74d8643f50a3cb0794069c4f441efd855a4549a1d04624b2e3eac3b3bf50245c` (official) and `b1f4ab709dfd3efc39ba44067b091dec79f3c160913eed0a2766a82a9bc4fa0a` (sensitivity)
  - Per-request grades: `.verification/claude-context-cases.json`

## Limitations

These are the limitations accepted in the [design](experiment07_claude_replication_design.md), plus what the results add:

- The questions are development-exposed.
- The warehouse is synthetic.
- Settings are not calibrated across providers, and the prompts were developed on GPT models.
- Costs are usage-priced and include this run's caching.
- Three draws describe variation. They do not support significance claims.
- Claude designed and implemented the study. SQL grading is automatic, and the owner made every clarification judgment.
- The format-lenient analysis was chosen after seeing the malformed answers, so it is descriptive only.
