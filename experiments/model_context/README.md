# Experiment 006 · model tier against business context

Can `gpt-6-luna` with curated business definitions match `gpt-6.1-sol` with only the schema, on the 36 Meridian finance questions from Experiment 005? This is a 2 × 2 grid of model and context, with three draws per question in each cell: 432 single-turn requests. See the [design](../../docs/experiment06_model_context_design.md) and [protocol](protocol.md).

| File | Role |
|---|---|
| `proposal.py` | Builds the 432 bodies from the accepted 005 evaluation bodies and freezes the manifest. Luna bodies are byte-identical to 005. Sol bodies differ only in the model. |
| `accounting.py` | Receipt checks and usage pricing for both models. Accepts the requested alias or its dated snapshot. |
| `analysis.py` | Frozen analyzer for the scored run, masked worksheet, and offline grading. |
| `replay.py` | Read-only audit of the seal, receipt bindings and usage, including a charged final request interrupted before its terminal event. |
| `proposals/r1/` | Frozen manifest and gzipped bodies. |
| `../../scripts/acquire_model_context.py` | One-time dispatcher with a per-request spending guard. |

Rebuild check (offline):

```bash
uv run --offline pytest tests/test_model_context.py
```

Audit the sealed GPT run from the repository root with the command below.

```bash
uv run --offline python -m experiments.model_context.replay gpt results/meridian-model-context-r1-once
```

See the [scored results](../../docs/experiment06_scored_results.md) for the completed one-time run. Any new acquisition requires a separately reviewed proposal and spending approval.
