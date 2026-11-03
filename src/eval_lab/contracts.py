"""Versioned, explicit boundaries between experiments, providers, and storage."""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$", max_length=120)]
PositiveInt = Annotated[int, Field(strict=True, gt=0)]
Money = Annotated[float, Field(ge=0, allow_inf_nan=False)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class TestCase(Contract):
    __test__ = False
    id: Identifier
    dataset_id: Identifier
    dataset_version: str
    task_input: dict[str, Any]
    ground_truth: dict[str, Any]
    split: str
    provenance: dict[str, Any]


class Condition(Contract):
    id: Identifier
    variables: dict[str, Any]
    provider: Literal["mock", "openai"] = "mock"
    model: str = "deterministic-fixture"
    options: dict[str, Any] = Field(default_factory=dict)


class Dataset(Contract):
    id: Identifier
    version: str
    path: str


class Pricing(Contract):
    version: str
    verified_date: str
    source_url: str
    model: str
    input_usd_per_million: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    output_usd_per_million: Annotated[float, Field(gt=0, allow_inf_nan=False)]


class ExperimentSpec(Contract):
    id: Identifier
    version: str
    research_question: str
    hypothesis: str
    primary_variable: str
    dataset: Dataset
    conditions: Annotated[list[Condition], Field(min_length=1)]
    repetitions: PositiveInt = 1
    seed: int = 42
    max_requests: PositiveInt
    max_spend_usd: Money = 0
    max_output_tokens: Annotated[int, Field(strict=True, ge=16)] = 256
    grader_id: str
    grader_version: str
    pricing: Pricing | None = None

    @model_validator(mode="after")
    def unique_conditions(self):
        if len({c.id for c in self.conditions}) != len(self.conditions):
            raise ValueError("Condition IDs must be unique")
        for condition in self.conditions:
            if self.primary_variable not in condition.variables:
                raise ValueError("Each condition must declare the primary variable")
        return self


class ModelRequest(Contract):
    """text -> parsed string; tool_calls -> parsed dict with tool_calls and optional text.

    output_format selects local normalization, not provider JSON-schema mode.
    Text-only requests cannot offer tools. Raw output is retained for both formats.
    """

    model: str
    messages: list[dict[str, str]]
    tools: list[dict[str, Any]] = Field(default_factory=list)
    output_format: Literal["tool_calls", "text"] = "tool_calls"
    options: dict[str, Any] = Field(default_factory=dict)
    max_output_tokens: Annotated[int, Field(strict=True, ge=16)] = 256

    @model_validator(mode="after")
    def text_without_tools(self):
        if self.output_format == "text" and self.tools:
            raise ValueError("Text-only requests cannot offer tools")
        return self


class Usage(Contract):
    input_tokens: Annotated[int, Field(strict=True, ge=0)]
    output_tokens: Annotated[int, Field(strict=True, ge=0)]


class ModelResponse(Contract):
    raw: dict[str, Any] = Field(default_factory=dict)
    parsed: Any = None
    finish_status: str = "completed"
    usage: Usage | None = None
    request_id: str | None = None
    model: str | None = None
    effective_options: dict[str, Any] = Field(default_factory=dict)
    latency_ms: Annotated[float, Field(ge=0)] = 0
    error: str | None = None


class GradeResult(Contract):
    passed: bool
    valid_output: bool = True
    score: Annotated[float, Field(ge=0, le=1)]
    submetrics: dict[str, bool | float] = Field(default_factory=dict)
    diagnostics: list[str] = Field(default_factory=list)
    grader_version: str


class RunRecord(Contract):
    run_id: Identifier
    trial_id: str
    case_id: Identifier
    condition_id: Identifier
    repeat: int
    dataset_id: str
    dataset_version: str
    ground_truth_ref: str
    ground_truth: dict[str, Any]
    request_hash: str
    prompt_hash: str
    request: ModelRequest
    provider: str
    model: str
    offered_tool_ids: list[str]
    tool_definition_bytes: int
    estimated_input_tokens: int
    response: ModelResponse
    grade: GradeResult | None
    status: Literal[
        "passed", "task_failed", "invalid_output", "provider_error", "grader_error", "interrupted"
    ]
    error: str | None = None
    estimated_cost_usd: Money | None
    cost_basis: str


class RunManifest(Contract):
    run_id: Identifier
    experiment: ExperimentSpec
    mode: str
    config_hash: str
    dataset_hash: str
    source_hashes: dict[str, str]
    git_revision: str | None
    git_dirty: bool | None
    pricing_version: str
    prompt_hashes: list[str]
    request_hashes: list[str]
    environment: dict[str, str]
    started_at: str
    ended_at: str | None = None
    planned_trials: int
    projected_cost_usd: Money
    status: str = "running"
    totals: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None
