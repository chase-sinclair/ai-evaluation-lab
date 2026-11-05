# Crossref name-to-ROR development evaluation

**The offline evaluation works. The reviewed 36-link/12-no-match target remains open.** We froze 48 nominations before retrieval, retained 30 source-supported single targets, and set aside 10 records with attribution, identifier or specificity problems. Eight further records have an empty Crossref label and await independent adjudication. The 38-query development diagnostic uses those eight source labels provisionally. Independent project reviews of no-match cases completed: **zero**. Every nomination and exclusion is preserved. [Frozen queries and source evidence](../experiments/entity_matching/ror/dataset.json) · [Review decisions](../experiments/entity_matching/ror/review.json)

| Source stratum | Nominated | In diagnostic | Excluded | Correct at 0% escalation |
|---|---:|---:|---:|---:|
| One ID, normalized registry field | 18 | 18 | 0 | 18 |
| One ID, other wording | 18 | 12 | 6 | 8 |
| Empty source label | 12 | 8 pending | 4 | 6 provisionally |
| Total | 48 | 38 | 10 | 32 |

**Source and split.** Crossref's CC0 release 19699937 contains human annotations through April 2026. The registry comes from ROR v2.6, April 14, 2026. The loader verifies both file SHA-256s against the Phase 3C pins. A salted hash of the original sequence number orders candidates within fixed quotas. Only consistent, non-alternate, single active ROR or empty annotations can enter. The prefilter removes identifier patterns, certain award/program terms, and very short or long strings. Empty-label nominations also require an organization-type word. One nomination per normalized name and positive ID prevents repeat organizations from dominating. The rules deliberately sample both easy registry forms and varied wording. This constructed mix cannot estimate deployment prevalence. Local AI-assisted screening recorded reasons before calibration. No LLM predictions influenced nomination or labels. [Source and cache reproduction instructions](phase3c_crossref_feasibility.md) · [Crossref release](https://zenodo.org/records/19699937) · [ROR data terms](https://ror.readme.io/docs/data-dump)

All nominations, excluded rows, earlier preview and audit rows, and displayed candidate IDs are development-exposed. The quarantine expands over immediate registry relationships, identical IDs, names, registry names, alternate annotations, acronym forms and normalized award/name families. Its closure reserves **579 source rows**. Future held-out assignment is closed pending a manual overlap audit for translations, related entities, unseen aliases and NIL name families. No other row has been designated held-out. [Quarantine receipt](../experiments/entity_matching/ror/quarantine.json)

**Retrieval.** The index searches **122,562 active IDs**. For each query it ranks each organization's best normalized canonical name, label, alias or acronym by padded character-trigram Dice, descending, then ROR ID. It offers up to five distinct IDs with a positive score. Every nomination returned five. The registry CSV sometimes combines multiple values in one language group with commas. The index preserves canonical names with commas and skips ambiguous comma-containing groups to avoid inventing aliases. Each candidate records its matched form, rank order, score, country and up to two aliases. Candidate construction accepts only the query string. The source label is joined afterwards to measure its unrestricted rank.

**Baseline and difficulty.** Maximize correct development decisions on a prespecified 5 × 3 threshold grid, then minimize wrong links, then prefer stricter cutoffs. The selected baseline asserts rank one at score ≥0.75 and runner-up margin ≥0.03, otherwise abstains. Uncertainty ordering uses distance to the decision boundary, with query ID breaking ties. The full grid and exact training rows are frozen. Calibration and measurement share the same provisional data. [Calibration grid and query decisions](../experiments/entity_matching/ror/baseline.json)

| Measure | Development result |
|---|---:|
| Target found in top five | 29/30 (96.7%) |
| Correct selection given target available | 26/29 (89.7%) |
| Correct target resolution over all links | 26/30 (86.7%) |
| Correct decisions including provisional NILs | 32/38 (84.2%) |
| Wrong asserted links / missed true links | 3 / 4 |
| Correct / incorrect abstentions | 6 / 3 |
| Asserted-link precision / recall / F1 | .897 / .867 / .881 |
| Full-registry baseline with the same acceptance rule | 32/38 |

The unrestricted search produced the same decisions because both baselines use rank one and rank two. Row 970, “Hoffmann - LaRoche Pharmaceuticals”, resolves in the source to an active Swiss record at rank eight. A policy restricted to the five offered IDs cannot repair this miss. Among 16 queries with a runner-up margin below .10, the baseline got 10 correct. It got 22/22 correct in the clear group. The weak-score group (top score below .65 after separating close margins) was empty. Source ambiguity and proximity of retrieval scores are different questions.

