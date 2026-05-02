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
REGISTRY = ROOT / "registry" / "lattice-deployment-topology.yaml"
REQUIRED_MODES = {"local-m2-demo", "tenant-sandbox", "org-fleet"}
REQUIRED_PLANES = {"system_plane", "lifecycle_plane", "user_plane", "agent_plane", "shell_plane"}
REQUIRED_SITE_SURFACES = {
    "device-registration",
    "experience-profile-selection",
    "release-set-build-request",
    "artifact-download",
    "enrollment-token-issue",
    "compliance-dashboard",
    "rollback-dashboard",
}
REQUIRED_RELEASE_OBJECTS = {"ReleaseSet", "BootReleaseSet", "PolicyBundle", "BillOfMaterials", "Fingerprint", "AuditLog"}
REQUIRED_FORBIDDEN_SECRET_LOCATIONS = {"git-repository", "nix-store", "build-logs", "command-output"}
REQUIRED_BOOT_MENU = {"SourceOS", "SourceOS Recovery", "macOS"}
REQUIRED_RECOVERY_CAPABILITIES = {
    "fetch-authorized-release-set",
    "inspect-release-set",
    "apply-system-target",
    "repin-user-agent-closures",
    "rollback-system-plane",
    "rotate-device-keys",
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
        return fail("PyYAML is required for deployment topology validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeDeploymentTopologyRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = require_mapping(data.get("umbrella"), "umbrella")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella issue mismatch")
        require(umbrella.get("work_order") == "work-order-0", "work order mismatch")
        require(umbrella.get("operating_model_ref") == "registry/lattice-operating-model.yaml", "operating model ref mismatch")

        modes = as_list(data.get("deployment_modes"), "deployment_modes")
        mode_ids = {mode.get("id") for mode in modes if isinstance(mode, dict)}
        require(mode_ids == REQUIRED_MODES, f"deployment modes mismatch: {mode_ids}")
        for mode in modes:
            require_mapping(mode, "deployment mode")
            for key in ["purpose", "control_plane", "device_scope", "execution_scope", "status"]:
                require(key in mode, f"deployment mode {mode.get('id')} missing {key}")
        local = next(mode for mode in modes if mode.get("id") == "local-m2-demo")
        require(local.get("status") == "first-implementation-target", "local M2 demo must be first implementation target")

        planes = require_mapping(data.get("planes"), "planes")
        require(set(planes) == REQUIRED_PLANES, f"planes mismatch: {set(planes)}")
        for name, plane in planes.items():
            plane = require_mapping(plane, f"planes.{name}")
            for key in ["owner_repo", "substrate", "mutation_policy", "accepts", "emits"]:
                require(key in plane, f"{name} missing {key}")
            as_list(plane.get("accepts"), f"{name}.accepts")
            as_list(plane.get("emits"), f"{name}.emits")
        require(planes["agent_plane"].get("owner_repo") == "SocioProphet/agentplane", "agent plane owner mismatch")
        require("policy-decision" in planes["agent_plane"].get("accepts", []), "agent plane must accept policy decision")

        site = require_mapping(data.get("control_plane_site"), "control_plane_site")
        require(site.get("owner_repo") == "mdheller/socioprophet-web", "site owner mismatch")
        surfaces = set(as_list(site.get("required_surfaces"), "control_plane_site.required_surfaces"))
        missing_surfaces = sorted(REQUIRED_SITE_SURFACES - surfaces)
        require(not missing_surfaces, f"missing site surfaces: {missing_surfaces}")

        services = require_mapping(data.get("artifact_services"), "artifact_services")
        release_store = require_mapping(services.get("release_store"), "artifact_services.release_store")
        release_objects = set(as_list(release_store.get("required_objects"), "release_store.required_objects"))
        missing_release = sorted(REQUIRED_RELEASE_OBJECTS - release_objects)
        require(not missing_release, f"missing release objects: {missing_release}")
        for service_key in ["cache_store", "proof_store"]:
            service = require_mapping(services.get(service_key), f"artifact_services.{service_key}")
            as_list(service.get("required_objects"), f"{service_key}.required_objects")

        boot = require_mapping(data.get("enrollment_and_boot"), "enrollment_and_boot")
        require(boot.get("registration_primitive") == "self-generated-device-key", "registration primitive mismatch")
        require(boot.get("enrollment_model") == "opt-in-token-gated", "enrollment model mismatch")
        require(boot.get("boot_release_set_required") is True, "BootReleaseSet must be required")
        apple = require_mapping(boot.get("apple_silicon_path"), "apple_silicon_path")
        require(apple.get("strategy") == "asahi-compatible-installer-entry-plus-sourceos-recovery-entry", "Apple Silicon strategy mismatch")
        missing_boot = sorted(REQUIRED_BOOT_MENU - set(as_list(apple.get("boot_menu_goal"), "apple.boot_menu_goal")))
        require(not missing_boot, f"missing Apple boot menu entries: {missing_boot}")
        missing_recovery = sorted(REQUIRED_RECOVERY_CAPABILITIES - set(as_list(apple.get("recovery_capabilities"), "apple.recovery_capabilities")))
        require(not missing_recovery, f"missing recovery capabilities: {missing_recovery}")
        pc = require_mapping(boot.get("generic_pc_path"), "generic_pc_path")
        transport = set(as_list(pc.get("required_transport"), "generic_pc_path.required_transport"))
        require("signed-boot-manifest" in transport, "generic PC path must require signed manifest")
        require("per-device-authorization" in transport, "generic PC path must require per-device authorization")

        netsec = require_mapping(data.get("networking_and_secrets"), "networking_and_secrets")
        require(netsec.get("default_network_posture") == "deny-by-default-for-agent-space", "default network posture mismatch")
        require(netsec.get("enrollment_network_posture") == "control-plane-only", "enrollment network posture mismatch")
        require(netsec.get("secrets_model") == "secret-door-required", "secrets model mismatch")
        forbidden = set(as_list(netsec.get("secrets_forbidden_locations"), "secrets_forbidden_locations"))
        missing_forbidden = sorted(REQUIRED_FORBIDDEN_SECRET_LOCATIONS - forbidden)
        require(not missing_forbidden, f"missing forbidden secret locations: {missing_forbidden}")

        rollback = require_mapping(data.get("storage_and_rollback"), "storage_and_rollback")
        for key in ["system_rollback", "user_rollback", "agent_rollback", "release_rollback"]:
            require(key in rollback, f"storage_and_rollback missing {key}")
        require(rollback.get("rollback_receipt_required") is True, "rollback receipt must be required")

        validation = require_mapping(data.get("validation_requirements"), "validation_requirements")
        for key in [
            "require_deployment_modes",
            "require_planes",
            "require_control_plane_site",
            "require_artifact_services",
            "require_enrollment_and_boot",
            "require_networking_and_secrets",
            "require_storage_and_rollback",
            "require_apple_silicon_path",
            "require_generic_pc_path",
            "require_no_secret_in_repo_store_or_logs",
            "require_policy_for_agent_execution",
            "require_agentplane_for_execution",
        ]:
            require(validation.get(key) is True, f"validation_requirements.{key} must be true")
    except Exception as exc:
        return fail(str(exc))
    print("OK: validated Lattice deployment topology")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
