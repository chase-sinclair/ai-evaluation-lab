# Experiment 007 · Claude replication of model tier against context

Does Experiment 006's finding replicate on a second provider? That finding was that a cheap model with curated context beats an expensive model without it. This study runs `claude-haiku-5-5` (cheap) against `claude-sonnet-5-5` (expensive), at the same rates as `gpt-6-luna` and `gpt-6.1-sol`. It uses the 006 grid, questions, draws and order: 432 requests. See the [design](../../docs/experiment07_claude_replication_design.md) and [protocol](protocol.md).

| File | Role |
|---|---|
| `proposal.py` | Derives every Messages API body from the frozen 006 body in the same position, with identical texts, and freezes the manifest. |
| `accounting.py` | Receipt checks, usage pricing and stop-reason classification for Claude responses. |
| `analysis.py` | Replays the sealed ledger, builds the masked worksheet with carried-over 006 judgments, scores with 006's frozen functions, and evaluates the pre-registered replication criteria. |
| `proposals/r1/` | Frozen manifest and gzipped bodies. |
| `../../scripts/acquire_claude_context.py` | One-time dispatcher with a per-request spending guard. |

Offline check:

```bash
uv run --offline pytest tests/test_claude_context.py
```

No live request has been sent. A run needs owner approval of the exact proposal digest, reviewed revision and cap, plus an Anthropic credential in the owner's own environment.
