# Phase 3A: enterprise tool-selection feasibility

November 4, 2026. **Do not launch the proposed 12-case or 120-case study from this
pool.** A smaller 3-versus-5-tool development probe is supported provisionally;
the substantive study needs more source and independent label review. No model
outcomes informed selection, exclusion, tool counts or recommendations.

## Audit boundary and actual yield

Inspected exactly **40 previously unreviewed records**, `multiple_57..99` excluding
76, 81 and 93, at Gorilla revision `f7cf7359b7ac615a0b294831c5ba2bc95ee4a000`.
The contiguous block follows the previously inspected business example 56; it is
purposeful discovery sampling, not a random estimate of BFCL-wide eligibility.
No additional live-category records were inspected. All 40 and their task families
are now development-exposed. Previously reviewed cases were not counted again.

The [unchanged source rows, schemas and keys](audits/phase3a/source_records.json),
[case-by-case review](audits/phase3a/review.json), [catalog references](audits/phase3a/catalogs.json)
and [reproducible counts/hashes](audits/phase3a/summary.json) are retained with
[attribution/license](audits/phase3a/NOTICE.md). Source input and answer files are
316,583 and 32,254 upstream bytes. A bounded refetch verified parsed equality with
the existing cache; cache files add one final newline, so upstream hashes are
recorded separately. No archive, benchmark dependencies or new data categories.

| Evidence | Actual count |
|---|---:|
| Audited candidate records / conservatively grouped families | 40 / 30 |
| Provisionally label-eligible records / families | 12 / 11 |
| Excluded records | 28 |
| Eligible business-function domains | 6 |
| Eligible no-call cases | 0 |
| Account-management or state-changing transaction cases retained | 0 |
| Source function occurrences / distinct names | 99 / 97 |
| Conflicting definitions under the same name / wire-name collisions | 0 / 0 |
| Function schemas rejected by the current converter | 5 |
| Eligible gold variants passing schema and existing subset-grader checks | 41 |
| Independent human reviews / model requests | 0 / 0 |

“Eligible” means a provisional, single-call **label** can be defended from the
question and stated interface. It does not mean an adequate competing catalog,
human-certified uniqueness, production API availability or successful workflow.
These are real public benchmark records, largely synthetic service interfaces;
consumer-facing retail/hospitality analogues are not production enterprise evidence.
Queries may retrieve current prices, but route selection does not require executing
the tool or knowing its current result. No outputs or transactions are simulated.

Exclusions, with one primary reason per record:

| Reason | Count | IDs after `multiple_` |
|---|---:|---|
| Outside declared business-operation scope | 18 | 60, 63, 64, 65, 66, 68, 69, 70, 72, 73, 83, 84, 85, 89, 96, 97, 98, 99 |
| Overlapping native capabilities or ambiguous intent | 4 | 61, 71, 77, 78 |
| Requested constraint not established by schema | 2 | 62, 91 |
| Native schema/default conflict | 1 | 79 |
| Requested action differs from tool action | 1 | 82 |
| Answer-key interpretation not supported | 2 | 88, 92 |

The ledger records secondary issues too. Examples: 78 has string defaults on array
parameters; 79 describes default `any` outside its enum; 88 accepts an unstated PC
platform and uses unsupported `optional` metadata; 92 maps vegetarian to vegan,
narrowing the requested result set. No answer keys or original schemas were repaired.
Near-duplicate families include legal lookup (58/59), environmental forecast
(60/63/64), route information (65/66), population lookup (71/72), museum information
(78/79), sports statistics (83/84/85), recipes (89/91), and circle geometry (97/98).
Mathematical families also overlap earlier development exposure and remain excluded.

## Competing-tool feasibility

Each sample retains every native tool and its original definition. Added tools
come only from the 40 audited rows, including valid functions from excluded cases.
A bad source question does not automatically invalidate all its function schemas.
Functions with unsupported metadata were not converted or silently rewritten.
Sample catalog counts below are **constructed, AI-reviewed ceilings within these
explicit pools**, not theoretical maxima over all BFCL or independent certification.

N = same business object with a related, non-substitutable operation; A = adjacent
operation/object in a plausible shared workflow; F = unrelated but mandatory native
tool. The classification and answer-uniqueness rationale are in `catalogs.json`.
Broad marketplace/travel pools are weak competitors and must not be called uniformly
hard or homogeneous enterprise catalogs.

