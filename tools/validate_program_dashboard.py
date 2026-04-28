#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "program-dashboard-rollup.example.json"
REQUIRED_WORKSTREAMS = {
    "Release/Install",
    "SourceOS Carry",
    "Prophet CLI",
    "Holmes",
    "Platform Registry",
    "Agent Execution",
    "DevSecOps Intelligence",
    "SourceOS Boot/Spec",
    "Labs/MLOps",
    "Web/UI",
    "Policy Fabric",
    "Alexandrian Academy",
}
REQUIRED_FIELDS = {
    "workstream",
    "percentComplete",
    "basis",
    "lastMergedPR",
    "activeIssueRefs",
    "activePRRefs",
    "currentBlockers",
    "nextAction",
    "timeToFirstActionMs",
    "timeToMergeMs",
    "turnsToCompletion",
    "agentHandoffCount",
    "validationStatus",
    "mergeGateStatus",
}
ALLOWED_STATUS = {"pass", "warn", "fail", "not-evaluated"}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if not EXAMPLE.exists():
        return fail(f"missing {EXAMPLE}")
    data = json.loads(EXAMPLE.read_text())
    if data.get("apiVersion") != "sociosphere.socioprophet.dev/v1":
        return fail("apiVersion must be sociosphere.socioprophet.dev/v1")
    if data.get("kind") != "ProgramDashboardRollup":
        return fail("kind must be ProgramDashboardRollup")
    spec = data.get("spec", {})
    program_percent = int(spec.get("programPercentComplete", -1))
    if not 0 <= program_percent <= 100:
        return fail("spec.programPercentComplete must be 0..100")
    workstreams = spec.get("workstreams", [])
    if not workstreams:
        return fail("spec.workstreams must not be empty")
    names = set()
    for idx, record in enumerate(workstreams):
        prefix = f"workstreams[{idx}]"
        missing = sorted(REQUIRED_FIELDS - set(record))
        if missing:
            return fail(f"{prefix} missing fields: {missing}")
        name = record["workstream"]
        if name in names:
            return fail(f"duplicate workstream: {name}")
        names.add(name)
        percent = int(record["percentComplete"])
        if not 0 <= percent <= 100:
            return fail(f"{prefix}.percentComplete must be 0..100")
        for list_field in ["activeIssueRefs", "activePRRefs", "currentBlockers"]:
            if not isinstance(record[list_field], list):
                return fail(f"{prefix}.{list_field} must be a list")
        for field in ["timeToFirstActionMs", "timeToMergeMs", "turnsToCompletion", "agentHandoffCount"]:
            if int(record[field]) < 0:
                return fail(f"{prefix}.{field} must be non-negative")
        if record["validationStatus"] not in ALLOWED_STATUS:
            return fail(f"{prefix}.validationStatus is invalid")
        if record["mergeGateStatus"] not in ALLOWED_STATUS:
            return fail(f"{prefix}.mergeGateStatus is invalid")
        if not str(record["basis"]).strip():
            return fail(f"{prefix}.basis is required")
        if not str(record["nextAction"]).strip():
            return fail(f"{prefix}.nextAction is required")
    missing_workstreams = sorted(REQUIRED_WORKSTREAMS - names)
    if missing_workstreams:
        return fail(f"missing required workstreams: {missing_workstreams}")
    print(f"OK: validated {len(workstreams)} program dashboard workstreams")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
