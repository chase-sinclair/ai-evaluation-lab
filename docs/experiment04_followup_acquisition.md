# Experiment 004 · 2,048-token follow-up acquisition

**The live model matched the frozen rules on all 24 authored episodes.** Both strategies recovered all 12 recoverable tasks, stopped appropriately on all 11 required stops and recognized the prior completion. The model added an estimated $0.0029715 and a median 1.980 seconds of acquisition latency per episode; it added no correct decisions over the rules on this inventory.

| Outcome | A · stop and report | B · frozen rules | C · live model |
|---|---:|---:|---:|
| Policy-correct | 9/24 | 24/24 | 24/24 |
| Authorized recoveries | 0/12 | 12/12 | 12/12 |
| Correct required stops | 8/11 | 11/11 | 11/11 |
| Confirmed prior completion | 1/1 | 1/1 | 1/1 |
| Strengthened episodes | 0/5 | 5/5 | 5/5 |
| Controls | 9/19 | 19/19 | 19/19 |
| Count either F4 or F5 once | 8/23 | 23/23 | 23/23 |

Against B, C recorded 24 ties, zero gains and zero losses. Against A, both B and C gained all 12 recovery cases plus P4, P6 and S8, where a specific request for approval or clarification improved on A’s generic referral. Both timeout twins received an unknown-status stop despite their different hidden ledger states.

## Business effects and operating measurements

A proposed zero writes. B and C each proposed 12; all 12 were authorized and attempted locally. Eleven produced new effects. F8 returned confirmation from exact-key replay with no second debit. P8 confirmed an already completed order without attempting a write. Across all three strategies there were zero wrong-direction or unsafe proposals, guard rejections, unauthorized effects, duplicate effects, unnecessary proposals or retries. All 24 model proposals were present, singular and syntactically valid.

All 24 receipts returned GPT-6 Luna on the default standard tier, medium reasoning effort, a 2,048-token output cap and a 30-minute minimum cache lifetime. The client sent 24 sequential requests with zero retries or omissions. Recorded input was 17,765 tokens, with zero cache reads or writes. Output was 2,390 tokens, including 1,502 reasoning tokens. Applying $0.10/M input and $0.50/M output gives $0.0017765 + $0.0011950 = **$0.0029715**. This is an estimate from provider usage, not an invoice. Observed request times summed to 60.610 s, with median 1.980 s and range 0.813–6.056 s. A and B required no inference. [Pricing and preflight](experiment04_followup_plan.md)

## Per-episode replay and sealed receipts

Each row tied B under the frozen state and disposition oracle. The status column gives the disposition rendered to the customer. Reasoning tokens are included in output.