| ID | Domain / target | Audited tools | N / A / F | 5 / 15 / 30 by size alone |
|---|---|---:|---|---|
| 57 | Finance / compound interest | 6 | 2 / 3 / 0 | yes / no / no |
| 58 | Professional services / divorce lawyer | 7 | 0 / 6 / 0 | yes / no / no |
| 59 | Professional services / criminal lawyer | 7 | 0 / 5 / 1 | yes / no / no |
| 67 | Workplace utility / translate | 3 | 2 / 0 / 0 | no / no / no |
| 74 | Market analytics / auction price | 3 | 0 / 1 / 1 | no / no / no |
| 75 | Market analytics / paint popularity | 5 | 1 / 2 / 1 | yes / no / no |
| 80 | Retail / instrument shop | 9 | 0 / 8 / 0 | yes / no / no |
| 86 | Retail / named-store board-game recommendation | 5 | 1 / 3 / 0 | yes / no / no |
| 87 | Retail support / game patch | 5 | 2 / 2 / 0 | yes / no / no |
| 90 | Hospitality / group restaurant | 19 | 3 / 15 / 0 | yes / yes / no |
| 94 | Hospitality / hotel quote | 19 | 0 / 18 / 0 | yes / yes / no |
| 95 | Finance / currency conversion | 7 | 0 / 6 / 0 | yes / no / no |

Only **57, 87 and 90** have enough N/A tools for the old five-tool 2/2 quota.
**None** meets the 15-tool 7/7 or 30-tool 14/15 quotas. Two broad travel catalogs
reach 15 tools by size, but neither supplies seven near competitors. No catalog
reaches 20 or 30. Thus **5/10/20 is also unsupported** across a meaningful paired set.
The one repeated source name is `weather_forecast` (three identical occurrences);
it is not counted as three distinct tools. No rename other than existing reversible
wire mapping is needed. Unsupported metadata occurs at 77:1, 82:0, 82:1, 88:0, 88:1.

Concrete source-derived examples:

- **57:** compound interest on 1000 at 0.05 for ten years, four periods per year.
  Simple interest is not equivalent; portfolio projection needs a stock and lacks
  quarterly compounding. FX conversion/stock lookup add distinct finance operations.
- **58/59:** two differently named lawyer searches can satisfy the same kind of
  request. They cannot be pooled as “distractors.” Each sample excludes the other;
  both records form one family, leaving few credible near competitors.
- **67:** translation, sentiment and word count offer a clean three-function
  contrast, but no defensible fourth/fifth workplace-text function exists in this pool.
- **86:** the query explicitly names BoardGameGeek, so Amazon is a plausible but
  non-substitutable retailer. The label specifies two players and strategy; we do
  not grade the subjective quality of a recommendation returned by a tool.
- **87:** Xbox patch lookup competes with reviews and prices for the same game.
  Only `games.update.find` performs the requested operation; game/platform and the
  optional global region are fully specified by the question/default.
- **90:** seafood in Seattle for five people requires `restaurant.find_group`.
  Other restaurant searches cannot represent all location/cuisine/group constraints;
  events and hotel/car prices cannot return the requested restaurant list.
- **94:** the user asks for a Hilton room quote, not a reservation. Room description
  and three nights fit the quote schema; no other hotel-pricing function is available.
  Many trip tools can be offered, but count alone would exaggerate difficulty.
- **92, excluded:** a vegetarian-and-gluten-free request is labeled vegan-and-gluten-free.
  Accepting that key would hide a changed query meaning; it is not repaired here.

## Supported recommendation before any model outcomes

Replace the proposed 5/15/30 study with a **3/5-tool development probe**, only if
the owner wants further integration evidence while dataset discovery continues.
The four supported example cases are **57, 86, 87 and 90**, spanning finance, retail
and hospitality: **four paired cases, eight requests, one repetition, all positive**.
86 and 87 share their expanded game catalog, so they are not four independent
enterprise environments. This is not a substantive enterprise reliability study.

All native tools stay in the three-tool set. The five-tool condition adds exactly
two source-derived **adjacent** operations, keeping each case's near competitors
fixed (two for 57/87; one for 86/90). This replaces the infeasible fixed-ratio quota
with a controlled expansion of adjacent tools around existing plausible competitors.
Tool count remains the single manipulated variable. No case or catalog was chosen
using model accuracy. The research question and possible null/ceiling outcome stand.

