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

REQUIRED_LANES = {
    "canonical-contracts",
    "platform-vertical-fixture",
    "runtime-production",
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
    "SocioProphet/lattice-forge#10",
    "SocioProphet/prophet-platform-fabric-mlops-ts-suite#33",
    "SocioProphet/policy-fabric#39",
    "SocioProphet/sociosphere#237",
    "SocioProphet/sherlock-search#29",
    "SocioProphet/slash-topics#22",
    "SocioProphet/new-hope#6",
    "SocioProphet/agentplane#75",
    "SocioProphet/cloudshell-fog#29",
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


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def as_list(value: Any, field: str) -> list[Any]:
    require(isinstance(value, list), f"{field} must be a list")
    return value


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for topology validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be a mapping")
        require(data.get("kind") == "LatticeDataGovernAITopologyRegistration", "kind mismatch")
        umbrella = data.get("umbrella")
        require(isinstance(umbrella, dict), "umbrella must be mapping")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella.repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella.issue must be 291")

        spine = as_list(data.get("spine"), "spine")
        for required in ["DataProduct", "RuntimeAsset", "NotebookSession", "EvaluationBundle", "Factsheet", "PublicationArtifact", "PlatformAssetRecord"]:
            require(required in spine, f"spine missing {required}")

        lanes = as_list(data.get("lanes"), "lanes")
        lane_ids = {lane.get("id") for lane in lanes if isinstance(lane, dict)}
        missing_lanes = sorted(REQUIRED_LANES - lane_ids)
        require(not missing_lanes, f"missing lanes: {missing_lanes}")
        owner_repos = {lane.get("owner_repo") for lane in lanes if isinstance(lane, dict)}
        missing_owners = sorted(REQUIRED_OWNER_REPOS - owner_repos)
        require(not missing_owners, f"missing owner repos: {missing_owners}")
        tracking_refs = {lane.get("tracking_ref") for lane in lanes if isinstance(lane, dict)}
        missing_tracking = sorted(REQUIRED_TRACKING_REFS - tracking_refs)
        require(not missing_tracking, f"missing tracking refs: {missing_tracking}")

        for lane in lanes:
            require(isinstance(lane, dict), "each lane must be mapping")
            require(isinstance(lane.get("owns", []), list), f"lane {lane.get('id')} owns must be list")
            require(isinstance(lane.get("must_not", []), list), f"lane {lane.get('id')} must_not must be list")
        policy_lane = next(lane for lane in lanes if lane.get("id") == "policy-subjects")
        require("create-parallel-metadata-spine" in policy_lane.get("must_not", []), "policy lane must forbid parallel metadata spine")
        platform_lane = next(lane for lane in lanes if lane.get("id") == "platform-vertical-fixture")
        require("redefine-canonical-schemas" in platform_lane.get("must_not", []), "platform lane must not redefine canonical schemas")
        slash_lane = next(lane for lane in lanes if lane.get("id") == "topic-classification")
        require(slash_lane.get("role") == "public-topic-governance-surface", "Slash Topics role mismatch")
        new_hope_lane = next(lane for lane in lanes if lane.get("id") == "semantic-membrane")
        require(new_hope_lane.get("role") == "internal-semantic-membrane", "New Hope role mismatch")

        validation = data.get("validation_requirements")
        require(isinstance(validation, dict), "validation_requirements must be mapping")
        require(validation.get("forbid_parallel_metadata_spines") is True, "must forbid parallel metadata spines")
        require(validation.get("require_policy_before_publication") is True, "must require policy before publication")
        require(validation.get("require_runtime_before_execution") is True, "must require runtime before execution")
        require(validation.get("require_platform_record_before_search") is True, "must require platform record before search")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated Lattice Data/GovernAI topology registration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
