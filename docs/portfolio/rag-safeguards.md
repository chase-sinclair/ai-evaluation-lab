# Which RAG Reliability Safeguards Are Worth Deploying?

*Draft for owner review · AI Evaluation Lab, Experiment 03*

A facilities employee asked whether a contractor could enter Annex B during a closure. The generator correctly cited the signed restriction and said no. A second model checking that answer blocked it. In a deployed desk, the employee would have received a referral instead of the site-specific instruction.

**My recommendation for this workload is to start with standard retrieval-augmented generation (RAG), with citations and permission to ask a question or abstain.** Across 36 enterprise scenarios, it produced 32 fully correct decisions. Checking evidence before answering produced the same 32. Checking answers before release reduced that count to 28 and roughly doubled estimated inference cost. Four referrals are observable; the value of each depends on what it replaced.

## The implementation decision

An enterprise can pay for a second model call on every employee or customer question. Before generation, it can check whether the evidence is sufficient and sometimes avoid generating an answer. After generation, it can inspect the actual claims, but the generation cost has already been incurred. I wanted to know when either check earns its place in the workflow.

## How I evaluated the choice

A first pilot used 24 fictional service-desk requests. The evidence gate blocked six. Standard RAG had already abstained appropriately on all six, and both paths shared a minor error naming who issues a collection code.

The second study used 36 new questions: 12 routine, 12 with incomplete or ambiguous evidence, and 12 with conflicting, stale or misleading evidence. Each question had a fixed packet. We generated one answer and reused its exact text across architectures so a different generator draw could not explain a gain or loss. The verifier saw the real answer only after generation. Its 36 request bodies were frozen and separately approved before dispatch. The 108 resulting customer outcomes resolved to 40 distinct replies for AI-assisted, source-relative review.

## What the extra checks bought

| Phase B workflow | Fully correct | Estimated cost for 36 | Median modeled response time |
|---|---:|---:|---:|
| Standard RAG | 32/36 | $0.0024700 | 1.52 s |
| Evidence check before generation | 32/36 | $0.0042786 | 2.77 s |
| Answer verification before release | 28/36 | $0.0049961 | 3.03 s |

The pre-gate passed every packet. The verifier withheld two supported policy answers, a useful clarification about which campus handled a key replacement, and an abstention that explained why a dry-freight payout cap could not be applied to refrigerated goods. The generic freight referral was still safe. Giving it full credit would raise the verifier to 29/36. Neither check prevented an observed unsupported answer under the supplied grades.

Four baseline replies missed strict completeness requirements. For example, the credit analyst got a sound explanation of why the covenant ratio could not be computed, but the reply omitted the requested formula. The appropriate fix depends on whether the customer needs a safe warning, a reproducible calculation, or an authorized decision.

## My contribution

I directed the architecture comparison, reviewed and strengthened the scenarios, approved the two acquisition stages separately, and required that an unnecessary refusal count against a safeguard. Codex assisted with the implementation, acquisition audits and offline paired reporting. The Phase B judgments are AI-assisted and await my approval.

## What I would recommend to a customer

Ask the support owner for recent failures that changed a customer decision. Trace each to the retrieved packet, the generated claim and the action someone took. A missing signed rider points toward document retrieval. A wrong number copied from an otherwise adequate filing is a reason to shadow an answer verifier. A discretionary approval belongs with the authorized decision maker. Compare consequential errors actually prevented with correct replies delayed or suppressed, and include handling time for every new referral.

These figures come from fictional packets, one generator draw per question and one model family. Reviewers can reasonably disagree about completeness and citation scope. Modeled latency excludes retrieval and queueing; no customer ROI was measured. Before deployment, repeat the comparison on representative traffic, measure failure prevalence and severity, and audit the replies that any proposed check would suppress. [Technical evidence](../experiment03_paired_findings.md) · [Grading sensitivities](../experiment03_phase_b_review.md) · [Deployment playbook](../fde_deployment_playbook.md)
