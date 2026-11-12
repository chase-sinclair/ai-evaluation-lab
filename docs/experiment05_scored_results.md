# Experiment 005 v3 · offline architectural review

B (curated context) and C (expanded context) each met 18/36 business contracts, compared with 1/36 for A (schema only). C gained four questions over B and lost four others. D (bounded stateless discovery) met 5/36, including two required clarifications. These are paired observations on a single acquisition.

| Arm | Policy /36 | Financial SQL /32 | Clarification /4 | Excluding Q16 /35 |
|---|---|---|---|---|
| A | 1 | 1 | 0 | 1 |
| B | 18 | 17 | 1 | 17 |
| C | 18 | 17 | 1 | 17 |
| D | 5 | 3 | 2 | 4 |

Q16 is a balanced-ledger output task on which invoice controls can reproduce the expected result. Removing it costs B, C and D one success each and leaves the ranking unchanged.

| Arm | Submitted SQL | Admission failures | Admitted | Failed after admission | Executed | Wrong financial result on answerable SQL | SQL on ambiguous case | Over-refusals | Incomplete clarifications | Malformed |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 7 | 2 | 5 | 0 | 5 | 4 | 0 | 25 | 4 | 0 |
| B | 27 | 7 | 20 | 0 | 20 | 2 | 1 | 6 | 2 | 0 |
| C | 24 | 5 | 19 | 0 | 19 | 1 | 1 | 9 | 2 | 0 |
| D | 8 | 1 | 7 | 1 | 6 | 3 | 0 | 20 | 0 | 6 |

An over-refusal is a clarification on an answerable question. Incomplete clarification counts apply to clarification submissions on ambiguous questions. D also returned malformed decisions on Q35 and Q36. SQL submitted on ambiguous questions is counted separately from wrong financial results.

## Paired changes

### A to B

- Gain (17): Q01, Q04, Q05, Q06, Q07, Q09, Q10, Q16, Q17, Q18, Q19, Q22, Q25, Q26, Q29, Q30, Q33
- Loss (0): none
- Tie (19): Q02, Q03, Q08, Q11, Q12, Q13, Q14, Q15, Q20, Q21, Q23, Q24, Q27, Q28, Q31, Q32, Q34, Q35, Q36

### A to C

- Gain (17): Q01, Q03, Q04, Q05, Q06, Q09, Q10, Q16, Q17, Q20, Q21, Q22, Q25, Q26, Q27, Q29, Q33
- Loss (0): none
- Tie (19): Q02, Q07, Q08, Q11, Q12, Q13, Q14, Q15, Q18, Q19, Q23, Q24, Q28, Q30, Q31, Q32, Q34, Q35, Q36

### B to C

- Gain (4): Q03, Q20, Q21, Q27
- Loss (4): Q07, Q18, Q19, Q30
- Tie (28): Q01, Q02, Q04, Q05, Q06, Q08, Q09, Q10, Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q22, Q23, Q24, Q25, Q26, Q28, Q29, Q31, Q32, Q33, Q34, Q35, Q36

### B to D · separate workflow comparison

- Gain (1): Q34
- Loss (14): Q01, Q02, Q04, Q05, Q06, Q07, Q09, Q10, Q17, Q19, Q25, Q26, Q29, Q30
- Tie (21): Q03, Q08, Q11, Q12, Q13, Q14, Q15, Q16, Q18, Q20, Q21, Q22, Q23, Q24, Q27, Q28, Q31, Q32, Q33, Q35, Q36

Q01A used March charge days for net billed cost, a usage clock where the contract requires the invoice posting clock. B and C passed on both snapshots. On Q20, B selected month_id 202508 for the August allocation, while the warehouse uses 8. Its SQL executed and failed on both snapshots; C passed. B also lost Q21 at the SQL allowlist (TimeToStr). In the opposite direction, C lost Q07 at the Values node and asked for clarification on Q18, Q19 and Q30; B met all four contracts. A grammar rejection leaves the financial semantics of that submission untested.

On Q34, B and C supplied SQL despite unspecified scope. D explicitly asked whether to include all cost centers or one center and declared scope, producing its only paired gain over B. D lost fourteen other cases. Q29D was the only admitted SQL query that failed during execution. DuckDB could not bind the proposed usage_date column on either snapshot.

## Clarification adjudication

Eleven distinct question/wording entries received five adequate and six inadequate independent judgments. They map to twelve clarification episodes on required-clarification questions: five had adequate wording and seven inadequate wording. Four earned credit: Q33B, Q33C, Q33D and Q34D. Q33A also had adequate wording, but declared scope in addition to the required period and cost basis. On Q35, A/B/C named the expected savings-basis dimension but all three wordings were judged inadequate. Neither wording nor dimension labels alone establish credit.

## Usage and observed latency

| Arm | Requests | Input | Cache reads | 30m writes | Output | Reasoning | USD estimate | API seconds | Tool seconds |
|---|---|---|---|---|---|---|---|---|---|
| A | 36 | 54071 | 52920 | 1043 | 19802 | 16954 | 0.010571375 | 196.692 | 0 |
| B | 36 | 88739 | 87588 | 1043 | 52947 | 42464 | 0.027490555 | 518.762 | 0 |
| C | 36 | 217835 | 216684 | 1043 | 35670 | 26673 | 0.020143015 | 403.693 | 0 |
| D | 242 | 215647 | 33574 | 48189 | 51376 | 42276 | 0.045435765 | 738.046 | 0.102358 |

