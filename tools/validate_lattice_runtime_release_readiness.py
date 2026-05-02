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
REGISTRY = ROOT / "registry" / "lattice-runtime-release-readiness.yaml"
MANIFEST = "runtime-promotion-manifest:lattice-runtime-promotion-manifest:0.2.0"
RUNTIME_REFS = {
    "runtime-asset:prophet-python-ml:0.1.0",
    "runtime-asset:prophet-ray-ml:0.1.0",
    "runtime-asset:prophet-beam-dataops:0.1.0",
}
REQUIRED_REFS = {
    "SocioProphet/lattice-forge#13",
    "SocioProphet/policy-fabric#43",
    "SocioProphet/prophet-platform#308",
    "SocioProphet/cloudshell-fog#33",
    "SocioProphet/sociosphere#243",
}
REQUIRED_EVIDENCE = {
    "RuntimeAsset",
    "SBOM",
    "scan-report",
    "attestation",
    "signature",
    "external-scanner-evidence",
    "external-signing-authority-evidence",
    "human-approval",
}
REQUIRED_COMMANDS = {
    "/lattice runtime release manifest inspect --manifest lattice-runtime-promotion-manifest:0.2.0",
    "/lattice runtime release policy inspect --manifest lattice-runtime-promotion-manifest:0.2.0",
    "/lattice runtime release readiness inspect",
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


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for runtime release readiness validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeRuntimeReleaseReadinessRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = data.get("umbrella")
        require(isinstance(umbrella, dict), "umbrella must be mapping")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella.repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella.issue mismatch")

        refs = data.get("refs")
        require(isinstance(refs, dict), "refs must be mapping")
        actual_refs = set(refs.values())
        missing_refs = sorted(REQUIRED_REFS - actual_refs)
        require(not missing_refs, f"missing refs: {missing_refs}")

        manifest = data.get("manifest")
        require(isinstance(manifest, dict), "manifest must be mapping")
        require(manifest.get("ref") == MANIFEST, "manifest ref mismatch")
        evidence = set(as_list(manifest.get("required_evidence"), "manifest.required_evidence"))
        missing_evidence = sorted(REQUIRED_EVIDENCE - evidence)
        require(not missing_evidence, f"missing evidence: {missing_evidence}")

        runtime_refs = set(as_list(data.get("runtime_refs"), "runtime_refs"))
        require(runtime_refs == RUNTIME_REFS, "runtime_refs mismatch")

        posture = data.get("policy_posture")
        require(isinstance(posture, dict), "policy_posture must be mapping")
        require(posture.get("dev_release") == "allow", "dev_release mismatch")
        require(posture.get("stable_release") == "allow-with-required-evidence", "stable_release mismatch")
        require(posture.get("generated_only_stable_release") == "deny", "generated_only_stable_release mismatch")
        require(posture.get("policy_fabric_required") is True, "policy_fabric_required must be true")

        commands = set(as_list(data.get("shell_commands"), "shell_commands"))
        require(commands == REQUIRED_COMMANDS, "shell_commands mismatch")

        validation = data.get("validation_requirements")
        require(isinstance(validation, dict), "validation_requirements must be mapping")
        for key in [
            "require_runtime_evidence_ref",
            "require_runtime_policy_ref",
            "require_platform_readiness_ref",
            "require_shell_command_ref",
            "require_manifest_v020",
            "require_all_runtime_refs",
            "require_generated_and_external_evidence",
            "require_policy_fabric_for_release_decision",
            "require_no_network_secrets_or_host_mutation",
        ]:
            require(validation.get(key) is True, f"{key} must be true")

        safety = data.get("safety")
        require(isinstance(safety, dict), "safety must be mapping")
        require(safety.get("network") == "none", "network must be none")
        require(safety.get("secrets") == "none", "secrets must be none")
        require(safety.get("host_mutation") is False, "host_mutation must be false")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated Lattice runtime release readiness registration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
