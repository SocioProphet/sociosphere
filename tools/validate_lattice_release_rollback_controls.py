#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "lattice-release-rollback-controls.yaml"
REQUIRED_OBJECTS = {"ReleaseSet", "BootReleaseSet", "RollbackReceipt"}
REQUIRED_CHANNELS = {"dev", "demo", "staging", "stable"}
REQUIRED_PROMOTION_STATES = {"draft", "built", "signed", "assigned", "deployed", "attested", "compliant", "promoted", "held", "rolled-back"}
REQUIRED_BLOCKERS = {"ci-failure", "policy-deny", "topology-missing", "rollback-path-unhealthy", "release-evidence-missing", "owner-approval-missing"}
REQUIRED_PROMOTION_RECEIPTS = {"build-receipt", "validation-receipt", "signature-receipt", "assignment-receipt", "deployment-receipt", "attestation-receipt", "compliance-receipt", "promotion-receipt"}
REQUIRED_ROLLBACK_TRIGGERS = {"failed-health-check", "failed-policy-check", "failed-attestation", "artifact-integrity-failure", "security-incident", "operator-rollback-request"}
REQUIRED_ROLLBACK_RECEIPTS = {"rollback-receipt", "previous-release-ref", "target-release-ref", "policy-decision-ref", "incident-or-change-ref", "post-rollback-health-receipt"}
REQUIRED_LOOP_OBSERVES = {"validation-status", "health-status", "attestation-status", "compliance-status", "rollback-path-health"}
REQUIRED_LOOP_DECIDES = {"promote", "hold", "rollback", "require-review"}
REQUIRED_LOOP_ACTS = {"assign-release-set", "block-release-set", "rollback-release-set", "open-incident"}


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def as_list(value: Any, field: str) -> list[Any]:
    require(isinstance(value, list) and value, f"{field} must be non-empty list")
    return value


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{field} must be mapping")
    return value


def require_contains(value: Any, required: set[str], field: str) -> None:
    actual = set(as_list(value, field))
    missing = sorted(required - actual)
    require(not missing, f"{field} missing {missing}")


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for release rollback controls validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeReleaseRollbackControlsRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = require_mapping(data.get("umbrella"), "umbrella")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella issue mismatch")
        require(umbrella.get("work_order") == "work-order-0", "work order mismatch")
        require(umbrella.get("observability_sre_ref") == "registry/lattice-observability-sre.yaml", "observability ref mismatch")

        objects = as_list(data.get("release_objects"), "release_objects")
        object_ids = {item.get("id") for item in objects if isinstance(item, dict)}
        require(object_ids == REQUIRED_OBJECTS, f"release objects mismatch: {object_ids}")
        objects_by_id = {item["id"]: item for item in objects if isinstance(item, dict)}
        for object_id, item in objects_by_id.items():
            require_mapping(item, f"release_objects.{object_id}")
            require("owner_repo" in item, f"{object_id} missing owner_repo")
            as_list(item.get("required_fields"), f"{object_id}.required_fields")
        require("release_set_id" in objects_by_id["ReleaseSet"].get("required_fields", []), "ReleaseSet missing release_set_id")
        require("signed_boot_manifest_ref" in objects_by_id["BootReleaseSet"].get("required_fields", []), "BootReleaseSet missing signed manifest")
        for field in ["previous_release_ref", "target_release_ref", "policy_decision_ref", "change_or_incident_ref"]:
            require(field in objects_by_id["RollbackReceipt"].get("required_fields", []), f"RollbackReceipt missing {field}")

        channels = as_list(data.get("channels"), "channels")
        channel_ids = {item.get("id") for item in channels if isinstance(item, dict)}
        require(channel_ids == REQUIRED_CHANNELS, f"channel ids mismatch: {channel_ids}")
        stable = next(item for item in channels if item.get("id") == "stable")
        stable_requirements = set(as_list(stable.get("promotion_requires"), "stable.promotion_requires"))
        for gate in ["signed-release-set", "runtime-release-evidence", "policy-fabric-allow-decision", "rollback-receipt-template-present", "owner-approval-present"]:
            require(gate in stable_requirements, f"stable promotion missing {gate}")

        promotion = require_mapping(data.get("promotion_flow"), "promotion_flow")
        require_contains(promotion.get("states"), REQUIRED_PROMOTION_STATES, "promotion_flow.states")
        require_contains(promotion.get("blockers"), REQUIRED_BLOCKERS, "promotion_flow.blockers")
        require_contains(promotion.get("required_receipts"), REQUIRED_PROMOTION_RECEIPTS, "promotion_flow.required_receipts")

        rollback = require_mapping(data.get("rollback_flow"), "rollback_flow")
        require_contains(rollback.get("triggers"), REQUIRED_ROLLBACK_TRIGGERS, "rollback_flow.triggers")
        targets = require_mapping(rollback.get("rollback_targets"), "rollback_flow.rollback_targets")
        for key in ["system_plane", "user_plane", "agent_plane", "release_assignment"]:
            require(key in targets, f"rollback target missing {key}")
        require_contains(rollback.get("required_receipts"), REQUIRED_ROLLBACK_RECEIPTS, "rollback_flow.required_receipts")
        require(rollback.get("rollback_health_required_before_promotion") is True, "rollback health must be required before promotion")

        receipts = require_mapping(data.get("receipt_controls"), "receipt_controls")
        for key in ["immutable_once_written", "content_address_required", "actor_ref_required", "timestamp_required", "policy_decision_ref_required", "topology_ref_required", "proof_store_required"]:
            require(receipts.get(key) is True, f"receipt_controls.{key} must be true")

        loop = require_mapping(data.get("cybernetic_release_loop"), "cybernetic_release_loop")
        require_contains(loop.get("observes"), REQUIRED_LOOP_OBSERVES, "cybernetic_release_loop.observes")
        require_contains(loop.get("decides"), REQUIRED_LOOP_DECIDES, "cybernetic_release_loop.decides")
        require_contains(loop.get("acts"), REQUIRED_LOOP_ACTS, "cybernetic_release_loop.acts")

        validation = require_mapping(data.get("validation_requirements"), "validation_requirements")
        for key in [
            "require_release_objects",
            "require_channels",
            "require_promotion_flow",
            "require_rollback_flow",
            "require_receipt_controls",
            "require_cybernetic_release_loop",
            "require_rollback_health_before_promotion",
            "require_policy_decision_ref_for_release_action",
            "require_previous_release_ref_for_rollback",
            "require_proof_store_for_receipts",
        ]:
            require(validation.get(key) is True, f"validation {key} must be true")
    except Exception as exc:
        return fail(str(exc))
    print("OK: validated Lattice release rollback controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
