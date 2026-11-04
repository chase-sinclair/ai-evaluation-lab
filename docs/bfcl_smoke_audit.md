# Phase 2.5 — six-request audit and execution readiness

Date: November 4, 2026. **Preparation only. No paid requests executed or authorized.**
This supersedes the execution-preparation deferrals in the Phase 2 smoke proposal.

## Fresh request audit

Reviewed each of the six actual request objects, their tool order/descriptions/schemas,
and their expected outcomes separately from request generation. Compared questions
and original answer records to the pinned raw source files cached during Phase 2.
This is a fresh assistant audit, not a claim of a second human reviewer or external
research review. Dataset revision remains
`f7cf7359b7ac615a0b294831c5ba2bc95ee4a000`; no dataset or tool-set edits were made.

| Order | Case / condition | Expected outcome and optional-argument audit | Original function position (zero-based) | Schema bytes | Result |
|---|---|---|---:|---:|---|
| 1 | irrelevance_0 / tools_30 | Triangle area is requested. BMI requires weight and height, not base and height. No call; no optional BMI fields. | 14 | 11209 | Pass |
| 2 | simple_python_13 / tools_5 | Call calculate_area_under_curve with function x**2 (or the listed lambda/y= alternatives) and interval [1.0, 3.0]. Method may be omitted or trapezoidal. | 1 | 2149 | Pass with type caveat below |
| 3 | simple_python_0 / tools_5 | Call calculate_triangle_area with integer base=10, height=5. Unit may be omitted or units. | 4 | 1965 | Pass |
| 4 | simple_python_13 / tools_30 | Same integration question, function schema and alternatives as row 2; method remains optional. | 3 | 11477 | Pass with type caveat below |
| 5 | irrelevance_0 / tools_5 | Same triangle-area question and inapplicable BMI tool as row 1. Correct outcome remains no call. | 2 | 1881 | Pass |
| 6 | simple_python_0 / tools_30 | Same triangle question, integer arguments and optional unit as row 3. | 29 | 11293 | Pass |

All added tools are the exact authored record-lookup pool: only `record_id:string`
is accepted; descriptions restrict them to existing stored fields and explicitly
exclude calculation/solving/integration/differentiation/code execution. None of the
three questions requests a stored record or provides an identifier. No alternate
valid tool exists in any of the six sets under the offered capabilities. Mathematical
targets from other cases are absent, especially from the no-call requests.

Each request contains only the common instruction, original user question, offered
schemas and inference fields. No answer-key object, provenance, expected tool label,
or audit annotation is sent. Numbers/formulas stated in the original questions are
task inputs, not leaked labels. Poison-label tests still produce identical requests.
Required lists, descriptions and optional fields match the original schemas; type
conversion and `strict=false` remain unchanged. No null/blank argument is inserted.

The canonical request SHA-256 values, in execution order, were recomputed and match:

```text
f0ec87559690ac91a995eb78acabd79b1f99ea850cf6c2b1e6fc5f443679db55
19e62fdf95def0bd4b4bc31c8957713800cc00ee35fb77f2e431a6a88b1ebdb7
94281073740e3fd7d73059883fcbd730eb6bfb96b35d83531d490d3aa07176c6
79b64812179b61467c7ae9fe1f4fa96d8e97e2ceb4dec9e1c9c9d39473a9f6cd
f353dc83913b29bc5f328840d5e0610a7bf702e46566db2a6b9a1a7da8679c66
fd5159f3f414698348c14cbd45c638ff95ca9f0af3cc7c32f73286250264fcca
```

The entire Phase 2 manifest is pinned by canonical SHA-256
`c28821663e194956db707d6b595b0c1ee93356aacefabb8193098bdac583833b`.
The request manifest, case file, original configuration and source locks remain
unchanged. `prepare_bfcl --check` verifies the historical digest, every request and
all non-implementation metadata. It permits only explicitly documented current
grader/source metadata differences; it does not rewrite the old implementation hashes.
New run manifests record current source hashes and grader **0.2.1**. Dataset remains 0.2.0.

