# BFCL development pilot proposal — Phase 1.5

**Historical proposal. Phase 2 preparation is documented in
[bfcl_phase2_design.md](bfcl_phase2_design.md) and
[bfcl_smoke_test.md](bfcl_smoke_test.md). Those documents supersede the 20-case,
60-request plan, exclusions, payload-approval status and illustrative budget below.**

Reviewed November 3, 2026. **For owner review; no live run authorized.** This is a
derived expanded-choice-set study, not an official BFCL score. No additional experiment
module has been implemented. The inspected category and answer files are small text
files, read via GitHub; no archive, database, or benchmark package was downloaded.
No third-party question, schema, or answer files are committed here.

## Exact sources and subset

Freeze Gorilla commit **f7cf7359b7ac615a0b294831c5ba2bc95ee4a000** (official BFCL V4
reproduction checkpoint). Sources inspected at that revision:

- [Simple Python inputs](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_simple_python.json)
- [Simple Python answer alternatives](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/possible_answer/BFCL_v4_simple_python.json)
- [Irrelevance inputs](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_irrelevance.json)
- [AST checker](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/ast_checker.py)
- [Evaluation runner / irrelevance logic](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/eval_runner.py)
- [Dataset license declaration](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/README.md)

Select exactly `simple_python_0` through `simple_python_15` inclusive and
`irrelevance_0` through `irrelevance_3` inclusive: **20 development cases**.
Selection is purposeful for schema/grader compatibility, not random or representative.
The repeated mathematics families make even these 20 IDs correlated. Keep all these
IDs and near-duplicate families out of any later held-out evaluation.

The input files are 283,274 and 159,940 bytes respectively at this revision (previous
metadata inspection). Parse newline-delimited JSON; join answers by ID, never by row
position. Require exactly one match per ID, stable source/selected-row SHA-256 hashes,
dataset revision and transformations in the future manifest. Irrelevance uses the
category's zero-call rule; the official runner notes no separate answer file for it.
Answers remain grader-only and must never enter requests.

Apache-2.0 is declared by the pinned dataset README; preserve the license, attribution,
applicable notices and modification notices if approved source/checker code is later
redistributed. Owner approval is still required before committing benchmark payloads.

## Semantic review and exact distractor design

For each case retain its original single offered function. Add the first 4, 14, or 29
entries from this fixed authored list, yielding 5/15/30 total tools:

```
invoice, customer, ticket, order, warehouse, shipment, supplier, purchase_order,
inventory, product, employee, department, expense, refund, subscription, contract,
quote, payment, project, timesheet, asset, location, tax_code, currency_rate,
campaign, lead, appointment, service_plan, audit_event
```

Exact template for each entry X:

- Name: `lookup_record_X`.
- Description: `Read an existing X business record by its identifier. Returns stored fields only; does not calculate, solve, integrate, differentiate, or execute code.`
- Parameters: JSON object with one required string `record_id`, no additional properties.
- No tool execution; the experiment grades selection only.

Manual semantic audit of the inspected requests and original schemas:

| Selected IDs | Requested capability | Added-tool alternate-answer audit |
|---|---|---|
| simple_python_0, 10, 11 | Triangle area | All 29 templates only retrieve business records; none computes geometry. |
| simple_python_1 | Factorial | No arithmetic/recursive calculation capability. |
| simple_python_2 | Hypotenuse | No norm or distance calculation capability. |
| simple_python_3, 4, 5, 6 | Quadratic roots | No polynomial solving capability. |
| simple_python_7, 8, 9, 12 | Circle geometry | No circumference/area calculation capability. |
| simple_python_13, 15 | Definite integration | No integration or function evaluation capability. |
| simple_python_14 | Derivative | No differentiation capability; original schema's optional evaluation point needs review. |
| irrelevance_0 | Triangle area; original tool is BMI | Neither BMI nor any added record lookup computes triangle area. |
| irrelevance_1 | Quadratic roots; original tool sums lists | No root solver; record retrieval cannot substitute. |
| irrelevance_2 | Quadratic roots; original tool is geographic distance | No root solver or valid lookup request. |
| irrelevance_3 | Perpendicular-line slope; original tool finds critical points | Neither critical-point search nor record lookup answers the requested slope. |

