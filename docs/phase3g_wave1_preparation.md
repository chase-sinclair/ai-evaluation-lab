# Phase 3G · Wave 1 review preparation (no release)

**Status: PREPARED TEMPLATES ONLY — NOT STAFFED, NOT DRAWN, NOT DISTRIBUTED.**
Owner authorization covers **preparation** of a blinded 40-family feasibility review (20 positive-source nominations and 20 source-empty nominations). It does not authorize human adjudication, an additional 160 families, a holdout freeze, or paid model requests. No reviewed holdout labels or model results exist.

This operational handoff implements the [sampling manifest](phase3g_sampling_manifest.json), [reviewer workflow](phase3g_reviewer_workflow.md) and [preregistered protocol](phase3g_protocol.md). Those documents take precedence if a template conflicts. The repository is **public**: commit ONLY blank schemas and this runbook; never commit a real queue, a name-bearing packet, the source annotation, the custodian crosswalk or reviewer evidence.

## Staffing and release gate

Assign and document privately:
- **Custodian:** has read access to original Crossref labels, strata, queue, source IDs, quarantine and family graph. Does not adjudicate identities.
- **Reviewer A and Reviewer B:** two *different human people*. Each independently searches the pinned April 14, 2026 ROR v2.6 registry. Neither has access to source labels/strata, candidate lists, scores, baseline, prior model outcomes, other reviewer decisions, or the custodian crosswalk. Log any AI or research assistance; AI is **not** an independent human reviewer.
- **Disagreement adjudicator:** a third human, blinded to Crossref labels, model outputs and policy data, with the two sealed evidence trails only. The source-aware custodian must not serve as a blind adjudicator.

Secure the distribution method and separate permissions for the two reviewers before packet release. Require an affirmative human confirmation of assignments, capacity, permissions and the readiness checklist; do not infer it from template existence. Estimated first-wave effort is **18–32 total person-hours**, subject to actual measurements.

## Protected working area (not in Git)

Use an access-controlled location under `.verification/phase3g-wave1/` (already gitignored), or an equivalently access-controlled off-repository store. Git ignore is **not** access control: check directory, cloud-sync, backup, sharing and collaborator permissions separately.

```text
.verification/phase3g-wave1/
  custodian/      # source queue, annotation + stratum, seq_no, family membership, hashes, exclusion ledger
  reviewer-a/     # blinded packet and A-only completed worksheet
  reviewer-b/     # blinded packet and B-only completed worksheet
  adjudicator/    # disagreements and sealed evidence, no publisher labels
  reporting/      # aggregate first-wave findings; private until publication review
```

Do not copy any of these populated files to `docs/`, GitHub branches, issues, PRs, Actions artifacts, screenshots, chat messages, or portfolio pages.

## Steps after a separate staffing/packet authorization

1. **Verify the frame, before drawing.** Reproduce the pinned Crossref and ROR checksums and Phase 3G population membership hashes; confirm 579 historical quarantine rows, all documented exposure seeds and nine cited Phase 3E registry IDs. Check relationship/alias/name-family collisions. Abort on any mismatch. No alternative source or regenerated seed is permitted without a versioned design review.
2. **Draw exactly 20 from each source stratum** according to `phase3g_sampling_manifest.json` (same seed, family order, representative rule, no within-family replacement). Draw from the committed independent eligible family frame, not from reviewer suggestions. Preserve full queue provenance privately; record reasons for any prohibited/unsupported case, without selecting a substitute opportunistically.
3. **Blind the combined 40.** Mix by the manifest's SHA-256 presentation ordering; assign opaque, unique IDs unrelated to `cr-<seq_no>`, family keys, labels, strata or ranks. Verify exact set equality between sealed crosswalk and the two name-bearing packets. Reviewer packet schema is only `opaque_id,deposited_name`; shuffle each reviewer's presentation without revealing source stratum. Both reviewers evaluate the **same 40 names**.
4. **Security preflight.** Mechanically inspect packet headers and values for any source labels, ROR answer IDs, hidden strata, source sequence numbers, family identifiers, candidate scores, baselines, policy ranks or model outputs. A deposited name that itself contains an organization identifier must be reviewed for inadvertent answer leakage. Test that reviewers cannot open each other's worksheet or any custodian record. Store a SHA-256 receipt for every sealed packet/worksheet.
5. **Release only after explicit staffing and packet approval.** Distribute separate worksheets and the blinded guidance. Reviewers investigate independently, enter actual search terms, consulted records, relationship/status evidence, dated sources, decision, duration and assistance; seal/sign their own results before any comparison. No communication about cases until both are sealed.
6. **Reconcile separately.** Give the third adjudicator the two sealed evidence trails only, not publisher or model labels. Keep original decisions and reasons. After adjudication, custodian compares final identity to original source annotation and rechecks development/family independence. Exclude unsupported, source-discordant, unresolved or cross-family-conflicted nominations; never alter the original source label or relabel a stratum to boost yield.
7. **Report, then stop.** Complete the first-wave aggregate report with per-stratum attempted/accepted counts, first exclusion reason, initial agreement, disagreements, adjudications, unresolved counts, elapsed review time, acceptance-rate uncertainty and projected review hours. Return to owner for a new decision. **Do not recruit further families or call a model.**

## Human review standard

Decisions are `LINK` (with an **active** full ROR URL), `NO_SUPPORTED_ACTIVE_MATCH` (identifiable referent, documented search and explicit rebuttal of plausible competing records), or `INSUFFICIENT` (ambiguous, vague, historical mismatch, mixed attribution, or weak evidence). A zero-result search or omission from the five offered candidates is *never* sufficient alone to assert a no-match. Reviewers should inspect translations, country, agency/subunit distinctions, aliases, acronyms, inactive records and parent/successor links. Do not show candidate lists or the Crossref source answer to reviewers. The 20/20 source strata are **nominations**, not final adjudicated outcomes.

## Abort and escalation criteria

**STOP** on missing genuinely independent humans or a blinded third adjudicator; excessive or unapproved effort; unverified source hashes; broken quarantine/overlap; mixed or incorrect stratum draw; leaked answer/stratum/model information; shared reviewer decisions; incomplete sealed receipt; unsupported no-match claims; disagreement not resolved; or any request to use paid APIs. Quarantine any compromised packet, document the failure and ask the owner to approve a new versioned process. If even the upper Wilson yield bound projects inability to reach the quota within the remaining ceilings (225 positive / 100 empty nominations), stop for redesign. Otherwise report uncertainty and request a bounded continuation decision.

## Included blank templates

- [Blinded case packet schema](review/phase3g_packet_template.csv) (no names or cases)
- [Reviewer A worksheet](review/phase3g_reviewer_A_template.csv) and [Reviewer B worksheet](review/phase3g_reviewer_B_template.csv) (separate empty files)
- [Sealed custodian crosswalk schema](review/phase3g_custodian_crosswalk_template.csv) (schema only; populated content must stay private)
- [Disagreement adjudication schema](review/phase3g_adjudication_template.csv)
- [Release gate](review/phase3g_release_gate.md) and [first-wave report](review/phase3g_wave1_report_template.md)

**Open gates:** reviewer identities/capacity not confirmed; custodian and adjudicator not assigned; actual 40-family draw not performed; packets not generated or inspected; no human adjudications or live requests. The protocol's 200-family target remains conditional.
