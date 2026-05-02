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
REGISTRY = ROOT / "registry" / "lattice-security-isolation-model.yaml"
REQUIRED_SCOPE = {"system-plane", "lifecycle-plane", "user-plane", "agent-plane", "shell-plane", "control-plane-site", "artifact-services"}
REQUIRED_THREATS = {
    "prompt-injection-to-tool-misuse",
    "untrusted-artifact-processing",
    "secret-exposure",
    "lateral-movement-across-workspaces",
    "runtime-escape",
    "supply-chain-drift",
    "policy-bypass",
    "unauthorized-network-egress",
}
REQUIRED_PROFILES = {"container", "vm", "layered-vm-container", "microvm-mesh"}
REQUIRED_RISK_LEVELS = {"low", "medium", "high", "extreme"}
REQUIRED_SECRET_FORBIDDEN = {"git-repository", "nix-store", "build-logs", "command-output", "image-layers"}
REQUIRED_NETWORK_MODES = {"none", "control-plane-only", "restricted-egress", "full-egress-with-policy-exception"}
REQUIRED_FORBIDDEN_MOUNTS = {"host-root", "docker-socket", "unmanaged-secret-store"}
REQUIRED_SUPPLY_ARTIFACTS = {"ReleaseSet", "BillOfMaterials", "signed-manifest", "runtime-promotion-manifest", "verification-receipt"}
REQUIRED_INCIDENT_RECEIPTS = {"incident-receipt", "policy-impact-receipt", "runtime-impact-receipt", "tenant-impact-receipt", "secret-impact-receipt", "network-impact-receipt", "post-incident-review"}


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
        return fail("PyYAML is required for security isolation validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeSecurityIsolationModelRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = require_mapping(data.get("umbrella"), "umbrella")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella issue mismatch")
        require(umbrella.get("work_order") == "work-order-0", "work order mismatch")
        require(umbrella.get("deployment_topology_ref") == "registry/lattice-deployment-topology.yaml", "deployment topology ref mismatch")

        scope = require_mapping(data.get("security_scope"), "security_scope")
        applies = set(as_list(scope.get("applies_to"), "security_scope.applies_to"))
        require(REQUIRED_SCOPE <= applies, f"security scope incomplete: {sorted(REQUIRED_SCOPE - applies)}")

        threats = as_list(data.get("threat_classes"), "threat_classes")
        threat_ids = {item.get("id") for item in threats if isinstance(item, dict)}
        require(threat_ids == REQUIRED_THREATS, f"threat class mismatch: {threat_ids}")
        for item in threats:
            require_mapping(item, "threat class")
            require("minimum_control" in item, f"threat {item.get('id')} missing minimum_control")
            require("required_evidence" in item, f"threat {item.get('id')} missing required_evidence")

        profiles = as_list(data.get("isolation_profiles"), "isolation_profiles")
        profile_ids = {item.get("id") for item in profiles if isinstance(item, dict)}
        require(profile_ids == REQUIRED_PROFILES, f"profile ids mismatch: {profile_ids}")
        profiles_by_id = {item["id"]: item for item in profiles if isinstance(item, dict)}
        for profile_id, item in profiles_by_id.items():
            as_list(item.get("allowed_for"), f"{profile_id}.allowed_for")
            controls = set(as_list(item.get("minimum_controls"), f"{profile_id}.minimum_controls"))
            require(controls, f"{profile_id} controls missing")
        require("no-network-by-default" in profiles_by_id["microvm-mesh"]["minimum_controls"], "microvm must default to no network")
        require("evidence-bundle-required" in profiles_by_id["microvm-mesh"]["minimum_controls"], "microvm must require evidence bundle")

        risk = require_mapping(data.get("risk_to_isolation"), "risk_to_isolation")
        require(set(risk) == REQUIRED_RISK_LEVELS, f"risk levels mismatch: {set(risk)}")
        require(risk["low"].get("minimum_profile") == "container", "low risk profile mismatch")
        require(risk["medium"].get("minimum_profile") == "vm", "medium risk profile mismatch")
        require(risk["high"].get("minimum_profile") == "microvm-mesh", "high risk profile mismatch")
        require(risk["extreme"].get("minimum_profile") == "microvm-mesh", "extreme risk profile mismatch")
        require(risk["high"].get("network_default") == "none", "high risk network default must be none")
        require(risk["extreme"].get("network_default") == "none", "extreme risk network default must be none")

        controls = require_mapping(data.get("security_controls"), "security_controls")
        secrets = require_mapping(controls.get("secrets"), "security_controls.secrets")
        require(secrets.get("model") == "secret-door-required", "secret model mismatch")
        forbidden = set(as_list(secrets.get("forbidden_locations"), "secrets.forbidden_locations"))
        require(REQUIRED_SECRET_FORBIDDEN <= forbidden, f"secret forbidden locations incomplete: {sorted(REQUIRED_SECRET_FORBIDDEN - forbidden)}")
        network = require_mapping(controls.get("network"), "security_controls.network")
        require(network.get("default_posture") == "deny-by-default-for-agent-space", "network default mismatch")
        modes = set(as_list(network.get("allowed_modes"), "network.allowed_modes"))
        require(REQUIRED_NETWORK_MODES <= modes, f"network modes incomplete: {sorted(REQUIRED_NETWORK_MODES - modes)}")
        fs = require_mapping(controls.get("filesystem"), "security_controls.filesystem")
        mounts = set(as_list(fs.get("forbidden_mounts"), "filesystem.forbidden_mounts"))
        require(REQUIRED_FORBIDDEN_MOUNTS <= mounts, f"forbidden mounts incomplete: {sorted(REQUIRED_FORBIDDEN_MOUNTS - mounts)}")
        runtime = require_mapping(controls.get("runtime"), "security_controls.runtime")
        runtime_receipts = set(as_list(runtime.get("required_receipts"), "runtime.required_receipts"))
        for receipt in ["environment-fingerprint", "capability-manifest", "isolation-profile-receipt"]:
            require(receipt in runtime_receipts, f"runtime receipt missing {receipt}")
        supply = require_mapping(controls.get("supply_chain"), "security_controls.supply_chain")
        supply_artifacts = set(as_list(supply.get("required_artifacts"), "supply_chain.required_artifacts"))
        require(REQUIRED_SUPPLY_ARTIFACTS <= supply_artifacts, f"supply artifacts incomplete: {sorted(REQUIRED_SUPPLY_ARTIFACTS - supply_artifacts)}")

        policy = require_mapping(data.get("policy_enforcement"), "policy_enforcement")
        require(policy.get("policy_owner") == "SocioProphet/policy-fabric", "policy owner mismatch")
        require(policy.get("execution_owner") == "SocioProphet/agentplane", "execution owner mismatch")
        require(policy.get("topology_owner") == "SocioProphet/sociosphere", "topology owner mismatch")
        rules = require_mapping(policy.get("rules"), "policy_enforcement.rules")
        for key in [
            "policy_required_before_authoritative_action",
            "agentplane_required_before_execution",
            "topology_required_before_production_registration",
            "generated_only_release_to_stable_forbidden",
            "secret_access_requires_secret_door",
            "high_risk_workloads_require_microvm_mesh",
        ]:
            require(rules.get(key) is True, f"policy rule {key} must be true")

        incident = require_mapping(data.get("incident_security_receipts"), "incident_security_receipts")
        receipts = set(as_list(incident.get("required_for_security_incident"), "incident_security_receipts.required_for_security_incident"))
        require(REQUIRED_INCIDENT_RECEIPTS <= receipts, f"incident receipts incomplete: {sorted(REQUIRED_INCIDENT_RECEIPTS - receipts)}")

        validation = require_mapping(data.get("validation_requirements"), "validation_requirements")
        for key in [
            "require_security_scope",
            "require_threat_classes",
            "require_isolation_profiles",
            "require_risk_to_isolation",
            "require_security_controls",
            "require_policy_enforcement",
            "require_incident_security_receipts",
            "require_no_secrets_in_repo_store_logs_or_images",
            "require_policy_before_authoritative_action",
            "require_agentplane_before_execution",
            "require_microvm_for_high_risk",
        ]:
            require(validation.get(key) is True, f"validation {key} must be true")
    except Exception as exc:
        return fail(str(exc))
    print("OK: validated Lattice security isolation model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
