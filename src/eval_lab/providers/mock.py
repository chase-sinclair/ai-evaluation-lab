"""Deterministic software-test double. Reads requests, never answer keys."""

import re

from eval_lab.contracts import ModelRequest, ModelResponse
from eval_lab.core.hashes import digest


class MockProvider:
    def __init__(self, seed: int):
        self.seed = seed

    def generate(self, request: ModelRequest) -> ModelResponse:
        text = request.messages[-1]["content"]
        calls = []
        if match := re.search(r"invoice (INV-\d+)", text):
            calls = [{"name": "lookup_invoice", "arguments": {"invoice_id": match[1]}}]
        elif match := re.search(r"customer (CUS-\d+)", text):
            calls = [{"name": "customer_status", "arguments": {"customer_id": match[1]}}]
        elif "Create a support ticket" in text:
            calls = [
                {
                    "name": "create_ticket",
                    "arguments": {
                        "title": "Printer offline",
                        "priority": "low",  # Deliberate wrong argument.
                    },
                }
            ]
        elif match := re.search(r"orders for (CUS-\d+)", text):
            calls = [{"name": "search_orders", "arguments": {"customer_id": match[1], "limit": 2}}]
            if len(request.tools) >= 15:
                calls[0]["name"] = "customer_status"  # Deliberate wrong name.
        return ModelResponse(
            raw={"fixture_provider": True, "tool_calls": calls},
            parsed={"tool_calls": calls},
            request_id=f"mock-{digest([request.model_dump(), self.seed])[:20]}",
            model=request.model,
            effective_options={"seed": self.seed},
        )
