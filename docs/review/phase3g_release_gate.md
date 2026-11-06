# Phase 3G wave 1 · owner/custodian release gate

**Default: BLOCKED.** Filling this checklist does not itself authorize releasing cases; the owner must separately confirm the staffing and packet.

## People and access
- [ ] One named, trained custodian with access to source labels; custodian will not adjudicate
- [ ] Two distinct named human reviewers, independent case decisions, time capacity confirmed
- [ ] A separate, blinded third human adjudicator available for disagreements
- [ ] Reviewer A cannot see Reviewer B's decisions, and vice versa
- [ ] Neither reviewer nor adjudicator can see source annotations, strata, candidate ranks, model outputs or the sealed crosswalk
- [ ] Permissions and distribution channels tested, including cloud sync, backups and external share links

## Sampling and privacy
- [ ] Pinned Crossref/ROR checksums and Phase 3G frame membership hashes reproduced
- [ ] Historical 579-row quarantine, review supplement and exposure closure reproduced
- [ ] 20 positive-source + 20 empty-source **nominations** drawn with exact manifest algorithm
- [ ] Exactly 40 unique eligible family representatives; deterministic seed and queue ranks sealed
- [ ] Combined presentation blinded/shuffled; opaque IDs unique and not derived visibly from source IDs
- [ ] Reviewer A/B packets contain **only** opaque ID and deposited name
- [ ] Source label/stratum, full ROR answer ID, candidate lists, scores, family keys, review notes and model outcomes absent from reviewer packets
- [ ] Source/content and overlap checks performed; no identifier leakage from names overlooked
- [ ] Case packet, private crosswalk and reviewer worksheet hashes recorded; full set equality checked
- [ ] No populated crosswalk, case packet or review evidence committed, uploaded to GitHub, or posted in chat

## Workflow and boundaries
- [ ] Both reviewers will seal original worksheets before comparison or discussion
- [ ] Third adjudicator only sees reviewer evidence trails, not source/model labels
- [ ] Source-annotation reconciliation follows independent adjudication, never precedes it
- [ ] Per-stratum yield, disagreements, exclusions, review time and projection report prepared
- [ ] Stop conditions and 18–32 person-hour estimate acknowledged
- [ ] Owner separately approves **release of the blinded 40**, not 200-family adjudication
- [ ] No paid requests or further family recruitment authorized

**Custodian signoff:** ____________________  **Date:** __________

**Owner release approval:** ______________  **Date:** __________

Until both signoffs and all checks are complete: **DO NOT RELEASE CASES OR BEGIN REVIEW.**
