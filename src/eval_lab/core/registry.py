"""Discover trusted repository-local experiments; no runner registration required."""

import importlib.util
import sys
from pathlib import Path
from typing import Protocol

import yaml

from eval_lab.contracts import Condition, ExperimentSpec, GradeResult, ModelRequest, ModelResponse
from eval_lab.contracts import TestCase as Case


class Experiment(Protocol):
    spec: ExperimentSpec
    directory: Path

    def load_cases(self) -> list[Case]: ...
    def validate(self, cases: list[Case]) -> None: ...
    def build_request(self, case: Case, condition: Condition) -> ModelRequest: ...
    def grade(
        self, case: Case, response: ModelResponse, *, request: ModelRequest
    ) -> GradeResult: ...


def discover(root: Path) -> list[str]:
    return sorted(p.parent.name for p in root.glob("*/experiment.yaml"))


def load(name: str, root: Path) -> Experiment:
    if name not in discover(root):
        raise ValueError(f"Unknown experiment {name!r}; available: {discover(root)}")
    directory = (root / name).resolve()
    spec = ExperimentSpec.model_validate(
        yaml.safe_load((directory / "experiment.yaml").read_text())
    )
    if spec.id != name:
        raise ValueError("Experiment ID must match its directory")
    module_name = f"_eval_experiment_{name}"
    module_spec = importlib.util.spec_from_file_location(
        module_name, directory / "experiment.py", submodule_search_locations=[str(directory)]
    )
    if module_spec is None or module_spec.loader is None:
        raise ValueError("Missing experiment.py")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)
    return module.Experiment(spec, directory)
