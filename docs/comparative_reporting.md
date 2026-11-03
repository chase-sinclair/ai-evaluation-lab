# Comparative reporting

Aggregate keys retain their previous meanings. Summaries now add `conditions`,
`paired_comparisons`, and a descriptive-only note. Runner and CLI supply planned
per-condition denominators, including conditions with no recorded trials. The public
summary function can still accept only records and total planned count; condition
denominators then explicitly say `recorded_only`, since missing allocation is unknown.

Each condition includes accuracy, task/invalid/provider/grader failure counts and rates,
mean measured latency, reported usage, known estimated costs, unknown-cost counts,
and cost per correct task. Unknown cost is not imputed to zero. Latency describes recorded
attempts, including failures. Repetition counts and unique recorded cases are separate.

Pairs match dataset ID/version and case ID, then require identical recorded repetition
sets. Within each case compute right-minus-left success, latency and cost differences;
average case means equally. Missing/unequal pairs are excluded and counted, not converted
to failures. Cost comparisons disclose their smaller paired denominator when costs are
unknown. Recorded failures contribute zero success. Partial-run paired estimates can be
biased; the all-planned condition denominators remain primary. Duplicate trial keys are errors.
No p-values or significance claims are produced for the synthetic fixture.

`ModelRequest.output_format` is a local normalization selector: `text` yields a parsed
string; `tool_calls` yields a dictionary with a `tool_calls` list and optional `text`.
Raw sanitized provider output is retained. Text-only requests reject offered tools;
unexpected returned calls are invalid outputs, not silently successful empty text.
Incomplete provider responses remain invalid under either mode. Mock text mode echoes
the request's final content; it is a deterministic test double, not language inference.
See the [official SDK text accessor](https://developers.openai.com/api/reference/python).
