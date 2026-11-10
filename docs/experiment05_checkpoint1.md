# Experiment 005 · Warehouse and answer-key verification

**Decision requested.** Keep the two-snapshot business-result test and the proposed SQL worker limits. Increase the prospective final-answer allowance to 2,048 output tokens and the discovery allowance to six calls. Ten of 32 answerable questions exceed the original three-call allowance when the analyst must actually retrieve all required definitions. These are offline feasibility results. Model accuracy, discovery efficiency, refusal rates, inference latency and actual spend remain unmeasured. [Approved design](experiment05_sql_context_design.md)

## Warehouse

Meridian Cloud Services has two fictional providers, USD billing, UTC dates and 2025 usage. Posting month 13 represents January 2026. A keyed BLAKE2s quantity variation, fixed seeds and stable business keys preserve reproducibility. Monetary columns are DECIMAL(18,6). Separate effective-dated pricing and ownership, July output gaps, conflicting or blank tags, missing lifecycle metadata, co-covered charges, delayed credits and revised deliveries each have a defined interpretation. Assign missing direct ownership to Unassigned. Invoice controls accumulate source economic events before duplicate or corrected deliveries are emitted. They share the synthetic source of truth with the events and cannot detect every incorrect generator assumption. [Generator](../experiments/finops_sql/generate.py) · [Schema with keys](../experiments/finops_sql/schema.sql)

| Tables | Development / evaluation A / evaluation B rows |
|---|---|
| provider, account, project, region | 2, 16, 64, 4 respectively in each |
| service_class, service, sku, resource | 3, 10, 40, 1,200 in each |
| cost_center, team, resource_owner | 8, 16, 2,514 in each |
| resource_tag | 1,069 / 1,070 / 1,070 |
| fiscal_period, monthly_budget, output_day | 12, 96, 23,329 in each |
| invoice, charge_revision, usage_day | 208, 343,600, 328,500 in each |
| commitment, price_schedule, shared_split | 2, 320, 24 in each |
| commitment_application | 8,003 / 8,023 / 8,011 |

Each of the three snapshots was generated twice. All 22 CSVs and the separate economic event stream reproduced per snapshot. The checkpoint verifies canonical manifest digests and source hashes, opens the mounted database read-only and compares its binary digest before and after evaluation. CSVs are the portable reproducibility target. DuckDB storage layout can vary. All ten accounting controls passed on all three snapshots, including invoice balance, credit origins, allocation conservation, owner shares and intervals, price matches, amortization, covered units and fiscal boundaries. The eight development tasks cover independent periods and one clarification about Finance's spending scope and basis. Their numeric outputs and the evaluation keys stay outside model inputs. [Snapshot bindings](../experiments/finops_sql/checkpoint.py) · [Controls and development inventory](../experiments/finops_sql/controls.py)

## Answer validation

**Q01–Q32 each passed on evaluation A and B.** Python iterates economic events and uses Decimal arithmetic. SQL reconstructs latest logical charges from export deliveries. For Q18 and Q19, Python also reads the delivery history because the economic ledger alone cannot establish arrival time or duplicate count. Both methods use the same business definitions and dimension facts. Their implementation independence provides a cross-check; an independent human oracle review is outstanding. Ranked cases retain order, other cases compare row multisets, IDs and counts are exact, financial amounts round to cents and ratios to six places. A floating-point rate change rounded to negative zero in SQL during development. The comparator now canonicalizes signed zero after rounding. All 32 graded outputs change between evaluation snapshots. A repeated answer across seeds is still only one question outcome. [Python calculation](../experiments/finops_sql/oracle.py) · [SQL references](../experiments/finops_sql/references.py)

Six plausible accounting errors each changed the graded result on **both** snapshots. Q01 distinguishes raw deliveries from latest charges and usage dates from posting dates. Q02 distinguishes list from effective cost. Q20 detects multiplying pool cost across recipients without weights. Q23 detects substituting December ownership at the June handoff. Q12 detects averaging monthly rates instead of dividing period totals. These controls establish discrimination against these specific errors. Other incorrect queries can still coincide with a key.

| Clarification | Two defensible interpretations exercised on each snapshot | Required clarification |
|---|---|---|
| Q33 · Team spend | January billed leader and October effective-cost leader differ | Period and cost basis |
| Q34 · Budget variance | Period-six Engineering and Research variances differ | Reporting center or organizational scope |
| Q35 · Discount savings | July list-to-contract gap and actual savings on covered units differ | Meaning of discount savings |
| Q36 · Atlas unit cost | Last calendar quarter per completed transaction and per metered SKU X unit differ | Output denominator and, if metered, applicable SKU |

