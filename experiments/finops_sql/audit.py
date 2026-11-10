"""Run the same isolated worker for each arm of the offline reference audit."""

import json
import subprocess


def sandbox(snapshot, queries):
    cmd = [
        "docker",
        "run",
        "--rm",
        "-i",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "64",
        "--memory",
        "512m",
        "--memory-swap",
        "512m",
        "--cpus",
        "1",
        "--mount",
        f"type=bind,source={(snapshot / 'warehouse.db').resolve()},target=/warehouse.db,readonly",
        "meridian-worker:checkpoint1",
    ]
    result = subprocess.run(
        cmd,
        input=json.dumps(queries),
        capture_output=True,
        text=True,
        check=True,
        timeout=10 * len(queries) + 60,
    )
    return json.loads(result.stdout)
