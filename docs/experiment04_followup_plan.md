# Experiment 004 · prospective 2,048-token acquisition

**Owner decision pending.** After P3 reached the first pilot’s 512-output-token limit, the owner requested a separate proposal with a larger allowance. All 24 episodes would run from the beginning. Only follow-up receipts would enter its evaluation. The first pilot is permanently closed at six requests, five completed, 4/5 evaluable correct, one observed loss on P8 and $0.0011733 estimated spend. [Interrupted pilot audit](experiment04_live_acquisition.md)

## Approval target

- Canonical digest: `68575ca194e925d3ace007b08f98b6704ff4bcbd84e011be6d9ece2df96bcb24`
- Manifest file SHA-256: `6f8b6e914a1f06f5b024d77e643d60ce8f19e3d788589c7b56977cdde60554c1`
- Single-use destination: `results/recovery-followup-2048-once/` (unused).
- Up to 24 sequential GPT-6 Luna Responses requests, standard tier, 2,048 output tokens each, original 30-minute cache policy, native proposals only, zero retries and no resume.
- [Frozen bodies and bindings](../experiments/recovery/request-manifest-2048.json) · [Prospective dispatcher](../scripts/acquire_recovery_followup.py)

The offline preflight reconstructs the original plan and compares each follow-up row to the corresponding original row after replacing only the output cap and recalculating size, allowances and hash. This checks the exact public inputs, prompt, tool definitions, inference settings, order and source-checkpoint binding. The HTTP hook validates the actual outgoing JSON before each send. The original approval digest is rejected.

## Proposed spending

The 24 canonical bodies total 103,528 bytes. At one input token per byte plus 256 per request, the input allowance is 109,672 tokens. The output allowance is 49,152 tokens, including reasoning. Standard short-context pricing checked November 10, 2026 was $0.10/M input, $0.01/M cache read, $0.125/M for 30-minute cache writes and $0.50/M output. Reserving all input at the write rate gives $0.013709 for input plus $0.024576 for output, or **$0.038285**. The **proposed estimated-spend cap is $0.05**. The extra byte in each serialized cap accounts for the $0.000003 increase over the preliminary reserve. Account model metadata confirmed access without inference. [Official pricing](https://developers.openai.com/api/docs/pricing)

## Ordered body hashes

| Position | Episode | Input allowance | Canonical body SHA-256 |
|---:|---|---:|---|
| 1 | F1 | 4,163 | `405b155e2d43c11b7fb7ad4c5aea39d16e88f49ab35604237e3c59688d4c4118` |
| 2 | P6 | 4,568 | `b5f45129c45c4aa005b67fd969c9d79f7657397e14a2b644e665c22646a2108a` |
| 3 | P8 | 4,639 | `f506a6ccf74011bba564803f31c6c23f54947bf06b1cafbace72a62b40660376` |
| 4 | S5 | 5,373 | `3dd5c147d907312d0fd6845b186a3a96bfb26a8e42383d6899406d3405449a97` |
| 5 | S3 | 4,850 | `807ccd9039d76c07f541b7c29e18e6de5f3c37f35122d6936c805cc330b43dba` |
| 6 | P3 | 4,657 | `193eb969c2aa3976df554639f01e6aeead657a12572e45d7ac93246f03c95acb` |
| 7 | P5 | 4,912 | `f25b9c8ade70640ed7da63f0410c9bc9b872e5ba74c9f8ec40f01ecf97d70142` |
| 8 | S6 | 4,411 | `6e21912e00146c414a76d1ce92b63c180ed0fbbbee12b3f4327d4ca4998c0164` |
| 9 | F6 | 4,837 | `fa33152cd1e2dd4a2bed192a7ab1ed4998772a9f6f33db6b21a927e386a31756` |
| 10 | S2 | 4,494 | `6b47b4d4b512113024f8e31d21d4dd30621613b4aad7c67802493126294454b3` |
| 11 | P4 | 4,691 | `727bf6c5708f73281f5dd43b19b8cb2e67a44473a00d94957e7e52930c325151` |
| 12 | F2 | 4,045 | `6cb714a9c137328218b5541a00bc3b84b5b0c86cae5b488fbd1bd2e622234956` |
| 13 | F3 | 4,053 | `b1e8cf997f5e71d089a2825be24149e10b5db0cc3b679ac0f011caa6a4b9a91f` |
| 14 | P7 | 4,027 | `f42e6d0a09132fa2e0ea07e70564b481487d140772bb77b8359be03a05bfbd38` |
| 15 | S4 | 4,847 | `d038fbe4d5409958cbeb2691acf7e1b9805e8a6de4277afabc9a0ce1d3af412a` |
| 16 | F7 | 4,036 | `e1730af6d2f8515f05e5f7ac56e94374de0f9639690cc1b2743e777c47fab06d` |
| 17 | P1 | 4,466 | `7f398fc4c366fa393e79105461b6198fa1e48d605a37e0660ba2e4fecbee7f7f` |
| 18 | F5 | 4,459 | `e9592a7cdb2a50c127c425d4eec6bfc75820e39472df7320ab1ca2472138bbd3` |
| 19 | P2 | 4,520 | `e07aa64e1babf14dcfcc3f117f7a1315ebcf497be20190e050b8a6c9cac91abf` |
| 20 | S1 | 4,842 | `695f4309e334e0870e9e7dc283c4f6ce5010dca35b33cc2c9ecdcff22699dd55` |
| 21 | S8 | 5,002 | `279b646df231b9593aa975a48c8f6c8e66bbdfa61ac49dfb1e80ef4d6db9fccf` |
| 22 | F4 | 4,459 | `e9592a7cdb2a50c127c425d4eec6bfc75820e39472df7320ab1ca2472138bbd3` |
| 23 | S7 | 4,805 | `84a18ca874be0a963c16fd373964c3c38b860989bf926cff3bd96a4cef72ae4f` |
| 24 | F8 | 4,516 | `0ca44d877cefc2156a25da5ec9c837f4d72bc7a34d179b975ddbe52920cbbd3d` |

## Run boundary

A future acquisition requires explicit owner approval of this digest and cap. Verify the clean proposal revision, pricing, current model access, unused destination and reserve again before dispatch. The dispatcher persists each raw receipt before deciding whether to continue. Valid usage on an incomplete response counts toward spending; the incomplete response ends acquisition and is ineligible for replay. An incorrect, absent, malformed or multiple proposal in a completed response goes to the original grader as a case failure. Provider, integrity, tier, cache-policy, accounting and budget failures stop acquisition with a planned denominator of 24. No follow-up outcome exists at this checkpoint.