The as-of clock is January 31, 2026. Retain identical clarification instructions and SQL/clarification envelopes across arms. Choosing either numeric interpretation without asking fails the clarification case. Contradictions between declared dimensions and the clarification text require masked review.

## SQL execution boundary

DuckDB 1.4.4 and SQLGlot 28.10.1 run inside a pinned-base Linux image. One disposable unprivileged child validates and renders the AST for each query. The worker has one CPU, one DuckDB thread, a 300 MB DuckDB budget, a 512 MiB container limit, zero spill, a five-second deadline, a 1,000-row limit and a 1 MiB result limit. The only host mount is the read-only warehouse. The container has no network, Linux capabilities or host credentials. Configuration is locked and external access and extension autoload/install are disabled. The binder resolves columns in allowed relations. The intentionally narrow SQL subset may reject legitimate alternative SQL. Audit equivalent development formulations before freezing the accepted grammar. [Worker](../experiments/finops_sql/worker.py) · [Container boundary](../experiments/finops_sql/audit.py)

| Evaluation snapshot | Reference queries completed | Slowest observed worker time | Highest child peak RSS |
|---|---:|---:|---:|
| A | 32/32 | 0.995 s | 165.6 MiB |
| B | 32/32 | 0.498 s | 166.3 MiB |

Times include parsing, opening the DB, query execution and result checks, excluding container startup. RSS is per child, while the 512 MiB hard limit covers the container. These are local feasibility observations; future machine load and alternative query plans will vary. The same worker rejected mutation, external table reads, extension installation, configuration changes, catalog access, unauthorized functions, multiple statements and over-limit rows on every snapshot.

## Context interpretation and discovery

A versus B changes which business information is available. B versus C preserves B as a prefix and adds accurate operational metadata, representation examples and length, changing relevance density as well as volume. D changes the workflow and permits extra model turns. Keep D separate from the primary A/B/C comparison.

Preclassification before inference uses overlapping groups. Q03 is schema-sufficient given the ordinary meaning of compute, East and hours. Q01–02 and Q04–32 depend on business definitions to some extent. Q02–04, Q06–08, Q10–18 and Q20–32 are also sensitive to joins, aggregation grain or effective dates. Q18–19 and Q29–31 are the additional-context-sensitive subgroup because delivery precedence, raw tag values or JSON representations may make examples helpful. B still contains the necessary policy. Q33–36 are ambiguous by design.

The reviewer-only table below records the complete-schema/definition discovery path for each answerable question. A minimum counts one catalog call plus one describe call per group of up to three required entries. Every returned ID is available from the search or a prior public cross-reference. Free-text searches can use business or schema terms; they expose no record values. The witness attains the lower bound for the stated information inventory. A model might guess a join from less evidence, or spend extra turns navigating. No example rows are required by these paths. Do not serialize the paths or the information inventory into model inputs. [Executable paths, catalog and definitions](../experiments/finops_sql/discovery.py)

