# Meridian v3 owner review · November 11, 2026

**Review the development pilot first.** The evaluation reserve is **$5.008329** under the proposed $5.50 cap. The separate five-episode pilot reserves **$0.153159625** under $0.17. Both are prospective and unauthorized. Seven development SQL answers passed through the SDK and isolated grader. Actual Luna completion, navigation, latency and financial accuracy under v3 remain unmeasured.

## What happened in v2

The owner accepted commit `c6fb697d359778260fb9f6dcfb5745b18ad0077d` as permanent historical evidence. Read the original response bytes and associated request/event files locally. Recomputed SHA-256 for all 188 files named in the seal and the canonical ledger digest. They match the published seal. No historical candidate was executed, regraded or resumed for this diagnosis. Original configuration, scores, receipts, financial keys and result directory remain as acquired. [Sealed audit](finops_acquisition_audit.md)

The following observations paraphrase the actual terminal messages. The numbered receipt identifies its original bytes in the ignored local acquisition. Arm letters are the historical assignment.

| Question | Arm and receipt | What the reply asked to clarify |
|---|---|---|
| Q01 | B 011, D 019, A 020 | Which March (B), or which year for March (D and A). |
| Q01 | C 012 | Whether March meant invoice posting month or charge usage day. |
| Q07 | D 032, B 034 | Which year for June and July. |
| Q07 | A 033 | Both the year and the SKU ID denoted by X. |
| Q10 | A 036, B 037 | Which year's June. |
| Q10 | D 045 | Both the year and the entity meant by Atlas. The model said the catalog results did not identify them. |
| Q22 | D 026, A 027, B 028 | Which year's July. |
| Q23 | B 046 | Which June, and whether before/after referred to the parts of that month around the handoff. |
| Q30 | A 001, B 002 | Which year for September 30. |
| Q30 | C 003 | Whether conflict was across project resources or within a resource, and whether the affected field counted resources. |

**Inference.** Twelve replies asked only which month/year to use, three coupled that issue with a second question, and two asked about clock or grain alone. The v2 as-of date established a cutoff but gave no common default year. This is a plausible explanation for the first 15, including B 011's less specific wording. It cannot explain all 17. The receipts reveal what was requested, not an internal causal chain. Some bindings were harder in particular arms. A received DDL only, including no X-to-ID glossary. Q10D spent six valid calls, searched for Atlas, received an empty catalog result, and inspected team examples. The public catalog searches metadata; a name can instead be resolved in a query if a corresponding name field exists. Q01C had access to the closing convention and Q30C had label definitions, yet still asked about interpretation. Preserve this residual measurement uncertainty.

| Receipt | Observation | Implication for v3 |
|---|---|---|
| Q07C 035 | Used conditional aggregates with FILTER in a CTE. Historical validator stopped at the Filter AST node. | Support aggregate predicates and validate their descendants. |
| Q22C 021 | Used a correlated NOT EXISTS subquery. Historical validator stopped at Exists. | Support existence predicates with scoped relation and expression checks. |
| Q23C 047 | Provider reported incomplete/max_output_tokens after 29.358 s, 5,913 input and 2,048 output, all 2,048 reasoning. Four reasoning items, no visible answer. | Account for reasoning before visible output and allow a longer read. Required completion length is unknown. |

Neither rejected query reached DuckDB in the historical grader. Their business correctness remains unknown. The 60 s HTTP timeout did not cause Q23C. A complex ownership question may have required more reasoning, but the receipt cannot establish why or how much more. The largest completed v2 response used 1,446 output tokens. The interruption, after 21 completed episodes, prevented 122 episodes from starting.

## Prospective changes

| Component | v2 | v3 |
|---|---|---|
| Shared context | UTC as of January 31, 2026 | Identical new developer preamble in A/B/C/D, including every later D turn. Ordinary month/day and named quarters use historical reporting year 2025. Explicit years, fiscal periods and separately documented January 2026 postings retain their meaning. An omitted reporting period remains unspecified. |
| Interpretation | Existing field and clarification instructions | Use available wording, fields and metadata for the clock, entity and grain. Permit named-value lookup in SQL and suggest following catalog/description links. No question IDs, answer values, SQL templates or private keys in the preamble. |
| Worker | Narrow frozen allowlist | Scoped physical relations, correlated EXISTS/NOT EXISTS, aggregate FILTER, QUALIFY, conditional averages/counts, windows, deterministic scalar/date functions and null-safe comparisons. |
| Responses | 2,048 output tokens, 60 s timeout | 25,000 total output per request, medium reasoning, 900 s read inactivity, 10 s connect/pool, 30 s write, zero retries. |
| Design | 36 questions × 4 arms, 22 tables, 2 evaluation snapshots | Same questions, aliases, ordering, sources, Python/SQL oracle bindings, matched grading and discovery tools. New developer-message hashes, archives, budgets, approval identities and result paths. |

