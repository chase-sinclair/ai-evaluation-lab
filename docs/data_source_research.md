# Documentation-only dataset feasibility review

Verified **November 3, 2026**, after the offline engine passed its acceptance flow.
Inspection covered official pages, maintainer README/license/grader files, and small
repository metadata responses through GitHub and web tools. No benchmark records,
database archives, model weights, or benchmark stacks were downloaded or installed.
No paid API calls were made. Proposed subsets below are plans, not approved imports.

The structured [catalog](../datasets/catalog.yaml) records each source's maintainers,
provenance, format, version, size, license status, setup, split risks, grader, budget
assumptions, and blockers. Unknown means not verified, not implicitly permitted.

## Recommendation

These rankings are engineering judgments based on the inspected sources, not measured
performance results. Legal/source readiness takes precedence over ease or enthusiasm.

| Decision | First choice | Next choice | Qualification |
|---|---|---|---|
| Easiest robust first published study | BFCL controlled subset | WDC Products | BFCL fits the implemented interface; WDC data rights remain unresolved. |
| Most direct database/FDE relevance | BIRD Mini-Dev | BFCL | BIRD needs a pinned database and a safe execution grader first. |
| Lowest inference cost | WDC rules/LLM/hybrid | BFCL small pilot | Rules need no model calls; legal uncertainty blocks WDC adoption for now. |
| Agent security relevance | AgentDojo | Authored later mock API tasks | Defer until a bounded multi-step runtime exists. |

**Proposed next action for approval:** BFCL V4 at the official reproduction checkpoint,
20 pilot cases (16 single Python calls and 4 irrelevance cases), each under 5/15/30 tools,
one repetition: **60 calls**. Freeze a separate 100-case set only after pilot/grader issues
are fixed. Do not claim that 20 pilot cases establish reliability, or that a modified
choice-set study is an official BFCL leaderboard score.

## BFCL — adopt conditionally

