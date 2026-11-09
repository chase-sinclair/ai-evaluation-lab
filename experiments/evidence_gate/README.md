# Alder Desk evidence gate · frozen plan for approval

**24 questions, 48 separate requests.** Each question gets one generator and one gate request with the same ordered three-passage packet. Generator-first and gate-first alternate within each family. Only the question and packet enter the user message. The [fixtures](fixtures.json) preserve the 12 original passages, 24 questions and reviewer keys. The [manifest](manifest.json) contains every body, logical and body SHA-256, pricing snapshot, dataset digest, acquisition order and exact fixed referral.

A1–A6 and P1–P6 expect PASS. M1–M6 also expect PASS because a focused clarification or accurate conditional explanation is possible. An unconditional answer may still be wrong. U1–U6 expect BLOCK. U5 and U6 omit an existing passage. The other four lack a corpus answer. All labels apply to the supplied packet.

## Approval boundary

Digest `d70bbdd6966d554ff08dd1a885cfc47b2738b965a52e2d7f82cf535defaa7947`. The offline check is `uv run --offline python -m experiments.evidence_gate.plan`. A future authorized invocation would append `--live --approval-digest <digest>`. Before executing, confirm exact clean approved commit, account availability, unchanged pricing, unused single-use results directory and reproduced freeze. No live request is authorized.

Use the global Responses endpoint, gpt-6-luna, standard tier, inference defaults, no tools, store disabled, sequential, zero retries. Generator output limit 512, gate limit 256. Standard rates checked November 9, 2026 in USD per million tokens: input 0.10, output 0.50, cached reads 0.01, 30-minute writes 0.125 and 12-hour writes 0.25. Reserve 60,462 input tokens (canonical UTF-8 body bytes plus 256 per request) at the highest input rate and 18,432 output tokens at 0.50/M. **Reserve $0.02433150; proposed cap $0.05.** This is an estimated spending bound. Stop on integrity, provider, incomplete output, malformed verdict, tier/model, usage or budget failure. Preserve partial receipts. Do not resume. A valid but wrong verdict is an experimental observation. [Pricing source](https://developers.openai.com/api/docs/pricing)

## Paired replay and review

After a run, use `uv run --offline python -m experiments.evidence_gate.report results/alder-v1-once .verification/alder-review.json` with an existing private output directory. The command creates a new blinded worksheet and prints the analyst report. Complete a copy following the [worksheet guide](review.md), then pass that file to the same command with `--reviewed`. Never commit raw responses or populated reviews.

PASS replays the generator text unchanged. BLOCK uses the fixed referral. The runner's generator grade verifies a nonempty completed text response only. The gate grade measures packet-relative verdict accuracy. Neither grade measures answer quality. Use human-reviewed pairs for that endpoint. Report claim-to-ID precision, supported claim citation coverage, decision counts by family and evaluable denominators. Unattempted and invalid stages remain failures or missing pairs.

Credit a prevention only when standard actually made an unsupported claim and gated avoided it. A block duplicating a correct abstention earns no repair. Show lost useful A and P answers and lost M clarifications. For each evaluable pair compare observed generator latency with **modeled serial-workflow latency** (gate plus generator on PASS, gate alone on BLOCK). Report paired added latency and incremental usage-priced cost alongside the separate acquisition bill estimate. Retrieval time and deployment overhead are unmeasured.

Advance only if at least one actual unsupported answer is prevented, all previously correct A/P answers are preserved, and the owner accepts the clarification losses, added cost and modeled delay. A lower volume of factual assertions cannot justify adoption. Standard RAG may be sufficient, or the small authored cohort may leave the decision unresolved. No accuracy, latency or cost outcomes have been observed.
