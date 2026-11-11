# Meridian v2 acquisition audit

**Interrupted and sealed on request 47 (Q23, arm C).** The provider returned incomplete/max_output_tokens with 2,048 output tokens, all attributed to reasoning. No terminal SQL or clarification was graded for that request. The reviewed dispatcher stopped immediately. Of 144 planned episodes, 22 started, 21 yielded a terminal decision, one was interrupted and 122 were never started. There were zero retries or resumptions.

Across all arms, 47 Responses requests to gpt-6-luna and 25 local discovery calls used 78,752 input tokens (46,110 cache reads and 12,154 cache writes) and 15,283 output tokens (12,953 reasoning). Total usage-estimated cost, including the incomplete request, was **$0.011670650**. Observed API time summed to 322.429 s; local discovery took 0.021 s.

Recomputed all sealed file hashes and the ledger digest, parsed original response bytes, matched each unique response ID to its ordered request, verified initial and dynamic bodies, replayed the discovery histories, reconciled the charged usage and regraded the four SQL submissions on both source-verified snapshots. The terminal raw provider body SHA-256 is `b323f56ce67a98523ab255eb6a55721fade7eb0b69fc82bdba415b3ee48e1641`.

**Interpretation.** C's Q10 unit-cost query produced the only correct business result. D's Q30 query executed but grouped tag conflicts at project grain before counting resources; the key requires conflicting normalized values within each resource. Two C submissions hit the frozen worker's SQL allowlist. Those rejections leave their financial semantics untested. All 17 clarification replies occurred on designated answerable questions. Arm-masked wording inspection found requests for the calendar year, scope, or interpretation of the reporting metric. These are over-refusals under the frozen rubric; a missing year in the literal question helps explain why clarification could appear reasonable. None of the four required-clarification questions reached any arm, so there was no wording eligible for positive clarification credit. The zeroes against planned denominators below do not measure clarification ability.

Only five questions produced four-way paired observations. Q16 was unsent in every arm, so excluding it changes the planned denominator alone. All 25 discovery calls returned valid records; three D episodes used the entire six-call budget and none produced a correct terminal outcome. This partial prefix cannot establish the preferred context architecture.

The original sealed acquisition supplied all observations below. Each correct SQL decision required a typed result match on both evaluation snapshots. An acquisition interruption or unsent case has no task grade.

| Arm | Evaluable/36 | Correct/36 | SQL-correct/32 | Clarifications/4 | Submitted-SQL | Valid-SQL | Executed-SQL | Wrong-financial | Over-refusals | Inappropriate-SQL | Malformed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| B | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 |
| C | 5 | 1 | 1 | 0 | 3 | 1 | 1 | 0 | 2 | 0 | 0 |
| D | 5 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 4 | 0 | 0 |

| Arm | Requests | Input | Output | Reasoning | Cache-read | Cache-write | Estimated-USD | API-seconds | Discovery-calls | Invalid-discoveries | Tool-seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 5 | 6782 | 1260 | 1104 | 5300 | 1467 | 0.000867875 | 19.363 | 0 | 0 | 0 |
| B | 6 | 13924 | 1390 | 1197 | 11440 | 2466 | 0.001119450 | 31.27 | 0 | 0 | 0 |
| C | 6 | 35440 | 6308 | 5310 | 29370 | 6052 | 0.004206000 | 102.974 | 0 | 0 | 0 |
| D | 30 | 22606 | 6325 | 5342 | 0 | 2169 | 0.005477325 | 168.822 | 25 | 0 | 0.021 |

Paired changes count only questions with terminal decisions in both arms. Gain means the second arm repaired the first; ties include paired failures.

| Comparison | Pairs | Gains | Losses | Ties |
|---|---|---|---|---|
| A→B | 5 | 0 | 0 | 5 |
| A→C | 5 | 1 | 0 | 4 |
| B→C | 5 | 1 | 0 | 4 |
| B→D | 5 | 0 | 0 | 5 |

Excluding Q16 (35 planned per arm): A 0/35, B 0/35, C 1/35, D 0/35. A Q16 pass establishes balanced-ledger output only. D is a separate stateless workflow with user-role discovery records. D completed episode counts by discovery depth (0–6): [0, 0, 0, 1, 1, 0, 3].

| Question | A | B | C | D |
|---|---|---|---|---|
| Q01 | over-refusal | over-refusal | over-refusal | over-refusal |
| Q02 | unsent | unsent | unsent | unsent |
| Q03 | unsent | unsent | unsent | unsent |
| Q04 | unsent | unsent | unsent | unsent |
| Q05 | unsent | unsent | unsent | unsent |
| Q06 | unsent | unsent | unsent | unsent |
| Q07 | over-refusal | over-refusal | SQL rejected | over-refusal |
| Q08 | unsent | unsent | unsent | unsent |
| Q09 | unsent | unsent | unsent | unsent |
| Q10 | over-refusal | over-refusal | correct SQL | over-refusal |
| Q11 | unsent | unsent | unsent | unsent |
| Q12 | unsent | unsent | unsent | unsent |
| Q13 | unsent | unsent | unsent | unsent |
| Q14 | unsent | unsent | unsent | unsent |
| Q15 | unsent | unsent | unsent | unsent |
| Q16 | unsent | unsent | unsent | unsent |
| Q17 | unsent | unsent | unsent | unsent |
| Q18 | unsent | unsent | unsent | unsent |
| Q19 | unsent | unsent | unsent | unsent |
| Q20 | unsent | unsent | unsent | unsent |
| Q21 | unsent | unsent | unsent | unsent |
| Q22 | over-refusal | over-refusal | SQL rejected | over-refusal |
| Q23 | unsent | over-refusal | incomplete | unsent |
| Q24 | unsent | unsent | unsent | unsent |
| Q25 | unsent | unsent | unsent | unsent |
| Q26 | unsent | unsent | unsent | unsent |
| Q27 | unsent | unsent | unsent | unsent |
| Q28 | unsent | unsent | unsent | unsent |
| Q29 | unsent | unsent | unsent | unsent |
| Q30 | over-refusal | over-refusal | over-refusal | wrong result |
| Q31 | unsent | unsent | unsent | unsent |
| Q32 | unsent | unsent | unsent | unsent |
| Q33 | unsent | unsent | unsent | unsent |
| Q34 | unsent | unsent | unsent | unsent |
| Q35 | unsent | unsent | unsent | unsent |
| Q36 | unsent | unsent | unsent | unsent |

Selected execution diagnostics: Q22C unapproved node Exists; Q07C unapproved node Filter

Ledger digest: `e1a4d4768efa33d634ec93a64a0f6e42fca152332d65def2428a539a8b0bb6b3`. Seal file SHA-256: `2df251786ecfad8ababe42bb24ec6eaa0a5c49f35b0e4bd8596c9abe2ae0a820`. The local seal contains individual receipt hashes.
