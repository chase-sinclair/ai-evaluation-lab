# Experiment 006 acquisition protocol, revision 1

Apply the design in `docs/experiment06_model_context_design.md`. The frozen proposal is `proposals/r1`. Luna bodies are the accepted Experiment 005 v3 evaluation bodies for arms A and B. Sol bodies differ only in the model field.

Send the 432 requests once, in manifest order, with no SDK retries, resumption or reruns. Before each request, require that the accounted spend plus that request's worst-case cost stays within the approved cap. If it would not, stop sending, seal and report every remaining request as unsent. Do not reorder to fit the cap.

Before accounting, verify each response's model (the requested alias or its dated snapshot), standard tier, compatible echoed settings, complete usage, input within the frozen bound and a unique response ID. Accept an incomplete response attributed only to `max_output_tokens` at the frozen ceiling, with no provider error, as an acquired output-exhaustion failure. Charge it and continue. Any other provider, transport, accounting or integrity failure stops the run globally. Seal the result directory on completion, guard stop or failure.

Score offline only after replaying the sealed ledger against the frozen bodies. Grade SQL in the isolated v3 worker on both evaluation snapshots, using the Experiment 005 typed keys. Give the clarification reviewer only the masked worksheet (question and wording), never model, context or draw. Report unsent, interrupted and exhausted requests separately from terminal decisions. Report each draw against its full denominator of 36.
