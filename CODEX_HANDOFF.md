# AI Evaluation Lab — Project Handoff for Codex

**Repository:** https://github.com/chase-sinclair/ai-evaluation-lab  
**Date:** November 3, 2026  
**Status:** New repository; initial scaffold and research engine to be built  
**Audience:** Codex, project owner, technical reviewers

> **Implementation directive:** Read this document before modifying the repository. Build a small, tested, reusable evaluation engine, plus one complete **offline** experiment. Separately research benchmark datasets for future studies. Do **not** implement all proposed experiments, bulk-download third-party datasets, or make paid model API calls during scaffolding.

---

## 1. Purpose and positioning

**AI Evaluation Lab** is a modular Python research framework for conducting **controlled, low-cost experiments about the practical reliability and economics of AI systems in business workflows**.

It addresses decisions faced by Forward Deployed Engineers (FDEs), AI Product Managers, AI Implementation/Solutions Engineers, and enterprise AI strategy teams:

- How reliably does an AI assistant select the right tool when many tools are available?
- When should a business use a deterministic method instead of an LLM, or combine both?
- Does providing richer database context make text-to-SQL more reliable?
- Does bounded error recovery materially increase task success, and is the extra cost justified?
- How do security controls and prompt-injection defenses affect an agent's completion of authorized tasks?
- When does a more expensive model or reasoning mode outperform a cheaper configuration on objectively graded tasks?

**This is not a SaaS app, generic chatbot, agent demo, document-only benchmarking project, or attempt to recreate a large evaluation platform.** The deliverables are reusable evaluation infrastructure, transparent experimental protocols, immutable run results, reproducible analyses, and evidence-based *deployment recommendations*.

The user's portfolio will eventually showcase the lab as a technical engineering project and individual experiments as research case studies. **Do not generate findings, performance claims, charts with invented results, or conclusions before real experiments have been executed.**

### Success definition

The framework is successful when an engineer can add a new experiment with a different dataset and grading method **without rewriting the core runner**, execute it under a strict budget, and reproduce per-case predictions, grades, failures, cost/latency measurements, and aggregate findings.

---

## 2. Non-negotiable principles

1. **One GitHub repository and shared execution framework; independent experiments.** Each study may require its own data, task logic, controls, and deterministic grader. Do not force data reuse.
2. **Objectively checkable outcomes.** Prefer benchmark ground truth, executable expected states, numeric answers, canonical function calls, or independently verified labels. Do not use an LLM judge as the primary correctness grader.
3. **Control the independent variable.** For causal claims, compare paired cases while holding other relevant factors fixed. Distinguish controlled experiments from broader *system comparisons* involving multiple design changes.
4. **Low operating cost.** Mock and test modes must work entirely offline and free. Live API mode requires explicit opt-in, a nonzero finite budget, and request limits.
5. **Reproducibility.** Log exact model IDs, effective parameters, prompt and config hashes, dataset and grader versions, seeds, tool schemas/order, raw/parsed responses, errors, usage, latency, and estimated cost.
6. **Failures count.** Invalid outputs, API errors, no-call mistakes, extra calls, and timeouts must not silently disappear from the results.
7. **Research hygiene.** Separate pilot/development and held-out cases. Never put ground-truth labels into model inputs or tune prompts against the final locked evaluation set.
8. **Minimal initial architecture.** No frontend, API service, authentication, cloud infrastructure, Databricks, vector database, LangGraph, MCP, or multi-agent subsystem at this stage.
9. **Business utility.** Every completed public study should conclude with an evidence-based deployment decision, cost trade-off, and limitations.
10. **No private client material.** Do not use employer/client documents, confidential information, personal credentials, or real user/customer records.

---

## 3. Experiment roadmap — candidates, not immediate build tasks

