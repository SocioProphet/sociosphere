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
REGISTRY = ROOT / "registry" / "lattice-data-governai-lanes.yaml"

NOTEBOOK_RUNTIME_REF = "runtime-asset:prophet-python-ml:0.1.0"
RAY_RUNTIME_REF = "runtime-asset:prophet-ray-ml:0.1.0"
BEAM_RUNTIME_REF = "runtime-asset:prophet-beam-dataops:0.1.0"

REQUIRED_LANES = {
    "canonical-contracts",
    "platform-vertical-fixture",
    "platform-expanded-product-surfaces",
    "runtime-production",
    "runtime-profile-bindings",
    "governed-mlops-execution",
    "policy-subjects",
    "topology-registration",
    "search-indexing",
    "topic-classification",
    "semantic-membrane",
    "execution-consumer",
    "developer-home",
}
REQUIRED_TRACKING_REFS = {
    "SourceOS-Linux/sourceos-spec#75",
    "SocioProphet/prophet-platform#299",
    "SocioProphet/prophet-platform#300",
    "SocioProphet/prophet-platform#301",
    "SocioProphet/prophet-platform#302",
    "SocioProphet/prophet-platform#303",
    "SocioProphet/prophet-platform#304",
    "SocioProphet/prophet-platform#305",
    "SocioProphet/prophet-platform#306",
    "SocioProphet/lattice-forge#10",
    "SocioProphet/lattice-forge#11",
    "SocioProphet/prophet-platform-fabric-mlops-ts-suite#33",
    "SocioProphet/policy-fabric#39",
    "SocioProphet/policy-fabric#40",
    "SocioProphet/sociosphere#237",
    "SocioProphet/sociosphere#238",
    "SocioProphet/sociosphere#239",
    "SocioProphet/sherlock-search#29",
    "SocioProphet/sherlock-search#30",
    "SocioProphet/sherlock-search#31",
    "SocioProphet/slash-topics#22",
    "SocioProphet/slash-topics#23",
    "SocioProphet/slash-topics#24",
    "SocioProphet/new-hope#6",
    "SocioProphet/new-hope#7",
    "SocioProphet/new-hope#8",
    "SocioProphet/agentplane#75",
    "SocioProphet/agentplane#76",
    "SocioProphet/agentplane#77",
    "SocioProphet/cloudshell-fog#29",
    "SocioProphet/cloudshell-fog#30",
}
REQUIRED_OWNER_REPOS = {
    "SourceOS-Linux/sourceos-spec",
    "SocioProphet/prophet-platform",
    "SocioProphet/lattice-forge",
    "SocioProphet/prophet-platform-fabric-mlops-ts-suite",
    "SocioProphet/policy-fabric",
    "SocioProphet/sociosphere",
    "SocioProphet/sherlock-search",
    "SocioProphet/slash-topics",
    "SocioProphet/new-hope",
    "SocioProphet/agentplane",
    "SocioProphet/cloudshell-fog",
}
REQUIRED_SPINE = {
    "DataProduct",
    "RuntimeAsset",
    "RuntimeProfileBinding",
    "NotebookSession",
    "EvaluationBundle",
    "Factsheet",
    "PublicationArtifact",
    "PlatformAssetRecord",
    "ModelZooEntry",
    "PromptAsset",
    "RAGPipeline",
    "ResearchPackage",
    "TrainingDataset",
    "EvaluationDataset",
    "ActiveMetadataEvent",
    "TrustPostureSummary",
}
REQUIRED_EXPANDED_ASSETS = {
    "ModelZooEntry",
    "PromptAsset",
    "RAGPipeline",
    "ResearchPackage",
    "TrainingDataset",
    "EvaluationDataset",
    "ActiveMetadataEvent",
    "TrustPostureSummary",
    "RuntimeProfileBinding",
}
REQUIRED_RUNTIME_REFS = {NOTEBOOK_RUNTIME_REF, RAY_RUNTIME_REF, BEAM_RUNTIME_REF}
REQUIRED_ROLE_BINDINGS = {
    "NotebookSession": NOTEBOOK_RUNTIME_REF,
    "QueryRun": NOTEBOOK_RUNTIME_REF,
    "PublicationArtifact": NOTEBOOK_RUNTIME_REF,
    "ModelZooEntry": RAY_RUNTIME_REF,
    "ModelRuntimeProfile": RAY_RUNTIME_REF,
    "ModelEndpoint": RAY_RUNTIME_REF,
    "RayJobDryRunPlan": RAY_RUNTIME_REF,
    "RAGPipeline": RAY_RUNTIME_REF,
    "EvaluationBundle": RAY_RUNTIME_REF,
    "BeamPipelineDryRunPlan": BEAM_RUNTIME_REF,
    "TrainingDatasetRecipe": BEAM_RUNTIME_REF,
    "QualityProfile": BEAM_RUNTIME_REF,
    "VectorIndex": BEAM_RUNTIME_REF,
}


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def as_list(value: Any, field: str) -> list[Any]:
    require(isinstance(value, list), f"{field} must be a list")
    return value


