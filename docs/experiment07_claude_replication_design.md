# Experiment 007 · Does "context beats model tier" replicate on Claude models?

*Design for owner review, November 15, 2026. No implementation or inference is authorized by this document.*

## Decision

Experiment 006 found that on the Meridian finance SQL workload, `gpt-6-luna` with curated definitions beat `gpt-6.1-sol` with the schema alone. It averaged 15.3 against 6.7 correct out of 36, at about 29% of the cost. Curated context also lifted the expensive model the most, to 24.0. That evidence comes from one provider. This study asks whether the same pattern holds on a second provider's cheap and expensive models, with everything else unchanged. A team choosing a vendor should know whether the lesson is about the workload or about one model family.

The question is **replication, not ranking**. The study does not set out to decide whether GPT or Claude is better at finance SQL. Reasoning effort is not calibrated identically across providers, and the instructions were first developed against GPT models. A cross-provider score difference is therefore reported descriptively but carries no conclusion.

## Models

Current standard rates on the Claude API, prompts up to 100,000 tokens, USD per million tokens, checked November 15, 2026 on the Anthropic pricing page:

| Role | Model | Input | 5-minute cache write | Cache read | Output | Matching 006 model |
|---|---|---:|---:|---:|---:|---|
| Cheap | `claude-haiku-5-5` | 0.10 | 0.125 | 0.01 | 0.50 | `gpt-6-luna`, identical rates |
| Expensive | `claude-sonnet-5-5` | 2.00 | 2.50 | 0.10 | 10.00 | `gpt-6.1-sol`, identical rates |

The rates match 006 line for line, so cost comparisons across the two studies need no adjustment. Requests use global routing, the default. US-only inference would add a 1.1× multiplier, and the dispatcher rejects any receipt that reports it. Every prompt in this study is under 5,000 tokens, far below Haiku's 100,000-token threshold for higher prices. The dispatcher still checks each receipt against it.

## Design

The same 2 × 2 grid, questions, draws and order as Experiment 006:

| Cell | Model | Context |
|---|---|---|
| Haiku · A | `claude-haiku-5-5` | schema |
| Haiku · B | `claude-haiku-5-5` | curated |
| Sonnet · A | `claude-sonnet-5-5` | schema |
| Sonnet · B | `claude-sonnet-5-5` | curated |

There are 36 questions, three draws, and 432 single-turn requests. The order uses 006's per-draw question shuffle (seed 6006), with the four cells in the same rotating positions. Haiku takes Luna's slots and Sonnet takes Sol's, so each Claude request occupies the same place in the run as its 006 counterpart. Every draw finishes before the next begins.

### Request mapping

Each Claude request is derived mechanically from the frozen 006 request in the same position.

| Experiment 006 (OpenAI Responses API) | Experiment 007 (Claude Messages API) |
|---|---|
| `developer` message: reporting conventions, instructions and context package | Top-level `system`, one text block with the identical text |
| `user` message: canonical JSON of question and report fields | One `user` message with the identical text |
| `max_output_tokens: 25000` | `max_tokens: 25000` |
| `reasoning: {effort: "medium"}` | `thinking: {type: "adaptive"}` and `output_config: {effort: "medium"}`, set explicitly because Sonnet 5.5 defaults to `high` |
| `prompt_cache_options: {ttl: "30m"}` | `cache_control: {type: "ephemeral"}` on the system block (5-minute lifetime) |
| `service_tier: "default"` | Standard tier, global routing. No `speed`, `inference_geo` or `fallbacks` |

**No server-side fallbacks.** Fallbacks would let a declined request be re-run on a different model, which would put another model's answers inside a cell. The parameter is deliberately left out. Any refusal is recorded as that model's outcome.

**Prompt caching.** Both models cache prompts of 512 tokens or more, and every system block here is longer than that. Requests sharing a prefix recur within a minute or two, so the 5-minute lifetime stays warm without the 1-hour lifetime's doubled write price. 006 used a 30-minute lifetime, which affects cost only, never answers.

**No pilot or tuning on Claude.** The prompts, context packages and questions are the 006 texts unchanged. No Claude request is sent before the approved run. If the first live request is rejected for a configuration reason, the run stops after that request, at a cost of cents. A corrected configuration then becomes a separately frozen revision that needs its own approval.

Tests enforce the mapping. For every request, the system text and user text must equal the 006 developer and user text exactly. The only differences allowed are the model, the request envelope and the cache marker.

## Outcomes and grading

Grading is identical to Experiments 005 and 006. Every SQL answer must pass the admission grammar. It must then return the expected typed result on both evaluation snapshots in the isolated `meridian-worker:v3` sandbox. The four ambiguous questions need exactly the required clarification dimensions and an adequate question.

**Terminal handling:**

| Response | Treatment |
|---|---|
| `stop_reason: "end_turn"` | Parse the concatenated text blocks with the 005 answer parser. Thinking blocks are ignored and are empty by default. |
| `stop_reason: "max_tokens"` at the 25,000 ceiling | Acquired output-exhaustion failure. Charge it and continue, as in 006. |
| `stop_reason: "refusal"` | Acquired refusal failure. Charge it, record `stop_details`, count it as incorrect and continue. |
| Any other stop reason, an API error, or an accounting or integrity failure | Stop the whole run and seal it. |

