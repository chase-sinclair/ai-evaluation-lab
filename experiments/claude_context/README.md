# Experiment 007 · Claude replication of model tier against context

Does Experiment 006's finding replicate on a second provider? That finding was that a cheap model with curated context beats an expensive model without it. This study runs `claude-haiku-5-5` (cheap) against `claude-sonnet-5-5` (expensive), at the same rates as `gpt-6-luna` and `gpt-6.1-sol`. It uses the 006 grid, questions, draws and order: 432 requests. See the [design](../../docs/experiment07_claude_replication_design.md) and [protocol](protocol.md).

| File | Role |
|---|---|
| `proposal.py` | Derives every Messages API body from the frozen 006 body in the same position, with identical texts, and freezes the manifest. |
| `accounting.py` | Receipt checks, usage pricing and stop-reason classification for Claude responses. |
| `analysis.py` | Frozen analyzer for the scored run, masked worksheet, offline grading and pre-registered replication criteria. |
| `../model_context/replay.py` | Read-only audit of the seal, receipt bindings and usage, including a charged final request interrupted before its terminal event. |
| `proposals/r1/` | Frozen manifest and gzipped bodies. |
| `../../scripts/acquire_claude_context.py` | One-time dispatcher with a per-request spending guard. |

Offline check:

```bash
uv run --offline pytest tests/test_claude_context.py
```

Audit the sealed Claude run from the repository root with the command below.

```bash
uv run --offline python -m experiments.model_context.replay claude results/meridian-claude-context-r1-once
```

See the [scored results](../../docs/experiment07_scored_results.md) for the completed one-time run. Any new acquisition requires a separately reviewed proposal and spending approval.
