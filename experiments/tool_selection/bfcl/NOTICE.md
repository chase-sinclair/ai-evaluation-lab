# BFCL attribution and modifications

This directory contains a small development subset of the Berkeley Function Calling
Leaderboard (BFCL), Gorilla / UC Berkeley contributors, from
`ShishirPatil/gorilla@f7cf7359b7ac615a0b294831c5ba2bc95ee4a000`.

Citation: Fanjia Yan, Huanzhi Mao, Charlie Cheng-Jie Ji, Tianjun Zhang, Shishir G.
Patil, Ion Stoica, and Joseph E. Gonzalez. *Berkeley Function Calling Leaderboard*,
2024. [Official project](https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html).

The [pinned dataset README](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/data/README.md)
declares Apache-2.0. The accompanying LICENSE reproduces the upstream
[repository license](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/LICENSE).
Source and answer URLs, hashes, IDs, original records and revision are retained in
`development_cases.jsonl` and `sources.lock.json`.

Modifications by this project (November 3, 2026): selected 18 development records;
excluded two ambiguous records; wrapped unchanged source rows/answers in the local
case/provenance contract; authored record-lookup distractors; converted schema types
and dotted function names only for requests; generated expanded 5/15/30-tool
requests. No original questions, descriptions, or answer alternatives were rewritten.

`../bfcl_grader.py` is a narrow independent adaptation of the pinned Apache-2.0
[Python AST checker](https://github.com/ShishirPatil/gorilla/blob/f7cf7359b7ac615a0b294831c5ba2bc95ee4a000/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/ast_checker.py).
`conformance.json` records official-checker decisions for authored probes; it is
software verification evidence, not model output or research results. No full
benchmark package or checker dependency tree is redistributed. The local no-call
metric deliberately rejects malformed, incomplete, and refused responses.

`development_requests.json` is a frozen **input manifest**, containing no predictions
or real-model outcomes. Labels are confined to case files and grader-side metadata;
the `request` objects contain only prompts and tools.

This derivative development study is not an official BFCL benchmark evaluation.