Cache reads and writes partition input; reasoning is included in output. C used more input than B but fewer output tokens, costing less at the observed cache rates. D used 242 HTTP requests, accounted for $0.045435765 of the total $0.103640710 and incurred 738.046 seconds of cumulative API time. Local discovery took 0.102358 seconds. Of 36 D episodes, one used one discovery, one used two, one used five and 33 used all six. Five of 206 selections returned the generic invalid-or-oversized response, all on describe calls (Q07, Q15, Q20, Q30 and Q31). Budget saturation is observable; its causal effect on correctness was not isolated.

## Case-level scoring ledger

Each cell identifies the disposition and whether it satisfied the entire contract. SQL is graded on both independent evaluation snapshots.

| Question | A | B | C | D |
|---|---|---|---|---|
| Q01 | SQL failed contract | sql pass | sql pass | clarify fail |
| Q02 | sql pass | sql pass | sql pass | malformed fail |
| Q03 | SQL rejected | clarify fail | sql pass | clarify fail |
| Q04 | SQL rejected | sql pass | sql pass | clarify fail |
| Q05 | SQL failed contract | sql pass | sql pass | SQL failed contract |
| Q06 | SQL failed contract | sql pass | sql pass | clarify fail |
| Q07 | clarify fail | sql pass | SQL rejected | clarify fail |
| Q08 | clarify fail | SQL rejected | SQL rejected | clarify fail |
| Q09 | clarify fail | sql pass | sql pass | malformed fail |
| Q10 | clarify fail | sql pass | sql pass | malformed fail |
| Q11 | clarify fail | clarify fail | clarify fail | clarify fail |
| Q12 | clarify fail | clarify fail | clarify fail | clarify fail |
| Q13 | clarify fail | SQL rejected | SQL rejected | clarify fail |
| Q14 | clarify fail | SQL rejected | SQL rejected | clarify fail |
| Q15 | clarify fail | SQL rejected | SQL rejected | clarify fail |
| Q16 | SQL failed contract | sql pass | sql pass | sql pass |
| Q17 | clarify fail | sql pass | sql pass | SQL failed contract |
| Q18 | clarify fail | sql pass | clarify fail | sql pass |
| Q19 | clarify fail | sql pass | clarify fail | clarify fail |
| Q20 | clarify fail | SQL failed contract | sql pass | clarify fail |
| Q21 | clarify fail | SQL rejected | sql pass | SQL rejected |
| Q22 | clarify fail | sql pass | sql pass | sql pass |
| Q23 | clarify fail | SQL failed contract | clarify fail | clarify fail |
| Q24 | clarify fail | SQL rejected | SQL failed contract | clarify fail |
| Q25 | clarify fail | sql pass | sql pass | clarify fail |
| Q26 | clarify fail | sql pass | sql pass | clarify fail |
| Q27 | clarify fail | clarify fail | sql pass | clarify fail |
| Q28 | clarify fail | SQL rejected | clarify fail | clarify fail |
| Q29 | clarify fail | sql pass | sql pass | execution failed |
| Q30 | clarify fail | sql pass | clarify fail | clarify fail |
| Q31 | clarify fail | clarify fail | clarify fail | malformed fail |
| Q32 | clarify fail | clarify fail | clarify fail | SQL failed contract |
| Q33 | clarify fail | clarify pass | clarify pass | clarify pass |
| Q34 | clarify fail | SQL failed contract | SQL failed contract | clarify pass |
| Q35 | clarify fail | clarify fail | clarify fail | malformed fail |
| Q36 | clarify fail | clarify fail | clarify fail | malformed fail |

## Integrity and limitations

All 144 planned outcomes were terminal and reconciled to 350 unique requests and 206 discovery records. Zero exhausted, interrupted, unsent or unaccounted attempts. The source checkout differed from approved scorer 46c15339f9dcbe767ae7e3dba6cd986ee2099205 only in progress and verification documentation. Verified all 1,751 sealed files and replayed the receipt ledger. The original worksheet remained intact; the copied review had exactly the same identifiers, questions and wordings, with only Boolean adequacy decisions changed.

| Artifact | SHA-256 or canonical ledger digest |
|---|---|
| Original worksheet | affd0375b0f3da89e2873aa9722ff628e69add15623a24852fc5a8826ef4982e |
| Completed review | 08d44429c4293e9b61e3b03f9a6b864051baee61df34c54a52e5e1bbb2352fff |
| Seal | 5f136beda3c3cdd97d3daa55e4e174b746594b5b2492a1f56099ae5f5d5bec79 |
| Ledger | ba05d8c60ce0dd58043c044d7a39e276a76f5a1b8668f891c0355237188b3c4b |
| Isolated v3 image | c50b100afbc0be5f15f60f82baca751b2d185c6512ccdccc50f2548f344ba9d7 |
| Verified evaluation A database | 4bab9a49c8222ea0864cdf647536f655cb824fa6327040b81d395f1c0423a3e2 |
| Verified evaluation B database | 4e8252dbd761fd4fccd303f17ce231486806f6890c9086ac24d7cadf25a0820d |
| Machine report | d6986bcf9d2f5b509e4f36af1c29d9c745ed3e5c7348117f238a61d6168399f4 |

The frozen command checked source manifests, warehouse CSVs, economic streams, per-question financial key bindings and database identity around isolated execution. This synthetic warehouse tests output agreement on two snapshots, not general SQL equivalence. Only four questions required clarification. Each question/condition was sampled once; neither repeated-run variability nor a causal effect of context size alone can be estimated. V3 reused questions after inspecting the v2 prefix. Historical and pilot observations are excluded. Costs are usage estimates and latency is observed API time. Architecture selection and publication remain pending owner review.
