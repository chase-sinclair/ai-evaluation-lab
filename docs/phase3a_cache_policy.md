# Proposed prospective cache policy — explicit 30 minutes

Reviewed November 4, 2026. **Proposal and offline calculator only.** The shared
adapter/runner and historical smoke protocol remain unchanged. No paid request
tested server acceptance; the installed SDK was tested with a local fake transport.

The official [prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)
documents request-level `prompt_cache_options.ttl="30m"`, with a minimum lifetime
and total write rate of 1.25 times ordinary input. Per-block breakpoints may override
that TTL. Maximum retention, including reported `24h`, is a separate control and
does not establish a 24-hour write rate. A minimum lifetime is not a deletion deadline.
The [Responses reference](https://developers.openai.com/api/reference/resources/responses/methods/create)
documents implicit versus explicit breakpoint mode. The proposed body contains:

```json
{
  "model": "gpt-6-luna",
  "service_tier": "default",
  "prompt_cache_options": {"mode": "implicit", "ttl": "30m"},
  "store": false,
  "parallel_tool_calls": false,
  "max_output_tokens": 4096
}
```

This fragment is not a runnable request. Complete inputs and function tools must
be frozen separately. Use the implicit breakpoint; prohibit **all explicit
breakpoints**, prewarming, previous-response/conversation links and unknown body
fields. Compare the complete actual serialized payload with its approved hash
immediately before sending. A later implementation must enforce this at the
transport boundary, not merely check a configuration object. No hosted tools.
The proposed complete body limit is 8,000 UTF-8 bytes; the offline validator rejects
larger bodies. Contradictory reported prewarming or output above the requested
ceiling also prevents continuation.

## Separate evidence, assumptions and reserves

1. **Provider-reported USD:** null unless the provider actually supplies a monetary
   charge; token usage is not an invoice. The current Responses evidence supplies
   counters, so the proposal never claims a provider-reported dollar amount.
2. **Reported-usage-priced estimate:** price ordinary input, cache reads, writes by
   reported lifetime and output at the dated snapshot. If positive writes lack a
   lifetime breakdown, this value remains **null**, even when requested TTL is known.
   The historical smoke is not retrospectively assigned a TTL or a new cost.
3. **Policy-based estimate:** only after exact-body validation and consistent total,
   read/write and output counters, estimate every write at the explicitly requested
   30m rate. Label that assumption separately; never insert inferred counters or
   TTL into provider usage. If no TTL echo/breakdown is returned, record the observed
   lifetime as unknown. A positive 12h write counter or contradictory TTL echo
   violates policy and prevents continuation, rather than being priced as 30m.
4. **Spending protection:** reserve the larger of the frozen request's full-output
   byte-based bound and the observed total-input/output cost at the highest reviewed
   input/write rate. Do not rely on the cheaper policy estimate or cache discounts
   to release budget. Unknown/malformed counters retain the frozen reservation and
   halt. An approved future ledger must charge this conservative amount, then check
   the next request's full reserve against the finite cap before scheduling it.

Under this **prospective** proposal, missing lifetime detail alone would no longer
block a new run if all request-policy and usage checks pass and the owner explicitly
accepts policy-based estimates. This is an assumption about compliance with the
requested TTL, not evidence of backend billing. Actual retention may be longer.
Missing counts or tier, contradictory telemetry, malformed usage, incomplete/error
responses, hash drift or any unauthorized body field still stop execution with
zero retries. Provider tier must be observed as `default`; absence is not confirmation.

The [pricing page](https://developers.openai.com/api/docs/pricing), checked November 4,
lists Luna standard rates per million tokens: input $0.10, cached read $0.01, output
$0.50. Cache writes are $0.125 for 30m or $0.25 for 12h using the documented total
rate multipliers. Keep model, service tier, source URL, verification date and pricing
version in every estimate. Reverify before approval; no invoice precision is claimed.

## Offline evidence and implementation boundary

`scripts/cache_policy_proposal.py` is a pure calculator/validator with no network
or provider construction. Its `continue_eligible` output means eligibility under
the **proposed policy only**, not authorization to send another request. Tests
demonstrate unknown reported lifetime versus a separate policy estimate, mixed/long
lifetime violations, observed tier mismatch, counter inconsistency, payload drift,
hosted-tool/history/breakpoint rejection, conservative reserves and exact SDK body
serialization through `httpx.MockTransport`. No credentials or sockets are used.

For illustrative counters of 1,000 total input, 200 reads, 500 writes and 100 output,
ordinary input is 300; absent write-lifetime detail leaves reported-usage-priced cost
unknown. The separate 30m policy estimate is $0.0001445. Spending reserves remain
larger and include full output allowance. Tests preserve the input evidence unchanged.

The current live runner still stops on unknown costs and the adapter still rejects
optional settings. Wiring this policy into an approved future experiment requires
a small reviewed change and transport-boundary checks; it is deliberately deferred
with full Phase 3 implementation. Approval must cover this accounting distinction,
the exact 30m payloads, current rates and finite request/spending caps. Old smoke
artifacts and grades are untouched, and `bfcl-smoke-v1` is never rerun.
