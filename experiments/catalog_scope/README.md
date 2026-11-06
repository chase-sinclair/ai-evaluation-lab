# Experiment 02 · How large should a freight agent’s tool catalog be?

**Ready for owner review.** Twelve original Northline Freight requests each face the same three nested catalogs. Eight requests require exactly one operation with exact arguments. Four require no call. The unit of comparison is the scenario: **12 paired cases, 36 proposed requests, one response per case and condition**. This is a single-turn routing study. The tools are fictional and have no execution backend.

## What changes

| Tools | Available operations | Serialized tool definitions | Complete canonical request body |
|---:|---|---:|---:|
| 5 | Forecast arrival, move an appointment start, read unpaid balance, hold a payout, read received units | 1,430 bytes | 2,075–2,101 bytes |
| 10 | Add one adjacent lookup per domain, such as invoice due date or assigned dock door | 2,704 bytes | 3,349–3,375 bytes |
| 20 | Add two close alternatives per domain, such as original versus paid invoice amount or preview versus commit a dock move | 5,565 bytes | 6,210–6,236 bytes |

Every scenario asks the same question in all conditions. Tool names, descriptions, strict schemas, system instructions and model settings are fixed. All five core operations remain available. Each added function returns a different fact or performs a different action. For example, the amount already paid cannot answer how much remains unpaid, and a preview cannot commit a move. The four no-call controls cover a draft-only request, a missing booking ID, a definition and an explicit prohibition on access. Their rationales and expected arguments stay outside model inputs. [Scenario fixtures](scenarios.yaml) · [Catalog](catalog.yaml)

For the eight required calls, each target occupies the midpoint of a different eighth of the list (rounded to an available index), with the same relative-position stratum in all three conditions. The remaining tools use a seeded per-case hash order. No-call cases use a preassigned focal tool to vary layout without adding a cue to the user text. A seeded shuffle interleaves the 36 trials. No content or order was tuned from model outcomes.

## Scoring and deliverable after a run

Primary outcome is exact action accuracy per catalog, out of 12 planned trials. Grade native Responses function-call items. Required cases need one offered function, a schema-valid argument object and the exact authored values. No-call cases need zero calls and a completed response; the quality of the prose is outside the endpoint. A written description of a call cannot satisfy a required call. A refusal or empty model output cannot earn a correct no-call. Multiple calls, unoffered names and malformed payloads are invalid. An offered but incorrect operation or a schema-valid wrong value is a task error.

Report exact successes, missed and wrong calls, tool identity on the eight required cases, unnecessary calls on the four no-call cases, schema validity on emitted calls and exact arguments conditional on correct identity. Include measured denominators and separate invalid, provider, grader and unattempted counts. Break out potentially consequential writes (committing a move or holding/releasing a payout) from read errors by inspecting the recorded name. Compare each scenario across conditions, including gains as well as regressions; the shared summary provides all three paired comparisons.

Report mean request latency, reported input/output tokens and estimated USD per condition, known totals and missing telemetry. Schema/body bytes above are observed **offline sizes**. Token allowances below are budgeting heuristics. Actual token consumption and inference latency require live responses. The generic mock summary is a plumbing check; its timings and grades carry no model-performance interpretation.

## Exact live proposal · pending separate approval

- **Model and endpoint:** `gpt-6-luna`, OpenAI Responses, standard service tier (`default`), global endpoint, `store=false`, automatic function choice and parallel tool calls disabled. No hosted tools, function execution, tool results, retries or follow-up turns. Model inference parameters use provider defaults, with reported settings retained. Account access is unverified. [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)
- **Limits:** sequential, at most 36 requests, 1,024 output tokens per request including reasoning, proposed estimated-spend cap **$0.07**. The full-body reserve is **$0.05571150**, using 149,118 input-token allowances (canonical UTF-8 body bytes plus 256 per request) and 36,864 output tokens. All input is reserved at the highest documented standard short-context write rate. Actual usage-priced estimates use reported cache partitions. Unknown cost stops the run.
- **Rates checked November 6, 2026:** per million tokens, $0.10 uncached input, $0.01 cached read, $0.125 for a 30-minute write, $0.25 for a 12-hour write and $0.50 output. The reserve is a conservative estimate rather than a provider billing guarantee. No cache lifetime or billed dollar amount is inferred. [OpenAI pricing](https://developers.openai.com/api/docs/pricing)
- **Approval digest:** `ba9ef652722bd5e7611b8713c7dbe3ae4ee4d7e608239fc733623dc0846cc999`. The canonical JSON digest covers the order, prompts, schemas, answer-key dataset hash, per-trial logical and body hashes, runtime config, pricing and cap. Reconstruct any body using the shared settings, its case's messages, and the ordered list of function definitions. [Frozen manifest](request-manifest.json) · [Proposed settings](live-proposal.yaml)
- **Execution boundary:** only after explicit owner approval, recheck model and dated prices, run the offline freeze check, and use the reviewed checkout with the fixed run ID. Before every transmission the dispatcher verifies the ordered body and logical hashes. It stops on drift, a prior run directory, provider failure, unexpected model/tier, missing or inconsistent accounting, grader error or a token/spending guard. Preserve partial records. Wrong answers and invalid model outputs with complete telemetry remain observations. Do not rerun a partial or failed attempt without a new decision.

Offline commands, from the repository root:

```sh
uv run --offline eval-lab validate catalog_scope
uv run --offline eval-lab run catalog_scope --dry-run
uv run --offline eval-lab run catalog_scope --mode mock
uv run --offline python -m experiments.catalog_scope.freeze
```

Only the following command would dispatch live requests. It has **not** been run against the API:

```sh
uv run --offline python -m experiments.catalog_scope.approved_run --live --approval-digest ba9ef652722bd5e7611b8713c7dbe3ae4ee4d7e608239fc733623dc0846cc999
```

The package manager’s offline flag controls dependency resolution. The explicit live entry point would use the network. The SDK transport test exercises that path locally with scripted responses and blocked sockets.

## Interpretation

This design evaluates expanding a deliberately curated catalog into adjacent and confusable operations. Tool count, semantic competition and prompt length grow together. Strict schemas limit the types of malformed arguments one can observe. The small authored sample and single draw per cell support case-level implementation decisions, not population estimates. All target operations are in the small catalog by construction, so the benefit of broader access for **newly supported tasks** is unmeasured. No real model outcomes or downstream business costs have been observed.
