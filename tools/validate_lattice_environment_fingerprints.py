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
REGISTRY = ROOT / "registry" / "lattice-environment-fingerprints.yaml"
REQUIRED_KINDS = {
    "SystemFingerprint",
    "UserEnvironmentFingerprint",
    "AgentEnvironmentFingerprint",
    "ReleaseSetFingerprint",
    "ArtifactFingerprint",
    "PolicyFingerprint",
    "TenantWorkspaceFingerprint",
    "RollbackFingerprint",
}
REQUIRED_BINDINGS = {"release", "execution", "catalog_ingestion", "rollback"}
REQUIRED_RECEIPTS = {
    "deployment-receipt",
    "execution-receipt",
    "rollback-receipt",
    "evidence-bundle-receipt",
    "compliance-receipt",
}
REQUIRED_RECEIPT_FIELDS = {
    "fingerprint_ref",
    "fingerprint_digest",
    "policy_decision_ref",
    "topology_ref",
    "actor_ref",
    "timestamp",
}


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


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for environment fingerprint validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeEnvironmentFingerprintRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = require_mapping(data.get("umbrella"), "umbrella")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella issue mismatch")
        require(umbrella.get("work_order") == "work-order-0", "work order mismatch")
        require(umbrella.get("release_rollback_controls_ref") == "registry/lattice-release-rollback-controls.yaml", "release rollback ref mismatch")

        kinds = as_list(data.get("fingerprint_kinds"), "fingerprint_kinds")
        kind_ids = {item.get("id") for item in kinds if isinstance(item, dict)}
        require(kind_ids == REQUIRED_KINDS, f"fingerprint kind ids mismatch: {kind_ids}")
        for item in kinds:
            item = require_mapping(item, "fingerprint kind")
            require("owner_repo" in item, f"{item.get('id')} missing owner_repo")
            fields = set(as_list(item.get("required_fields"), f"{item.get('id')}.required_fields"))
            require("generated_at" in fields, f"{item.get('id')} missing generated_at")
            if item.get("id") != "ArtifactFingerprint":
                require("digest" in fields, f"{item.get('id')} missing digest")
        by_id = {item["id"]: item for item in kinds if isinstance(item, dict)}
        require("measured_boot_digest" in by_id["SystemFingerprint"].get("required_fields", []), "SystemFingerprint missing measured_boot_digest")
        require("isolation_profile_ref" in by_id["AgentEnvironmentFingerprint"].get("required_fields", []), "AgentEnvironmentFingerprint missing isolation profile")
        require("previous_release_ref" in by_id["RollbackFingerprint"].get("required_fields", []), "RollbackFingerprint missing previous release")
        require("rbac_policy_ref" in by_id["TenantWorkspaceFingerprint"].get("required_fields", []), "TenantWorkspaceFingerprint missing RBAC policy")

        rules = require_mapping(data.get("fingerprint_rules"), "fingerprint_rules")
        for key in [
            "content_address_required",
            "canonical_json_required",
            "actor_ref_required_for_mutating_fingerprints",
            "generated_at_required",
            "policy_decision_ref_required_for_execution_and_release",
            "topology_ref_required_for_release_and_rollback",
        ]:
            require(rules.get(key) is True, f"fingerprint_rules.{key} must be true")
        require(rules.get("digest_algorithm") == "sha256", "digest algorithm mismatch")
        require(rules.get("digest_prefix") == "sha256:", "digest prefix mismatch")

        bindings = require_mapping(data.get("provenance_bindings"), "provenance_bindings")
        require(set(bindings) == REQUIRED_BINDINGS, f"provenance bindings mismatch: {set(bindings)}")
        for key, binding in bindings.items():
            binding = require_mapping(binding, f"provenance_bindings.{key}")
            required = set(as_list(binding.get("required_fingerprints"), f"{key}.required_fingerprints"))
            require(required <= REQUIRED_KINDS, f"{key} contains unknown fingerprint kinds")
        require("ReleaseSetFingerprint" in bindings["release"]["required_fingerprints"], "release binding missing ReleaseSetFingerprint")
        require("AgentEnvironmentFingerprint" in bindings["execution"]["required_fingerprints"], "execution binding missing AgentEnvironmentFingerprint")
        require("TenantWorkspaceFingerprint" in bindings["catalog_ingestion"]["required_fingerprints"], "catalog binding missing TenantWorkspaceFingerprint")
        require("RollbackFingerprint" in bindings["rollback"]["required_fingerprints"], "rollback binding missing RollbackFingerprint")

        receipts = require_mapping(data.get("receipt_links"), "receipt_links")
        receipt_fields = set(as_list(receipts.get("required_receipt_fields"), "receipt_links.required_receipt_fields"))
        missing_fields = sorted(REQUIRED_RECEIPT_FIELDS - receipt_fields)
        require(not missing_fields, f"missing receipt fields: {missing_fields}")
        receipt_types = set(as_list(receipts.get("receipt_types"), "receipt_links.receipt_types"))
        missing_receipts = sorted(REQUIRED_RECEIPTS - receipt_types)
        require(not missing_receipts, f"missing receipt types: {missing_receipts}")

        validation = require_mapping(data.get("validation_requirements"), "validation_requirements")
        for key in [
            "require_fingerprint_kinds",
            "require_required_fields",
            "require_fingerprint_rules",
            "require_provenance_bindings",
            "require_receipt_links",
            "require_sha256_digest_prefix",
            "require_policy_decision_binding",
            "require_topology_binding_for_release_and_rollback",
            "forbid_mutating_receipts_without_actor",
        ]:
            require(validation.get(key) is True, f"validation {key} must be true")
    except Exception as exc:
        return fail(str(exc))
    print("OK: validated Lattice environment fingerprints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
