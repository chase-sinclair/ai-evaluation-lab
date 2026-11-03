# Offline tool selection fixture

Five locally authored synthetic tasks run against 5, 15, and 30 function schemas,
once per condition: 15 trials. Invoice lookup, customer status, ticket creation,
order search, and an impossible physical transport request have explicit answer keys.
No offered tool can transport a parcel. Ticket creation is explicitly disallowed by
the no-call task, preventing it from being a plausible substitute.

Every condition shares the same query, system prompt, model settings, and four target
schemas. Larger sets only add read-only business-record distractors. A seed-derived
ranking fixes each tool's relative order within a case. The runner separately shuffles
trial order using the seed. Requests, tool IDs/order, schema byte lengths, and conservative
input-token estimates are stored. More tools also mean more prompt text: any future
study concerns expanded choice sets, not tool count independent of context length.

The mock uses fixed request-text rules. It intentionally gives the ticket the wrong
priority, and uses the wrong tool for orders at 15/30 tools. It makes no call for the
physical transport task. This is an engineered software fixture, not a model or research
result. Expected software check: 10 passing and 5 failing trials.

Grader 0.1.0 compares structured call count, canonical name, and exact typed arguments.
Object key ordering and JSON serialization whitespace are irrelevant. String contents,
case, whitespace inside strings, scalar types (including integer vs float), extra keys,
and call ordering are significant. No fuzzy matching, coercion, or answer-key adjustment.
Unknown tools, schema violations, and malformed calls are invalid outputs. Missing/extra
calls and valid calls with wrong values are separately diagnosed. Correct zero-call
behavior requires an explicit parsed empty call list and a completed provider response.

All cases are development fixtures. They must never become a published held-out benchmark.
