# Meridian SQL · offline acquisition-readiness review

**Owner decision requested.** Review the report fields, oracle packet, bounded discovery contract and exact proposal before considering live acquisition. The proposal reserves **$0.842857750** against a proposed **$1.00** ceiling. The only inference transport implemented for this checkpoint is local HTTP simulation. A credentialed model-catalog lookup confirmed account visibility for `gpt-6-luna` on November 10, 2026. No inference was dispatched. [Reviewer packet](experiment05_oracle_review.md) · [Manifest](../experiments/finops_sql/proposals/v1/manifest.json) · [Exact initial bodies, gzip JSON array](../experiments/finops_sql/proposals/v1/bodies.json.gz)

## What is fixed

The 36 question texts, both economic snapshots, reference SQL, Decimal calculations and sandbox resource settings come from the accepted checkpoint. There are 144 paired question/arm outcomes and at most 360 requests. A seeded question order and rotating arm order place each arm in each ordinal position nine times. Each question/arm starts a fresh episode. The shared Responses builder specifies standard tier (`default`), medium reasoning, 2,048 maximum output tokens, `store=false`, and a 30-minute cache policy. The user message contains the original question and an ordered SQL display-field list for **every** question, including clarification cases. The field list sets aliases and presentation shape. The same clarification option and dimension vocabulary apply throughout. No question ID, worked calculation, expected disposition or numeric key is serialized. [Approved design](experiment05_sql_context_design.md) · [Request builder](../experiments/finops_sql/episode.py)

| Arm | Public context delivery | Actual context bytes | Context tokens¹ |
|---|---|---:|---:|
| A | Named structural DDL block with all 22 tables and declared keys | 4,675 | 1,078 |
| B | A followed by curated grains, metrics, joins and policy in that order | 9,556 | 2,044 |
| C | Exact B prefix followed by full dictionary, lineage, operations and development sample registry | 23,356 | 5,605 |
| D | Empty initial context; bounded discovery tools | 0 | 0 |

Each file uses UTF-8, LF, a named delimiter and stable JSON where applicable. The manifest records individual file hashes, lengths, actual token counts, package hashes and each complete initial request in dispatch order. Examples are the first three rows in each deterministic development export, in source order and original CSV string representation. They are included as public synthetic examples in C; D can request those same rows. A/B/C receive no tools. A versus B varies information availability. B versus C also varies length and relevance density. D measures a different workflow with multiple turns and navigation overhead. [Public artifacts](../experiments/finops_sql/public/v1/) · [Package serialization](../experiments/finops_sql/packages.py)

## D discovery and transcript contract

- `catalog(query)` searches by token overlap with stable ID ordering. Empty search lists the table grains; a nonempty search returns at most eight IDs. Only returned IDs enter this episode's known set.
- `describe(ids)` accepts one to three distinct known IDs. Only the explicit glossary links in returned descriptions grant additional IDs. A guessed ID or a table name mentioned inside explanatory text does not grant access. `examples(table)` also requires a known table. Tools only read versioned public artifacts.
- Each turn permits either a final JSON answer or one native function call. A single invalid call consumes a slot and yields a bounded error. Multiple proposals, mixed prose and a proposal, missing answers, malformed JSON and proposals with tools disabled are distinct or recorded invalid outcomes. After six calls the seventh request omits the tools. A final answer can arrive on the first turn.
- The transcript is stateless across Responses requests. Each new request includes the original instructions and question followed by the ordered public local discovery records as data messages. Private reasoning and grading feedback never enter that history. Argument input is bounded to 256 UTF-8 bytes. A result must fit 800 tokens¹ and its entire escaped history message must fit 2,048 bytes. Invalid raw proposals stay in the receipt; the next turn sees the bounded error. Each turn persists its body before transport and records the raw response, prior history digest, and, where a call is served, returned record, bytes, tokens, tool latency and resulting history digest.
- All 32 reviewer paths replayed through the enforced tool interface. Nine take two calls, 13 take three, nine take four and one takes five. These are minima for obtaining the declared complete set of definitions when IDs must be discovered. A model can take a different path or fail to find the definitions. Six calls leave one navigation step on the longest documented path. Every three-ID description combination fits the measured result-token ceiling. The largest three-ID history message is 1,666 bytes and the largest example history message is 1,299 bytes. Witness paths are evaluator-only. [Reachability evidence](experiment05_checkpoint1.md)

## Grading and oracle review

The worker now returns DuckDB column types alongside names and values. The grader checks the required alias sequence, width, numeric type family, unit-scaled value, exact integer/count fields, NULL positions, multiplicity, and the business-key precision on both snapshots. Ordered Q02 and Q06 preserve ranking. Other comparisons use row multisets. Amounts round half-up to cents and rates to six places. Units are checked by comparing the numeric result in the contracted scale on both snapshots. Equivalent values alone cannot establish the causal correctness of a formula.