**Reported per cell**, as in 006: correct answers out of 36 for each draw, the mean and range, stability per question, usage-priced cost, cost per correct answer, and observed API time.

**Pre-registered replication criteria**, fixed before any Claude request:

1. **Primary:** Haiku · B scores more correct decisions than Sonnet · A in every one of the three draws. In 006, Luna · B led Sol · A in all three draws.
2. **Secondary:**
   - Curated context raises each Claude model's score in every draw.
   - Paired on the same question and draw, Haiku · B gains more decisions than it loses against Sonnet · A.
3. **Reported but not a criterion:** whether Sonnet · B exceeds Haiku · B, and every cross-provider difference.

The write-up will say plainly whether the primary criterion held, held partly or failed.

## Clarification review

This study is designed and implemented by Claude, about Claude models, so Claude will not draft the clarification adequacy judgments. The masked worksheet shows only question and wording, never model, context, draw or provider. The owner either reviews it directly or has a non-Anthropic model draft judgments, as ChatGPT did in Experiment 005, before accepting them. If a worksheet item's question and wording exactly match an item the owner accepted in 006, the 006 judgment carries over and is listed as reused. The same rubric applies:
- **Q33:** period and cost basis.
- **Q34:** cost center or scope.
- **Q35:** both the list-minus-contracted discount and commitment savings named as the alternative.
- **Q36:** output unit and SKU for the denominator.

SQL grading is fully automatic and unaffected by who built the study.

## Budget and spending guard

**Expected spend.** In 006, the same workload at the same rates cost $0.825 in total. Token usage will differ by model, so the planning estimate is **$1–3**.

**Worst case.** Every request could produce 25,000 output tokens, which gives a reserve of about $62. Input bounds use the request's UTF-8 byte count plus 256. For this English and SQL text, that is a conservative ceiling on tokens. Claude's tokenizer is not available offline, so the dispatcher enforces the bound on every receipt and stops the run if reported input exceeds it.

**Proposed guard and cap.** The same per-request guard as 006 applies: no request is sent unless the accounted spend plus that request's worst case stays within the cap. The proposed cap is **$15**.

## Implementation plan

Everything below is offline until the owner approves a frozen digest.

| Component | Location | Notes |
|---|---|---|
| Anthropic SDK | `pyproject.toml` dev group, `uv.lock` | The official `anthropic` Python package, MIT-licensed and pinned. Live use only. Tests run offline with a mock transport. |
| Request builder and freeze | `experiments/claude_context/proposal.py`, `proposals/r1/` | Derives the 432 bodies from the frozen 006 proposal and verifies its digest first. |
| Receipt checks and pricing | `experiments/claude_context/accounting.py` | Checks model identity, `stop_reason`, the usage fields (`input_tokens`, `cache_creation_input_tokens` split by lifetime, `cache_read_input_tokens`, `output_tokens`), the global inference region and the 100K threshold. |
| Dispatcher | `scripts/acquire_claude_context.py` | Same freeze, approval, guard, seal and fail-stop pattern as 006. It sends with the SDK's raw-response interface and stores the raw HTTP body. It sets an explicit 900-second timeout, matching 006's read timeout, with zero SDK retries. |
| Replay, worksheet and scoring | `experiments/claude_context/analysis.py` | Reuses 006's grading, scoring and summary functions. Adds the replication criteria and a two-provider comparison table. |
| Tests | `tests/test_claude_context.py` | Text identity with 006, order alignment, pricing, every terminal case, guard stop, fault injection, seal and replay, and summary math. |

**Credentials.** The owner sets `ANTHROPIC_API_KEY` in their own environment, or signs in with `ant auth login`. Credentials never enter the repository, the manifest or a log.

## Run protocol

The protocol follows Experiment 006:
1. **Freeze** the request bodies and manifest.
2. **Approve:** the owner confirms the digest, reviewed revision, cap, current rates and Anthropic credit.
3. **Run once**, with no retries.
4. **Seal** the results.
5. **Audit:** replay the ledger and produce the masked worksheet.
6. **Review:** the owner or a non-Anthropic drafter judges the worksheet.
7. **Grade** offline.
8. **Report:** the replication verdict plus the descriptive cross-provider table.

## Limitations accepted in advance

- The questions are development-exposed: they were inspected in 005 and used in 006.
- The warehouse is synthetic, and the reference answers share accounting assumptions.
- **Settings are not calibrated across providers.** "Medium" effort, adaptive thinking and the tokenizers differ between providers. Absolute Claude-versus-GPT gaps are not interpretable as model quality.
- **Possible home-field advantage.** The prompts and context packages were developed and debugged against GPT models in Experiment 005.
- **Cache lifetimes differ:** five minutes here against 30 in 006. This affects cost only.
- **Conflict of interest.** Claude designed and implemented this study. SQL grading is automatic, and clarification review is kept away from Claude.
- Three draws describe variation. They do not support significance claims.
