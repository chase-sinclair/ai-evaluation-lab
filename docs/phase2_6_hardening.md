# Phase 2.6: prospective accounting and diagnostics

Reviewed November 4, 2026. No paid requests. The original smoke findings, grades,
configuration, dataset and result files remain unchanged.

## Cache policy clarification

OpenAI documents `prompt_cache_retention=24h` as maximum retention, independently
of `prompt_cache_options.ttl`, the minimum lifetime used for cache-write pricing.
For GPT-5.6 and later, the documented default minimum is 30 minutes; Responses also
supports 12 hours. Writes cost 1.25 times or 2.5 times ordinary input respectively
(total rates, not additional surcharges). There is no documented 24-hour write
price to infer from the retention field. Different breakpoints can use different
minimum lifetimes. Minimum lifetime is not a deletion deadline. Sources checked
November 4: [caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)
and [Responses reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create).

The six preserved smoke responses have null/absent `prompt_cache_options` and no
`cache_write_tokens_details`; three report positive write totals. Consequently the
old short-cache calculation remains a **scenario**, not reconstructed billing.
The previously reported maximum retention alone is neither proof of a 12-hour
write price nor proof of a protocol change. No historical cost or grade was rewritten.

## Accounting contract

`Usage.cache` retains read/write totals, writes split by minimum lifetime, reported
minimum TTL, maximum retention and service tier. Missing values stay null. Totals
must be nonnegative integers, reads plus writes cannot exceed input, and lifetime
counts must sum to the reported write total. Ordinary input is total minus reads
minus writes. Output already includes reasoning tokens; it is charged once.

`Pricing.cache` specifies service tier and separate read/write rates. The parent
snapshot supplies exact model, source URL, verification date and version. It is
omitted from serialization when absent, preserving frozen legacy config hashes.
No historical configuration was migrated. For a future reviewed Luna standard-tier
snapshot, the format would be:

```yaml
version: openai-standard-2026-11-04-cache-v1
verified_date: '2026-11-04'
source_url: https://developers.openai.com/api/docs/pricing
model: gpt-6-luna
input_usd_per_million: 0.10
output_usd_per_million: 0.50
cache:
  service_tier: default
  read_usd_per_million: 0.01
  write_usd_per_million: {'30m': 0.125, '12h': 0.25}
```

These are dated estimated USD rates, not invoice verification; see the official
[pricing page](https://developers.openai.com/api/docs/pricing). This example is
documentation, not an executable or approved live configuration.

The adapter reads cache details from SDK raw JSON, including additive fields that
may not have full SDK typing. It records reported cache options without changing
the request payload. Invalid accounting leaves raw evidence intact and usage
unavailable. Missing counters, prices, tier correspondence or write-lifetime
breakdown produce an unknown cost with a reason. Response-level minimum TTL alone
does not establish every breakpoint's TTL. No maximum-retention-to-price mapping
or implicit default-price substitution is made.

Each new run record has `cost_details`: source/version/date, tier, cache policy,
token partition, component costs and total, or an explicit uncertainty reason.
Legacy totals-only usage and legacy pricing retain their old arithmetic under
`legacy_totals_only`; that compatibility estimate is not cache-aware billing.
The OpenAI adapter always constructs cache metadata, so actual new Responses
outputs cannot silently enter that legacy path. Cache-aware pricing paired with
totals-only usage is unknown. New snapshots reserve the highest configured input
or write rate in preflight, require both supported write rates and standard tier,
and preserve the existing bounded output/request/spending guards. The sequential
runner durably records a response and stops before another call if cost is unknown.

Compatibility limitation: old snapshots remain loadable and their old preflight
estimates are unchanged. They are archival, not approved for another live run;
future approvals must use a complete current cache snapshot. A future response
that repeats the smoke's missing lifetime detail will intentionally halt execution.
Resolving that requires owner-reviewed billing evidence or a separately approved
conservative accounting policy; this change does not invent one.

## Diagnostic contract

Strict BFCL grader `0.2.1`, answer alternatives and primary pass/invalid/failure
classifications are unchanged. Additional metrics have independent version
`bfcl-diagnostics-v1` and apply only to newly graded responses:

| Metric | Meaning |
|---|---|
| `schema_valid_arguments` | Completed, well-shaped response; every emitted call is offered and its arguments satisfy that request's JSON Schema. An empty call list passes this structural check. |
| `tool_selection_correct` | Completed response selects exactly the expected offered function, or no function for a no-call case. Argument values/types do not determine this diagnostic. |
| `benchmark_exact_correct` | Exact copy of the strict primary BFCL pass result, including its normalization and Python type rules. |

Malformed envelopes, refusals and incomplete responses do not receive positive
diagnostics. A recognized target with malformed argument text can have correct
selection but invalid schema. Integer interval `[1, 3]` is JSON-number compatible,
yet fails the pinned BFCL float-list rule; `[1.0, 3.0]` may pass. Neither diagnostic
rescues a benchmark failure. Existing `full_call`/`well_formed` keys are retained.

Shared summaries aggregate experiment-supplied submetrics without BFCL-specific
runner logic, per condition and overall, with measured/unmeasured record counts
and diagnostic versions. Means cover measured records, **not** all planned cases;
provider failures must still be read from primary failure rates. Missing metrics
in older records are not treated as false or silently backfilled. Cache partitions
also disclose their coverage. Existing primary paired summaries remain unchanged.

## Preservation and verification

The original smoke was only read for cache field inspection and file hashing;
it was not rerun, regraded, summarized into its directory or modified. SHA-256:

| File under ignored `results/bfcl-smoke-v1/` | SHA-256 |
|---|---|
| manifest.json | e1d5ac94c2b0b0baab9d059ed47ccbe7674196f8515f7727b2739049260147cb |
| plan.json | a979593b8c76e6d1eb829e487c195d654af80bba12f7c45f069edde7dbf5a1a3 |
| records.jsonl | a7692e77f026e634728d338ed104648d5e4b7ea25ecd85996a6998a7de65d5a0 |
| summary.json | dc83c4a1fae1b65dab2ed319dab1480429d5642acc355529d77aba84b58096f7 |

Offline tests cover mixed TTLs, no double charging, malformed/missing counters,
missing rates, tier mismatch, conservative reserves, SDK field preservation,
uncertain-cost stopping, strict numeric types, malformed/unoffered calls, no-call,
incomplete output and diagnostic denominators. The 388 existing checker decisions
remain regression evidence. See [verification](verification.md) for final commands
and results. No raw results, external dataset files or credentials are added to Git.