Sample sets and seeded nested ordering are recorded, with hashes, sizes and target
indices. Their schemas occupy **1,335–2,038 bytes at three tools** and
**2,686–3,267 bytes at five**. Definitions, optional parameters and descriptions
are unchanged across treatments. The old 20% distribution-matching constraint is
not fully attainable: case 57's median description length rises 29 to 69 bytes;
case 87's median property count rises 2 to 3. Do not claim matching succeeded.
These changes are measured consequences of adding the actual catalog entries.
Context size and target position remain confounded with expansion; no padding or
description rewriting is introduced. Hash ordering preserves relative order, not
absolute target position; sample positions are not balanced in four cases.

Primary benchmark metric: strict BFCL-compatible full-call correctness, paired
**five minus three tools**. Secondary: correct function selection/no-call decision,
JSON Schema validity, argument/type errors, wrong/extra/missing calls, provider and
incomplete failures, latency, token components, separate cost estimates and cost
per correct case. Preserve planned denominators and all failures. Report per-case
changes, not significance claims. No-call performance cannot be estimated here.
Final prompts, model/inference settings and treatment order still need freezing;
sample catalogs are not executable model requests.

The original **12-case 9-call/3-no-call pilot is infeasible from this audited pool**:
there are no negatives, only 11 provisional positive families and just four credible
small-catalog examples. Keep remaining eligible families for offline development,
not backfilling to hit 12. Future development target: 12 independent families only
after another approved source audit supplies the missing coverage and negatives.

The original **120-case held-out target is unsupported**. Recommend a conditional
first held-out target of **24 untouched families (18 positive, 6 native no-call),
48 requests at 3/5 tools**, after feasibility is established in a separately
authorized pool. None is selected now. There are 154 unreviewed `multiple` IDs after
the six prior and 40 current reviews, an ID upper bound rather than an eligible
family count; the category supplies no native no-call labels. A future custodian
must audit bounded `live_multiple` and irrelevance sources without exposing them
to prompt tuning. Do not infer yield or power from this purposeful block. At 24
pairs, worst-case approximate 95% difference half-width is about 40 percentage
points; this target is for modest descriptive scope, not small-effect detection.

## Verification, licensing, effort and approval

Source-derived: questions, tool definitions and alternative answer labels.
Automated: revision/ID bounds, native-tool retention, schema/name consistency,
41 eligible gold variants, hashes/counts, frozen sample ordering and repeatability.
AI-assisted: relevance, ambiguity, families, domain labels and answer uniqueness.
**Independent human verification: none.** Tests do not establish semantic truth.

Independent reviewers must check every query/key alternative and every offered
tool in the largest selected catalog, especially legal-search overlaps, scope of
portfolio calculations and restaurant group constraints. Preserve exclusions and
do not replace failures based on model performance. Estimate **4–6 person-hours**
for two reviewers to validate the four-case probe and resolve disagreements;
**10–16 person-hours** to independently review the full 40-case ledger/catalogs.
These are planning estimates, not logged review time. A 24-case held-out release
adds roughly 12–20 person-hours plus source-discovery time; actual yield is unknown.

Apache-2.0 permits redistribution subject to license/notices; this owner-authorized
bounded evidence includes both. Upstream references/hashes and modifications are
recorded. The current converter rejects nonstandard `optional` keywords; the current
BFCL importer accepts single-source-function rows only. Gold-variant checks reuse
the existing strict subset grader with a target-specific audit view; they do not
prove a full multiple-function integration or equivalence to all official grading.
No source calls are executed. A later approved implementation needs multiple-tool
grading tests, immutable manifests and leakage checks before paid execution.

Proposed model remains `gpt-6-luna`, Responses, standard tier, sequential, zero
retries, output ceiling 4,096. With illustrative 2,000 input/200 output tokens per
request and all input charged as 30m writes, eight calls cost **$0.0028**; using
12h writes as a reserve scenario gives **$0.0048**. These are assumptions, not measured
usage. For a frozen body ceiling of 8,000 UTF-8 bytes plus 256 framing tokens,
the highest reviewed input/write rate yields
`8 × (8,256 × $0.25 + 4,096 × $0.50) / 1,000,000 = $0.032896`.
Propose **$0.05 / eight requests** only after actual payload preflight. For 48 future
held-out requests the same reserve is $0.197376, proposed cap $0.25 separately.
Rates and the prospective explicit-30m policy are in [the accounting proposal](phase3a_cache_policy.md).

Owner gates: accept the reduced scope/conditions and validity limits; approve
independent label/catalog review and further bounded source audit; resolve all
disagreements; approve the separate accounting policy; then authorize minimal
experiment integration and freeze requests/prices/settings before any paid run.
No held-out implementation, 54-request execution, smoke modification or paid call
was performed. The broad enterprise study remains a **no-go on current evidence**.
