# Proposed first inexpensive API smoke test

November 3, 2026. **Not executed; owner approval required.** This tests endpoint,
schema, normalization, usage accounting and grading compatibility. Six calls cannot
establish a model comparison, tool-count effect, or enterprise deployment conclusion.

Recommend **`gpt-6-luna`** via OpenAI Responses API. The official
[model page](https://developers.openai.com/api/docs/models/gpt-6-luna) lists native
function calling, a 1,050,000-token context and 128,000-token output limit. On the
verification date it lists only this alias, not a dated snapshot. Record the requested
ID, returned model ID and effective settings; explicitly accept alias drift for this
smoke test. Reverify availability and prices at approval time. Do not invent a snapshot
identifier or silently substitute another model.

Use standard service, public US/global endpoint, text only, no hosted tools, no Batch,
Flex, Fast, long-context or regional-processing pricing. Listed standard prices are
**$0.10/M input and $0.50/M output**; cached input is $0.01/M and cache writes $0.125/M.
Conservative arithmetic below takes no cache-read discount and separately allows all
input at the cache-write rate. Prices were verified November 3, 2026 from the model
page; they are estimates rather than a billing guarantee.

## Fixed settings and six requests

The checked-in `experiments/tool_selection/bfcl/smoke_proposal.yaml` is a proposal,
not an executable ExperimentSpec or live authorization. Use the six exact requests
marked `smoke_proposal=true` in the frozen development manifest, in their existing
seeded order:

| Order | Case | Tools | Purpose |
|---|---|---:|---|
| 1 | irrelevance_0 | 30 | Correct no-call despite many schemas |
| 2 | simple_python_13 | 5 | Float array and string-alternative grading |
| 3 | simple_python_0 | 5 | Optional argument preserved |
| 4 | simple_python_13 | 30 | Same integration target in larger set |
| 5 | irrelevance_0 | 5 | No-call in smaller set |
| 6 | simple_python_0 | 30 | Same triangle target in larger set |

Each request's full payload and SHA-256 are in `bfcl/development_requests.json`.
The proposal uses one repetition, seed 42, unchanged target schemas and messages,
`max_output_tokens=4096`, `tool_choice=auto`, `parallel_tool_calls=false`,
`strict=false` for every tool and `store=false`. The existing adapter uses zero
retries and a 60-second timeout. No function is executed.

No temperature, top-p, seed or reasoning setting is sent: the existing adapter rejects
optional inference settings. Luna's documented default reasoning effort is medium;
do not label this a temperature-zero or deterministic model run. Capture reported
defaults. The 4096 output bound includes room for hidden reasoning; truncation is a
failed request, not permission to increase the limit mid-run. Function schema handling
follows the official [function-calling guide](https://developers.openai.com/api/docs/guides/function-calling),
including explicit non-strict schemas to preserve optional fields.

## Token and cost planning

Exact schema sizes range from 1,881 to 11,477 UTF-8 bytes across these six requests.
Summing serialized-request bytes / 4 plus 256 framing tokens per request gives about
**12,084 input tokens** (a heuristic, not tokenizer output or measured usage).
Plan for **500–1,500 billed output tokens per request**, including reasoning,
or **3,000–9,000 total**; this is a planning assumption, not a prediction verified
against this model. At standard rates that is approximately **$0.00271–$0.00571**.

The engine's more conservative byte-per-token-plus-framing estimate gives **43,740
input tokens**; maximum output is **6 × 4096 = 24,576 tokens**. Standard-rate upper
planning estimate: `43740 × 0.10/M + 24576 × 0.50/M = $0.016662`.
Charging all input at $0.125/M instead yields **$0.0177555**. Even twice that
estimate fits the proposed **$0.05 total spending limit and six-request maximum**.
These heuristics and the guard are best-effort, not a provider billing cap. Account
credit/top-up purchases are not authorized by a five-cent request budget.

For context only, the full 54-request development matrix projects $0.1480089 using
the standard conservative estimate. It is **not** included in smoke approval and
its checked-in ExperimentSpec deliberately retains `max_spend_usd: 0`.

## Approval, aborts and validation

Owner approval must cover: these six hashes and cases, transfer of the small public
Apache-2.0 subset, the model alias limitation/default settings, verified rate snapshot,
six requests, 4096 output tokens each, and the $0.05 cap. This does not authorize
another model, retries, the full pilot, held-out data, or paid account provisioning.

After approval, prepare a bounded invocation using the existing runner/immutable
record store for **only these six requests**; do not run the 54-case plan with a
six-request cap (preflight correctly rejects that). A live six-request invocation
has deliberately not been activated in this preparation phase. First compare its
rendered payloads to the frozen hashes and rerun budget preflight. Preserve sanitized
raw/parsed responses, request IDs, sent/reported settings, usage, statuses, latency,
source and request hashes; retain all errors and unattempted planned trials.

Run sequentially, no retries. Abort automatically on a provider error, timeout,
missing usage, or insufficient remaining estimated budget (existing runner behavior).
An uncertain billed request consumes a request slot; do not replay it. Before starting,
abort on schema/manifest drift, account/model unavailability, unsupported settings,
price changes or inability to enforce the six-request ceiling.

Task errors, malformed responses and output truncations count as failures and do not
trigger replacement calls. Finish at most the approved six requests, then **stop before
any further experiment** if any response is incomplete, refused, malformed, missing
model/settings/usage evidence, or disagrees with independently reviewed grading.
Check every call against its *actually offered* tool list, not just the complete
dataset catalog, during this six-response audit. An unexpected wire schema/default
also blocks expansion. Correct or incorrect task selection alone is not grounds
to edit the answer key or retry; report it as observed.

Acceptance for the smoke: server accepts unchanged optional schemas, completed
responses normalize correctly, all six attempts/failures are accounted for, reported
usage supports cost estimates, labels never appear in sent input, and deterministic
grades agree with manual inspection. Success does not require 100% model accuracy.
Any proposed fix must be versioned, tested offline and reviewed before additional
spend. No held-out research run is approved or implemented by this document.