| Question | Minimum calls | Full entries in describe order (each group is one call) |
|---|---:|---|
| Q01 | 2 | charge_revision · invoice · @closing |
| Q02 | 3 | charge_revision · service · sku → @closing · @costs |
| Q03 | 3 | region · resource · service → service_class · sku · usage_day |
| Q04 | 3 | charge_revision · service · service_class → sku · @closing · @costs |
| Q05 | 2 | charge_revision · invoice · @closing |
| Q06 | 3 | charge_revision · sku · @closing → @costs |
| Q07 | 4 | charge_revision · region · resource → sku · usage_day · @closing → @codes · @variance |
| Q08 | 3 | charge_revision · resource · usage_day → @closing · @codes · @variance |
| Q09 | 3 | charge_revision · invoice · @closing → @variance |
| Q10 | 4 | charge_revision · output_day · project → resource · @closing · @costs → @output |
| Q11 | 3 | charge_revision · output_day · resource → @closing · @costs · @output |
| Q12 | 4 | charge_revision · output_day · project → resource · @closing · @costs → @output |
| Q13 | 4 | charge_revision · fiscal_period · monthly_budget → resource_owner · shared_split · team → @allocation · @closing · @fiscal |
| Q14 | 5 | charge_revision · cost_center · fiscal_period → monthly_budget · resource_owner · shared_split → team · @allocation · @closing → @fiscal |
| Q15 | 4 | charge_revision · fiscal_period · monthly_budget → resource_owner · shared_split · team → @allocation · @closing · @fiscal |
| Q16 | 2 | charge_revision · invoice · @closing |
| Q17 | 2 | charge_revision · invoice · @closing |
| Q18 | 2 | charge_revision · invoice · @closing |
| Q19 | 2 | charge_revision · invoice · @closing |
| Q20 | 3 | charge_revision · shared_split · @allocation → @closing |
| Q21 | 4 | charge_revision · cost_center · fiscal_period → resource_owner · shared_split · team → @allocation · @closing · @fiscal |
| Q22 | 3 | charge_revision · resource_owner · @allocation → @closing |
| Q23 | 3 | charge_revision · resource_owner · @allocation → @closing · @codes |
| Q24 | 3 | charge_revision · resource_owner · team → @allocation · @closing |
| Q25 | 4 | charge_revision · commitment · commitment_application → invoice · usage_day · @closing → @codes · @commitments |
| Q26 | 4 | charge_revision · commitment_application · price_schedule → resource · @closing · @codes → @commitments |
| Q27 | 3 | charge_revision · commitment · commitment_application → @closing · @codes · @commitments |
| Q28 | 3 | charge_revision · commitment_application · @closing → @commitments |
| Q29 | 2 | resource_tag · usage_day · @labels |
| Q30 | 2 | resource · resource_tag · @labels |
| Q31 | 4 | charge_revision · resource · service → service_class · sku · @closing → @costs · @labels |
| Q32 | 2 | charge_revision · invoice · @closing |

## Budgets for owner review

The 32 reference queries in JSON final-answer envelopes span **78–426 tokens** with locally cached cl100k_base as a tokenizer proxy. This measures a known valid answer, without reasoning. At the longest reference, 1,024 leaves approximately 598 tokens for reasoning and alternative expression; 2,048 leaves approximately 1,622. Reasoning demand and the live model's tokenizer are unverified. Use the same 2,048 cap per model turn in every arm, count truncation explicitly, and recheck sizes and pricing before an acquisition freeze.

The longest required retrieval path takes five calls. Recommend **six discovery calls**, one per turn plus a final tool-disabled turn, leaving one additional navigation or example lookup on the hardest question. Retain zero SQL feedback, no retries, a three-ID describe limit and the 800-token local result cap. The largest response on the verified paths was 339 proxy tokens. Future dispatch must enforce the actual model's envelope, including tool arguments, returned metadata and repeated history.

| Arm | Maximum model calls | Reserved input per question | Maximum output per question | Planning reserve |
|---|---:|---:|---:|---:|
| A | 36 | 4,000 | 2,048 | $0.054864 |
| B | 36 | 9,000 | 2,048 | $0.077364 |
| C | 36 | 22,000 | 2,048 | $0.135864 |
| D | 252 | 77,000 cumulative | 14,336 | $0.604548 |
| Total | 360 | | | **$0.872640** |

D input allowances in turn order are 2k, 5k, 8k, 11k, 14k, 17k and 20k. At most 216 local tool calls. The prior planning rates of $0.125/M input and $0.50/M output imply an additional $0.184320 for doubling the output allowance at this revised maximum turn count. Proposed ceiling **$1.00**, subject to current pricing, an exact serialized reserve, cache accounting and separate approval. At the design's illustrative two seconds per model call, serial inference would be two seconds per A/B/C episode and two to fourteen seconds in D plus local tool time. Acquisition will need observed per-turn timing and separate SQL execution timing.

**Optional external check.** Defer BIRD Mini-Dev. Its maintainers document multiple SQL dialects and revised annotations. A small independently audited SELECT subset could later test portability beyond Meridian, but would require pinned databases, rights review, dialect-specific reference execution and a fresh evidence-delivery design. Keep its outcomes separate from this paired FinOps study. No dataset download was needed. [BIRD Mini-Dev maintainers](https://github.com/bird-bench/mini_dev)

## Reproduce and review

From a clean checkout with Docker and locked dependencies, use an unused output directory.

```text
uv sync --locked
docker build -t meridian-worker:checkpoint1 experiments/finops_sql
uv run --offline python -m experiments.finops_sql.generate .verification/finops
uv run --offline python -m experiments.finops_sql.checkpoint .verification/finops
```

The owner decision covers the clarification dimensions, discovery coverage standard and proposed output/turn budgets. The next phase would prepare context packages and acquisition controls. Keep all reference calculations, paths, expected results and worker diagnostics on the evaluator side. This checkpoint grants no spending authority.