A parser/policy rejection fails SQL validity. An admissible query with a binder error fails execution. A query that executes and returns the wrong financial result fails business correctness. A timeout without worker telemetry leaves validity unknown. Grade one question once across its two snapshots. Q33–36 must ask for the accepted dimensions. An exact dimension set advances to masked review of the actual wording; the dimension label alone earns no automatic business-correct grade. [Typed grader](../experiments/finops_sql/grading.py) · [Private-key digest bindings](../experiments/finops_sql/oracle-bindings.json)

The reviewer packet covers all 36 cases. Every row of all 64 answerable query executions passed the typed contract and independent Decimal comparison. The packet flags Q14's percentage presentation: the shorthand in the original inventory gives the ratio, while the accepted fiscal policy and both calculations report percentage points. The implementation retains that existing rule. All four ambiguity witnesses remain available for owner inspection. [36-question reviewer packet](experiment05_oracle_review.md)

## Requests and spending

| Arm | Maximum model calls | Initial body bytes per question | Initial body tokens¹ | Reserved input, all turns | Reserved output | Estimated maximum USD |
|---|---:|---:|---:|---:|---:|---:|
| A | 36 | 6,326–6,414 | 1,659–1,674 | 238,391 | 73,728 | 0.066662875 |
| B | 36 | 11,348–11,436 | 2,684–2,699 | 419,183 | 73,728 | 0.089261875 |
| C | 36 | 26,628–26,716 | 6,560–6,575 | 969,263 | 73,728 | 0.158021875 |
| D | 252 | 2,278–2,366 | 498–513 | 2,166,905 | 516,096 | 0.528911125 |
| **Total** | **360** | | | **3,793,742** | **737,280** | **0.842857750** |

The proposal contains **108 complete fixed-context requests and 36 complete initial discovery requests**. Up to 216 later D bodies depend on prior tool calls. The manifest binds their deterministic construction code and per-turn budgets. D allows at most 216 local discovery calls. Its worst-case serialized history growth is 12,288 bytes; the largest seventh body is bounded at 13,820 bytes after tools are removed. Across the 36 questions the maximum input allowances for successive D turns are 2,622, 4,670, 6,718, 8,766, 10,814, 12,862 and 14,076. The reserve uses the serialized byte ceiling plus 256 framing tokens per call, all reserved input at the 30-minute write rate, and the full output allowance including reasoning. Unknown provider framing and actual billing require preflight and receipt reconciliation before any future deployment.

¹ Token counts are actual local cl100k_base measurements of the indicated strings, including the canonical JSON body where specified. The pinned tokenizer library has no GPT-6 Luna mapping. Provider tokenization and actual cache partitions remain unverified. Seven SQL answers to the separate development questions required 47–234 proxy tokens in their final JSON envelopes; a representative D08 clarification required 26. The longest SQL example leaves about 1,814 tokens for reasoning and alternate SQL under the proposed cap. There is no live evidence that every answer will finish within it.

The November 10 standard short-context price check found $0.10/M uncached input, $0.01/M cached input, $0.125/M 30-minute writes and $0.50/M output. Official documentation lists Responses function calling and medium reasoning for Luna. The metadata lookup verified access; live settings, metering, and account-specific billing still need confirmation against sealed receipts if acquisition is authorized. [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna) · [OpenAI pricing](https://developers.openai.com/api/docs/pricing)

## Approval and interruption

- Canonical proposal digest: `9c98d2017cd245272d9cc548adf6a3aea33e78ae4caaf914a0cd430281f11d47`
- Manifest file SHA-256: `8c5d757611d0938be37b57d776149ee7eb7eb1b991c6403cb6c0bd419f4f911c`
- SHA-256 of canonical uncompressed body array: `ca1bb6ee71a468bf75110c6e3dc0d8ebbc27d7be1ce29eef70f4c8c87d577f23`

Before paid acquisition, require owner approval of the exact proposal, settings, turn ceilings and spending cap, and a separately verified live dispatcher. It must check a clean revision, regenerate the digest/bounds, verify model access and prices, enforce single use, and reconcile remaining reserve before every send. Preserve request/response receipts before advancing. Stop on transport or provider failure, incomplete output, integrity drift, missing or inconsistent usage, unexpected model/tier/cache settings, or budget breach. Seal the partial run with planned, sent, evaluable and unsent counts by arm. Keep completed malformed answers as graded failures. No retries, resumption or substitution. Final comparisons must retain all 36 planned units per arm and report acquisition failures separately.

The repository tests exercise valid SQL, clarification and review, malformed or absent answers, invalid and multiple discovery calls, budget exhaustion, truncated responses, provider errors, SQL rejection, binding errors and executable financial errors. The Docker-backed path takes a scripted SDK response through the worker and grader on both snapshots in every condition. [Offline verification](../tests/test_finops_readiness.py)
