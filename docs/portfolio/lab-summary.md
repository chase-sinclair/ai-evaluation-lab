# Five deployment decisions from AI Evaluation Lab

Five completed experiments address different decisions. Each uses its own workload, baseline and outcome definition. The package is ready for owner review before Lab closure or website integration.

| Study | Deployment decision | Evidence and remaining limit |
|---|---|---|
| [Entity matching](entity-matching.md) | Keep deterministic retrieval and abstention. Show a model’s proposed correction to a reviewer before changing attribution. | One repair in four live responses on a 38-name development cohort. The independent holdout was retired after feasibility review. |
| [Tool catalog scope](tool-catalog.md) | Expose the tools needed for the authorized workflow and independently gate consequential writes. | All catalog sizes passed the harder shared scenarios. With the release capability missing, the assistant proposed the opposite payout operation. No write executed. |
| [RAG safeguards](rag-safeguards.md) | Start with standard retrieval and cited answers. Consider selective verification where consequential errors justify the review cost. | The baseline and evidence check scored 32/36, the answer verifier 28/36. The synthetic evidence packets and one model family limit transfer. |
| [Recovery after tool failure](recovery.md) | Encode documented safe corrections. Escalate when authority or transaction state is unresolved. | Rules and the model each scored 24/24 in the follow-up, versus 9/24 for stop-and-report. The simulated system supplied normalized incident facts. |
| [Financial SQL context](finops-sql.md) | Start controlled development with curated financial definitions. Keep expanded context under consideration and require independent checks before release. | Both reached 18/36, with four questions passing only under each design. Discovery reached 5/36. Shared financial rules and synthetic data limit what agreement on two snapshots establishes. |

The common deployment question is who can act on a model’s answer and what evidence that person needs. A valid tool call can request the wrong write, just as an executable query can count the wrong dollars. Across these studies, measured quantities include task outcomes, recorded usage and observed times. Production adoption, review labor, maintenance savings and return on investment remain unmeasured. [Study format](study-format.md) · [Project record](../PROGRESS.md)
