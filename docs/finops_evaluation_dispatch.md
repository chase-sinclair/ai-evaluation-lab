# Full Meridian evaluation · pre-execution review

This is an offline implementation checkpoint. Only a future owner decision can authorize the separately identified live acquisition. The accepted v2 and pilot result directories and original v3 manifests remain historical. Recomputed all 188 v2 and 56 pilot ledger entries, both canonical ledger digests and both seal-file hashes. Pilot observations are excluded from evaluation scoring. D06 matched the realized-rate development reference with a scheduled-rate calculation on one snapshot; semantic equivalence remains unestablished.

## Proposal and reserve

The revision extends original evaluation digest `1b3a5529069e19c9d219a58d4891c39c4fb51676a7ef548a482bd59ddddb61b1`. The 144 archived bodies, source questions, context, report fields, discovery constructors, financial keys and question/arm order carry forward. New bindings cover the prospective stopping rule, offline analysis and validated pilot receipt accounting. The reviewed Git revision additionally binds the dispatcher. [Revised manifest](../experiments/finops_sql/proposals/v3/evaluation-r1/manifest.json) · [Policy](../experiments/finops_sql/evaluation_r1/protocol.md)

| Identity | Value |
|---|---|
| Approval digest | `4eb6e593374585e11b349cc1341c82bda22048eb2a6ff69560dc7a82d214d36f` |
| Manifest SHA-256 | `9ec95361740e39ac9cc7dbe5ca0fa3361fb2167ace3d4f816c0415c48beb7a50` |
| Preserved body-array hash | `78a96d669a01f0509a4add647df452daf6126e5709316ff7c646544a84bdb986` |
| Fixed directory | `results/meridian-v3-evaluation-r1-once` |

4,066,632 bounded input tokens at $0.125/million plus 9,000,000 output tokens at $0.50/million reserve **$5.008329** under **$5.50**. The counting proxy is conservative and every turn still checks actual accounting. The five-episode pilot authorization is consumed.

## Mock acquisition evidence

| Scenario | Episodes reaching a terminal decision | Acquired exhaustion | HTTP requests | Discovery calls |
|---|---:|---:|---:|---:|
| Maximum D depth | 144 | 0 | 360 | 216 |
| Early D answer after one discovery | 144 | 0 | 180 | 36 |
| Accounted Q30D exhaustion on first D turn | 143 | 1 | 354 | 210 |

Request four in the exhaustion scenario consumed 25,000 simulated output tokens and cost $0.012511225 on scripted usage. The dispatcher released $0.08277525 across the six remaining Q30D bounds. The next request was the next frozen episode. The run finished with zero outstanding reserve. Recomputed all sealed file hashes and replayed bound wire bodies, discoveries and charges. Other reasons for incompleteness, contradictory settings, missing or inconsistent usage, unsupported writes, excess input/output, timeout, HTTP errors and duplicate IDs interrupt globally. The one-time directory also rejects reuse after interruption. No model quality is inferred from these tests.

## Offline results workflow

Use the same committed checkout and locked environment, source-verified evaluation fixtures and the isolated v3 grader. Preserve the original seal and compare its file SHA-256 against a separately recorded trusted value. Locally held checksums detect subsequent changes against that value. A crash before sealing requires manual read-only investigation.

1. Run the analysis module with the sealed directory alone. Save its JSON output to an ignored private worksheet. Share only that worksheet with the independent clarification reviewer. Items are deduplicated by question and wording, sorted by digest and omit arm, execution order, SQL results, claimed dimensions and scoring keys.
2. The reviewer sets each `adequate` field to true or false after checking whether the wording resolves the business ambiguity. Retain the original worksheet separately. The scorer rejects missing, extra, altered or undecided entries and also requires the exact original dimension set for positive credit.
3. Run the module again with the completed review and snapshot root. The report includes individual typed two-snapshot grades, per-arm planned correctness /36, SQL /32, clarification /4, /35 excluding Q16, case-level paired transitions and separate B-to-D changes. Acquired exhaustion contributes zero and remains separately labeled. Interrupted and unsent cases have no observed grade. Counts, request usage, costs, D depth, invalid selections and API/tool times accompany the ledger identity.

```powershell
uv run --offline python -m experiments.finops_sql.evaluation_r1.analysis results/meridian-v3-evaluation-r1-once > .verification/evaluation-clarifications.json
uv run --offline python -m experiments.finops_sql.evaluation_r1.analysis results/meridian-v3-evaluation-r1-once --review .verification/evaluation-reviewed.json --snapshots .verification/finops-verified > .verification/evaluation-report.json
```

## One-time operator command

Substitute only the owner-reviewed implementation SHA. Require the exact proposal, confirmed available credit and applicable project limits, unchanged standard rates, model access and an unused destination. A global failure consumes the run. The 900-second read timeout is an inactivity timeout. Model completion and full-run availability remain uncertain.

```text
uv run --offline python -m scripts.acquire_finops_evaluation --approval 4eb6e593374585e11b349cc1341c82bda22048eb2a6ff69560dc7a82d214d36f --reviewed-revision REVIEWED_SHA --available-usd 5.50 --confirm-current-standard-rates 0.10/0.01/0.125/0.50 --confirm-credit-and-project-limits
```
