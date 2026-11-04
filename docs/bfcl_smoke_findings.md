# Approved BFCL smoke execution — November 4, 2026

Executed the approved command once, on clean commit
`ca06c7c428dc47e2588c8d4b2d8b92bb84f09e68`, after readiness, frozen-manifest and
spending preflight passed. Run `bfcl-smoke-v1` lasted from 20:12:42 to 20:13:04 UTC
(15:12:42–15:13:04 America/New_York). Exactly six API requests were recorded, in the
audited order, sequentially with zero SDK retries. No model substitution, tool execution,
credit purchase, protocol change or subsequent experiment occurred.

All six provider responses completed with usage. No API/schema rejection, timeout,
refusal or incomplete response occurred. This establishes successful API transport,
schema acceptance and response normalization for these requests. It does **not**
establish full research-validation success: two outputs fail the frozen BFCL type rule,
and cost accounting omits reported cache-write premiums. Stop for owner review.

## Individual response review

| # | Case / tools | Observed response and manual comparison | Frozen grade |
|---|---|---|---|
| 1 | irrelevance_0 / 30 | No tool call; text gives triangle area 25 square meters. Correct zero-call outcome: BMI and record lookups cannot perform the requested operation. Text arithmetic is not the graded metric. | Pass |
| 2 | simple_python_13 / 5 | Calls offered calculate_area_under_curve with function `x^2`, interval `[1,3]`, method omitted. Correct offered function, formula matches BFCL normalization, allowed method omission. Integer interval elements violate BFCL's float-list rule. | Invalid output: invalid_arguments |
| 3 | simple_python_0 / 5 | Calls offered calculate_triangle_area with integer base 10, height 5 and optional unit units. Matches the key. | Pass |
| 4 | simple_python_13 / 30 | Same call/arguments and permitted method omission as #2. Correct offered function but same integer-versus-float-list failure. | Invalid output: invalid_arguments |
| 5 | irrelevance_0 / 5 | No tool call; text calculates triangle area 25 square meters. Matches the required no-call outcome. | Pass |
| 6 | simple_python_0 / 30 | Calls offered calculate_triangle_area with integer base 10, height 5 and optional unit units. Matches the key. | Pass |

All four emitted calls name tools actually offered in their respective requests.
All argument JSON parsed successfully and passes the offered JSON Schema. Both
integration calls are therefore **not malformed JSON or API schema rejections**:
the wire schema permits numeric array elements, while the frozen BFCL checker requires
Python float elements `[1.0,3.0]`. The stored invalid_output category reflects that
benchmark typing rule. Grader 0.2.1 was rerun offline on all records with their actual
requests and reproduced every stored grade. No grades, keys or raw records were edited.

The expression spelling `x^2` matches the frozen checker's punctuation normalization
of the accepted `x**2` string. This does not prove expression execution semantics;
no function was executed. That permissive normalization remains a documented limitation.

## Returned model, settings and measurements

**For every row below**, returned model ID was exactly **`gpt-6-luna`**, without a
dated snapshot identifier, and finish status was `completed`. Sent controls were
`max_output_tokens=4096`, `parallel_tool_calls=false`, `tool_choice=auto`, `store=false`,
and `service_tier=default`. Every offered schema had `strict=false`.
Every response reported temperature **1.0**, top_p **0.98**, reasoning effort **medium**,
reasoning mode **standard**, context **all_turns**, max_output_tokens **4096**,
parallel_tool_calls **false**, and service_tier **default**. Every raw response also reports
`prompt_cache_retention=24h`, although no retention policy was sent. This differs
from the short-cache pricing assumption and requires billing clarification. Temperature/top_p/reasoning
were provider defaults, not explicitly requested settings. No settings were inferred
from task success. Full sanitized provider fields remain in the ignored run records.

| # | Input tokens | Output tokens (reasoning subset) | Cache-write input tokens | Measured latency ms | Stored standard estimate USD | Short-cache rate scenario USD |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 1516 | 44 (27) | 1513 | 5447.569 | 0.000173600 | 0.000211425 |
| 2 | 414 | 28 (0) | 0 | 2849.194 | 0.000055400 | 0.000055400 |
| 3 | 390 | 27 (0) | 0 | 1357.273 | 0.000052500 | 0.000052500 |
| 4 | 1558 | 28 (0) | 1555 | 1073.697 | 0.000169800 | 0.000208675 |
| 5 | 372 | 72 (36) | 0 | 1908.910 | 0.000073200 | 0.000073200 |
| 6 | 1534 | 27 (0) | 1531 | 1250.668 | 0.000166900 | 0.000205175 |
| Total | **5784** | **226 (63)** | **4599** | **13887.311** | **0.000691400** | **0.000806375** |

Latency is the runner's measured duration of each provider invocation, not a server-only
measurement. Mean latency is 2314.552 ms; total run wall time also includes local work.
Reasoning tokens are already included in output tokens and must not be billed twice.
All six responses reported zero cache-read tokens. No usage field was missing.

The stored engine estimate uses all input at $0.10/M and output at $0.50/M. The raw
usage also reports cache_write_tokens, which the engine's simplified Usage/cost
contract does not price separately. At the approved short-cache write rate of $0.125/M,
the short-cache rate scenario is `0.0006914 + 4599 × (0.125 - 0.10)/1e6 = $0.000806375`.
This is a conditional calculation, **not a corrected invoice or overwritten result**.
The reported 24h retention is not resolved by the approved short-cache rate snapshot.
No extended-cache policy was requested. At the listed
12-hour write rate of $0.25/M the estimate would instead be $0.001381250. Both illustrative rate scenarios remain
well below the approved $0.05 estimated-spend cap, but neither establishes the actual
24h write charge. Actual billing and the applicable 24h rate were not verified.
The approved price sources and dated assumptions are in [the audit](bfcl_smoke_audit.md).

## Validation outcome and remaining issues

- Readiness/preflight: six frozen requests, 43,740 conservative input tokens, 24,576
  output-token ceiling, $0.016662 standard / $0.0177555 short-cache conservative cost.
  Both checks passed immediately before the one live invocation.
- Post-run verification: all six request hashes/order match the frozen manifest;
  actual tool membership, argument schema validity, stored grades and token/cost
  arithmetic checked offline. No parsing error or text replacement character was found.
- Frozen scoring: **4/6 pass**, **2/6 invalid_output**, zero provider/grader exceptions.
  Each condition has two passes out of three. These are three development cases
  under two treatments, not six independent tasks, and provide no evidence of a
  general tool-count effect or enterprise reliability.
- Integration transport worked, but overall validation is **qualified**, not an
  unconditional pass. The float-list rule demonstrates a schema/grader mismatch;
  the cost summary omits cache-write charges, and reported 24h cache retention differs
  from the preflight assumption. The single invalid_arguments
  diagnostic does not expose the exact argument/type distinction without manual review.
- Before any further experiment, review whether/how to version more precise grading
  diagnostics and usage pricing. Any grading change must be prospective and approved;
  retain this run's original grades. No implementation or protocol fixes were made here.

Raw plan, records, manifest and summary remain local under ignored
`results/bfcl-smoke-v1/`. This document is a derived review, not a raw response export.
Do not delete the run directory, retry these requests, or run the 54-request pilot or
held-out evaluation. The one-shot authorization has been used; further execution
requires new owner approval.