This checks all 20 requests against the entire 29-tool pool by its exact common
capability restriction: none asks for a business record or supplies a record ID.
There are no name collisions with the inspected target names. Do **not** pool the
mathematical targets across cases: that would invalidate irrelevance labels and create
alternate triangle/circle/quadratic tools. The semantic result applies only to this
specified easy pool; arbitrary harder distractors have not been validated.

Before execution, independently review the rendered 60 requests against this design
and hash them. That mechanical conversion and second-review gate remain outstanding.
The first pilot intentionally uses easy distractors; a later difficulty manipulation
requires its own semantic review and protocol, not silent substitution.

## Grader compatibility requirements

The inspected checker enforces call count and names, required arguments, allowed-value
lists, types, and optional omission. Its empty-string answer sentinel permits absence;
it is not an instruction to insert an empty argument. It allows integer-to-float conversion
for float parameters and applies string normalization. Its model-aware name conversion
handles dots. The existing fixture grader does not implement these semantics.

For the future importer, map `dict` to JSON Schema `object` and `float` to `number`;
keep descriptions, required lists, defaults, and accepted answers unchanged. Use a frozen
collision-checked bijection for dotted names and canonicalize back before grading.
Optional arguments must stay optional: forcing all arguments required or replacing omitted
values with null changes the task. Use non-strict function schemas where needed, explicitly
recorded, and verify provider acceptance before freezing the protocol.

Exercise every selected positive answer, allowed omission, alternative string/numeric form,
wrong name, wrong type, extra call and invalid argument against the pinned checker or a
separately validated compatibility layer. Inspect dependencies before importing checker code;
do not install its whole model stack. For expanded sets dispatch using the target's schema
(or multiple-function checker); the simple checker assumes the target is the first schema.

The official irrelevance path can treat decoding failure as no-call. This study deliberately
requires a completed, successfully parsed empty structured-call list. Malformed output,
refusal/incomplete handling, and API failure must be explicit rather than awarded success.
Report this metric difference. Case 5 requires `root_type=all` in its answer key despite
the schema default; case 14's symbolic-vs-point derivative intent needs owner review. Keep
these as documented compatibility probes, not clean evidence of model reasoning accuracy.

## Controls, budget, and analysis

Hypothesis: expanding the available choice set decreases full-call success; null: no
case-paired difference. Hold provider, exact model snapshot, prompt, original schema,
output limit, and distractor template fixed. Use seed 42 to rank offered names by
SHA-256 of canonical JSON `[seed, case_id, name]`, as in the fixture; larger sets are nested
and preserve relative order. Seed trial execution order independently and record it.
Target absolute position changes with added tools; record it and report this limitation.

Tool count necessarily increases context length. Record exact schema UTF-8 bytes, rendered
request hashes and estimated/reported token counts. Do not truncate targets/descriptions
or pad smaller conditions post hoc. This tests expanded choice sets, not pure count
independent of context length. Easy unrelated descriptions restrict generalizability.

Plan: **20 cases × 3 conditions × 1 repetition = 60 calls**, sequential, zero retries,
maximum 256 output tokens per call. Proposed spending ceiling: **$1**, conditional on
an owner-approved exact model and verified price snapshot whose full conservative
preflight fits. Illustrative arithmetic only: 4,000 input / 250 output tokens at $1/$4
per million gives $0.30 for 60 calls. This is not a price quote. No exact model or price
has been approved; no inference claims or paid execution are made here.

All 60 planned trials form the primary denominator. Report per-condition correctness,
failure categories, latency, usage and estimated cost; pair by dataset/version/case ID.
Do not count repetitions as independent tasks. Report descriptive differences and individual
failures only: no significance tests or confidence claims from this small, correlated
development set. Incomplete pairs are explicitly excluded from paired descriptive results,
while remaining failures stay in planned-denominator condition summaries.

Abort on uncertain usage/billing, failed schema/answer compatibility checks, approaching
request/spend limits, or changed source hashes. The spending guard remains best-effort.
Owner approval must cover this subset and its ambiguities, licensing, rendered distractor
audit, grader compatibility, model/settings, dated prices, request/spend ceilings, and data
handling. Implement/import only after that approval; do not launch directly from this document.
