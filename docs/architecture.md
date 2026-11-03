# Architecture

The CLI discovers trusted local `experiments/*/experiment.yaml` configurations and
loads the neighboring `experiment.py`. Each module exports `Experiment(spec, directory)`
with `load_cases`, `validate`, `build_request`, and `grade` methods. The runner knows
only this interface; a second experiment does not require a runner edit.

Pydantic contracts reject undeclared fields and invalid limits. Before execution the
runner validates all cases, builds the complete deterministic trial plan, freezes
requests and labels, and checks request/spending limits. Provider inputs contain no
answer keys. Requests use structured function schemas; no tool is actually executed.

Runs are sequential, with no automatic retries. `plan.json` is written exclusively
before any call. Every completed/error trial is appended and fsynced to `records.jsonl`.
The final `manifest.json` and `summary.json` are written once, including after a caught
interrupt. No run directory is reused. A hard process kill leaves the plan and durable
records; `summarize` identifies the unfinished run and ignores only a torn final JSONL
line. No automatic resume or rerun. Files are application-immutable, not tamper-proof.

Provider errors, incomplete outputs, invalid outputs, grader errors, and task failures
are separate statuses. Primary success uses all planned trials as denominator, including
unattempted trials in interrupted runs. Attempted success is also reported. Unknown
usage/cost remains null. Mock usage is null and estimated cost is zero, explicitly offline.

The optional OpenAI adapter uses Responses, custom function schemas, `store=False`, a
timeout, and zero SDK retries. It is lazy-loaded only for explicitly opted-in live mode.
Only bounded max_output_tokens is supported initially; optional inference parameters are
rejected rather than silently dropped. Returned model/settings are retained. An approved
exact model ID and a dated, model-matched user-supplied pricing snapshot are prerequisites.
Budget estimates use UTF-8 request bytes plus overhead as a conservative heuristic and
bounded output tokens; they are not a tokenizer or a hard billing guarantee. Missing live
usage or a provider error stops scheduling further requests because spend is uncertain.