The year rule supplies no period or cost basis for Q33, reporting scope for Q34, savings definition for Q35 or denominator/SKU for Q36. An explicit month in Q35 can be located while its savings interpretation remains open. An as-of reference in Q36 can locate the quarter while its unit remains open. Retain the existing independent interpretation witnesses and blinded wording review. Retain Q16 sensitivity and treat D versus B as a separate architecture comparison. **V3 is a failure-informed follow-up.** Reusing the evaluation questions after inspecting the v2 prefix precludes an untouched holdout interpretation. [Shared instructions](../experiments/finops_sql/v3/reporting.md) · [Analysis and approval protocol](../experiments/finops_sql/v3/protocol.md) · [Oracle review packet](experiment05_oracle_review_v2.md)

### SQL admission and sandbox

DuckDB 1.4 defines FILTER as a row condition local to an aggregate. EXISTS and NOT EXISTS test whether a subquery returns any rows. Both support useful analytical formulations without adding a file, network or mutation operation. The safety decision therefore depends on validating every nested expression and source. [DuckDB 1.4 FILTER](https://duckdb.org/docs/1.4/sql/query_syntax/filter) · [DuckDB 1.4 subqueries](https://duckdb.org/docs/1.4/sql/expressions/subqueries)

The new worker permits explicit AST classes and deterministic built-in functions. It walks the descendants of predicates, aggregate conditions, subqueries and window expressions, resolves base relations through CTE scopes and executes the rendered, validated tree. The 65,536-byte query limit and single SELECT/UNION root remain. Its image inherits the pinned DuckDB 1.4.4 / SQLGlot 28.10.1 checkpoint worker. Container invocation retains an unprivileged user, read-only filesystem and database mount, no network or capabilities, process/CPU/memory limits, locked DuckDB configuration, no external access or extensions, a disposable process with five seconds per query, and row and byte limits. SQL admission, execution and typed business correctness remain distinct decisions. [Worker](../experiments/finops_sql/v3/worker.py) · [Grader](../experiments/finops_sql/v3/grading.py)

The development compatibility corpus covers ten alternative read-only formulations, including correlated and nested subqueries, case-insensitive CTE references, conditional aggregates, date arithmetic, window navigation, null-safe comparisons and UNION ALL. Negative fixtures exercise mutations, multiple statements, external/unknown/qualified relations, catalog access, extension/configuration commands, nondeterministic functions inside predicates, recursion, internal row identifiers, query size and result limits. The tests use synthetic and development queries, separate from the 47 historical model replies. Unsupported constructs can still be rejected. [Compatibility tests](../tests/test_finops_v3.py)

## Development evidence and pilot

Ran all eight original development questions through all four versioned request configurations with SDK MockTransport. Seven distinct scripted SQL answers were parsed from the wire replies, executed once each in the v3 Docker worker on the source-verified development database and compared with pre-existing development outputs. Compared column names, types and unordered rows. The database hash was the same before and after. D08 produced a scripted clarification on scope and cost basis. No evaluation cases were used to calibrate these tasks.

| Task | Development check | D calls |
|---|---|---:|
| D01 | Ordinary January invoice postings, filtered sum after deduplication | 3 |
| D02 | Extra February deliveries, window rank and invoice clock | 3 |
| D03 | Explicit January 2026 postings for 2025 usage, correlated subquery | 3 |
| D04 | February pool allocation, weights, grouped and windowed totals | 3 |
| D05 | Effective-dated owners on January 1, 2025 | 3 |
| D06 | June–July regional rate change, joined usage, quantities and two aggregate filters | 4 |
| D07 | January 31 normalized tag conflicts; this snapshot's expected result is empty | 3 |
| D08 | A month with a known year leaves the spending entity and basis unresolved | 4 |

All D selections in the final rehearsal used previously disclosed IDs or glossary links. An initial D08 script requested an undisclosed glossary ID. Obtaining its cross-reference through an additional table description fixed that script without weakening the discovery rules. Synthetic 3,000-token telemetry tested accounting above the old limit. Neither those tokens nor the scripted SQL are Luna observations. The existing references provide the development comparison; D07's empty result alone gives weak discrimination. [Rehearsal and private development fixtures](../experiments/finops_sql/v3/development.py)

**Recommend a separate paid pilot before authorizing evaluation.** Its five frozen episodes are D01A, D03B, D04C, D06D and D08B. They cover both January interpretations, multi-step aggregation, discovery and retained ambiguity. At most 11 requests, 6 discoveries, 125,277 input allowance and 275,000 output tokens. Exact reserve **$0.153159625**, proposed cap **$0.17**, approval digest `1e89f432dd61667ada0743d42d301142313513bb126438231d49c788b3ac20f8`. Review five terminal decisions, four SQL contracts, D08 wording, actual latency, usage partitions and navigation before considering the full acquisition. Pilot and evaluation have independent budgets and single-use destinations. [Pilot manifest](../experiments/finops_sql/proposals/v3/development/manifest.json)

## 25,000 tokens and acquisition reserve

OpenAI documents a 128,000-token output maximum, a 1,050,000-token context window, medium reasoning, and Responses function calling for GPT-6 Luna. Its reasoning guide describes 25,000 as starting headroom shared between reasoning and visible output. The largest v3 evaluation input allowance is 27,730, leaving ample context headroom with 25,000 output. The request asks only for the terminal JSON or a discovery call. There is no target reasoning length. [Luna model limits](https://developers.openai.com/api/docs/models/gpt-6-luna) · [Reasoning and incomplete output](https://developers.openai.com/api/docs/guides/reasoning)

The longer read timeout is a design choice. Scaling Q23C's observed duration linearly to 25,000 tokens gives roughly six minutes; a single cutoff observation cannot predict the latency distribution. A 900-second read window allows for slower generation and queuing and applies per read, rather than imposing an end-to-end deadline. Preserve operator interruption and immediate stop on timeout or uncertain delivery. A partial reply may incur charges even if it has no visible content; record uncertainty and seal the attempt. Mock tests check the SDK's actual HTTP timeout options and one-attempt interruption. Live model access, credit and project request/token limits require reconfirmation.

The full archive binds 144 exact initial bodies and the deterministic constructor for up to 216 additional D bodies. Each turn reserves canonical serialized body bytes plus 256 framing tokens. A later D body reserves up to 2,048 escaped bytes per prior discovery record; the seventh uses the smaller tool-free envelope. Byte counts and cl100k tokenization are offline proxies. A billing allowance breach or unknown partition stops dispatch. Unused future D turns release reserve only after a terminal decision. Prices per million tokens are $0.10 ordinary input, $0.01 cache reads, $0.125 for 30-minute writes and $0.50 output. The bound assumes every input token is charged at the highest approved input rate. [Standard pricing](https://developers.openai.com/api/docs/pricing)

| Arm | Max requests | Input allowance | Output ceiling | Reserve USD |
|---|---:|---:|---:|---:|
| A | 36 | 265,680 | 900,000 | 0.483210 |
| B | 36 | 446,472 | 900,000 | 0.505809 |
| C | 36 | 996,552 | 900,000 | 0.574569 |
| D | 252 | 2,357,928 | 6,300,000 | 3.444741 |
| Total | 360 | 4,066,632 | 9,000,000 | **5.008329** |

Input reserve is $0.508329 and output reserve is $4.50, leaving **$0.491671** under the proposed $5.50 cap. Evaluation approval digest `1b3a5529069e19c9d219a58d4891c39c4fb51676a7ef548a482bd59ddddb61b1`. Digest possession conveys no authority. The proposed destinations are `results/meridian-v3-development-once` and `results/meridian-v3-evaluation-once`. The v3 deliverable freezes the proposals, grader, accounting and mock rehearsal. A reviewed v3 live dispatch integration and explicit cohort-specific authorization, credit and limits confirmation are outstanding. The historical dispatcher enforces the old identity and 2,048-token ceiling. [Evaluation manifest](../experiments/finops_sql/proposals/v3/evaluation/manifest.json) · [Offline proposal constructor](../experiments/finops_sql/v3/proposal.py)
