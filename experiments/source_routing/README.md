# Source routing pilot

Can a short source map help an AI reach authoritative evidence with less work? The paired comparison gives each model the same question, document collection, search implementation and response contract. The baseline receives the search instructions. The treatment also receives three lines describing what filings, transcripts and commentary establish.

## Workload

The portfolio research-note scenario was inspired by the public [FDE Simulation Helix exercise](https://github.com/kalyvask/fde-simulation/tree/main/simulations/1-full-engagement/helix-finance), whose repository is [MIT licensed](https://github.com/kalyvask/fde-simulation/blob/main/LICENSE). The four issuers, Market Ledger, 12 documents and 12 questions here were authored for this pilot. No third-party dataset, code, question, reference answer or grading rubric was imported or executed.

- Four questions ask about reported revenue, four about an executive's named driver, and four about a publisher's own analyst sample. Each issuer supplies all three types. The independent commentary is authoritative for its own survey and serves as a distractor for reported results and executive statements.
- Search ranks term overlap in document titles. Ties use a case-seeded ordering shared by both arms. A search reveals titles and IDs. An open reveals the text of a previously returned document. This keeps first result, first open and citation observable as different events.
- The fixed schedule has 12 questions × 2 arms × 3 provider families = 72 episodes. Each provider runs adjacent paired arms, alternating which arm runs first within each source type. The episode limit is six model turns including the final answer, so the ceiling is 432 model requests. The draft live output limit is 256 tokens per request. The offline harness enforces local byte and turn limits.
- The deterministic grader requires both the authored answer and the correct opened source. Case and whitespace differences in the answer are ignored. One strict JSON object is required. Invalid actions and exhaustion fail the episode. The corpus, paired order, messages and local limits are bound by the plan digest.

## Readouts

Report results separately per provider and arm. Keep all scheduled trials in the accuracy denominator. Show the gain and loss counts on matched questions. Report first search query, first result, first opened source type, cited source, and whether the authoritative source was ever opened. Save the action traces so searches before reaching authority can be inspected case by case.

For a live pilot, the primary efficiency measure is total usage-priced spend divided by correctly completed episodes, with elapsed time and total model, search and open calls reported alongside it. Include failed episodes in total spend. An arm with zero correct completions has an undefined cost per correct. Evidence of an efficiency gain requires lower cost per correct at equal or better task accuracy and an inspection of individual regressions. A drop in opens can support the proposed mechanism even if it does not cover the token overhead of the map.

This is a small development pilot with four issuer clusters and a deliberately simple search tool. A baseline that immediately finds the right source leaves little room for an improvement. The observed source order would describe each model with this instrumented document collection. Studying native search and public-site citations would require a separate protocol.

## Offline commands

```powershell
uv run --offline python -m experiments.source_routing plan
uv run --offline python -m experiments.source_routing smoke --traces
```

The scripted smoke supplies known actions to verify the trace and grader plumbing. It measures software behavior only. No credentials or network calls are involved.

## Draft live pilot

Candidate models are `gpt-6.2-sol`, `claude-sonnet-5-5`, and `gemini-4-argon`. Their published standard text rates on November 19, 2026 were $2 input and $10 output per million tokens at the planned prompt lengths. Gemini's introductory rates are scheduled to change December 1. Cached tokens and writes have separate rates. [OpenAI prices](https://developers.openai.com/api/docs/pricing) · [Claude prices](https://platform.claude.com/docs/en/about-claude/pricing) · [Gemini prices](https://aistudio.google.com/docs/pricing#gemini-4-argon)

Proposed spending limit is $5 for up to 432 requests, with a stop before the next call if its reserve would exceed the remaining budget. This is a proposed cap, not a spend estimate or a guarantee that the full matrix can complete at that cap. A live dispatcher needs approved provider settings, validated usage and cache accounting, an input allowance with per-call spending reserves, and durable receipts. Use text requests and local search only, with no native search charges or automatic retries. Before any paid run, freeze the wire settings and price snapshot, validate account access and reserves, and get explicit owner approval for the resulting protocol and limits.
