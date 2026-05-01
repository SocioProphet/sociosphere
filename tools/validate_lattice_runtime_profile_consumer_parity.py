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
REGISTRY = ROOT / "registry" / "lattice-runtime-profile-consumer-parity.yaml"

NOTEBOOK = "runtime-asset:prophet-python-ml:0.1.0"
RAY = "runtime-asset:prophet-ray-ml:0.1.0"
BEAM = "runtime-asset:prophet-beam-dataops:0.1.0"
BINDING = "runtime-profile-binding:lattice-data-governai:0.1.0"

REQUIRED_OWNER_REPOS = {
    "SocioProphet/lattice-forge",
    "SocioProphet/prophet-platform",
    "SocioProphet/prophet-platform-fabric-mlops-ts-suite",
    "SocioProphet/agentplane",
    "SocioProphet/sherlock-search",
    "SocioProphet/slash-topics",
    "SocioProphet/new-hope",
    "SocioProphet/policy-fabric",
    "SocioProphet/cloudshell-fog",
    "SocioProphet/sociosphere",
}
REQUIRED_TRACKING_REFS = {
    "SocioProphet/lattice-forge#11",
    "SocioProphet/prophet-platform#306",
    "SocioProphet/prophet-platform-fabric-mlops-ts-suite#34",
    "SocioProphet/agentplane#77",
    "SocioProphet/sherlock-search#32",
    "SocioProphet/slash-topics#25",
    "SocioProphet/new-hope#9",
    "SocioProphet/policy-fabric#41",
    "SocioProphet/cloudshell-fog#31",
    "SocioProphet/sociosphere#240",
}
REQUIRED_LANES = {
    "runtime-artifacts",
    "platform-runtime-bindings",
    "mlops-runtime-execution",
    "agentplane-runtime-consumer",
    "sherlock-runtime-index",
    "slash-runtime-topics",
    "newhope-runtime-membrane",
    "policy-runtime-gates",
    "cloudshell-runtime-routes",
    "topology-consumer-parity",
}
REQUIRED_ROLE_BINDINGS = {
    "NotebookSession": NOTEBOOK,
    "QueryRun": NOTEBOOK,
    "PublicationArtifact": NOTEBOOK,
    "ModelZooEntry": RAY,
    "ModelRuntimeProfile": RAY,
    "ModelEndpoint": RAY,
    "RayJobDryRunPlan": RAY,
    "RAGPipeline": RAY,
    "EvaluationBundle": RAY,
    "BeamPipelineDryRunPlan": BEAM,
    "TrainingDatasetRecipe": BEAM,
    "QualityProfile": BEAM,
    "VectorIndex": BEAM,
}


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def as_list(value: Any, field: str) -> list[Any]:
    require(isinstance(value, list), f"{field} must be a list")
    require(bool(value), f"{field} must not be empty")
    return value


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for runtime profile consumer parity validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeRuntimeProfileConsumerParityRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")

        umbrella = data.get("umbrella")
        require(isinstance(umbrella, dict), "umbrella must be mapping")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella.repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella.issue mismatch")
        require(umbrella.get("parent_registry") == "registry/lattice-data-governai-lanes.yaml", "parent registry mismatch")

        refs = data.get("runtime_profile_refs")
        require(isinstance(refs, dict), "runtime_profile_refs must be mapping")
        require(refs.get("notebook_runtime_ref") == NOTEBOOK, "notebook runtime ref mismatch")
        require(refs.get("ray_runtime_ref") == RAY, "ray runtime ref mismatch")
        require(refs.get("beam_runtime_ref") == BEAM, "beam runtime ref mismatch")
        require(refs.get("runtime_profile_binding_ref") == BINDING, "runtime profile binding ref mismatch")

        role_bindings = data.get("runtime_role_bindings")
        require(isinstance(role_bindings, dict), "runtime_role_bindings must be mapping")
        for role, runtime_ref in REQUIRED_ROLE_BINDINGS.items():
            require(role_bindings.get(role) == runtime_ref, f"role binding mismatch for {role}")

        lanes = as_list(data.get("consumer_parity_wave"), "consumer_parity_wave")
        lane_ids = {lane.get("id") for lane in lanes if isinstance(lane, dict)}
        missing_lanes = sorted(REQUIRED_LANES - lane_ids)
        require(not missing_lanes, f"missing lanes: {missing_lanes}")

        owner_repos = {lane.get("owner_repo") for lane in lanes if isinstance(lane, dict)}
        missing_owners = sorted(REQUIRED_OWNER_REPOS - owner_repos)
        require(not missing_owners, f"missing owner repos: {missing_owners}")

        tracking_refs: set[str] = set()
        for lane in lanes:
            require(isinstance(lane, dict), "lane must be mapping")
            require(isinstance(lane.get("tracking_refs"), list) and lane["tracking_refs"], f"lane {lane.get('id')} tracking_refs required")
            tracking_refs.update(lane["tracking_refs"])
            require(isinstance(lane.get("recognizes"), list) and lane["recognizes"], f"lane {lane.get('id')} recognizes required")
            require(isinstance(lane.get("must_not"), list) and lane["must_not"], f"lane {lane.get('id')} must_not required")
        missing_tracking = sorted(REQUIRED_TRACKING_REFS - tracking_refs)
        require(not missing_tracking, f"missing tracking refs: {missing_tracking}")

        mlops_lane = next(lane for lane in lanes if lane.get("id") == "mlops-runtime-execution")
        recognizes = "\n".join(str(item) for item in mlops_lane["recognizes"])
        require("RayJobDryRunPlan -> runtime-asset:prophet-ray-ml:0.1.0" in recognizes, "MLOps lane must bind Ray to Ray runtime")
        require("BeamPipelineDryRunPlan -> runtime-asset:prophet-beam-dataops:0.1.0" in recognizes, "MLOps lane must bind Beam to Beam runtime")
        require("collapse-ray-and-beam-onto-notebook-runtime" in mlops_lane["must_not"], "MLOps lane must forbid runtime collapse")

        shell_lane = next(lane for lane in lanes if lane.get("id") == "cloudshell-runtime-routes")
        shell_recognizes = "\n".join(str(item) for item in shell_lane["recognizes"])
        require("/lattice runtime pick prophet-ray-ml" in shell_recognizes, "CloudShell lane missing Ray runtime route")
        require("/lattice runtime pick prophet-beam-dataops" in shell_recognizes, "CloudShell lane missing Beam runtime route")
        require("bypass-policy-fabric" in shell_lane["must_not"], "CloudShell lane must forbid Policy Fabric bypass")
        require("bypass-agentplane" in shell_lane["must_not"], "CloudShell lane must forbid AgentPlane bypass")

        policy_lane = next(lane for lane in lanes if lane.get("id") == "policy-runtime-gates")
        require("RuntimeProfileBinding" in policy_lane["recognizes"], "Policy lane must recognize RuntimeProfileBinding")
        require("create-parallel-metadata-spine" in policy_lane["must_not"], "Policy lane must forbid parallel metadata spine")

        validation = data.get("validation_requirements")
        require(isinstance(validation, dict), "validation_requirements must be mapping")
        validation_refs = set(as_list(validation.get("required_tracking_refs"), "validation_requirements.required_tracking_refs"))
        missing_validation_refs = sorted(REQUIRED_TRACKING_REFS - validation_refs)
        require(not missing_validation_refs, f"validation refs missing: {missing_validation_refs}")
        validation_owners = set(as_list(validation.get("required_owner_repos"), "validation_requirements.required_owner_repos"))
        missing_validation_owners = sorted(REQUIRED_OWNER_REPOS - validation_owners)
        require(not missing_validation_owners, f"validation owners missing: {missing_validation_owners}")
        for key in [
            "require_runtime_profile_binding_before_agent_execution",
            "require_policy_before_runtime_launch",
            "require_runtime_profile_topics_before_newhope_membrane",
            "require_runtime_profile_index_before_shell_discovery",
            "forbid_runtime_schema_redefinition_outside_lattice_forge",
            "forbid_policy_bypass",
        ]:
            require(validation.get(key) is True, f"{key} must be true")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated Lattice runtime profile consumer parity registration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
