# Protocol gate before a real pilot

No live experiment is authorized by the handoff. The owner must approve:

1. Dataset and exact revision, license/use conditions, sample IDs, subset download, and size.
2. Provider, exact model ID, supported inference options, prompt, and bounded output tokens.
3. Dated pricing snapshot, request count, USD ceiling, and abort criteria.
4. Pilot protocol and data handling. No private material or credential-bearing prompts.

Protocol template:

- Hypothesis / null hypothesis; distinguish causal study from system comparison.
- Experimental unit, primary variable, paired conditions, fixed controls, confounders.
- Provenance, sample-selection seed, pilot/development split, frozen held-out IDs and hashes.
- Target and distractor selection; expert check that no distractor is a valid alternate.
- Versioned prompts and grading/equivalence rules; never tune on held-out failures.
- Model/provider/settings, repetitions, randomized order, planned requests and maximum cost.
- Correctness, task success, latency, usage, estimated cost, and cost per correct task.
- Failure policy: all planned trials in primary denominator; separate attempted denominator,
  provider errors, invalid outputs, grader errors, task failures, and unattempted trials.
- Abort on uncertain billing, approaching limits, invalid controls, or broken grader.
- Statistics: case-paired differences and case-clustered uncertainty; repeated calls are
  not independent samples. Cluster financial questions by filing/source where appropriate.
- Null/negative results, limitations, contamination threats, and deployment decision rules.

For a live configuration, change all condition providers/models consistently and add:

```yaml
# Placeholder only. Do not execute until every value and the protocol are approved.
max_spend_usd: 1.00
max_requests: 15
max_output_tokens: 256
pricing:
  version: owner-approved-snapshot-id
  verified_date: YYYY-MM-DD
  source_url: https://developers.openai.com/api/docs/pricing
  model: exact-approved-model-id
  input_usd_per_million: 1.0   # illustrative, NOT a verified price
  output_usd_per_million: 2.0  # illustrative, NOT a verified price
```

No real price/model is preselected. Rates must be positive and finite; the model must
match every request. Supply only `options: {}` in this first adapter. Unsupported
optional settings are rejected. Record provider-reported defaults after execution.
Server incompatibility is a provider error, not a reason to silently alter treatment.
Default endpoint only; no custom paid built-in tools, tool execution, or implicit retries.

After approval, install `uv sync --extra openai`, set `OPENAI_API_KEY` in the environment,
review `run <id> --mode live --live --dry-run`, then run with the same flags without
`--dry-run`. Even a live dry run makes no network call. CLI opt-in is a technical guard,
not a substitute for owner approval. The cap is best-effort: token estimation and billing
can differ, and a completed request can exceed the remaining estimate.

Adapter documentation verified November 3, 2026:
[Responses Python reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create),
[function calling](https://developers.openai.com/api/docs/guides/function-calling), and
[Python SDK](https://developers.openai.com/api/reference/python).
The implementation sends structured schemas, bounds output tokens, disables storage and
SDK retries, and retains usage, request ID, returned model, and reported inference settings.
It has local fake-transport coverage only; live account/model compatibility remains unverified.
