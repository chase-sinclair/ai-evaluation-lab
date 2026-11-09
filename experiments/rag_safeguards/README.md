# Enterprise RAG safeguards · Stage 1 approval packet

**36 question units, three customer outcomes per question, up to 108 sequential acquisition requests in two separately approved stages.** This implementation has been exercised with local scripted responses. Answer quality, operating cost and latency on real model responses remain unmeasured.

## What the owner would approve now

[Stage 1 exact bodies and ordered hashes](stage1.json) · [Questions, two-excerpt packets, keys and prompts](protocol.json) · [Approved design](../../docs/experiment03_phase_b_design.md)

- Approval digest: `ae2cedf7359d017a94a3be1d4b973bdf05ad784168f8e3a44c995bc0bcf4c92f`.
- Protocol SHA-256: `ce0eb649a6f7ef33ea1848086e1ba78104d666aedb71a13fd85fd7db2baf728b`. IDs and groups follow the design. The 12 routine controls and seven strengthened packets are included verbatim. Freeze the implementation commit alongside the manifest.
- 36 generator bodies (512 output tokens each) and 36 gate bodies (256 each). Sort by question ID; odd-numbered questions acquire the generator first and even-numbered questions the gate first. Both receive the same question and ordered excerpts. The system prompts carry the approved common authority rule and their stage instruction. No tools, labels, risk descriptions or unoffered passages enter the customer message.
- Global Responses API, `gpt-6-luna`, explicit standard tier (`default`), store disabled, provider inference defaults, 60-second timeout, sequential, zero retries, one immutable run directory. No tool execution or recovery calls.
- Exact canonical UTF-8 body bytes: generator **39,633** (range 1,012–1,351), gate **36,825** (934–1,273). Across 72 requests, 76,458 bytes plus 256 framing tokens per body yield **94,890** conservative input tokens. Output ceiling **27,648**.
- November 9: account model metadata confirmed without inference. Standard USD/M rates: $0.10 uncached input, $0.01 reads, $0.125 for 30-minute writes, $0.25 for 12-hour writes, $0.50 output. Input reserved entirely at the highest rate. Exact Stage 1 reserve **$0.03754650**, stage spending guard **$0.055224**, program ceiling **$0.10**. Reserve and receipt costs are estimates, not invoice charges. [Pricing](https://developers.openai.com/api/docs/pricing)

Reproduce offline with `uv run --offline python -m experiments.rag_safeguards.stages verify --stage 1`. After separate owner approval, reconfirm clean approved revision, account, prices, unused run directory and unchanged digest. The execution command would be:

```sh
uv run --offline python -m experiments.rag_safeguards.stages execute --stage 1 --live --approval-digest ae2cedf7359d017a94a3be1d4b973bdf05ad784168f8e3a44c995bc0bcf4c92f
```

## Stage 2 requires a new decision

Only after successful Stage 1 acquisition, run `uv run --offline python -m experiments.rag_safeguards.stages materialize --stage 2` locally. It verifies the Stage 1 seal, complete ledger and ordered receipts. For each generator it binds the request and receipt hashes, response ID and SHA-256 of the extracted UTF-8 text. The verifier user message contains exactly the original question, the two excerpts and that generator reply as a JSON string. The verifier uses the common authority and verifier instructions. Gate verdicts do not affect inclusion or verifier input.

Materialization writes the private 36-body proposal once and prints its new digest. Submit the exact ordered manifest, reviewed source bindings, remaining spend and reserve to the owner. Each verifier is limited to 256 output tokens and 3,600 input allowance including framing; no truncation. Stage 2 cap is the lesser of $0.037008 and the unspent cumulative cap. Stop for owner review if any envelope is exceeded. Real verifier bodies, their reserve and their approval digest do not exist yet.

Both dispatchers rebuild and match the approved manifest and each outgoing body. A provider error, invalid/incomplete stage response, model/tier mismatch, duplicate response ID, unknown accounting, or token/budget violation stops further scheduling. Partial receipts remain available. Reusing the single-use directory fails. Stage 2 dispatch requires its own explicit live flag and digest.

## Paired replay and grading

Use `uv run --offline python -m experiments.rag_safeguards.report .verification/enterprise-review.json` after acquisition. Give the reviewer the masked, deduplicated worksheet only. Preserve the original worksheet and complete a private copy. Use the same command with the copy and `--reviewed` to produce the analyst report. A fixed referral may reveal a block despite masking.

For each distinct reply, set reviewer, rationale, correctness and behavior (useful_answer, useful_partial, clarification, appropriate_abstention or other). Record each substantive claim's exact span, supporting or conflicting evidence, whether supported, each cited ID and its entailment, and whether the chosen source governs the subject, scope and date (null if authority is inapplicable). Cite both peers for unresolved conflicts. Empty claims are appropriate for a content-free referral. Have a second reader check decision-changing ambiguities if available. Format acceptance never establishes factual accuracy.

A uses the exact generator text. B and C pass it through unchanged on PASS and use the same frozen referral on BLOCK. Compare A→B, A→C and B→C per question and workload group. The report counts prevented unsupported answers, retained/introduced claim spans, preserved/lost correct or partial answers, redundant blocks and lost clarifications. It lists changed IDs and reports citation and authority numerators and denominators. Treat an empty denominator as unmeasured.

Report study acquisition telemetry separately from modeled serial customer workflows: A = generator; B = gate plus generator only on PASS; C = generator plus verifier even on BLOCK. The report gives stage-observed latency, tokens and usage-priced cost, modeled arm totals, paired differences and planned/evaluable denominators. Missing or failed required stages produce unavailable outcomes. Exclude seeded errors from all primary results. No seeded-error diagnostic is part of this implementation.
