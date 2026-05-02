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
REGISTRY = ROOT / "registry" / "lattice-replay-evidence-membrane.yaml"
BUNDLE = "urn:srcos:evidence-bundle:lattice-governed-execution-0001"
RAY = "runtime-asset:prophet-ray-ml:0.1.0"
BEAM = "runtime-asset:prophet-beam-dataops:0.1.0"
REQUIRED_REFS = {
    "SocioProphet/prophet-platform-fabric-mlops-ts-suite#35",
    "SocioProphet/sherlock-search#33",
    "SocioProphet/slash-topics#26",
    "SocioProphet/new-hope#10",
    "SocioProphet/sociosphere#247",
}
REQUIRED_ARTIFACTS = {
    "urn:srcos:artifact:community_truth_demo_ray_metrics",
    "urn:srcos:artifact:community_truth_demo_beam_quality",
    "urn:srcos:model:community_truth_demo_candidate",
}
REQUIRED_RECEIPTS = {
    "urn:srcos:lineage-receipt:ray-community-truth-demo-0001",
    "urn:srcos:lineage-receipt:beam-community-truth-demo-0001",
}
REQUIRED_COMMANDS = {
    "/lattice mlops ray run community_truth_demo --runtime prophet-ray-ml --dry-run",
    "/lattice dataops beam run community_truth_demo --runtime prophet-beam-dataops --dry-run",
}


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def as_list(value: Any, field: str) -> list[Any]:
    require(isinstance(value, list) and bool(value), f"{field} must be non-empty list")
    return value


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for replay evidence membrane registration validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeReplayEvidenceMembraneRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = data.get("umbrella")
        require(isinstance(umbrella, dict), "umbrella must be mapping")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella.repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella.issue mismatch")
        require(umbrella.get("parent_registry") == "registry/lattice-demo-readiness.yaml", "parent registry mismatch")

        refs = data.get("refs")
        require(isinstance(refs, dict), "refs must be mapping")
        actual_refs = set(refs.values())
        missing_refs = sorted(REQUIRED_REFS - actual_refs)
        require(not missing_refs, f"missing refs: {missing_refs}")

        asset = data.get("asset")
        require(isinstance(asset, dict), "asset must be mapping")
        require(asset.get("replay_evidence_bundle_ref") == BUNDLE, "bundle ref mismatch")
        require(asset.get("topic_ref") == "slash-topic://lattice/data-governai/replay-evidence", "topic ref mismatch")
        require(set(as_list(asset.get("runtime_refs"), "asset.runtime_refs")) == {RAY, BEAM}, "runtime refs mismatch")
        require(REQUIRED_ARTIFACTS <= set(as_list(asset.get("artifact_refs"), "asset.artifact_refs")), "artifact refs incomplete")
        require(REQUIRED_RECEIPTS <= set(as_list(asset.get("lineage_receipt_refs"), "asset.lineage_receipt_refs")), "lineage receipts incomplete")
        require(REQUIRED_COMMANDS <= set(as_list(asset.get("replay_command_refs"), "asset.replay_command_refs")), "replay commands incomplete")

        decisions = data.get("membrane_decisions")
        require(isinstance(decisions, dict), "membrane_decisions must be mapping")
        require(decisions.get("demo_review") == "allow", "demo_review decision mismatch")
        require(decisions.get("promotion_review") == "require-review", "promotion_review decision mismatch")

        validation = data.get("validation_requirements")
        require(isinstance(validation, dict), "validation_requirements must be mapping")
        for key in [
            "require_replay_evidence_search_index",
            "require_replay_evidence_topic_governance",
            "require_replay_evidence_membrane",
            "require_policy_fabric_decision_before_authoritative_use",
            "require_no_network_secrets_or_host_mutation",
            "forbid_runtime_ref_rewrite",
        ]:
            require(validation.get(key) is True, f"{key} must be true")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated Lattice replay evidence membrane registration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
