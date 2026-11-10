# Experiment 005 · Does More Database Context Make AI-Generated SQL More Reliable?

**Design for owner review.** A FinOps lead must decide how an analytics assistant learns what a dollar of cloud spend means. A query can execute, reconcile to a plausible total and still charge the wrong team. The deployment decision is whether to maintain a curated context package, preload the broader catalog, or let the assistant discover what it needs on demand.

## Comparisons and decision criteria

Use 36 paired evaluation questions, one draw per question per condition. A/B/C are the primary context-delivery comparison. The primary outcome is the paired change in correct business responses for B versus A and C versus B. Publish A versus C as well. Hypothesis: curated definitions help on joins, timing and cost basis; additional accurate material may help, distract or simply cost more. A ceiling or a loss for B is admissible. The secondary D-versus-B comparison evaluates an interactive architecture with a different call budget. A D gain cannot isolate the value of tools, information selection or an extra inference turn.

Prefer the lowest-overhead condition that preserves required answers and appropriate clarifications on this workload. Examine every gain and regression, especially confidently wrong financial answers. Before deployment weigh their observed severity on representative customer traffic against inference, catalog maintenance, analyst rework and response-time targets. This authored study measures inference overhead and wrong answers; customer labor cost and ROI require customer evidence.

## Proposed warehouse

