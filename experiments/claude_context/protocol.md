# Experiment 007 acquisition protocol, revision 1

Apply the design in `docs/experiment07_claude_replication_design.md`. The frozen proposal is `proposals/r1`. Each body is derived from the Experiment 006 body in the same position, which is verified against the approved 006 digest. The system text and user text are identical to the 006 developer and user text.

Send the 432 requests once, in manifest order, on the Claude Messages API. Use no SDK retries, resumption, reruns, server-side fallbacks, fast mode or priority tier. Before each request, require that the accounted spend plus that request's worst-case cost stays within the approved cap. If it would not, stop, seal and report the remainder as unsent.

Before accounting each response, verify:
- the model: the requested ID or its dated snapshot
- standard tier, standard speed and the global region
- complete usage, with a 5-minute-only cache-write split
- prompt tokens within the frozen bound and under 100,000
- output tokens within 25,000
- a unique `msg_` response ID

Classify the stop reason:
- `end_turn` is a terminal answer, parsed from the text blocks only.
- `max_tokens` at the frozen ceiling is an acquired output-exhaustion failure.
- `refusal` is an acquired refusal failure, with its category recorded.

Charge the last two and continue. Any other stop reason, or any provider, transport, accounting or integrity failure, stops the run globally. Seal on completion, guard stop or failure. Record request headers except authentication. Never record credentials.

Score offline only after replaying the sealed ledger. Grade SQL in the isolated v3 worker on both evaluation snapshots with the Experiment 005 typed keys. Claude does not draft clarification adequacy judgments. The owner reviews the masked worksheet, which shows only question and wording, or has a non-Anthropic model draft judgments for the owner to accept. Items whose question and wording exactly match an owner-accepted Experiment 006 judgment carry it over and are listed as reused. Evaluate the pre-registered replication criteria exactly as the design states them.
