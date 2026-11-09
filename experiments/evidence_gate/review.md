# Alder Desk human review worksheet

Use the generated worksheet after acquisition. Give the reviewer only the worksheet and this guide. Keep the separate replay report, verdicts, timings, costs and trial IDs with the analyst. One worksheet entry represents one distinct question/answer pair. Digest sorting mixes the arms reproducibly. The referral wording can reveal a block despite masking.

| Field | Reviewer entry |
|---|---|
| reviewer / rationale | Record name, review date and the reason for the decision. |
| claims | List every substantive factual claim separately. Copy its exact text into `span`. Use an empty list only when there is no substantive factual assertion. |
| support / evidence | For each span choose `supported`, `unsupported` or `contradicted`. Quote the supporting or conflicting packet passage, or explain the missing fact. Evaluate only the three offered passages. |
| citations | Per claim map each cited passage ID to true if it entails that claim, false otherwise. Use an empty object for an uncited claim. A valid ID can point to an irrelevant passage. |
| useful_correct | True only if the response delivers the keyed facts and appropriate treatment of gaps without an unsupported material assertion. |
| appropriate_abstention | True for a justified whole-answer abstention. Record justified limits within a partial answer in partial_handling. |
| over_refusal | True if the answer declined a request for which the packet supported a useful answer. |
| partial_handling | For P cases select complete or incomplete according to whether the reply answers the supported part and identifies the missing part. Otherwise use not_applicable. |
| clarification | For M cases select focused, conditional, or missed. A generic referral misses the clarification opportunity. Otherwise use not_applicable. |

The outside-packet ID list is a deterministic hint. Formatting and gate-label checks are automated. Entailment, correct use of a citation, and usefulness require human judgment. Record disputed interpretations in the rationale, seek a second reading for decision-changing cases if available and report whether a plausible alternative grade changes the recommendation. Leave incomplete reviews pending.
