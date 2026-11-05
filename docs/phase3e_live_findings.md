# Four-query Crossref live pilot · November 5, 2026

The owner-approved run completed at 21:07 UTC with four sequential attempts, four completed responses, and zero retries or execution errors. The integration preserved request order, exact logical and wire-body hashes, response usage, and grades. Separately, the model made three correct links and one correct abstention. The baseline missed one link, CNPq. Its uncertainty ranking put this case last among the four.

| Deposited query | Baseline | Returned decision | Grade | Input | Output (reasoning included) | Latency | Usage-priced USD |
|---|---|---|---|---:|---:|---:|---:|
| Research Grants Council of Hong Kong | Abstain | ABSTAIN | Correct abstention | 241 | 72 (63) | 5.181 s | 0.0000601 |
| Higher Education Commission, Pakistan | Correct link | [Higher Education Commission](https://ror.org/038y3sz68) | Correct link | 252 | 46 (30) | 1.678 s | 0.0000482 |
| Universidad de La Laguna | Correct link | [Universidad de La Laguna](https://ror.org/01r9z8p25) | Correct link | 247 | 50 (32) | 1.459 s | 0.0000497 |
| CNPq process | Abstain | [Conselho Nacional de Desenvolvimento Científico e Tecnológico](https://ror.org/03swz6y49) | Correct link | 251 | 56 (39) | 1.326 s | 0.0000531 |

Each returned link was in the query's frozen five-candidate list and exactly matched the single Crossref target. By the documented human review, the Hong Kong name had no supported active match in pinned ROR v2.6. All three positive targets were retrieved. The four responses matched the expected output format and parsed without errors.

| Escalation | Queries sent under the replay policy | Correct / 4 | Link precision / recall / F1 | Input / output tokens | Summed provider latency | Usage-priced USD |
|---|---|---:|---|---:|---:|---:|
| 0% | None | 3 | 1.000 / .667 / .800 | 0 / 0 | 0 s | 0 |
| 25% | Pakistan | 3 | 1.000 / .667 / .800 | 252 / 46 | 1.678 s | 0.0000482 |
| 50% | Pakistan, Hong Kong | 3 | 1.000 / .667 / .800 | 493 / 118 | 6.859 s | 0.0001083 |
| 100% | All four | 4 | 1.000 / 1.000 / 1.000 | 991 / 224 | 9.643 s | 0.0002111 |

Replay reused one acquired response per query. Costs in the four rows describe alternatives and must not be added together. Moving from 50% to 100% added $0.0001028 and repaired the one incorrect abstention. The first two escalations reproduced the baseline decisions. This development prefix has three positive labels and one reviewed no-match. One repaired case accounts for the entire measured benefit and gives little basis for selecting a deployment policy.

All responses reported model `gpt-6-luna`, standard service tier (`default`), 1,024 maximum output tokens, medium reasoning effort, temperature 1.0 and top_p 0.98. The latter inference settings were provider-reported defaults. The sent bodies contained no tools. The reported implicit cache TTL was 30 minutes with maximum retention of 24 hours. Reads and writes were zero for every response, with both write-lifetime counters present. The 224 output tokens include 164 reasoning tokens.

The standard short-context price row was rechecked before execution: per million tokens, $0.10 uncached input, $0.50 output, $0.01 cached reads, $0.125 for 30m writes and $0.25 for 12h writes. Pricing 991 uncached input and 224 output tokens gives **$0.0002111**. The policy-based estimate agrees. The conservative spending charge was **$0.00354375** against the approved **$0.005** cap. The API supplied no billed dollar amount. [Official pricing](https://developers.openai.com/api/docs/pricing)

All 14 run files, including the four attempt receipts, four accounting receipts and complete response records, are preserved under the ignored local directory `results/crossref-development-3e-once/`. The shared Git one-shot claim remains in place. Execution used clean revision `136990672fe8ab672af418492abc7b0e6a555d66`, approved plan digest `16c01224c3ee772e318c7326749b4084a3e0b72c2ca997a8e2bb8b13dc18de03` and validated review digest `a596c2fee9aad98b024c6a9dea809bac951eba167d8dba943c1474e6d544672e`. SHA-256 of records.jsonl is `52e2d0880e917290cf2aba94763dd3ad5640e125464321151e98e08719c44a78`, and of pilot-report.json is `5d1f36c6219e198ab77b1a69e2348a531c1c05624e2e0a64a5e6fc54ffaa24de`.
