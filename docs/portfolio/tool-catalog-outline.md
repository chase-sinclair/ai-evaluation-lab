# Does Giving an AI Agent More Tools Make It Less Reliable?

**Case-study outline · offline preparation only.** A freight operations team can give its agent five desk-specific functions or expose related operations throughout the business. The decision is whether broader access earns its extra prompt cost and the risk of a wrong action.

| Section | Material for the eventual study |
|---|---|
| Decision and alternatives | Compare the 5-tool desk catalog, a 10-tool catalog with adjacent lookups and a 20-tool catalog with close alternatives. Distinguish a wrong lookup from an unintended write. |
| Evaluation | Follow 12 fictional requests through each catalog. Score actual function identity, exact arguments and restraint on four no-call cases. Show all three outcomes for the same scenario. |
| Findings available now | Serialized tool definitions grew from 1,430 to 2,704 to 5,565 bytes. Target definitions stayed identical. Model reliability, actual tokens, latency and cost await approved execution. |
| Worked example to inspect | The operator asks to commit a revised dock start time. A preview has the same inputs but leaves the booking unchanged. Show the three observed decisions here after a run. |
| Trade-offs | Present counts out of 12, wrong calls and unnecessary calls, paired repairs/regressions, measured latency and usage-priced cost. Keep provider failures visible. Record access to new task types as an unmeasured benefit of breadth. |
| Eventual recommendation | If expansion adds material wrong actions or cost without helping the paired requests, favor the narrower desk catalog for those tasks. If reliability holds, weigh routing overhead and the value of additional supported work before broadening access. With mixed evidence, identify the specific tool pairs or permissions that deserve separation. |

The first live recommendation is pending evidence. [Study design and approval proposal](../../experiments/catalog_scope/README.md)
