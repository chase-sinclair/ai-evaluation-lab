# Phase 2 BFCL integration and research-design assessment

Reviewed November 3, 2026. Preparation only; no model calls or performance findings.
This document supersedes the 20-case plan and execution parameters in the
[Phase 1.5 proposal](bfcl_pilot_protocol.md). The research question and directional
hypothesis remain unchanged: expanded tool choice sets may reduce full-call accuracy.

## Frozen development dataset

Use Gorilla revision `f7cf7359b7ac615a0b294831c5ba2bc95ee4a000`, dataset
`bfcl-development` version `0.2.0`, grader `bfcl-python-subset` version `0.2.0`.
Keep `simple_python_0..15` **except 5 and 14**, plus `irrelevance_0..3`:
**14 call cases + 4 no-call cases = 18 cases**, 5/15/30 tools, one repetition,
**54 planned requests**. These are distinct IDs, not 18 independent task families.

Excluded before any model execution:

| ID | Reason |
|---|---|
| simple_python_5 | The question requests all roots; the optional root selector defaults to real roots, while the key requires all. Avoid conflating intent interpretation with selection. |
| simple_python_14 | A symbolic derivative is requested, but the optional evaluation point defaults to zero. Avoid symbolic-versus-point ambiguity. |

Do not replace exclusions based on observed model performance. The remaining keys
were reviewed against original questions and descriptions, including explicitly
requested inches in case 7 and Simpson integration in case 15. Those arguments are
schema-optional but answer-required; omitting them is a task failure. Unit/default
omissions in cases 0, 2, 8, 9, 10, 12 and 13 retain the upstream alternatives.

Exact source files (all at the revision above):

- [Simple inputs](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_simple_python.json), 283,274 bytes.
- [Simple answer alternatives](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/possible_answer/BFCL_v4_simple_python.json), 63,627 bytes.
- [Irrelevance inputs](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_irrelevance.json), 159,940 bytes.
- [AST checker](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/ast_checker.py), 25,032 bytes.
- [Irrelevance evaluation rule](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/eval_runner.py).
- [License declaration and category descriptions](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/README.md).

`experiments/tool_selection/bfcl/sources.lock.json` records SHA-256 of the exact raw
upstream bytes (including original EOF convention), plus canonical JSON hashes of
each retained input/answer row. The importer checks the revision, file hashes, byte
limits, ID uniqueness, missing rows, schema support, answer joins and selected-row
hashes. It reads only local files, with a 400,000-byte limit per source, and writes
exclusively to a new file. Cached whole category files are ignored by Git. Only the
selected records, attribution, Apache-2.0 license, verification vectors and request
manifest are committed under the user's Phase 2 integration authorization.

## Compatibility boundary

The shared runner, providers, contracts and experiment interface are unchanged.
BFCL-specific import, construction and grading live in `experiments/tool_selection`;
the original authored fixture remains the default experiment configuration.

Original source rows and answer alternatives remain in provenance/ground truth.
Requests map `dict` to `object`, `float` to `number`, and dots in names to underscores
with collision checks. Descriptions and optional/required arguments are unchanged;
`additionalProperties=false` reflects the checker's rejection of extra arguments.
Every offered function explicitly sets `strict=false`, so optional fields remain
optional in Responses API. No benchmark function or expression string is executed.

The narrow deterministic grader mirrors the selected Python AST rules: one exact
function, required arguments, gold alternatives, optional omission sentinel, Python
types, case/punctuation normalization, and ordered primitive arrays. In particular,
`4.0` is not an integer argument and bool is not int; top-level int-to-float coercion
is allowed but nested integer lists do not replace float lists in the pinned checker.
Do not silently extend these rules to nested dictionaries, Java, JavaScript, multi-call,
stateful tasks or arbitrary variable references.

`bfcl_conformance.py` runs explicitly selected functions from a locally cached,
hash-verified official checker, without its imports/model stack. It generated 388
decisions covering every retained positive case, all enumerated answer alternatives,
omissions, name/argument/type errors and normalized strings. Offline tests compare
the local grader with these frozen decisions. This is bounded compatibility evidence,
not proof of equivalence to the entire BFCL evaluator.

Known metric limits: BFCL string normalization removes punctuation including minus
and exponent symbols; it is not symbolic-math equivalence and can overaccept expression
strings. Retain this rule visibly for compatibility; do not interpret expression
grades as proof of mathematical correctness. No-call success requires a completed,
parsed empty call list; malformed output, refusal, incomplete responses and provider
errors fail. This is intentionally stricter than the official irrelevance decoder
path. No official BFCL score/comparability is claimed.

## Tool-set semantic audit and controls

Retain only each case's original function; never pool mathematical targets across
cases. Use the exact 29 record-only distractors listed in the Phase 1.5 proposal,
adding the first 4/14/29. Each takes only a record identifier and explicitly cannot
calculate, solve, integrate, differentiate or execute code. Every retained query
requests a calculation, supplies no business record identifier, and has no valid
record-retrieval interpretation. Therefore the added pool supplies no alternative
valid answer under its stated capabilities.

| Cases | Request and uniqueness review |
|---|---|
| simple_python_0, 10, 11 | Triangle area; only the original tool computes area. |
| simple_python_1, 2 | Factorial / hypotenuse; no added tool performs either operation. |
| simple_python_3, 4, 6 | Quadratic roots; no added root solver. |
| simple_python_7, 8, 9, 12 | Circle circumference/area; no competing geometry function. |
| simple_python_13, 15 | Definite integration; no competing integration function. |
| irrelevance_0 | Triangle area; original BMI function is inapplicable. |
| irrelevance_1, 2 | Quadratic roots; original summation / geographical distance functions are inapplicable. |
| irrelevance_3 | Perpendicular-line slope; critical-point search does not implement that operation. |