| ID | Study | Independent variable / comparison | Programmatic ground truth | Possible source |
|---|---|---|---|---|
| EXP-001 | **How many tools can an AI assistant reliably choose between?** | Count of available tools, with target unchanged | Expected tool name, typed arguments, or correct no-call | Authored five-case fixture first; BFCL later |
| EXP-002 | **When should businesses use traditional matching instead of an LLM?** | Rules vs LLM vs hybrid architecture | Labeled entity/product matching pairs | Web Data Commons Products |
| EXP-003 | **Does richer schema context improve text-to-SQL accuracy?** | Schema-context detail | Executed SQL result/state against reference | BIRD Mini-Dev |
| EXP-004 | **Does bounded retry/error correction improve task reliability?** | Repair pass enabled/disabled | Valid API action and expected final mock state | Local deterministic mock API cases |
| EXP-005 | **Can an agent resist untrusted prompt-injection content?** | Untrusted payload present/type | Authorized goal success, prohibited-action avoidance | AgentDojo |
| EXP-006 (optional) | **When is a frontier model worth the extra cost for business documents?** | Model tier or separately isolated scaffolding technique | Tagged financial facts, typed calculations, known absences | SEC EDGAR / XBRL; public documents |

**Current recommendation:** build the core platform with a tiny EXP-001 offline fixture; separately research feasibility and licensing for EXP-001 through EXP-005. EXP-006 is not assumed to be the flagship experiment.

### Design caveats to preserve

- **Tool count (EXP-001):** Increasing tool count also increases prompt size. Keep query, target tool name/schema, and model settings fixed; construct controlled distractors, use seeded order, and record total tool-schema tokens. This tests the effect of *expanded choice sets*, not pure count independent of prompt length.
- **Entity matching (EXP-002):** Rules vs LLM vs hybrid is a deployment-strategy comparison, not one isolated causal variable. Describe it accurately.
- **Text-to-SQL (EXP-003):** Compare execution results under a safe read-only database snapshot, not string equality with reference SQL.
- **Document study (EXP-006):** SEC XBRL involves period, unit, taxonomy, filing, and amendment choices; public availability does not magically imply unambiguous ground truth.

---

## 4. Two bounded workstreams for Codex

### Workstream A — Build a working research engine (primary)

Implement the shared framework plus **one tiny fully functioning offline experiment**. The mock study exists to validate architecture and scoring, **not** to establish publishable research findings.

Build:

- Installable Python package and CLI.
- Strongly typed experiment, condition, case, request, response, grade, and run contracts.
- Experiment registry or simple discovery mechanism.
- Sequential runner with reproducible trial generation and finite limits.
- Mock model provider plus a single real provider adapter, but **no real calls during setup**.
- Deterministic grader for tool-call correctness.
- Immutable per-run result directories, raw JSONL records, manifest, and summary.
- Offline unit and end-to-end tests.
- Clear documentation, including instructions for adding the next experiment.

### Workstream B — Research datasets and feasibility (secondary)

**Yes, research datasets now—but do not ingest and implement them all now.** Create a concise dataset catalog that investigates authoritative benchmark sources, ground-truth quality, licensing, access, versioning, size, and grading complexity.

This workstream must not delay shipping a functional Workstream A.

- **Allowed:** Research official documentation and repo metadata, inspect schemas, identify version-pinned small subsets, record URLs and limitations.
- **Not allowed without owner approval:** Bulk downloads, expensive scraping, paid APIs, installing heavy benchmark stacks, claiming unknown licenses are permissive, writing full EXP-002+ implementations.
- If network access is unavailable, mark entries **unverified** rather than fabricating details.

---

## 5. Recommended technology decisions

| Concern | Choice | Rationale |
|---|---|---|
| Language | Python 3.12+ | Fits evaluation and enterprise-AI engineering tasks |
| Package/dependencies | `uv`, `pyproject.toml`, checked-in `uv.lock` | Reproducible local environments |
| Validation | Pydantic | Typed contracts, config validation |
| CLI | Typer | Simple commands and help text |
| Configuration | YAML | Versioned experiment setup |
| Testing | pytest | Fully offline tests |
| Lint/format | Ruff | Lightweight quality gate |
| Results | JSONL + JSON manifest/summary | Transparent, portable, easy to inspect |
| Analytics | Standard library first; Pandas later if needed | Avoid premature dependencies |
| Database | None initially | Files are sufficient for initial pilots |
| Model providers | Mock + one real provider adapter | Inexpensive vertical slice; extensible |
| UI | None initially | Portfolio website will eventually show precomputed reports |

