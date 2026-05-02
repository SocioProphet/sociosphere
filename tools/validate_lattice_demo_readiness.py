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
REGISTRY = ROOT / "registry" / "lattice-demo-readiness.yaml"

REQUIRED_REFS = {
    "SocioProphet/prophet-platform#307",
    "SourceOS-Linux/sourceos-spec#75",
    "SocioProphet/lattice-forge#11",
    "SocioProphet/lattice-forge#12",
    "SocioProphet/prophet-platform#306",
    "SocioProphet/prophet-platform-fabric-mlops-ts-suite#34",
    "SocioProphet/agentplane#77",
    "SocioProphet/sherlock-search#32",
    "SocioProphet/slash-topics#25",
    "SocioProphet/new-hope#9",
    "SocioProphet/policy-fabric#42",
    "SocioProphet/cloudshell-fog#31",
    "SocioProphet/sociosphere#243",
}
REQUIRED_DEMO_PATH = [
    "catalog-search",
    "data-product-inspection",
    "runtime-profile-selection",
    "notebook-launch-dry-run",
    "annotation-to-training",
    "ray-model-dry-run",
    "beam-quality-dry-run",
    "model-zoo-review",
    "prompt-rag-evaluation",
    "publication-review-and-reproduction",
    "active-metadata-indexing",
    "trust-posture-review",
]
REQUIRED_CHECKS = {
    "data-product",
    "runtime-profile-catalog",
    "annotation-to-training",
    "model-zoo",
    "prompt-rag-eval",
    "publication-review",
    "active-metadata",
    "trust-reputation",
    "policy-governance",
    "developer-home",
}
REQUIRED_RUNTIME_REFS = {
    "notebook_runtime_ref": "runtime-asset:prophet-python-ml:0.1.0",
    "ray_runtime_ref": "runtime-asset:prophet-ray-ml:0.1.0",
    "beam_runtime_ref": "runtime-asset:prophet-beam-dataops:0.1.0",
    "runtime_profile_binding_ref": "runtime-profile-binding:lattice-data-governai:0.1.0",
    "runtime_promotion_manifest_ref": "runtime-promotion-manifest:lattice-runtime-promotion-manifest:0.1.0",
}
REQUIRED_COMMANDS = {
    "/lattice data search community_truth_demo",
    "/lattice runtime pick prophet-python-ml",
    "/lattice runtime pick prophet-ray-ml",
    "/lattice runtime pick prophet-beam-dataops",
    "/lattice notebook launch community_truth_demo --runtime prophet-python-ml",
    "/lattice mlops ray run community_truth_demo --runtime prophet-ray-ml --dry-run",
    "/lattice dataops beam run community_truth_demo --runtime prophet-beam-dataops --dry-run",
    "/lattice govern review urn:srcos:evaluation-bundle:community_truth_demo_model_eval",
    "/lattice publication inspect urn:srcos:publication-artifact:community_truth_demo_report",
}


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def as_list(value: Any, field: str) -> list[Any]:
    require(isinstance(value, list), f"{field} must be list")
    require(bool(value), f"{field} must not be empty")
    return value


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for demo readiness validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeDemoReadinessRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = data.get("umbrella")
        require(isinstance(umbrella, dict), "umbrella must be mapping")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella.repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella.issue mismatch")
        require(umbrella.get("readiness_pr") == "SocioProphet/prophet-platform#307", "readiness PR mismatch")

        report = data.get("readiness_report")
        require(isinstance(report, dict), "readiness_report must be mapping")
        require(report.get("kind") == "LatticeDemoReadinessReport", "readiness report kind mismatch")
        require(report.get("tracking_ref") == "SocioProphet/prophet-platform#307", "readiness report tracking ref mismatch")
        require(report.get("state") == "demo-ready", "readiness state must be demo-ready")
        require(report.get("stable_runtime_promotion") == "blocked-pending-external-evidence", "stable runtime promotion must remain blocked")
        require(report.get("dev_runtime_promotion") == "allowed-with-generated-evidence", "dev runtime promotion mismatch")
        safety = report.get("safety")
        require(isinstance(safety, dict), "readiness safety must be mapping")
        require(safety.get("network") == "none", "network must be none")
        require(safety.get("secrets") == "none", "secrets must be none")
        require(safety.get("host_mutation") is False, "host_mutation must be false")

        refs = data.get("required_estate_refs")
        require(isinstance(refs, dict), "required_estate_refs must be mapping")
        actual_refs = set(refs.values())
        missing_refs = sorted(REQUIRED_REFS - actual_refs)
        require(not missing_refs, f"missing estate refs: {missing_refs}")

        runtime_refs = data.get("runtime_refs")
        require(isinstance(runtime_refs, dict), "runtime_refs must be mapping")
        for key, expected in REQUIRED_RUNTIME_REFS.items():
            require(runtime_refs.get(key) == expected, f"runtime_refs.{key} mismatch")

        demo_path = as_list(data.get("demo_path"), "demo_path")
        require(demo_path == REQUIRED_DEMO_PATH, "demo_path must match required sequence")
        checks = set(as_list(data.get("required_checks"), "required_checks"))
        missing_checks = sorted(REQUIRED_CHECKS - checks)
        require(not missing_checks, f"missing readiness checks: {missing_checks}")
        commands = set(as_list(data.get("shell_commands"), "shell_commands"))
        missing_commands = sorted(REQUIRED_COMMANDS - commands)
        require(not missing_commands, f"missing shell commands: {missing_commands}")

        validation = data.get("validation_requirements")
        require(isinstance(validation, dict), "validation_requirements must be mapping")
        validation_refs = set(as_list(validation.get("required_tracking_refs"), "validation_requirements.required_tracking_refs"))
        missing_validation_refs = sorted(REQUIRED_REFS - validation_refs)
        require(not missing_validation_refs, f"validation refs missing: {missing_validation_refs}")
        for key in [
            "require_all_demo_path_steps",
            "require_all_readiness_checks",
            "require_shell_command_surface",
            "require_dev_runtime_promotion_allowed",
            "require_stable_runtime_promotion_blocked",
            "require_no_network_secrets_or_host_mutation",
            "forbid_demo_ready_with_blockers",
        ]:
            require(validation.get(key) is True, f"{key} must be true")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated Lattice demo readiness registration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