Fixed controls: identical case messages and original target schema, prompt v1,
provider/model/options, output ceiling and distractor descriptions across treatments.
Seed 42 ranks names by SHA-256 of `[seed, case_id, name]`; nested sets preserve relative
order. Trial execution order uses the existing seeded runner shuffle. Record target
position: its absolute position can change. No post-hoc description edits or padding.
Record exact canonical schema bytes; count and context length remain confounded.
The negative capability wording and repeated distractor template are strong cues.

`bfcl/development_requests.json` freezes the complete 54-request matrix in execution
order, case/condition IDs, tool order/count, target/source/answer/prompt/request hashes,
schema bytes, versions, configuration, LF-normalized implementation hashes, and six
smoke-proposal flags. Each request includes only messages/tools/settings; no provenance
or labels are passed. Tests poison all labels/provenance and verify identical requests.
Expected alternatives are checked in every condition. Owner review of the frozen
rendering remains required before live execution; this automated audit is not an
independent human review.

## Validity assessment from additional inspected source data

Recommendation: use this set for integration and schema/usage smoke testing only.
It is not sufficient evidence for enterprise tool-selection reliability. Ceiling
effects are plausible because the one mathematical tool is unlike every added
business lookup; a model can often ignore almost the entire catalog. Repeated
triangle/circle/quadratic families further reduce diversity. This is a design
prediction, not a measured result. Increasing count also increases context length
and changes target position. Public BFCL items may be training-contaminated.

Inspected the small pinned
[multiple-function inputs](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_multiple.json)
and their
[answer alternatives](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/possible_answer/BFCL_v4_multiple.json).
Concrete examples, not newly imported cases:

| Inspected ID | Observation from question, schemas and gold | Implication |
|---|---|---|
| multiple_46 | Sort names among filter, sum and sort tools; key selects sort. | More competition, though operation words remain obvious. |
| multiple_55 | Stock versus weather forecasting; key selects stock for Google. | Shared forecasting language, but easy domain separation. |
| multiple_56 | Average closing price versus trading volume/revenue; all share company/days/source arguments. Gold is Apple's 60-day average closing price. | Stronger enterprise candidate: same domain and similar schemas, distinct requested metric. |
| multiple_81 | Concert versus festival booking with overlapping add-ons. Gold selects the named artist's concert and backstage access. | Useful competing transaction tools; preserve artist/event and add-on constraints. |
| multiple_76 | Question includes asking material options, while gold orders a sculpture. | Exclude pending intent audit; do not accept an information request as authorization to transact. |
| multiple_93 | Question names a hotel, but hotel-booking schema lacks hotel identity. | Exclude or resolve lost specificity before treating full-call success as task success. |

Also inspected only a bounded 65,536-byte prefix of
[live multiple-function inputs](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/BFCL_v4_live_multiple.json),
reviewing the first five complete records; no full live-category download. The
drink/food edits in `live_multiple_0-0-0` and `live_multiple_1-0-1` have nested
preferences/defaults and realistic competing tools. The first requires interpretation
of a very-hot request against a coarser temperature enum. `live_multiple_2-1-0`
contains ride-related parameters beside a weather-oriented description; it needs
exclusion/audit. The remaining two mix transport and weather, a weaker distinction.
Live answer keys were not inspected, so none of these has verified label compatibility.
They are leads for a future audit, not approved evaluation cases.

For a later held-out study, prioritize single-call multiple-function categories with
nearby **but non-substitutable** capabilities, such as average price versus volume
and revenue. Keep native tool sets intact and add audited domain neighbors. Require
two reviewers to evaluate each query against every offered tool and document why
each distractor cannot fulfill it; reject overlaps instead of forcing one gold label.
For no-call examples, review the full largest set to ensure additions do not create
a valid call. Semantic similarity alone is not evidence of answer uniqueness.

Predefine easy versus near-neighbor distractor strata; balance description length,
schema complexity, optional fields and lexical cues before seeing results. Freeze
within-stratum pools across 5/15/30 conditions and use balanced ordering across cases.
Analyze choice-set effects within strata, explicitly retaining context-length
confounding; any added difficulty factor requires a separately approved protocol.
Keep the existing hypothesis, report null/ceiling outcomes, and do not select
distractors or cases to manufacture accuracy drops.

All reviewed IDs and near-duplicate task families are development material. No
held-out set has been selected, downloaded, implemented or evaluated here. Later
freeze untouched families before prompt tuning and choose sample size/cluster-aware
analysis from an explicit precision target. Current 18-case results, if approved,
will be descriptive case-paired differences with all failures retained, not
significance claims. Repetitions do not create new independent cases.

## Reproduction (offline)

From repository root, after `uv sync --locked`:

```text
uv run --offline python -m experiments.tool_selection.prepare_bfcl --check
uv run --offline pytest
uv run --offline ruff check .
uv run --offline ruff format --check .
```

The frozen subset makes CI independent of upstream downloads. To audit reimport,
place the three exact raw files at their relative paths under an ignored local cache
and run the following with a **new** output filename:

```text
uv run --offline python -m experiments.tool_selection.bfcl_data --source-dir datasets/cache/bfcl --output datasets/cache/bfcl/reimport.jsonl
uv run --offline python -m experiments.tool_selection.bfcl_conformance --checker datasets/cache/bfcl/ast_checker.py --output datasets/cache/bfcl/conformance-check.json
```

Compare their parsed contents to the committed case/vector artifacts. Neither command
fetches anything. `prepare_bfcl --output NEW_PATH` also writes exclusively to a new
file; changes to a frozen manifest need review and versioning. This command cannot
execute a model. The main CLI still defaults to the original five authored cases.