`bfcl/smoke_readiness.json` additionally records hashes of the actual Responses
JSON bodies. These differ from ModelRequest hashes because the adapter maps messages
to input, omits local output_format/options fields and adds API controls. The adapter
now explicitly sends `service_tier=default` for standard pricing, alongside
`store=false`, `tool_choice=auto` and `parallel_tool_calls=false`. Real SDK fake-transport
tests compare all six transmitted JSON bodies to the audited bodies. Hashes refer to
canonical JSON, not insignificant HTTP serialization whitespace. Payload/configuration
drift fails readiness verification before any provider construction.

## Grading correction and preserved limits

The runner supplies the actual ModelRequest as keyword-only grading context.
BFCL grading fails closed when it is absent and checks function membership against
`request.tools`, never the full distractor catalog. A warehouse lookup is therefore
invalid under tools_5 but a valid-shaped, incorrect task answer under tools_30.
Malformed arguments remain invalid; offered correct targets and completed no-call
responses retain their established grades. The generic runner knows nothing about BFCL.
Text-only experiments accept the context without using tools; the extension guide
and contract tests demonstrate that interface.

The shared runner also accepts an optional exact permutation of already validated
trial IDs. It cannot add, duplicate or drop trials. This small generic option preserves
the six rows' frozen order instead of reshuffling the reduced 3-case/2-condition view.
Default experiment ordering remains unchanged. No other experiment is implemented.

Known grading caveats are preserved, not silently repaired: the pinned BFCL checker
requires float elements `[1.0,3.0]` for case 13 and rejects `[1,3]`, despite JSON Schema
number accepting both. String normalization is not mathematical equivalence. Report
these as metric limitations when inspecting live responses. They do not create an
alternate valid tool or justify tuning the frozen questions/keys after observing output.

## Model, pricing and bounded execution

Rechecked the [official Luna model page](https://developers.openai.com/api/docs/models/gpt-6-luna)
and [pricing page](https://developers.openai.com/api/docs/pricing) on November 4, 2026:
`gpt-6-luna` is listed with Responses function calling; only the alias is published.
Reasoning effort is omitted and documented to default to medium. Standard text prices
remain $0.10/M input, $0.50/M output; 30-minute cache writes are $0.125/M (12-hour
writes are $0.25/M). No extended-cache policy is requested. Publication establishes
documented availability, **not this account's access**. No credential check or model
endpoint request was made. Account acceptance and returned model/settings remain live risks.

Executable configuration: `experiments/tool_selection/bfcl_smoke.yaml` selects the
same three cases and two conditions through a local view of the existing experiment.
Maximum six calls, $0.05 estimated spend, 4096 output tokens/call, sequential,
zero retries, 60-second timeout, no hosted tools, no function execution. The live
factory pins `https://api.openai.com/v1` instead of following a base-URL environment
override. Credentials must already be securely configured; do not paste them into commands.

Offline preflight (safe to run now, also the command's default behavior):

```powershell
py -3.13 -m uv run --offline python -m experiments.tool_selection.smoke_bfcl --preflight
```

Observed preflight: **6 trials, 43,740 conservative input tokens, 24,576 maximum output
tokens, $0.016662 standard estimate, zero provider calls**. Charging all input at
the 30-minute cache-write rate gives **$0.0177555**; even the 12-hour write rate would
give $0.023223, below the cap. The earlier typical-usage planning range remains
$0.00271–$0.00571, not a measured prediction. Estimates/guards are not billing guarantees.

**Exact execution command, only after explicit owner approval:**

```powershell
py -3.13 -m uv run --offline python -m experiments.tool_selection.smoke_bfcl --live
```

Run from repository root. Here `uv --offline` prevents dependency downloads; the
explicit `--live` flag would still permit the six paid API requests. Do not run it
during preparation. The command rechecks manifest/configuration/transport hashes and
spending before calling the existing runner. Run ID is fixed to `bfcl-smoke-v1`;
artifacts go to ignored `results/bfcl-smoke-v1/`. An existing directory blocks a
second invocation before provider creation, including after a failed/partial attempt.
Do not delete it to retry. No resume or replacement-call behavior was added.

The existing live guards stop scheduling on API errors/timeouts, missing usage or
insufficient budget; the immutable plan and partial records remain. Malformed,
incomplete and incorrect responses count as failures and are never retried. After
at most six attempts, inspect all responses, usage, reported settings and deterministic
grades before any further spending. Approval for this smoke does not authorize the
54-request pilot or a held-out study. No research design or dataset changes are proposed.
