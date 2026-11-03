import json
import os
from pathlib import Path

from pydantic import TypeAdapter

from eval_lab.contracts import Identifier, RunRecord
from eval_lab.core.hashes import canonical


def run_path(root: Path, run_id: str) -> Path:
    TypeAdapter(Identifier).validate_python(run_id)
    return root / run_id


def write_once(path: Path, value) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(canonical(value) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


class ResultStore:
    def __init__(self, root: Path, run_id: str):
        self.path = run_path(root, run_id)
        self.path.mkdir(parents=True, exist_ok=False)
        (self.path / "records.jsonl").touch(exist_ok=False)

    def append(self, record: RunRecord) -> None:
        with (self.path / "records.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(canonical(record) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    def write(self, filename: str, value) -> None:
        write_once(self.path / filename, value)


def read_records(path: Path) -> tuple[list[RunRecord], list[str]]:
    records, warnings = [], []
    data = (path / "records.jsonl").read_bytes()
    lines = data.splitlines(keepends=True)
    for index, line in enumerate(lines):
        try:
            records.append(RunRecord.model_validate(json.loads(line)))
        except (ValueError, UnicodeDecodeError):
            if index == len(lines) - 1 and not line.endswith(b"\n"):
                warnings.append("Ignored torn final record; run may have been interrupted")
            else:
                raise
    return records, warnings
