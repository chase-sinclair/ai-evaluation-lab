# Meridian SQL · v2 pre-acquisition decision record

**Ready for owner review.** Moving Q07 across the July 1 rate transition makes both components independently testable on the existing warehouse. Q16 remains useful for checking the shape and values of a balanced invoice report, but an exact result cannot establish that the SQL independently calculated invoice actuals. [Corrected 36-question packet](experiment05_oracle_review_v2.md) · [Frozen v2 manifest](../experiments/finops_sql/proposals/v2/manifest.json) · [Exact v2 initial bodies](../experiments/finops_sql/proposals/v2/bodies.json.gz)

## Case-level changes

| Case | Decision | Effect on grading |
|---|---|---|
| Q07 | Compare June to July for East compute SKU X. Use the June realized rate for volume, then July units for the rate change. | Both independent oracles and both snapshot bindings changed. Output fields remain `volume, price` in USD. |
| Q08 | Keep the June–July bridge across all regions. | Its third term isolates changes in regional mix. Q07 measures two effects within one region. |
| Q14 | Define `variance_pct` as 100 × (allocated actual − budget) / budget, expressed as a percent of budget. | 888.14 means actual exceeded budget by **888.14% of budget**. Both original numeric keys reproduce. |
| Q16 | Keep the September balanced-ledger task. Classify it as result-only evidence when interpreting accuracy. | Both original numeric keys reproduce. The shortcut below passes. |
| Other 32 cases | Retain their wording, financial definitions and dispositions. | The 28 other numeric cases and four clarification keys were rechecked. |

### Q07 discrimination

| Snapshot | Volume effect | Rate effect | Sum | Independently summed July less June contracted charges |
|---|---:|---:|---:|---:|
| Evaluation A | −$16.15 | +$295.52 | +$279.37 | +$279.37 |
| Evaluation B | −$77.94 | +$280.64 | +$202.70 | +$202.70 |

In each snapshot, volume fell and the rate increase more than offset it. The negative control preserves the correct volume calculation and returns zero for price. It fails on both snapshots. A separate query sums the signed contracted usage charges directly. That result reconciles to the two graded terms at cent precision. The generator, economic event streams, logical charge selection and physical snapshots retain their original bindings. [Executable controls](../experiments/finops_sql/controls.py)

### Q16 shortcut

```sql
SELECT id, control AS actual, control, 0 AS residual
FROM invoice
WHERE posting_month = 9
```

The isolated worker executed this query and the two-snapshot typed grader's comparison accepted all **16/16 invoice rows on each snapshot**, including aliases, types and residuals. The checkpoint now detects any change in this known equivalence. Keep the independent charge-side balance checks. For reporting, describe a Q16 pass as correct balanced-ledger output and disclose the shortcut. If detecting discrepancies becomes a business requirement, the smallest follow-up would pair an explicitly dated provisional delivery view with a final control and require identification of the affected invoices. That would require separate task and oracle approval. An intentionally unbalanced final ledger would undermine the existing conservation control.

## D history decision

D uses native function selection on the current turn. Each subsequent request is stateless and repeats the original question, instructions and an ordered transcript of local tool selections and results serialized into user-role data messages. The session grants describe/sample access only to previously discovered IDs. The SQL sandbox, private keys and previous model reasoning are outside this transcript.

Retain this mechanism for the secondary comparison. It represents an application that owns its metadata session, filters disclosures and supplies a bounded evidence transcript. All 32 authorized discovery paths replayed; the longest still needs five of six calls. A native linked call/result history would give the model explicit tool provenance and call IDs, and better represent an application that deploys that interface. It could affect navigation, reasoning continuity, reliability and token overhead. This study supplies no comparative evidence between those representations. A switch would require new dynamic templates, transcript bounds, budget calculations and approval. Interpret D specifically as the tested stateless workflow; use A/B/C for the primary context comparison.

## Proposal and verification

The original v1 manifest, bodies, questions and oracle-binding file remain available. The v2 manifest identifies the v2 question file and reuses the identical v1 context assets. B is still a byte-for-byte prefix of C. All four arms receive the same shared instruction edit. An automated diff compares every initial body and its position against v1: the only differences are the percent terminology in 144 bodies and the new Q07 period in four of those bodies. A private binding comparison identified Q07 alone among all 32 numeric cases on each snapshot. All changes precede inference.

| Arm | Maximum requests | Reserved input tokens across all turns | Reserved output tokens | Estimated maximum USD |
|---|---:|---:|---:|---:|
| A | 36 | 238,716 | 73,728 | 0.0667035 |
| B | 36 | 419,508 | 73,728 | 0.0893025 |
| C | 36 | 969,588 | 73,728 | 0.1580625 |
| D | 252 | 2,169,180 | 516,096 | 0.5291955 |
| **Total** | **360** | **3,796,992** | **737,280** | **0.8432640** |

The proposal freezes 108 fixed-context bodies and 36 initial D bodies. It binds the constructor and per-turn limits for up to 216 subsequent D bodies. Each turn retains the 2,048-token output limit. The reserve uses the accepted November 10 pricing assumptions, $0.125/M reserved input and $0.50/M output. The proposed ceiling remains **$1.00**. Input allowances cover repeated history; measured tokenizer counts remain local proxies. Live reasoning demand, actual cost and model performance are unmeasured. [Prior budgeting method and deployment prerequisites](experiment05_checkpoint2.md)

- Canonical v2 proposal digest: `82539bc63c44e9bced2111989c9fcd59f7b867941d70b3e3d943479778e31733`
- Manifest file SHA-256: `abfa3681186734b32a1211a027bcf73e36bd1ff77da9fec1a2530db4c4924f9c`
- Canonical uncompressed body-array SHA-256: `c12b6d4dfa80eb767e1427b71bd788e10a59d36e658b598b8a6bde2b49cc0183`

Reproduce the full checks with the checkpoint-1 Docker worker and verified snapshots. Run `python -m experiments.finops_sql.checkpoint ROOT`, then `python -m experiments.finops_sql.review ROOT OUTPUT.md`. Set `FINOPS_VERIFIED_ROOT` to that root for the offline pytest suite. To reproduce the acquisition proposal, run `python -m experiments.finops_sql.proposal UNUSED_DIRECTORY` in the locked environment. The automated freeze test compares the complete proposal and decompressed bodies. The checkpoint awaits owner review and grants no authority to dispatch.
