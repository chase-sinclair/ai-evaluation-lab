# Crossref development pilot readiness · November 5, 2026

**Ready for owner approval.** Chase Sinclair completed the eight-query review on November 5, 2026. The review was human-conducted with AI-assisted research. The existing validator accepted all eight decisions. The one-shot command can send **four** requests, the first four in the existing frozen order. This is the smallest sample that gives distinct, exact 0/25/50/100% policies (0/1/2/4). It can check integration, including abstention. An accuracy or cost-effectiveness conclusion needs a larger reviewed sample.

**For the reviewer:** share only the [identity worksheet](review/funder_identity.md). Save the completed copy as `.verification/phase3e-review.md`. Search the entire checksum-verified April 14 ROR v2.6 snapshot, including aliases, inactive names, and successor relationships. Record one active ROR ID, no supported match, or insufficient evidence for each query. Record sources/searches, reviewer and date. After locking those decisions, use the separate [candidate sheet](review/funder_offers.md) to record whether an offered ID resolves each query. Membership in this focused review set may itself suggest how cases were selected. Both sheets omit original annotations, baseline choices and similarity scores. One human review suffices for development and provides no inter-reviewer agreement estimate.

**Cohort.** For each of the eight names, the reviewer recorded no supported active-organization match in ROR v2.6 and separately recorded no match among the five offered IDs. All decisions agree with the frozen labels. The development cohort contains 30 single-target and eight reviewed no-match queries from 48 original nominations and ten exclusions. The completed worksheet is a local review receipt alongside the original calibration and freeze. A single reviewer provides development evidence with no inter-reviewer agreement measurement. [Phase 3D evidence](phase3d_crossref_resolution.md)

| Frozen group | Queries | Correct baseline decisions |
|---|---:|---:|
| Registry-form names | 18 | 18/18 |
| Alternative wordings | 12 | 8/12 |
| Reviewed no-match | 8 | 6/8 |
| All diagnostic queries | 38 | 32/38 |

Recall@5 was 29/30 and selection given retrieval was 26/29. Asserted-link precision, recall and F1 were .897, .867 and .881. The alternative-wording group retains the valid Hoffmann-La Roche target at rank eight. The development-only calibration and artificial group mix limit interpretation. [Calibration and query decisions](../experiments/entity_matching/ror/baseline.json)

**Freeze and price.** The complete revision binds each logical request and exact Responses body by SHA-256. GPT-6 Luna uses the standard service tier, an explicit implicit-cache minimum TTL of 30 minutes, zero explicit cache breakpoints, store=false, no tools, sequential execution and zero retries. Other inference settings use provider defaults. Every valid output fits in 25 UTF-8 bytes. A limit of 1,024 tokens leaves room for reasoning as well as the returned ID or ABSTAIN. Local SDK tests parsed both forms and validated the body cap. Live reasoning needs and account access remain unmeasured. An incomplete output stops this version. [Complete revised manifest](../experiments/entity_matching/ror/phase3e_requests.json) · [Model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)

| Scope | Exact request count | Maximum output tokens total | Conservative reserve | Estimated-spend cap |
|---|---:|---:|---:|---:|
| Executable prefix · cr-830, cr-2819, cr-744, cr-2775 | 4 | 4,096 | $0.00354375 | **$0.005** |
| Complete development planning matrix | 38 | 38,912 | $0.03398625 | **$0.05** |

At illustrative 600 uncached input / 100 output tokens per query, four requests cost $0.00044. The reserve instead uses canonical serialized bytes plus 256 input tokens per body, prices every input token at the highest documented cache-write rate, and includes the full output allowance. Standard short-context rates checked November 5 were $0.10/M uncached input, $0.01/M cached reads, $0.125/M 30m writes, $0.25/M 12h writes, and $0.50/M output. The $0.05 cap covers all 38 under these assumptions. Only the four-request prefix has a dispatch entry point. [OpenAI pricing](https://developers.openai.com/api/docs/pricing) · [Cache policy](https://developers.openai.com/api/docs/guides/prompt-caching)

**Verification and execution.** From the checked-out repository, this command rebuilds and compares the revised request freeze, runs spending preflight and prints the approval digest. It performs zero provider calls.

```sh
uv run --offline python -m experiments.entity_matching.ror.dispatch
```

Only after review and explicit owner approval, the exact command for the four requests is:

```sh
uv run --offline python -m experiments.entity_matching.ror.dispatch --live --approve-plan 16c01224c3ee772e318c7326749b4084a3e0b72c2ca997a8e2bb8b13dc18de03 --review .verification/phase3e-review.md
```

Here `uv --offline` applies to package installation. The explicit `--live` branch sends network requests. Use the designated checkout and configured account after reconfirming pricing. The command claims a fixed receipt in Git's common directory across linked worktrees, then an exclusive run directory under results. It never resumes a partially attempted run. Network exceptions and rate limits stop after the first attempt. Do not delete either receipt or start another clone to retry. Any future extension to 38 must account for existing acquisitions and obtain a new authorization.

Before each send the transport checks method, endpoint, serialized body digest, order, remaining count and reserve, and durably writes the actual body receipt. The shared runner stores the response and grade before the stop decision. Unexpected model, tier, cache policy, longer writes, refusal, incomplete output, invalid ID, inconsistent input partition or totals, missing usage, or budget violation stop further scheduling. A valid incorrect ID is a task failure and remains in the analysis. The report records usage-priced costs where the observed partition suffices, an explicit 30m policy estimate where only write lifetime is unknown, and conservative charges for spending protection. It never infers a write price from a 24h maximum retention value. An invoice amount remains unknown. Missing records after an interruption require individual inspection.
