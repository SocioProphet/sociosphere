#!/usr/bin/env python3
"""Validate EdgeHostLifecycleBinding fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/edge/edge_host_lifecycle_binding.v1.schema.json"
FIXTURE = ROOT / "fixtures/edge/sourceos-nlboot-kubeedge-binding.sample.v1.json"
REQUIRED = [
    "record_version",
    "binding_id",
    "edge_node_id",
    "site_ref",
    "fleet_ref",
    "workspace_ref",
    "device_claim_ref",
    "host_identity_ref",
    "attestation_ref",
    "sourceos_release_set_ref",
    "nlboot_boot_release_set_ref",
    "recovery_policy_ref",
    "rollback_plan_ref",
    "enrollment_state",
    "validated_at",
    "policy_bundle_refs",
    "evidence_refs",
    "classification",
]
KUBEEDGE_REQUIRED = [
    "role",
    "version",
    "topology_ref",
    "autonomy_policy_ref",
    "workload_policy_ref",
    "partition_behavior",
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"top-level object required: {path}")
    return value


def main() -> int:
    schema = load_json(SCHEMA)
    fixture = load_json(FIXTURE)
    declared = set(schema.get("required", []))
    for field in REQUIRED:
        if field not in declared:
            fail(f"schema missing required field: {field}")
        if field not in fixture:
            fail(f"fixture missing required field: {field}")
    if fixture["record_version"] != "v1":
        fail("record_version must be v1")
    if not fixture.get("policy_bundle_refs"):
        fail("policy_bundle_refs must be non-empty")
    if not fixture.get("evidence_refs"):
        fail("evidence_refs must be non-empty")
    kubeedge = fixture.get("kubeedge")
    if isinstance(kubeedge, dict) and kubeedge.get("selected") is True:
        for field in KUBEEDGE_REQUIRED:
            if not kubeedge.get(field):
                fail(f"kubeedge selected but missing {field}")
    print("edge host lifecycle binding passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
