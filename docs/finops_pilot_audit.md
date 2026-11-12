# Experiment 005 · sealed v3 development pilot

All five development episodes completed once from the approved clean revision `b2e15eb3610455e15e634836b439b80bff193203`. The operator confirmed credit above $0.17 and sufficient organization/project spending permissions and accepted fail-stop handling of unknown rate-limit headers. The reviewed dispatcher revalidated the proposal and model access using the standard global endpoint. Published standard rates matched the approved schedule. The result directory is consumed. No retries, substitutions, interruption or unaccounted attempts.

| Episode | Terminal decision and offline result |
|---|---|
| D01A | SQL admitted and executed. It targeted January 2025 but used 202501 for the invoice posting-month field. The warehouse uses 1 for that January. SUM returned NULL against expected $427,547.01. This is a period-encoding error and a financial miss. |
| D03B | Asked which cost basis to use for the explicitly dated postings. The original contract expects billed postings of −$300.00. Over-refusal, with no SQL to grade and no observed wrong-year predicate. |
| D04C | SQL admitted and executed. Used February 2025 and allocated $19,707.408 and $13,138.272 to centers 0 and 1. Both rows reconciled to the $32,845.68 total and matched the financial contract. |
| D06D | SQL admitted and executed. Used June and July 2025, with the correct SKU and West region. Returned a 0.040000 increase, matching the reference at six decimals. Used scheduled rates directly; the reference computes realized contracted cost per unit. The output match on this snapshot does not establish equivalence under other data. |
| D08B | Correctly requested clarification and explicitly distinguished billed and effective cost. Neither the wording nor the declared dimensions asked which entity Finance covers. Incomplete under the two-dimension contract. |

Three SQL submissions, all valid and executable. Two correct financial results across four expected SQL episodes. Two clarification decisions, including one on an answerable task. Two of five decisions met their complete business contract. No unsafe or unsupported SQL rejection occurred.

D06 used three catalog searches and three describe calls in this order: catalog for contracted rates, describe price_schedule/commitment/sku, catalog for glossary and geographic terms, catalog for @codes, describe @codes, describe region. Each selection reproduced from the prior public disclosures. No invalid or oversized result. The seventh request had tools disabled and returned SQL with FILTER. All other episodes finalized on the first request.

| Episode | Requests | Input | Cache read | 30m write | Output | Reasoning | Estimated USD | API seconds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D01A | 1 | 1,496 | 0 | 1,493 | 763 | 644 | 0.000568425 | 10.950 |
| D03B | 1 | 2,464 | 0 | 2,461 | 224 | 186 | 0.000419925 | 3.185 |
| D04C | 1 | 6,050 | 0 | 6,047 | 744 | 516 | 0.001128175 | 8.394 |
| D06D | 7 | 6,075 | 0 | 1,045 | 1,489 | 1,109 | 0.001378125 | 21.709 |
| D08B | 1 | 2,458 | 2,433 | 22 | 227 | 192 | 0.000140880 | 2.892 |
| Total | 11 | 18,543 | 2,433 | 11,068 | 3,447 | 2,647 | 0.003635530 | 47.130 |

D06 local discovery took 0.002614 s in total. Cache columns are subsets of input; reasoning is included in output. Repriced usage at the approved per-million rates ($0.10 ordinary input, $0.01 reads, $0.125 writes, $0.50 output). This is an estimate from receipts, without invoice reconciliation. [Standard pricing](https://developers.openai.com/api/docs/pricing)

## Verification and decision

Rehashed all 56 files covered by the seal and recomputed the ordered ledger digest. Matched the five frozen initial requests, all six dynamic bodies, prior histories, exact wire payloads, 11 distinct response IDs, parsed/raw responses, terminal messages and tool records. Independently reconciled input/output bounds, usage partitions, individual charges and total to the seal. Compared admitted queries on the source-verified development snapshot against its original hash-bound keys with equivalent numeric types, financial precision to cents and rates to six decimals. Database digest agreed before and after execution. Used isolated v3 worker image `sha256:c50b100afbc0be5f15f60f82baca751b2d185c6512ccdccc50f2548f344ba9d7`.

Ledger digest `60aa0f81c5de2f37b585720fe396213ccde2f7e40574f8543f92e574aeb6f7e7`. Seal file SHA-256 `97371d4045c532b1fd9c2b433c3372a31847e7b8eccc159e373b5c0dd945a96a`. All raw evidence stays in the ignored single-use directory.

**Recommendation.** The pilot demonstrated operational feasibility of bounded acquisition, including maximum-depth discovery, terminal SQL, receipt accounting and isolated grading. Proceed to owner review of full-evaluation implementation readiness. The 144-outcome acquisition still needs a separately reviewed dispatcher and authorization. Five development episodes cannot establish full-run completion probability or evaluation accuracy. Retain the observed business errors for interpretation and keep the frozen prompts and keys. No further inference was dispatched.
