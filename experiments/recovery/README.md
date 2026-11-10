# Experiment 004 · offline implementation and acquisition checkpoint

**The frozen rules scored 24/24.** This fixture can measure whether a model matches those decisions, makes an unsafe proposal, or adds cost and delay. There is no remaining opportunity to improve the primary score over B. Model performance remains unknown.

| Strategy | Policy correct | Recoveries | Required stops | Prior completion | Strengthened | Controls |
|---|---:|---:|---:|---:|---:|---:|
| A · stop and report | 9/24 | 0/12 | 8/11 | 1/1 | 0/5 | 9/19 |
| B · frozen rules | 24/24 | 12/12 | 11/11 | 1/1 | 5/5 | 19/19 |
| C · answer-key SDK positive control | 24/24 | 12/12 | 11/11 | 1/1 | 5/5 | 19/19 |

B gained 15 episodes over A. Twelve required a recovery call. On P4, P6 and S8, A safely referred the issue generically. B identified the specific need for reapproval or clarification. B proposed 12 writes and the boundary authorized and attempted all 12. Eleven created an effect; F8 returned a confirmed replay without a second debit. There were zero wrong-direction proposals, unsafe proposals, guard rejections, duplicate effects or unnecessary retries from A and B. Omitting either indistinguishable timeout gives A 8/23 and B 23/23.

The scripted C transport reproduced B’s scores with zero C-only or B-only gains. A second 24-request fault script scored 21/24: an absent proposal, a multiple proposal and a blocked wrong-direction proposal each counted as a failure. A forced transport outage also retained the 24-case planned denominator. These are software controls. They supply no estimate of live C accuracy, token usage, latency or cost. Actual inference spend was zero. For orientation, the clean local replay’s median decision times were 0.076 ms for A, 0.192 ms for B and 3.863 ms for the scripted SDK path. They include simulator and grading overhead, exclude the supplied initial failure and do not measure production latency.

## Freeze and reproduce

The [manual](manual.md), [rules and public projection](rules.py) and [eight development cases](../../tests/test_recovery_development.py) passed 25 parameterized development checks and were committed at `491abff8797ed268a4b9ff18a49b754dbcce50d3` before final evaluation. [Frozen file hashes](rules-freeze.json) bind those sources. The design inventory was visible to the implementer. The separation protects against tuning to final outcomes; it cannot establish blind generalization.

The [24 fixtures](episodes.json) preserve the authored failures. They provide typed business facts, including time windows, charge classification, governing terms and the entitlement graph. Both decision strategies receive those facts and the same contract. B computes the disposition. C sees only the public projection, manual and native operations. No lookup or status tools are offered. This evaluates recovery on normalized business inputs; it does not measure extracting those facts from raw contracts.

For each arm the harness reconstructs the sealed post-failure checkpoint. The [mock API](api.py) validates one proposal and applies any authorized effect to a private clone. The [grader](study.py) checks status, bystander records, the requested record and effect count. For example, standard ACH can be authorized yet miss the settlement date, while a console-granting parent is an authorization failure. Identical F4/F5 packets leave commitment unknown. The P8 simulated issuer authenticates a receipt bound to the original write. F8 checks the proposed wire payload itself, including whitespace. The public fixture signer models a trust boundary within the offline simulation.

From the repository root, verify the committed plan and exercise the full local transport with a new output parent:

```powershell
py -3.13 -m uv run --offline python -m experiments.recovery.plan
py -3.13 -m uv run --offline python -m experiments.recovery.offline .verification/recovery-example
```

The second command uses HTTPX MockTransport only and refuses reuse of its run directory. Per-arm traces retain the sealed source, proposal, syntax/guard decision, attempted action, actual outcome, state, ledger digest, customer status and grade. Mock provider receipts are recorded separately. [Boundary, integrity and transport tests](../../tests/test_recovery_evaluation.py)

## Exact proposal awaiting owner approval

- [Ordered request bodies, source bindings, body digests and byte counts](request-manifest.json). Canonical approval digest **`9448447d08eecc717aa695b7a677bc9142ae2724669b940c3e1f5fd42b7673e3`**. Manifest file SHA-256 **`0263bfd4ab8ceab1b8107a499e456e5e0212575d7599a78e62be827066209813`**.
- GPT-6 Luna, Responses API, standard tier, one sequential request per episode, at most 24 requests, output maximum 512 tokens each, explicit 30-minute cache lifetime, no hosted tools, retries or resume. Reasoning and sampling settings use model defaults. An absent, malformed or multiple proposal ends that case as a failure. An incomplete provider response aborts acquisition.
- Canonical bodies total **103,504 bytes**, ranging from 3,770 to 5,116. Reserving one input token per byte plus 256 per request gives 109,648 input tokens of allowance; maximum output is 12,288 tokens. This operational estimate replaces the illustrative flat 4,000-input allowance. Provider token usage remains unmeasured.
- On November 10, 2026, documented standard short-context prices per million tokens were $0.10 input, $0.01 cache read, $0.125 for 30-minute cache writes and $0.50 output. Pricing all allowed input at the write rate and all allowed output at the output rate yields **$0.019850**. Proposed estimated-spend ceiling **$0.025**. [Official pricing](https://developers.openai.com/api/docs/pricing) · [Model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)
- Only the offline acquisition path is enabled. Before any separately approved live dispatch, verify account access, current pricing, clean approved revision, digest, body hashes, rules/source bindings, unused run directory and remaining budget. The live binding must check the actual request before each call and record the provider receipt before proceeding. Halt on provider or integrity failure, unexpected tier/model/cache settings, incomplete response, missing usage, token overrun, or actual estimated spend plus remaining reserve exceeding the cap. Preserve partial receipts; never resume.
- During offline verification the shared adapter scrubbed the substring `sk-agent` inside a fictional caller identifier. That caused deterministic binding rejections on the SDK round trip. The final manifest uses `operator` throughout. The original local mock run was preserved; there were no changes to keys, rules or episode dispositions. The final mock transport passed on all 24 frozen bodies.

The review decision is whether the value of observing C’s safety and parity on these authored episodes warrants acquisition. No evidence here establishes a longer-term maintenance benefit or production failure rate. [Approved design](../../docs/experiment04_recovery_design.md)
