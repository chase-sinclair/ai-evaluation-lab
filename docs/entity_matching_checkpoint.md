# Phase 3B checkpoint — local product matching

**Paused.** No WDC text was submitted to a model. The substantive BFCL tool-count study is deferred, not completed, and the proposed four-case probe was not run. See the [dataset decision](entity_matching_dataset_decision.md) before resuming any work.

Preserved work in `experiments/entity_matching/`: bounded validation-member acquisition; IDs, source row/file hashes and original benchmark labels in `development.json`; deterministic baseline; shared-engine binary acquisition; offline policy replay; authored four-pair connectivity check. The product-specific prompt and weights should not be reused unchanged for organizations. No change to the shared runner. All merchant fields, caches and raw run records remain outside Git.

The [WDC Products benchmark](https://webdatacommons.org/largescaleproductcorpus/wdc-products/) derives product identities from cleaned identifier clusters in 2020 web-shop data. Its pairwise variants vary training size, corner-case mixture and unseen products. Its authors' manual 600-pair label check reported about 4% errors; this is not an estimate for our particular subset. We read only the three fully-seen small **validation** members (~3 MB compressed), 2,500 pairs each. No training/test split or source corpus was consumed. The receipt pins member hashes, original pair, offer and cluster IDs, labels and hard-negative flags. No human relabeling.

Development selection: archive order 20/50/80; sort by salted pair-ID hash per archive, take 12 matches, 24 source-flagged hard negatives and 24 other negatives with no offer reuse across the 180 pairs. The baseline averages token overlap and character alignment of titles, plus available bilateral brand, description and comparable price evidence, using fixed weights and threshold 0.55. Scores use projected attributes only; uncertainty is proximity to threshold, not a calibrated probability. An incorrect, confident score may never be escalated under a small policy. No test labels used.

| Actual development result | N | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| All pairs | 180 | 14 | 23 | 22 | 121 | .378 | .389 | .384 |
| 20% mixture | 60 | 3 | 9 | 9 | 39 | .250 | .250 | .250 |
| 50% mixture | 60 | 4 | 5 | 8 | 43 | .444 | .333 | .381 |
| 80% mixture | 60 | 7 | 9 | 5 | 39 | .438 | .583 | .500 |

Accuracy .750; false-positive rate 23/144; false-negative rate 22/36. All 23 false positives occurred among the 72 flagged hard negatives. Archive percentages are not per-pair difficulty grades. These are development-only results vs source labels, not model performance.

Policies take floor(N × percentage / 100) in a single uncertainty ranking, tie-broken by case ID. Replay uses at most one recorded response per pair and shows pairs repaired/harmed, invalid outputs and baseline fallbacks. All cases remain in denominators; unknown spend and undefined ratios remain null. Timing is baseline scoring/ranking plus summed recorded sequential call latency; it excludes offline grading overhead. Dollars cover estimated provider charges, not labor or total deployment cost. The authored demo exercises the runner, immutable storage and replay with four mock predictions (one deliberately invalid); it supplies no research evidence.

To reproduce the **existing** checkpoint offline from the ignored local cache: `uv run --offline python -m experiments.entity_matching.prepare --check`. The four-pair software check needs no cache: `uv run --offline python -m experiments.entity_matching.demo`.

**Archived WDC pilot proposal, not for execution:** 12 pairs (one match, two hard negatives and one other negative per mixture), selected by independent hash before grading. Ordered IDs and exact canonical request/body hashes are in the receipt. The proposal used gpt-6-luna, Responses API, standard tier, model defaults, sequential, zero retries, 4,096 maximum output tokens and $0.05 ceiling. Offline preflight: 14,896 conservative input tokens, 49,152 maximum output tokens, $0.028300 reserved using the maximum documented short-context cache-write rate. This is a reserve, not a bill or a forecast of model performance. [Price source, checked 2026-11-04](https://developers.openai.com/api/docs/pricing). No purchase, calls, hypothetical escalation gains, or permission to transmit.
