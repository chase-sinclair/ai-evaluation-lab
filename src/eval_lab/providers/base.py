from typing import Protocol

from eval_lab.contracts import ModelRequest, ModelResponse


class Provider(Protocol):
    def generate(self, request: ModelRequest) -> ModelResponse: ...
