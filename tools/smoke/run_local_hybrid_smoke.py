#!/usr/bin/env python3
"""Run the first local-hybrid smoke path across sibling repo checkouts.

Expected workspace layout by default:

<workspace-root>/sociosphere
<workspace-root>/agentplane
<workspace-root>/TriTRPC

The script may also be pointed at explicit file paths.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_workspace_root() -> Path:
    return repo_root().parent


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_python_json(script: Path, args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["python3", str(script), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", type=Path, default=default_workspace_root())
    parser.add_argument("--lane", default="tenant")
    parser.add_argument("--resolver-script", type=Path, default=None)
    parser.add_argument("--dispatch-script", type=Path, default=None)
    parser.add_argument("--worker-script", type=Path, default=None)
    parser.add_argument("--capability-descriptor", type=Path, default=None)
    parser.add_argument("--task-plan", type=Path, default=None)
    parser.add_argument("--policy-decision", type=Path, default=None)
    args = parser.parse_args()

    workspace_root = args.workspace_root.resolve()
    agentplane_root = workspace_root / "agentplane"
    tritrpc_root = workspace_root / "TriTRPC"

    resolver_script = args.resolver_script or agentplane_root / "capability-registry" / "resolve_binding_stub.py"
    dispatch_script = args.dispatch_script or agentplane_root / "gateway" / "dispatch_stub.py"
    worker_script = args.worker_script or agentplane_root / "worker-runtime" / "execute_stub.py"
    capability_descriptor = args.capability_descriptor or agentplane_root / "capability-registry" / "examples" / "summarize.abstractive.v1.json"
    fixture_dir = tritrpc_root / "spec" / "slices" / "local_hybrid_v0" / "fixtures" / "remote_allowed_redacted"
    task_plan = args.task_plan or fixture_dir / "task-plan.output.example.json"
    policy_decision = args.policy_decision or fixture_dir / "policy-decision.output.example.json"

    binding = run_python_json(resolver_script, [str(capability_descriptor), "--lane", args.lane])

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        binding_path = tmp / "binding.json"
        binding_path.write_text(json.dumps(binding, indent=2), encoding="utf-8")

        dispatch = run_python_json(dispatch_script, [str(task_plan), str(policy_decision), str(binding_path)])

        worker_request = {
            "taskId": dispatch["taskId"],
            "capabilityInstanceId": dispatch["capabilityInstanceId"],
            "input": dispatch["input"],
            "executionPolicy": {
                "sideEffectsAllowed": false,
                "networkEgressAllowed": false
            }
        }
        worker_request_path = tmp / "worker-request.json"
        worker_request_path.write_text(json.dumps(worker_request, indent=2), encoding="utf-8")

        worker_result = run_python_json(worker_script, [str(worker_request_path)])

    result = {
        "binding": binding,
        "dispatch": dispatch,
        "workerRequest": worker_request,
        "workerResult": worker_result,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
