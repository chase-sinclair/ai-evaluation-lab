# Experiment 02 · Does giving an AI agent more tools make it less reliable?

**The pilot reached a ceiling.** GPT-6 Luna made the correct tool decision on all 12 freight-desk scenarios with 5, 10 and 20 available functions. Moving from 5 to 20 tools increased input tokens by 2.25× and estimated API cost by 77.4%. It yielded no observed repair or regression. For these five desk operations, I recommend the smaller catalog as the default. [Frozen study design](../experiments/catalog_scope/README.md)

## Quality and operating cost

| Offered tools | Exact decisions | Correct required calls | Correct no-calls | Mean latency per request | Summed latency | Input tokens | Output tokens | Estimated API cost |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 12/12 | 8/8 | 4/4 | 0.995 s | 11.941 s | 4,044 | 422 | $0.0006154 |
| 10 | 12/12 | 8/8 | 4/4 | 1.133 s | 13.596 s | 5,544 | 381 | $0.0007449 |
| 20 | 12/12 | 8/8 | 4/4 | 1.316 s | 15.787 s | 9,108 | 362 | $0.0010918 |
| **All requests** | **36/36** | **24/24** | **12/12** | **1.148 s** | **41.324 s** | **18,696** | **1,165** | **$0.0024521** |

Latency is elapsed time around each sequential provider request, including network time. These are single observations per scenario and condition. Cost uses reported token counts and the approved standard short-context rates of $0.10 per million input and $0.50 per million output tokens. All 36 responses reported zero cache reads and writes. The API returned no billed dollar amount. The conservative preflight reserve was $0.05571150 against the $0.07 estimated-spend cap. [OpenAI pricing](https://developers.openai.com/api/docs/pricing)

## Per-scenario outcomes

“Exact” means the response contained precisely one native call to the named offered function, with all arguments schema-valid and equal to the frozen answer. “No call” means a completed response without a function call. The benchmark grades the action, not the quality of the prose. The columns reuse the same 12 scenarios; the run used 36 distinct responses. [Authored prompts and keys](../experiments/catalog_scope/scenarios.yaml)

| Scenario | Expected action | 5 tools | 10 tools | 20 tools |
|---|---|---|---|---|
| arrival-west | `shipment_eta` for SH-214 | Exact | Exact | Exact |
| dock-morning | `move_dock_slot` for BK-083, Dec 2 at 09:30 UTC | Exact | Exact | Exact |
| invoice-residual | `invoice_balance` for FI-771 | Exact | Exact | Exact |
| payout-duplicate | `hold_payout` for PY-031, reason “duplicate claim” | Exact | Exact | Exact |
| delivery-damage | `received_units` for DL-221 and BX-10 | Exact | Exact | Exact |
| dock-evening | `move_dock_slot` for BK-119, Dec 4 at 18:00 UTC | Exact | Exact | Exact |
| payout-audit | `hold_payout` for PY-058, reason “audit pending” | Exact | Exact | Exact |
| invoice-collections | `invoice_balance` for FI-904 | Exact | Exact | Exact |
| draft-only | Draft an ETA inquiry without looking up SH-460 | No call | No call | No call |
| unspecified-booking | Ask for the missing booking ID | No call | No call | No call |
| count-explainer | Explain expected versus received units | No call | No call | No call |
| conditional-hold | Acknowledge a possible future hold without acting | No call | No call | No call |

Every paired comparison had **0 gains and 0 regressions**. Across the 24 required responses there were zero wrong, missing or extra calls, zero unoffered functions, and zero schema or exact-value errors. Across the 12 no-call responses there were zero unnecessary calls. There were zero refusals, invalid or incomplete outputs, provider failures, grader failures or unattempted trials. All emitted calls were proposals; no function executed.

## Business decision

Use the **5-tool catalog for this desk’s tested workload**. It covered every required operation, handled every no-call scenario correctly and cost $0.0004764 less than the 20-tool catalog across the same 12 requests. The smaller catalog also exposes fewer operations. The study did not measure security incidents, realized business savings, or the benefit of completing work unique to the larger catalog. Broader access should have a concrete coverage requirement.

The results offer **no observed evidence of reduced reliability** as catalog size increased. They also cannot establish equivalent deployment reliability. The scenarios were authored, used explicit instructions and strict schemas, and each ran once per size. Adding tools also increased semantic competition and prompt length. The mean latency rose by about 0.32 s from five to twenty tools in this run; the measurements cannot isolate a stable latency penalty from provider and network variability.

## Execution and receipt integrity

On November 6, 2026 the clean checkout at `92a8ae98566a97c1646d18f9021c753c68b255f6` reproduced approval digest `ba9ef652722bd5e7611b8713c7dbe3ae4ee4d7e608239fc733623dc0846cc999`. The account’s model metadata and official pricing were checked before dispatch. The one-shot directory was absent. The run completed from 18:26:51 to 18:27:33 UTC with zero retries. All responses returned `gpt-6-luna`, tier `default`, medium reasoning and the 1,024-token output cap. The audit matched all 36 unique response IDs to the records, checked the logical and body hashes in run order, re-read the raw function calls against the offered schemas and answer keys, and recomputed the usage-priced costs. [Frozen manifest](../experiments/catalog_scope/request-manifest.json) · [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)

The immutable files remain in the ignored local run directory `results/northline-catalog-v1-once/`.

| File | SHA-256 |
|---|---|
| plan.json | `01e1b862c30f4a9025f1eaf16b686f92f4958de4e52689aee1ce56f5ae0d7e0d` |
| records.jsonl | `93129f8a9e543f9409d2b0e0f102f6c0bf2221a6f40fc88be217c6d74346de38` |
| manifest.json | `c8886aa298f5155fde715a488f94e2d5d861f638af1fcd608c63f1170c5de3ef` |
| summary.json | `1fce2a262610018dde9c3fadd654783c8daa3b23ef9a6d9cdf0a99858edcc895` |

The approved run is closed. Retries, resumed execution and expansion require a separate owner decision.