Use **current verified SDK documentation** when implementing the real adapter. Some model configurations don't support `temperature=0`, identical structured-output options, or the same reasoning controls. Record supported effective settings rather than silently dropping unsupported ones.

Potential future option: evaluate whether [Inspect AI](https://inspect.aisi.org.uk/) would save work on larger studies; **do not** import it into the first scaffold merely because it is well known.

---

## 6. Target repository structure

```text
ai-evaluation-lab/
├── AGENTS.md
├── CODEX_HANDOFF.md
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
│
├── src/eval_lab/
│   ├── __init__.py
│   ├── cli.py
│   ├── contracts.py
│   ├── core/
│   │   ├── registry.py
│   │   ├── runner.py
│   │   ├── budgets.py
│   │   ├── hashes.py
│   │   └── result_store.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── mock.py
│   │   └── openai_adapter.py
│   ├── grading/
│   │   ├── base.py
│   │   └── normalization.py
│   └── analysis/
│       └── summary.py
│
├── experiments/
│   ├── tool_selection/
│   │   ├── experiment.yaml
│   │   ├── experiment.py
│   │   ├── grader.py
│   │   ├── fixtures/cases.jsonl
│   │   └── README.md
│   └── _template/README.md
│
├── datasets/
│   ├── catalog.yaml
│   └── cache/                # gitignored external downloads
│
├── docs/
│   ├── architecture.md
│   ├── experiment_protocol.md
│   ├── adding_an_experiment.md
│   └── data_source_research.md
│
├── tests/
│   ├── test_contracts.py
│   ├── test_runner.py
│   ├── test_grader.py
│   ├── test_budget.py
│   └── test_mock_e2e.py
│
├── results/                  # gitignored raw run outputs
└── reports/                  # later: publishable summaries
```

The directory tree is a guide, not a mandate to create empty placeholder files. Prefer **working code over decorative folders**. A new experiment should not require editing the core runner. Keep experiment-specific logic and graders out of `src/eval_lab/core/`.

---

## 7. Minimal shared contracts

Implement simple Pydantic models or typed equivalents for:

- **TestCase:** stable ID, dataset ID/version, task input, ground truth, split, provenance/metadata.
- **Condition:** stable condition ID, independent-variable configuration, model/provider and supported inference settings.
- **ExperimentSpec:** experiment ID/version, research question/hypothesis, primary variable, dataset version, conditions, repeats, seed, limits, grader ID/version.
- **ModelRequest:** messages/input, requested model, tool schemas when relevant, output format, supported model options.
- **ModelResponse:** raw provider payload (sanitized for storage), parsed response/tool calls, finish status, usage, request ID, latency, and error.
- **GradeResult:** pass/fail, score, named submetrics, diagnostics, grader version.
- **RunRecord:** run/case/condition/repeat IDs, hashes, provider/model, raw/parsed output, grade, status/error, usage, estimated cost and latency.
- **RunManifest:** experiment and dataset versions/hashes, Git revision if known, pricing table version, prompt hashes, run limits, environment, start/end timestamps, totals, warnings.

A simple experiment module can expose:

```python
load_cases() -> list[TestCase]
build_request(case: TestCase, condition: Condition) -> ModelRequest
grade(case: TestCase, response: ModelResponse) -> GradeResult
```

It's acceptable to implement these as methods on a small `Experiment` class. **Avoid a plugin SDK or generalized workflow DSL.** Future studies involving multi-step tool execution can extend a small interface after the first vertical slice is proven.

### Grading contract details

For tool selection, grade the actual **structured function/tool call** rather than a natural-language string claiming which tool would be used. Compare:

1. Expected number of calls (including correct **zero-call** behavior).
2. Correct canonical tool name.
3. Correct typed and normalized argument values.
4. Full-call success; separately classify missing, extra, malformed, or invalid calls.

If representation equivalence is allowed (e.g. insignificant whitespace or numeric representation), specify the normalization rule before test execution. **Never let the grader peek at the candidate output and adjust the answer key.**

---

## 8. First experiment: offline `tool_selection` vertical slice

**Research question:** How does the number of available tool schemas affect the accuracy of model tool selection?

### Initial fixture

Author **five tiny business task cases** with exact expected tool calls and argument objects. Examples: invoice lookup, customer status, ticket creation, order search, and a request for which **none** of the offered tools is appropriate.

For the scaffold:

- Three conditions: `tools_5`, `tools_15`, `tools_30`.
- Same user request and target tool schema across conditions for each applicable case.
- Only add distractors; no target renaming or parameter changes.
- Seed tool ordering and preserve offered tool IDs/order in the run record.
- Use one repetition initially: five cases × three conditions = **15 trial records**.
- The mock provider must return a mix of correct, incorrect, and no-call predictions to test the grader. Its outputs must be deterministic for a given input/seed.
- At least one case must be graded as **correct to make no call**.

**Critical control:** For no-call cases, make sure none of the offered tools is an appropriate alternate. Tool counts also change context length; record tool-definition lengths and discuss that confounder in the future real study.

Illustrative config:

```yaml
id: tool_selection
version: 0.1.0
research_question: How does available tool count affect tool-call correctness?
primary_variable: tool_count
dataset:
  id: local-tool-fixtures
  path: experiments/tool_selection/fixtures/cases.jsonl
  version: 0.1.0
conditions:
  - id: tools_5
    tool_count: 5
  - id: tools_15
    tool_count: 15
  - id: tools_30
    tool_count: 30
repetitions: 1
seed: 42
provider: mock
model: deterministic-fixture
max_requests: 15
max_spend_usd: 0
```

**This mock experiment tests the software, not the hypothesis. Do not call its results research evidence.**

---

## 9. CLI and run lifecycle

Implement commands equivalent to:

```bash
uv sync
uv run eval-lab list
uv run eval-lab validate tool_selection
uv run eval-lab run tool_selection --mode mock
uv run eval-lab run tool_selection --dry-run
uv run eval-lab summarize <run_id>
uv run pytest
uv run ruff check .
```

Desired run lifecycle:

1. Load and validate experiment config, data, controls, and grader.
2. Freeze an immutable run manifest including config/dataset/prompt hashes and unique run ID.
3. Produce all case/condition/repetition trials in deterministic order or a recorded seeded randomization.
4. Preflight count, token estimate where feasible, projected spend, live-call permission, and limits. Dry run executes **zero provider calls**.
5. For each trial, build request, call mock or approved provider, retain response/error, normalize output, grade deterministically, and append record immediately.
6. Write aggregate summary with denominators, invalid/failure counts, correct results, latency and available usage/cost statistics.
7. Preserve partial results if execution fails. Do not silently rerun or erase previous attempts.

Recommended storage:

```text
results/<run_id>/
  manifest.json
  records.jsonl
  summary.json
```

No overwriting of existing run IDs. Report provider failures separately from grading errors and task failures; choose and document primary end-to-end success definitions before real studies.

---

## 10. Cost, privacy, and safety

- Default behavior is **offline/dry-run**; model API requests require an explicit `--live`-style opt-in.
- Every live run must supply finite `max_spend_usd`, `max_requests`, and bounded output tokens; reject invalid budgets.
- Use an estimated pricing table with a version/snapshot date and provider-reported usage where available. Record estimates as estimates—not exact bills.
- Stop scheduling new calls as budgets approach. **The cap is best-effort, not a hard billing guarantee**, since usage and billing may only be known after calls complete.
- Run sequentially initially; no unbounded parallelism or implicit retries.
- A future retry policy must be explicit and logged; don't mix retries into controlled treatments silently.
- Read credentials from environment variables. Keep `.env`, downloaded data caches, and raw experiment results out of Git by default.
- Mock/test runs must not require credentials or network access.
- Never send proprietary work, confidential client materials, sensitive user records, or credential-bearing prompts to third-party models.

---

## 11. Public dataset research (deliver a catalog, not bulk ingestion)

Create `datasets/catalog.yaml` and `docs/data_source_research.md`.

Research **official maintainers and authoritative sources**, prioritizing:

1. **Berkeley Function Calling Leaderboard (BFCL):** https://gorilla.cs.berkeley.edu/leaderboard — structured calls, no-call tasks, official grading utilities, available splits, and whether the benchmark can support a controlled tool-count extension without invalidating semantics.
2. **Web Data Commons Products:** https://webdatacommons.org/largescaleproductcorpus/wdc-products/index.html — labeled product/entity matches and manageable sample options.
3. **BIRD Mini-Dev:** https://github.com/bird-bench/mini_dev — text-to-SQL test cases, database files, expected execution grading, prerequisites.
4. **AgentDojo:** https://agentdojo.spylab.ai/ — programmatic task-success/security grading and environment setup; **research only**.
5. **SEC EDGAR/XBRL:** https://www.sec.gov/edgar/sec-api-documentation and https://data.sec.gov/ — optional later financial-data tasks, tagged financial facts and context issues; observe fair-access and license requirements.

For **each** data source, document:

- Official source and maintainers, citations/URLs, last verified date.
- Task relevance and which hypothesis it can test.
- Ground-truth labels and what makes them objectively checkable.
- Dataset format, official version/tag/commit, approximate size, minimal subset.
- License, redistribution restrictions, and commercial/API terms (mark unknown if not verified).
- Download method, local dependencies, expected effort, offline availability.
- Train/dev/test splits, contamination or leakage risks.
- Appropriate deterministic grader and equivalence/ambiguity concerns.
- Approximate model-call volume and cost, with assumptions labeled.
- Verdict: **adopt**, **investigate**, or **defer/reject** with specific rationale.

No large downloads, scraping runs, data redistribution, or paid experiments without project-owner approval. If Codex's environment cannot browse, make the research deliverable a clearly labeled verification checklist; **do not invent the source inspection**.

**Research recommendation expected:** a short table ranking which benchmark is the easiest robust first published study, which is best for FDE relevance, and which is lowest-cost. Source availability and legal conditions matter more than enthusiasm for a particular benchmark.

---

## 12. Protocol for later published studies

Before any paid experiment, author a brief protocol that includes:

- Hypothesis and null hypothesis.
- Experimental unit and the one intended manipulated variable—or label the work as a multi-factor/system comparison.
- Fixed controls, possible confounders, and validity threats.
- Dataset provenance, sample selection, frozen held-out set, and labels.
- Prompt/version and model/inference settings.
- Predefined scoring and error treatment; exact denominator rules.
- Planned repetitions, seeded randomization, cost/request ceiling, and abort criteria.
- Outcome measures: correctness, end-to-end task success, reliability/variability, latency, **cost per correct task**, not only token prices.
- Planned statistical summary: paired differences and uncertainty estimates, accounting for repeated calls per case and, where applicable, questions clustered within the same source.
- Explicit negative/null results and limitations.

Avoid using public benchmark test items as a prompt-development set; protect the final evaluation from iterative tuning.

---

## 13. Phase plan and acceptance criteria

### Phase 0 — Initialize the repository

- Create installable package, `uv` environment/lockfile, `AGENTS.md`, README, `.env.example`, `.gitignore`, and setup scripts only as needed.
- Define architecture and core contracts.

**Accept when:** fresh checkout installs and `eval-lab --help` runs; all current tests pass without network or credentials.

### Phase 1 — Working offline research engine (**must complete before adding experiments**)

- Implement config validation, registry, sequential runner, mock provider, deterministic tool grader, immutable run storage, summary, and cost gates.
- Implement five authored fixture cases × three tool-count conditions.
- Add tests proving scoring catches wrong name, wrong args, extra/missing calls, malformed output, and correct no-call.
- Verify no live request on mock/dry-run paths.

**Accept when:**

1. `uv run eval-lab list` shows `tool_selection`.
2. `uv run eval-lab validate tool_selection` checks all declared inputs.
3. `uv run eval-lab run tool_selection --mode mock` finishes offline, writing **15 trial records** (if fixture/config unchanged).
4. Each record has stable IDs, prediction, ground truth reference, grade, request hash, latency/status, and no fabricated paid-cost amount.
5. A deliberately wrong mock prediction is marked incorrect; a correct no-call is marked correct.
6. `uv run eval-lab summarize <run_id>` reports accurate denominators and outcomes.
7. `uv run pytest` and `uv run ruff check .` pass offline.
8. A failed or interrupted run preserves existing records and reports the failure.
9. New experiments can be added without changing core runner logic.

### Phase 2 — Bounded source discovery

- Complete `datasets/catalog.yaml` and `docs/data_source_research.md`, with official sources and verified or explicitly unverified licensing/versions.
- Recommend an initial real benchmark subset and list any obstacles.

**Accept when:** the owner can choose a dataset based on confirmed objective labels, manageable setup, cost, and license terms. **No bulk dataset ingestion yet.**

### Phase 3 — Real EXP-001 pilot (**not authorized by this handoff**)

- Obtain owner approval on selected benchmark subset, exact provider/model, price assumptions, and pilot spending cap.
- Import the approved subset and validate ground-truth compatibility.
- Run a low-cost pilot and inspect grader behavior and failure categories.
- Freeze a held-out evaluation protocol only after pilot defects are fixed.

**Accept when:** a first verified, programmatically graded result is available with raw records, reproducibility metadata, cost, and documented limitations.

### Phase 4 — Publish and extend (**future work**)

- Produce charts/reports only from actual results, plus a deployment decision and error examples.
- Implement EXP-002/EXP-003 independently using the same core runner.
- Integrate read-only report output with the portfolio site; do not make portfolio visitors run paid API calls.

---

## 14. AGENTS.md guidance for Codex

Write a concise root `AGENTS.md` with these enduring constraints:

- This is an empirical research framework, not an app; protect deterministic grading and experiment isolation.
- Prefer the smallest working implementation, with clear types and high-signal tests.
- New experiment logic belongs in `experiments/<name>`; shared runner remains domain-agnostic.
- All code paths run offline by default; any paid API call needs explicit opt-in and a finite spending limit.
- Never fetch large datasets or commit third-party benchmark files without checking license and owner approval.
- Do not fabricate research findings, scoring outcomes, model usage, or source verification.
- Run tests and linting before reporting completion.
- Record what was implemented, verified, deferred, and any unresolved blockers.

---

## 15. Instructions for Codex's first execution

**Start with Phase 0 and Phase 1.** If convenient, perform Workstream B as documentation-only research in a separate, bounded pass, but **do not let research block the offline vertical slice**.

1. Inspect the repository (expected initially empty).
2. Sketch a minimal architecture in `docs/architecture.md` and validate the contracts.
3. Implement the scaffold and offline `tool_selection` fixture end to end.
4. Run the exact acceptance commands; fix any failing test or incomplete requirement.
5. Commit a usable README and `AGENTS.md` with clear instructions.
6. Write dataset research catalog (verified sources only; mark unknowns).
7. Report: file tree, commands/results, sample run ID, what is complete, what is deferred, and any design tradeoffs made.

**Do not** build a React app, add a SQL database, start a paid model run, implement a full benchmark suite, or invest in generic plugin infrastructure. The highest-priority artifact is a **simple, functional, reproducible research engine**.

---

## 16. Suggested initial Codex prompt (send this after adding the handoff)

> Read `CODEX_HANDOFF.md` in full and treat it as the implementation contract. Implement **Phase 0 and Phase 1**: a minimal Python evaluation framework with offline mock provider, deterministic grading, a working `tool_selection` experiment (five test cases × three conditions), immutable result logging, cost guards, CLI, docs, and passing tests. Keep the architecture small and avoid premature abstraction. Do not call paid APIs or download large datasets. After the framework works, perform the **documentation-only** dataset feasibility review described in Workstream B, verifying official sources where browsing is available and explicitly marking unknowns. Report exactly what is working, the test results, tradeoffs, and what needs owner approval before a real pilot.

**End of handoff.**
