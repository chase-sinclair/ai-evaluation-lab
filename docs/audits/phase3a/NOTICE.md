# BFCL feasibility evidence: attribution and scope

Source: Berkeley Function Calling Leaderboard, Gorilla / UC Berkeley contributors,
`ShishirPatil/gorilla@f7cf7359b7ac615a0b294831c5ba2bc95ee4a000`.
Fanjia Yan, Huanzhi Mao, Charlie Cheng-Jie Ji, Tianjun Zhang, Shishir G. Patil,
Ion Stoica and Joseph E. Gonzalez, *Berkeley Function Calling Leaderboard* (2024).
[Official project](https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html).

The pinned [dataset README](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/README.md)
declares Apache-2.0; the accompanying LICENSE reproduces the upstream license
already retained by this repository. Owner-authorized Phase 3A audit scope is
bounded to 40 previously unreviewed records, not a benchmark archive.

Project modifications (November 4, 2026): selected `multiple_57..99` excluding
previously reviewed 76, 81 and 93; paired unchanged source questions/function
definitions with unchanged answer rows; wrapped them in provenance metadata and
reserialized as JSON. Original file URLs and SHA-256 hashes are in
`source_records.json`. Existing ignored cache files have an extra final newline;
upstream byte hashes are distinct, and all parsed rows were compared successfully.

`review.json` contains project-authored AI-assisted eligibility/family judgments;
`catalogs.json` contains source-function references, relevance judgments, alternative
route exclusions and sample sets. `summary.json` is deterministic audit evidence,
not model output. These four files are **development-exposed feasibility records**,
not an executable experiment or an untouched evaluation set. No independent human
review has occurred. See ../../phase3a_feasibility.md for limits and approval gates.

`scripts/audit_phase3a.py` checks these artifacts offline. Source function definitions
are preserved; diagnostic wire conversion reuses the existing dot-to-underscore,
dict-to-object and float-to-number conversion. It rejects unsupported metadata
rather than editing source schemas. The full multiple-function importer/grader is
not implemented. No official BFCL comparability or real-model finding is claimed.