def lane_refs(lane: dict[str, Any]) -> list[str]:
    if "tracking_refs" in lane:
        refs = lane["tracking_refs"]
        require(isinstance(refs, list) and refs, f"lane {lane.get('id')} tracking_refs must be non-empty list")
        return refs
    if "tracking_ref" in lane:
        ref = lane["tracking_ref"]
        require(isinstance(ref, str) and ref, f"lane {lane.get('id')} tracking_ref must be non-empty string")
        return [ref]
    raise ValueError(f"lane {lane.get('id')} missing tracking refs")


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for topology validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be a mapping")
        require(data.get("kind") == "LatticeDataGovernAITopologyRegistration", "kind mismatch")
        require(data.get("version") == "0.3.0", "version must be 0.3.0 for runtime profile registration")
        umbrella = data.get("umbrella")
        require(isinstance(umbrella, dict), "umbrella must be mapping")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella.repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella.issue must be 291")

        spine = set(as_list(data.get("spine"), "spine"))
        missing_spine = sorted(REQUIRED_SPINE - spine)
        require(not missing_spine, f"spine missing {missing_spine}")

        runtime_profiles = data.get("runtime_profiles")
        require(isinstance(runtime_profiles, dict), "runtime_profiles must be mapping")
        require(runtime_profiles.get("notebook_runtime_ref") == NOTEBOOK_RUNTIME_REF, "notebook runtime ref mismatch")
        require(runtime_profiles.get("ray_runtime_ref") == RAY_RUNTIME_REF, "ray runtime ref mismatch")
        require(runtime_profiles.get("beam_runtime_ref") == BEAM_RUNTIME_REF, "beam runtime ref mismatch")
        role_bindings = runtime_profiles.get("role_bindings")
        require(isinstance(role_bindings, dict), "runtime_profiles.role_bindings must be mapping")
        for role, runtime_ref in REQUIRED_ROLE_BINDINGS.items():
            require(role_bindings.get(role) == runtime_ref, f"runtime role binding mismatch for {role}")

        lanes = as_list(data.get("lanes"), "lanes")
        lane_ids = {lane.get("id") for lane in lanes if isinstance(lane, dict)}
        missing_lanes = sorted(REQUIRED_LANES - lane_ids)
        require(not missing_lanes, f"missing lanes: {missing_lanes}")
        owner_repos = {lane.get("owner_repo") for lane in lanes if isinstance(lane, dict)}
        missing_owners = sorted(REQUIRED_OWNER_REPOS - owner_repos)
        require(not missing_owners, f"missing owner repos: {missing_owners}")
        tracking_refs: set[str] = set()
        for lane in lanes:
            require(isinstance(lane, dict), "each lane must be mapping")
            tracking_refs.update(lane_refs(lane))
        validation = data.get("validation_requirements")
        require(isinstance(validation, dict), "validation_requirements must be mapping")
        validation_tracking_refs = set(as_list(validation.get("required_tracking_refs"), "validation_requirements.required_tracking_refs"))
        tracking_refs.update(validation_tracking_refs)
        missing_tracking = sorted(REQUIRED_TRACKING_REFS - tracking_refs)
        require(not missing_tracking, f"missing tracking refs: {missing_tracking}")

        for lane in lanes:
            require(isinstance(lane, dict), "each lane must be mapping")
            require(isinstance(lane.get("owns", []), list), f"lane {lane.get('id')} owns must be list")
            require(isinstance(lane.get("must_not", []), list), f"lane {lane.get('id')} must_not must be list")

        runtime_lane = next(lane for lane in lanes if lane.get("id") == "runtime-production")
        require("SocioProphet/lattice-forge#11" in lane_refs(runtime_lane), "runtime lane must include #11")
        runtime_owns = set(as_list(runtime_lane.get("owns"), "runtime-production.owns"))
        for owned in ["prophet-python-ml", "prophet-ray-ml", "prophet-beam-dataops"]:
            require(owned in runtime_owns, f"runtime lane missing {owned}")

        runtime_binding_lane = next(lane for lane in lanes if lane.get("id") == "runtime-profile-bindings")
        require("SocioProphet/prophet-platform#306" in lane_refs(runtime_binding_lane), "runtime-profile-bindings lane must include #306")
        require("redefine-runtime-asset-schema" in runtime_binding_lane.get("must_not", []), "runtime-profile-bindings must not redefine RuntimeAsset schema")

        execution_lane = next(lane for lane in lanes if lane.get("id") == "execution-consumer")
        require("SocioProphet/agentplane#77" in lane_refs(execution_lane), "AgentPlane execution lane must include #77")
        require("own-runtime-build-artifacts" in execution_lane.get("must_not", []), "AgentPlane must not own runtime build artifacts")

        policy_lane = next(lane for lane in lanes if lane.get("id") == "policy-subjects")
        require("create-parallel-metadata-spine" in policy_lane.get("must_not", []), "policy lane must forbid parallel metadata spine")
        require("SocioProphet/policy-fabric#40" in lane_refs(policy_lane), "policy lane must include expanded policy PR")
        platform_lane = next(lane for lane in lanes if lane.get("id") == "platform-vertical-fixture")
        require("redefine-canonical-schemas" in platform_lane.get("must_not", []), "platform lane must not redefine canonical schemas")
        expanded_lane = next(lane for lane in lanes if lane.get("id") == "platform-expanded-product-surfaces")
        expanded_owns = set(as_list(expanded_lane.get("owns"), "platform-expanded-product-surfaces.owns"))
        missing_expanded_owns = sorted((REQUIRED_EXPANDED_ASSETS - {"RuntimeProfileBinding"}) - expanded_owns)
        require(not missing_expanded_owns, f"expanded platform lane missing owns: {missing_expanded_owns}")
        slash_lane = next(lane for lane in lanes if lane.get("id") == "topic-classification")
        require(slash_lane.get("role") == "public-topic-governance-surface", "Slash Topics role mismatch")
        require("SocioProphet/slash-topics#24" in lane_refs(slash_lane), "Slash Topics lane must include expanded topic PR")
        new_hope_lane = next(lane for lane in lanes if lane.get("id") == "semantic-membrane")
        require(new_hope_lane.get("role") == "internal-semantic-membrane", "New Hope role mismatch")
        require("SocioProphet/new-hope#8" in lane_refs(new_hope_lane), "New Hope lane must include expanded membrane PR")
        sherlock_lane = next(lane for lane in lanes if lane.get("id") == "search-indexing")
        require("SocioProphet/sherlock-search#31" in lane_refs(sherlock_lane), "Sherlock lane must include expanded index PR")

        validation_expanded_assets = set(as_list(validation.get("expanded_asset_surfaces"), "validation_requirements.expanded_asset_surfaces"))
        missing_validation_assets = sorted(REQUIRED_EXPANDED_ASSETS - validation_expanded_assets)
        require(not missing_validation_assets, f"expanded_asset_surfaces missing {missing_validation_assets}")
        runtime_refs = set(as_list(validation.get("runtime_profile_refs"), "validation_requirements.runtime_profile_refs"))
        missing_runtime_refs = sorted(REQUIRED_RUNTIME_REFS - runtime_refs)
        require(not missing_runtime_refs, f"runtime_profile_refs missing {missing_runtime_refs}")
        require(validation.get("forbid_parallel_metadata_spines") is True, "must forbid parallel metadata spines")
        require(validation.get("require_policy_before_publication") is True, "must require policy before publication")
        require(validation.get("require_runtime_before_execution") is True, "must require runtime before execution")
        require(validation.get("require_platform_record_before_search") is True, "must require platform record before search")
        require(validation.get("require_runtime_profile_binding_before_agent_execution") is True, "must require runtime profile binding before agent execution")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated runtime-profile Lattice Data/GovernAI topology registration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
