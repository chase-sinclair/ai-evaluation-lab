import socket
from pathlib import Path

import pytest

from eval_lab.core.registry import load

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def no_network_or_credentials(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def blocked(*args, **kwargs):
        raise AssertionError("Network is forbidden in tests")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)


@pytest.fixture
def experiment():
    return load("tool_selection", ROOT / "experiments")


@pytest.fixture
def cases(experiment):
    return {c.id: c for c in experiment.load_cases()}