Use a fictional company, Meridian Cloud Services, with two invented cloud providers. Use USD only, UTC dates, integer source quantities and fixed-point money. Pin the terminology reference to **FinOps FOCUS 1.2** for billed, effective, list and contracted costs. The tables below are an internal analytical model. No conformance assessment is proposed. [FOCUS 1.2](https://focus.finops.org/docs/specification/v1-2/)

| Tables (22 total) | Grain and relationships |
|---|---|
| provider, account, project | One per ID. Account belongs to provider; project belongs to account. |
| region, service_class, service, sku | One per ID. SKU → service → class; region is a separate pricing and usage key. Each SKU has a declared usage unit. |
| resource, team, cost_center | One per ID. Resource → project and SKU; team → center. Resource JSON includes deployment metadata. |
| resource_owner, resource_tag | Owner interval per resource/team with share; multiple owners may overlap with shares totaling one. Tag row per resource/raw key/value/validity interval. Preserve case, whitespace, missing values and conflicting values. |
| fiscal_period, invoice | Period with half-open boundaries; invoice per account and billing period, carrying an independently generated control total. |
| usage_day, charge_revision | Metered resource/SKU/region/day with quantity; each logical charge has one or more export revisions with billed, effective, list and contracted amounts, invoice link, usage date, category, arrival time, revision and export ID. Purchases and adjustments can lack a resource or meter link. |
| price_schedule, commitment, commitment_application | Effective-dated SKU/region rates; one contract with purchase amount and term; bridge per commitment/charge with covered quantity and amortized value. Aggregate bridge amounts at their own grain. |
| shared_split, monthly_budget, output_day | Pool/period/recipient center and weight; approved budget per center/fiscal period; completed business transactions per project/day, including zero-output days. |

**Generation contract.** Generate a development snapshot and two distinct evaluation snapshots for calendar 2025, plus January 2026 postings for late charges. Target 16 accounts, 64 projects, 16 teams in eight centers, 1,200 resources, four regions and 40 SKUs. Aim for 250k–400k metered days and 300k–600k export rows per snapshot. Assign IDs and component-specific PRNG streams from a fixed master seed plus table name and logical key. Use deterministic seasonal volumes, midyear rate changes, ownership transfers and commitments with both utilized and unused value. Give related fixtures different business keys and amounts. Sort exports by stable keys. Freeze generator revision, seeds, schema, DuckDB build and per-table canonical hashes before inference. No provider exports or client records.

Generate economic events first, then export them. The canonical charge is the latest available revision at the requested cutoff, ordered by revision, arrival and export ID descending. A duplicate delivery carries identical financial fields. Late credits are separate signed events with a link to the original charge and their own posting invoice. For the internal effective-cost ledger distribute commitment purchase value across the service term; covered usage receives its amortized share and unused value gets a separate charge. Never add the purchase cash amount again to amortization. Billing-period actual uses net billed on the posting invoice. Operating actual uses effective cost on usage date. Fiscal periods follow a frozen 4-4-5 calendar. Charge direct spend to dated owners by share, retain missing ownership in Unassigned, and distribute designated pools only once using period weights. Carry full precision until final display rounding.

Assert FK integrity, interval uniqueness for active prices, deterministic revision selection, invoice reconciliation, conservation of ownership and pool shares, covered quantity ≤ metered quantity, contract amortization conservation over the term and uniqueness of budgets/output denominators. Reserve null resource IDs for documented charge categories. Include free-text billing memos and inconsistent tags; memos are descriptive and never the authority for financial classification. Tag policy trims and lowercases keys and values, treats blanks as missing, and marks competing normalized values unresolved. Map event time to a half-open interval. Generate a known example of each ambiguity, transfer, missing value, late posting and overlapping bridge relationship. Fail fixture validation if a required contrast disappears.

## What each model sees

Use one model/version, fixed inference settings, 1,024 maximum output tokens per request and identical developer instructions, question text, dialect, as-of clock, output-column/unit requirements and final answer contract. Give all arms a brief interface instruction: use supplied evidence, use discovery only if offered, return one query or ask one focused clarification. Never supply expected SQL, result rows or private test identifiers. All business facts available through discovery also occur in C.

| Condition | Exact delivery proposed |
|---|---|
| A · Basic schema | Preload `schema.sql` containing every user table, column, type, PK and declared FK, with no business comments. One generation, no tools. |
| B · Curated | Preload A followed by `dictionary.curated.json`, `metrics.md`, `joins.md`, `policy.md`. Include grains, supported cost bases, denominator and calendar conventions, required filters, precedence, bridge allocation and documented clarification dimensions. Same bundle for every question. |
| C · Expanded | Full B as a byte-identical prefix, followed by `dictionary.full.json`, `lineage.md`, `operations.md`, `registry.json`. Include accurate export fields, historical version notes with applicability dates, refresh cadence, catalog descriptions, low-level tags and frozen representative records. Avoid contradictory current policy or question-specific hints. |
| D · Self-service | Empty initial context block. Only neutral tool schemas, shared instructions and the question. Tool results are deterministic slices of C’s frozen artifacts; no database connection or arbitrary path is exposed. |

Version `context-manifest.json` with ordered file paths, byte lengths, SHA-256, artifact roles and generator revision. Serialize each permitted file in the listed order as a named UTF-8 LF block; JSON uses sorted keys, compact separators and stable array order. Store the exact concatenated bytes, final request body, token count and hash per case. Reject oversize packages before approval. A/B/C have no file picker, tool calls, SQL execution feedback or per-question retrieval. Expanded context changes both relevance density and length; report both.

**D tool interface.** (1) `catalog(query)` searches table names, column names and glossary headings by case-insensitive token overlap; empty query lists all 22 tables and one-line grains. Otherwise return up to eight ranked object IDs with stable ID tie-break. (2) `describe(ids)` returns up to three catalog IDs’ DDL, grain, joins or complete short metric/policy entries, by exact allowlisted ID. (3) `examples(table)` returns up to three preselected synthetic public rows from the registry, sorted by frozen sample ID. No filters, scans, aggregates, computed answers, oracle access or SQL execution. Select example rows from the public development snapshot without using evaluation keys. Freeze them in C and D across both private evaluation seeds. Cap each response at 800 model tokens using prevalidated record boundaries, with explicit omitted IDs/counts. These tools separate finding an object, interpreting its contract and inspecting its representation. Log searches, selections, bytes, tokens and retrieval latency.

Use the same approved clock, namespace and user privileges for every question. The registry is a deterministic export of all catalog entries in scope; record entry counts and package bytes so “expanded” is auditable. Expose longer lineage or operations material as indexed, individually retrievable short entries with stable IDs.

At most three sequential discovery calls, one per turn, plus one final generation (maximum four model requests per episode). D may finalize immediately. On turn four disable tools. Invalid discovery requests consume one slot and return a bounded error. Multiple calls in one response or another call on the final turn fails the episode. No retry or exploratory query execution. Freeze tool schemas, index, responses for exact arguments, transcript serialization, budget and final-turn rule. Before any paid acquisition bind a deterministic body-building contract to the original question and immutable prior response/tool-result hashes. Store every materialized body before sending. Account for repeated input on every turn.

## Evaluation inventory and proposed answer keys

The table gives the intended user request and result contract. Freeze literal questions, exact output schemas and numeric reference results after generating the warehouse and before any evaluation draw. Month names mean calendar months unless “fiscal” is stated. “Net billed” includes signed postings; “effective” uses the operating ledger. Except for explicit as-of requests, use the final export. Ties in rankings break by stable ID. Use one named compute SKU and homogeneous unit for price bridges. Names below are generator requirements.

| ID | Question | Expected output or reference calculation |
|---|---|---|
| 01 | What was March net billed cost? | One USD sum on March invoices. |
| 02 | Which three services had the highest April effective cost? | Three ordered service IDs and usage-date sums. |
| 03 | How many compute hours did East consume in May? | One quantity from eligible hour-based meter rows. |
| 04 | What was May list minus contracted cost for storage usage? | USD gap summed only on storage usage. |
| 05 | Which accounts increased net billed cost from March to April? | Account ID and positive dollar delta, absent month treated as zero. |
| 06 | Which service contributed most to the April–May effective-cost increase? | Service and largest signed delta, including services present in only one month. |
| 07 | Split East compute SKU X’s May–June contracted-cost change into volume and rate effects. | Two USD terms: (Q1−Q0)R0 and Q1(R1−R0), realized rates = contracted usage cost / units. |
| 08 | For SKU X, bridge June–July regional spend into volume, mix and rate. | Base-rate volume at old mix, new total × change in regional shares × old rates, and new regional units × rate changes. Sum equals contracted-cost delta. Seed both periods in each region. |
| 09 | What portion of June’s billed change from May came from credits? | Signed credit delta divided by signed total delta. |
| 10 | What was Atlas’s June effective cost per 1,000 completed transactions? | Project cost × 1,000 / total project output, aggregate each side first. |
| 11 | Which projects had July spend but no completed output? | Project IDs and effective cost, include missing output as zero. |
| 12 | How did Atlas unit cost change between Q2 and Q3? | Two weighted period rates and signed difference per transaction. |
| 13 | Which centers exceeded fiscal period 6 budget after allocation? | IDs and positive effective actual minus approved budget. |
| 14 | What was Engineering’s fiscal year-to-period-8 variance percentage? | (Sum allocated actual − sum budget) / sum budget. |
| 15 | Which centers had a Q3 fiscal budget but no allocated actual? | Center and unused budget, preserve budget side of join. |
| 16 | Reconcile September net billed to invoice controls by invoice. | ID, latest signed postings, control and residual. Check totals as well as residual. |
| 17 | How much October-posted credit refers to September usage? | Signed USD via original charge and posting invoice. |
| 18 | What was April billed as known May 1 versus at final close? | Two totals and revision delta, cutoff midnight UTC May 1 inclusive. |
| 19 | How much would summing raw June exports overstate net billed? | Raw sum minus latest-version sum for June invoice lines. |
| 20 | Allocate the August network pool to centers. | Recipient ID, weighted share of pool, conservation total. |
| 21 | Break down Research’s fiscal period 7 chargeback. | Direct, allocated-in and total effective cost, exclude pool sources from direct. |
| 22 | How much July direct effective cost lacked a dated owner? | Unassigned amount excluding shared pools. |
| 23 | Which team bore resource R17’s cost before and after its June handoff? | Team IDs and share-weighted direct cost using usage-day ownership. |
| 24 | How much would using Dec 31 owners move September direct cost by center? | Signed counterfactual minus historical allocation, retain Unassigned. |
| 25 | For contract K2, what share of July eligible units was covered? | Covered units / eligible units for its SKU and scope, deduplicate application grain. |
| 26 | How much contracted on-demand cost did K2 save on covered July usage? | Covered units × applicable contracted on-demand rate less applied amortized cost. |
| 27 | Reconcile K2’s August amortization. | Applied and unused USD and their sum versus scheduled service-month expense. |
| 28 | Compare quarterly commitment cash outlay and operating expense. | Calendar quarter, purchases billed and applied plus unused amortization. |
| 29 | What fraction of August active resources had a usable environment tag? | Distinct metered resources with one normalized value at Aug 31 / all active in month. |
| 30 | Which projects had conflicting environment tags at Sep 30? | Project IDs and distinct affected resources at date. |
| 31 | How much October compute cost had JSON lifecycle “ephemeral”? | Effective compute usage sum on matching resource metadata; missing path excluded. |
| 32 | Which accounts have different December usage-month and posting-month totals? | Account, signed billed totals under each clock and difference, include late postings. |
| 33 | Which team spent the most? | Clarify period and cost basis; both materially change ranking. |
| 34 | How far over budget are we for period 6? | Clarify reporting center/scope if requester has no default. Fiscal budget policy already specifies allocated effective actual. |
| 35 | What were July’s discount savings? | Clarify list-to-contract price gap versus commitment savings on covered usage. |
| 36 | What was Atlas’s unit cost last quarter? | Freeze clock at Jan 31 2026; clarify business output transactions versus metered usage units and the applicable SKU if metered. |

## Execution, ground truth and controls

Use embedded DuckDB for a small, reproducible snapshot and local result-set comparison. Pin exact package, platform image, collation, UTC timezone and settings in the implementation lock. Specify its SQL dialect in all arms: use explicit casts, DATE literals, DuckDB date functions and JSON extraction. Avoid vendor billing UDFs, dialect-specific warehouse commands and implicit ordering. The design tests analyst SQL on one engine. [DuckDB dialect](https://duckdb.org/docs/stable/sql/dialect/overview)

Require a single JSON final response: either `{"kind":"sql","query":"…"}` or `{"kind":"clarify","dimensions":["…"],"question":"…"}`. Give every question the same response options. Include requested output fields only when the user’s analytical request specifies them; never use the envelope to reveal the expected disposition or resolve an intended ambiguity. Freeze allowed dimension vocabulary for all arms, with per-case required dimensions kept private. Require one nonempty clarification that asks about the submitted dimensions; validate dimensions deterministically and flag text/field contradictions for masked owner review. SQL is evaluated once per hidden snapshot after generation, without feedback. A result with the wrong columns, duplicates, month boundaries or null handling can execute and still fail business correctness.

Treat generated SQL as untrusted. Parse using a pinned DuckDB-compatible parser, allow one read-only SELECT/CTE over allowlisted tables/columns and approved scalar/aggregate/window functions; reject catalog introspection, recursive queries, table functions, commands, external files, extension loading and non-deterministic functions. Run each query in a disposable unprivileged OS worker/container with no network, credentials or host mounts; mount only the immutable DB read-only. Disable external access and extension auto-install/load, lock configuration, use one thread, 512 MiB process memory, no spill, five-second wall timeout, 1,000 result rows and 1 MiB output. Terminate the worker on breach. Test adversarial and valid analytics offline before freeze. [DuckDB security guidance](https://duckdb.org/docs/stable/operations_manual/securing_duckdb/overview)

Use eight additional development questions on different IDs/time ranges (aggregation, revision, date, allocation, ownership, price bridge, tags and clarification). Tune prompts, tools and safety/test harness only there. The 36 named questions are evaluation-design exposed; hold out their final instances, seeds, numeric keys and all outputs from tuning. Release directions before implementation; seal actual keys privately before inference. Apply every generated query unchanged to two precommitted evaluation seeds with the same business identifiers and schema, independent economic values and contrasting edge cases. Score one question once. No separate model draws per seed.

Before inference a separate Python/Decimal oracle computes answers from generator event records and independently implements the metric definitions. A second calculation uses reviewer-authored reference SQL on exported tables. Do not share generator rollup functions with either checker. Reconcile both on both seeds, inspect sampled ledger traces and invoice controls, and have the owner review all clarification keys and material assumptions. This is a proposed validation workflow, with no completed independent review. Test plausible wrong solutions (latest owner, raw revisions, list instead of effective, monthly average of ratios, unweighted bridge join). Require each applicable wrong solution to disagree on at least one seed. For clarification cases exhibit two legitimate interpretations giving different answers. For answerable cases verify all necessary information exists in B/C and is reachable within D’s tool budget on a documented discovery path. Resolve disagreements before freeze; never revise keys in response to model outcomes.

Grade typed row multisets unless ranking requires order; preserve duplicate multiplicities and nulls. Require stable output aliases and units specified in a common question envelope, exact integer/ID equality, amounts rounded once to cents, rates/percentages to six decimal places with fixed decimal rounding. Declare zero denominator NULL. Primary policy-correct / 36 requires exact business result on both snapshots or correct clarification. Separately report SQL submission, parse/safety acceptance, executable queries / 32 answerable, execution success conditional on attempted SQL, correct results / 32, correct clarifications / 4, over-refusal and inappropriate SQL. Itemize policy blocks, syntax/binder errors, empty or wrong results, timeouts, malformed outputs, API failures and omissions. Show paired case IDs, gains/regressions and family-level counts. A clarification earns no SQL execution credit.

## Feasibility and proposed acquisition envelope

Reuse the Lab’s frozen manifests, sequential provider receipts, spending checks and paired reporting. New experiment-local components would be a generator, two oracles, isolated SQL worker and bounded metadata dispatcher. Stage offline milestones: approve this design; validate warehouse/oracles and sandbox; freeze exact packages, D contract, seeds, reference outputs and request budgets; review a separately costed live plan. No inference is authorized at this checkpoint.

Planning arithmetic uses the Lab’s [prior standard GPT-6 Luna pricing snapshot](experiment04_followup_plan.md), $0.125/M reserved input and $0.50/M output, subject to fresh model/price verification. Assume 1,024 output tokens per model request including reasoning and 2 seconds acquisition time per call **as a planning illustration**, not an SLA or measurement. Input figures are total prompt allowances including tools, schema and transcript. Freeze actual serialized sizes and a conservative bound for every permitted D turn before seeking approval.

| Arm | Requests for 36 cases | Input tokens per case (planning allowance) | Output allowance per case | Inference reserve for arm | Illustrative serial model time per case |
|---|---:|---:|---:|---:|---:|
| A | 36 | 4,000 | 1,024 | $0.036432 | 2 s |
| B | 36 | 9,000 | 1,024 | $0.058932 | 2 s |
| C | 36 | 22,000 | 1,024 | $0.117432 | 2 s |
| D | 36–144 | Up to 22,000 cumulatively (2k + 4k + 7k + 9k) | Up to 4,096 | $0.172728 | 2–8 s plus local discovery |

Execute questions in a seeded order with counterbalanced arm order to reduce timing and cache-order bias. Use fresh conversations per case/arm, zero transport retries, single-use acquisition records and stop on provider, accounting, integrity or budget failure. Charge malformed completed outputs to their arm. Retain the 36-case planned denominator when reporting partial acquisition.

Maximum **252 model requests, 108 local discovery calls, 144 paired arm outcomes and $0.385524 estimated reserve**. Proposed planning ceiling $0.45. If final curated content or D’s transcript cannot fit, return a revised envelope before acquisition. Measure actual input, output, reasoning and cache partitions, usage-priced cost, cost per correct answer, per-call latency, cumulative per-question model time, local tool time and final SQL execution time separately. Report median and range by arm and discovery depth. Include setup and catalog upkeep as unmeasured unless logged. One model, authored metadata, a single draw, synthetic deployment prevalence and only four clarification cases limit generalization; observed differences support a follow-up customer pilot, not an industry-wide threshold.