**Replay.** Acquire one immutable record per query through the existing sequential runner. Replay 0/25/50/100% using the same frozen candidates, prompt and prediction, selecting 0/9/19/38 queries by floor of the requested percentage. Valid responses are one offered ROR URL or ABSTAIN. Invalid, incomplete, missing or failed acquisitions fall back to the baseline and remain in denominators. A wrong asserted ID on a positive is both a false link and a missed link. Replay retains per-query transitions, gains/losses versus baseline, difficulty groups, estimated incremental F1 per additional API dollar and partial telemetry. Undefined ratios and unknown input/output token counts remain null.

The offline scripted run used 38 shared-engine records for all four policies. The full-escalation replay included eight invalid/incomplete fallbacks. Counts of correct decisions were 32/29/24/19, respectively, by construction of the test provider. Only the 0% row measures the deterministic baseline. Mock charges were $0. Model latency, token usage, actual invoice cost and live escalation gains remain unmeasured. On one local source rebuild, index construction took 5.1 s and all 48 searches together took 18.4 s. Replay reports baseline decision/ranking time and summed observed provider latency separately from that shared preparation time.

From the repository root:

```sh
uv run --offline python -m experiments.entity_matching.ror check
uv run --offline python -m experiments.entity_matching.ror baseline
uv run --offline python -m experiments.entity_matching.ror demo
uv run --offline python -m experiments.entity_matching.ror replay results/<run-id>
```

Only the source rebuild needs the two previously pinned local files. Demo and replay use the committed freeze and immutable local run directory. Model inputs contain the deposited organization string and ordered public candidate fields. Gold IDs, reviewer notes, score, margin and source identifiers are kept outside the request. The correct ID may legitimately appear among retrieved candidates.

**Independent review gate.** Give each of two reviewers the shuffled packet and access to the pinned registry. They should work separately, without seeing the Crossref answer, candidate ranks or each other's decisions. Record an ID, no registered match, or insufficient evidence, plus the registry search terms, evidence, reviewer and date. Reconcile disagreements separately. Preserve the original publisher label. Unresolved, multi-organization or unsupported cases stay excluded. If decisions change the cohort, version the dataset, recalibrate, and refreeze requests before approving a pilot. Reaching the original quota would require a separately recorded source-first nomination round. [Blinded review packet](../experiments/entity_matching/ror/blind_review.json)

**Frozen live proposal, pending approval.** The manifest contains the complete ordered 38 logical requests and canonical Responses API bodies with SHA-256s, model, config, dataset and calibration hashes. All use gpt-6-luna, standard tier, store=false, 4,096 maximum output tokens, explicit implicit-cache minimum TTL of 30 minutes, no explicit breakpoints, and provider defaults for unsent inference settings. No tools. Proposed execution is sequential with zero retries and at most one attempt per row. Availability and returned model/settings must be checked during any separately approved execution. The ordinary shared adapter does not add the proposed TTL. Only the offline body and locked-SDK transport have been validated. Live dispatch requires a reviewed wrapper that enforces these exact bodies and stop rules. [Frozen requests](../experiments/entity_matching/ror/proposal.json) · [Configuration](../experiments/entity_matching/ror/pilot.yaml) · [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)

Standard short-context prices checked November 4, 2026 were $0.10/M uncached input, $0.01/M reads, $0.125/M 30-minute writes, $0.25/M 12-hour writes and $0.50/M output. At an illustrative 600 uncached input and 100 output tokens per query, 38 calls would cost **$0.00418**. The ordinary engine preflight reserves $0.09193625. The complete-body preflight allows 58,121 input tokens at the highest supported write rate and 155,648 output tokens, reserving **$0.09235425** against the proposed **$0.15** cap. These are estimates. [Pricing](https://developers.openai.com/api/docs/pricing) · [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)

Before sending, abort on missing owner/review clearance, a changed source/config/body hash, unexpected tier/model/options, a missing or repeated case, a prior attempt, changed prices, or inadequate remaining reserve. After each attempt, retain its record and stop on provider/access error, unexpected model or tier, refusal/incomplete/invalid output, excess output, changed TTL, longer writes, inconsistent/missing usage or cap violation. Treat an absent lifetime breakdown as unknown. The explicit 30m policy can produce a separate conditional estimate only when the actual sent body has its approved hash and the observed service and counters pass validation. Reserve the greater of the frozen charge and the conservative observed charge. Maximum retention provides no evidence of minimum TTL. Report any bill independently of reported-usage pricing and policy estimates. Further dispatch requires approval of this accounting rule, the final cohort and budget.