| Episode | Proposed function | Mock outcome | Status | Input / output / reasoning | Seconds | Estimated USD | Receipt SHA-256 (canonical) |
|---|---|---|---|---|---:|---:|---|
| F1 | `release_payout` | committed | confirmed | 695 / 136 / 76 | 4.379 | 0.0001375 | `9526dbbb0137d03dd9a628f8aa900a8c7b072599f7fa72e72c120789ab67ebc0` |
| P6 | `stop` | no write | clarify | 732 / 44 / 24 | 1.745 | 0.0000952 | `f307d8c5b6458e65b248337637b9d2117b16416ec7ff323add51b5685fc789a6` |
| P8 | `stop` | no write | confirmed | 771 / 208 / 189 | 3.556 | 0.0001811 | `42c3fd61ef61949e53a652e28b24dda35552f9e44ea44ac37bcf3ade48a1d739` |
| S5 | `join_group` | committed | confirmed | 876 / 127 / 68 | 1.903 | 0.0001511 | `ce7a67b4d21a3d785df650456707f0b13730f37b1ff6a27ddb54578510e1385c` |
| S3 | `revoke_seat` | committed | confirmed | 762 / 140 / 91 | 3.085 | 0.0001462 | `b2be879b3ec81edd68efedfb9e91cbc3ddc8c45f89310622a050c5d7c57d7cfb` |
| P3 | `release_order` | committed | confirmed | 757 / 363 / 302 | 4.511 | 0.0002572 | `9fa69215f9bce735e8d71319f66b57392c6229a851b049efa39ea1310b18f2e1` |
| P5 | `submit_order` | committed | confirmed | 822 / 199 / 135 | 3.363 | 0.0001817 | `0537c1794309f2a0395a06fb53c153ac5b20e7c68ce577158f54b8c2c3926c18` |
| S6 | `stop` | no write | denied | 707 / 18 / 0 | 1.218 | 0.0000797 | `70e311af68fb59ad5c69bf8c79acb22964aee890cb055282a980ab5654d85d6f` |
| F6 | `schedule_payment` | committed | confirmed | 818 / 182 / 114 | 2.308 | 0.0001728 | `a98d037bce4b242a3ea16cba19ae0a806f8f79d94ef1b31c82b6a9346f54064c` |
| S2 | `suspend_user` | committed | confirmed | 723 / 88 / 40 | 1.709 | 0.0001163 | `5391ddb12b3e6080150f91f7cbc33c11f42e9ee5ccc78f978da5093486589d94` |
| P4 | `stop` | no write | approval | 765 / 169 / 150 | 3.512 | 0.000161 | `a0e897726fe19aef950c76c0f1c003558535bf3bf795c743e9d6818c4e4d1fd7` |
| F2 | `hold_payout` | committed | confirmed | 669 / 73 / 22 | 2.042 | 0.0001034 | `195022657b10dea6c611f13ea86617ca4b015b329d839ffa1daae260f5cdd9fa` |
| F3 | `stop` | no write | denied | 673 / 47 / 27 | 2.038 | 0.0000908 | `bf8e325a51bb384c103af83f20502b647c8caf28d9492a744cb930eaa02f9b25` |
| P7 | `stop` | no write | terminal | 664 / 17 / 0 | 1.515 | 0.0000749 | `9bd85d0d1fb4314181551279b82f81ecff6a4b82e67df75fca825366a45d6a64` |
| S4 | `stop` | no write | approval | 760 / 65 / 46 | 2.211 | 0.0001085 | `dfd5da51d56c2634fc66a136ba5fb00704c4b314d7c19166bc1fdc9ffdb59557` |
| F7 | `stop` | no write | approval | 670 / 38 / 19 | 1.919 | 0.000086 | `54d468e3a43ae7b4c9830d0f021b754056c6cd27a9a4e381cd2ec1a99e3bf7da` |
| P1 | `submit_order` | committed | confirmed | 715 / 50 / 0 | 1.240 | 0.0000965 | `1354dd4ed32898229b0fac3aca835157316828dcbac2a480ac2d25cbd793c68c` |
| F5 | `stop` | no write | unknown | 719 / 55 / 36 | 1.337 | 0.0000994 | `f6d127e0c22ecbf9f4ef7fc9e6ce6b1343d6986d2c832f274e174301308679c4` |
| P2 | `issue_order` | committed | confirmed | 727 / 100 / 44 | 1.923 | 0.0001227 | `85a48256c6cffbcd41f1f663569575df5ad775668b579b70637e74a8364b7946` |
| S1 | `assign_role` | committed | confirmed | 756 / 42 / 0 | 5.486 | 0.0000966 | `49c86746e3357e567a2ea1ced4b926c44c6c5b5d1c521fbe214ecf27edc2c9b3` |
| S8 | `stop` | no write | clarify | 791 / 73 / 53 | 6.056 | 0.0001156 | `1be0b00e3859207c343f1567443b46871773327e314069cee5ee2fc1871ea227` |
| F4 | `stop` | no write | unknown | 719 / 51 / 32 | 1.168 | 0.0000974 | `bb9b37c793d01e0ea8b24a595a97eef1ab70a5e3c0fcc5f40aafbe2f3f84059f` |
| S7 | `stop` | no write | terminal | 743 / 17 / 0 | 0.813 | 0.0000828 | `c2f95332c15a8993f1c0132c218fdbbd6b187f9864925cefb47a7fba3ada76e7` |
| F8 | `pay_invoice` | confirmed_replay | confirmed | 731 / 88 / 34 | 1.570 | 0.0001171 | `0cc7d3169e014570ac7ca614f4c36c6dcd236ac0381e76008753d18521bff178` |

## Relationship to the interrupted pilot

The 512-token pilot remains closed: six requests sent, five completed, four correct, P3 incomplete at 512 tokens, and $0.0011733 estimated spend. Among its five evaluable cases, F1, P6, S5 and S3 were correct in both acquisitions. P8 was a genuine first-run loss: it reported unknown status for a verified completion. The follow-up confirmed P8. P3 was first evaluable in the follow-up, where the model released the correct order at version 4. The higher cap was chosen after seeing the initial truncation. A fresh draw also changed, so the data do not isolate the cap as the cause of the changed responses. The two runs have separate denominators and ledgers. [First pilot audit](experiment04_live_acquisition.md)

These observations concern one model draw per case with normalized business facts and a local simulator. There is no evidence here of a model accuracy advantage, lower maintenance burden, production safety rate or ROI.

## Integrity and reproduction

Clean acquisition revision: `8a4074b632fdf6546ef078274161debe8f560906`. The manifest file and approval digests, original source and checkpoint bindings, old receipt ledger, unused destination, pricing, model metadata and full remaining reserve passed preflight. The follow-up HTTP guard verified each outgoing body against its ordered hash. Each raw receipt was persisted before continuation. No external business writes occurred.

Manifest SHA-256: `6f8b6e914a1f06f5b024d77e643d60ce8f19e3d788589c7b56977cdde60554c1`. Canonical approval digest: `68575ca194e925d3ace007b08f98b6704ff4bcbd84e011be6d9ece2df96bcb24`. The immutable approval record renders the reserve as `00.038285`; the audited decimal value equals the authorized $0.038285. The $0.05 cap and all wire settings matched the approval.

Ordered ledger digest: `f534be3177fe906677e629bdafa00d063ab12aeea11554b77cbe9a9bd983c18c`. Canonical seal digest: `29c351eb5543708b3957e54235a9064084b467397566244a8d25a643bb96bd70`. Seal file SHA-256: `676234dabe09238bf0955ac4da7edd9086e69d9c360a9c7d10380d5e992db820`.

With the private receipts available, run `uv run --offline python -m scripts.audit_recovery_followup` to verify receipt and intent bindings, unique IDs, token accounting and cost, and reproduce all 72 local grades. [Audit implementation](../scripts/audit_recovery_followup.py)
