#!/usr/bin/env python3
"""Run the first full seven-step local-hybrid smoke path across sibling repo checkouts."""

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
    args = parser.parse_args()

    workspace_root = args.workspace_root.resolve()
    agentplane_root = workspace_root / "agentplane"
    tritrpc_root = workspace_root / "TriTRPC"

    resolver_script = agentplane_root / "capability-registry" / "resolve_binding_stub.py"
    dispatch_script = agentplane_root / "gateway" / "dispatch_stub.py"
    worker_script = agentplane_root / "worker-runtime" / "execute_stub.py"
    evidence_script = agentplane_root / "evidence" / "append_event_stub.py"
    replay_script = agentplane_root / "replay" / "materialize_cairn_stub.py"
    capability_descriptor = agentplane_root / "capability-registry" / "examples" / "summarize.abstractive.v1.json"
    fixture_dir = tritrpc_root / "spec" / "slices" / "local_hybrid_v0" / "fixtures" / "remote_allowed_redacted"
    task_plan = fixture_dir / "task-plan.output.example.json"
    policy_decision = fixture_dir / "policy-decision.output.example.json"

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
                "sideEffectsAllowed": False,
                "networkEgressAllowed": False,
            },
        }
        worker_request_path = tmp / "worker-request.json"
        worker_request_path.write_text(json.dumps(worker_request, indent=2), encoding="utf-8")

        worker_result = run_python_json(worker_script, [str(worker_request_path)])

        evidence_request = {
            "event": {
                "eventId": "urn:uuid:stub-event-01",
                "parentEventId": "urn:uuid:stub-parent-00",
                "sessionId": "sess_01",
                "taskId": worker_result["taskId"],
                "actor": {"kind": "human", "id": "user:local"},
                "capability": "summarize.abstractive.v1",
                "policyHash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
                "executionLane": binding["binding"]["executionLane"],
                "workerId": worker_result["provenance"]["workerId"],
                "modelId": worker_result["provenance"]["modelId"],
                "toolchain": worker_result["provenance"]["toolchain"],
                "zoneCrossings": ["device->tenant", "tenant->device"],
                "inputDigest": worker_result["provenance"]["inputDigest"],
                "outputDigest": worker_result["provenance"]["outputDigest"],
                "artifactRefs": [],
                "startedAt": "2026-04-06T00:00:01Z",
                "finishedAt": "2026-04-06T00:00:03Z",
                "journalOffset": None,
                "cairnId": None
            }
        }
        evidence_request_path = tmp / "evidence-request.json"
        evidence_request_path.write_text(json.dumps(evidence_request, indent=2), encoding="utf-8")
        evidence_result = run_python_json(evidence_script, [str(evidence_request_path)])

        replay_request = {
            "taskId": worker_result["taskId"],
            "journalOffset": evidence_result["journalOffset"],
            "materializeArtifacts": True
        }
        replay_request_path = tmp / "replay-request.json"
        replay_request_path.write_text(json.dumps(replay_request, indent=2), encoding="utf-8")
        replay_result = run_python_json(replay_script, [str(replay_request_path)])

    result = {
        "binding": binding,
        "dispatch": dispatch,
        "workerRequest": worker_request,
        "workerResult": worker_result,
        "evidenceRequest": evidence_request,
        "evidenceResult": evidence_result,
        "replayRequest": replay_request,
        "replayResult": replay_result,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