The official leaderboard identifies its reproduction commit and package. The pinned data
README declares Apache-2.0 and documents structured category files and no-call evaluation.
Category metadata confirms that the two candidate input files together are below 0.5 MB;
answer files are additional. See the [leaderboard](https://gorilla.cs.berkeley.edu/leaderboard),
[pinned data documentation](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/README.md),
[file-size metadata](https://api.github.com/repos/ShishirPatil/gorilla/contents/berkeley-function-call-leaderboard/bfcl_eval/data?ref=f7cf7359b7ac615a0b294831c5ba2bc95ee4a000),
and [license](https://github.com/ShishirPatil/gorilla/blob/main/LICENSE).

Our proposed study is an extension: adding distractors can change the valid answer set.
Review each expanded set before freezing labels, particularly no-call tasks. Preserve
target schemas, request wording, and inference settings. Record schema lengths and seeded
order; analyze expanded choice sets with a context-length confounder. The current strict
fixture grader is deliberately **not** claimed compatible with BFCL's equivalences.
Port or wrap only the relevant official checker after examining selected answer keys.
The upstream [partial-evaluation option](https://github.com/ShishirPatil/gorilla/blob/main/berkeley-function-call-leaderboard/README.md)
can skip missing IDs, so our planned denominator must remain explicit and independently checked.

## WDC Products — investigate, blocked on data terms

WDC offers compact benchmark archives, binary labels, and an official offer-disjoint
split design. The 4.3 GB underlying corpus is unnecessary. Its [Products page](https://webdatacommons.org/largescaleproductcorpus/wdc-products/index.html)
provides sizes, attributes, split definitions, and links to small examples. The
[project license statement](https://webdatacommons.org/) explicitly covers the extraction
framework; this review did not establish a Products data license.

Request clarification before importing or publishing source records. Once resolved,
sample one variant and preserve its class balance or publish stratified weights. Use
precision/recall/F1, not accuracy alone; cluster pairs by product when estimating uncertainty.
Tune deterministic matching and hybrid thresholds on development data only. Label this
a comparison of deployment strategies, since rules/LLM/hybrid change more than one factor.
Identifier-derived labels are checkable but not guaranteed error-free.

## BIRD Mini-Dev — investigate; strong FDE follow-up

The [maintainer announcement](https://github.com/bird-bench/mini_dev/blob/1c49a375e76c471e218564da3f4617513d33e371/README.md)
and [canonical data card](https://huggingface.co/datasets/birdsql/bird_mini_dev/blob/main/README.md)
describe the October 2026 revision. It removes some overly revealing evidence and revises
labels. Avoid mixing historical annotations, current prompts, and unmatched databases.
The three dialect splits repeat question IDs; they are not independent train/test splits.
HF history/API retrieval failed here, leaving the dataset SHA and database sizes/digests
unverified. No database availability or runnable installation is claimed.

Use SELECT-only SQLite for the first follow-up. The inspected
[EX implementation](https://github.com/bird-bench/mini_dev/blob/1c49a375e76c471e218564da3f4617513d33e371/evaluation/evaluation_ex.py)
compares sets of result rows, discarding duplicate multiplicity and order. Define whether
the study reproduces that metric or uses a stricter bag/order-aware rule; don't silently
change it. Enforce read-only connections, query timeouts, and isolated snapshots.
Do not include the separate CRUD/LiveSQLBench extension.

The data card declares CC BY-SA 4.0. Its [license terms](https://creativecommons.org/licenses/by-sa/4.0/)
permit commercial adaptation subject to attribution, change notices, and ShareAlike;
underlying database notices still need review. A missing root LICENSE file (404) does
not override the card's declaration or establish terms for every database artifact.

## AgentDojo — defer

The [paper](https://arxiv.org/abs/2406.13352v3),
[task documentation](https://agentdojo.spylab.ai/concepts/task_suite_and_tasks/),
and [MIT license](https://github.com/ethz-spylab/agentdojo/blob/main/LICENSE) establish an
extensible state/trace-based benchmark. The original published task counts in the catalog
are not a verified count of the candidate 2026 commit. Pin both code and benchmark version.

Review callback polarity: the example `security` method detects the attacker's goal,
so a true result must not automatically become “safe.” Report authorized utility,
attacker success, and their joint outcome. Use fixed attacks first to avoid unbudgeted
attack-generation calls. Freeze task/attack splits and cap turns. Optional detector-model
downloads and the stateful runtime are outside Phase 1. The official
[results page](https://agentdojo.spylab.ai/results/) also cautions that differing
attack/defense combinations do not form a directly comparable leaderboard.

## SEC EDGAR / XBRL — defer

The [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
describes unauthenticated JSON facts, standard-taxonomy/entity-level scope, updates,
and period alignment caveats. The [FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions)
states reuse permissions and requires declared automated access; the
[developer page](https://www.sec.gov/about/developer-resources) sets a maximum aggregate
rate of 10 requests/second. Use a lower local rate with caching and backoff. No EDGAR
data endpoint was queried in this review.

This is source material rather than a ready-made labeled task set. Build a reviewed key
that fixes issuer, accession, amendment policy, concept, unit, and period. An absent standard
tag cannot establish that a fact is absent from a filing. Freeze source hashes and split by
filing/issuer to reduce leakage. Numeric grading should use Decimal and predefined tolerances.
The cost of label review outweighs its apparent API simplicity for a first study.

## Illustrative operating cost, not a provider quote

For comparability only, assume **$1/million input tokens and $4/million output tokens**,
no retries or cache discounts. These are hypothetical rates, not current prices and not
approval to spend. Engineering/setup time is estimated separately in the catalog.

| Plan | Calls | Assumed average input/output tokens per call | Hypothetical cost |
|---|---:|---:|---:|
| BFCL 20-case pilot × 3 conditions | 60 | 4,000 / 250 | $0.30 |
| BFCL later 100-case set × 3 | 300 | 4,000 / 250 | $1.50 |
| WDC 100 LLM + 20 hybrid escalations | 120 | 1,000 / 20 | $0.1296 |
| BIRD 20 cases × 2 contexts | 40 | 6,000 / 500 | $0.32 |
| AgentDojo 10 tasks × 2 × max 8 calls | up to 160 | 4,000 / 300 | $0.832 |
| SEC 20 questions × 2 configurations | 40 | 3,000 / 200 | $0.152 |

Actual prompt lengths, reasoning/output usage, multi-turn growth, and distinct model prices
can change these amounts substantially. Recompute with the exact approved model and rendered
requests; add a finite ceiling and abort rules. All sources still require owner approval
before ingestion or real model execution, as specified in `CODEX_HANDOFF.md` Phase 3.
