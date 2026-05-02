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
    "SocioProphet/prophet-platform-fabric-mlops-ts-suite#35",
    "SocioProphet/agentplane#77",
    "SocioProphet/sherlock-search#32",
    "SocioProphet/sherlock-search#33",
    "SocioProphet/slash-topics#25",
    "SocioProphet/slash-topics#26",
    "SocioProphet/new-hope#9",
    "SocioProphet/policy-fabric#42",
    "SocioProphet/cloudshell-fog#31",
    "SocioProphet/cloudshell-fog#32",
    "SocioProphet/sociosphere#243",
    "SocioProphet/sociosphere#244",
    "SocioProphet/sociosphere#245",
    "SocioProphet/sociosphere#246",
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
    "replay-evidence-bundle",
    "replay-evidence-discovery",
    "replay-evidence-topic-governance",
}
REQUIRED_RUNTIME_REFS = {
    "notebook_runtime_ref": "runtime-asset:prophet-python-ml:0.1.0",
    "ray_runtime_ref": "runtime-asset:prophet-ray-ml:0.1.0",
    "beam_runtime_ref": "runtime-asset:prophet-beam-dataops:0.1.0",
    "runtime_profile_binding_ref": "runtime-profile-binding:lattice-data-governai:0.1.0",
    "runtime_promotion_manifest_ref": "runtime-promotion-manifest:lattice-runtime-promotion-manifest:0.1.0",
}
REQUIRED_COMMANDS = [
    "/lattice data search community_truth_demo",
    "/lattice runtime pick prophet-python-ml",
    "/lattice runtime pick prophet-ray-ml",
    "/lattice runtime pick prophet-beam-dataops",
    "/lattice runtime bindings inspect",
    "/lattice notebook launch community_truth_demo --runtime prophet-python-ml",
    "/lattice data inspect urn:srcos:data-product:community_truth_demo",
    "/lattice mlops ray run community_truth_demo --runtime prophet-ray-ml --dry-run",
    "/lattice dataops beam run community_truth_demo --runtime prophet-beam-dataops --dry-run",
    "/lattice govern review urn:srcos:evaluation-bundle:community_truth_demo_model_eval",
    "/lattice publication inspect urn:srcos:publication-artifact:community_truth_demo_report",
    "/lattice publication export urn:srcos:publication-artifact:community_truth_demo_report",
]
REQUIRED_ARTIFACTS = {
    "urn:srcos:artifact:community_truth_demo_ray_metrics",
    "urn:srcos:artifact:community_truth_demo_beam_quality",
    "urn:srcos:model:community_truth_demo_candidate",
}
REQUIRED_RECEIPTS = {
    "urn:srcos:lineage-receipt:ray-community-truth-demo-0001",
    "urn:srcos:lineage-receipt:beam-community-truth-demo-0001",
}
REQUIRED_RAY_METRICS = {"factuality_f1", "grounding_precision", "training_records"}
REQUIRED_BEAM_METRICS = {"quality_completeness", "annotation_coverage", "duplicate_rate"}
REQUIRED_SURFACES = {"sherlock-search", "slash-topics", "policy-fabric", "agentplane", "cloudshell-fog", "new-hope"}
REQUIRED_TOPICS = {
    "replay_evidence_bundle": "/lattice/mlops/replay-evidence-bundle",
    "lineage_receipt": "/lattice/mlops/lineage-receipt",
    "metric_expectation": "/lattice/mlops/metric-expectation",
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
        require(data.get("version") == "0.4.0", "version mismatch")
        umbrella = data.get("umbrella")
        require(isinstance(umbrella, dict), "umbrella must be mapping")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella.repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella.issue mismatch")
        require(umbrella.get("readiness_pr") == "SocioProphet/prophet-platform#307", "readiness PR mismatch")
        require(umbrella.get("command_bundle_pr") == "SocioProphet/cloudshell-fog#32", "command bundle PR mismatch")
        require(umbrella.get("mlops_replay_evidence_pr") == "SocioProphet/prophet-platform-fabric-mlops-ts-suite#35", "MLOps replay evidence PR mismatch")
        require(umbrella.get("replay_evidence_index_pr") == "SocioProphet/sherlock-search#33", "Sherlock replay evidence PR mismatch")
        require(umbrella.get("replay_evidence_topic_pr") == "SocioProphet/slash-topics#26", "Slash Topics replay evidence PR mismatch")

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

        bundle = data.get("command_bundle")
        require(isinstance(bundle, dict), "command_bundle must be mapping")
        require(bundle.get("tracking_ref") == "SocioProphet/cloudshell-fog#32", "command bundle tracking ref mismatch")
        require(bundle.get("expected_step_count") == 12, "command bundle expected_step_count must be 12")

        replay = data.get("mlops_replay_evidence")
        require(isinstance(replay, dict), "mlops_replay_evidence must be mapping")
        require(replay.get("kind") == "ReplayEvidenceBundle", "replay evidence kind mismatch")
        require(replay.get("tracking_ref") == "SocioProphet/prophet-platform-fabric-mlops-ts-suite#35", "replay evidence tracking ref mismatch")
        require(replay.get("bundle_ref") == "urn:srcos:evidence-bundle:lattice-governed-execution-0001", "replay bundle ref mismatch")
        require(replay.get("discovery_ref") == "SocioProphet/sherlock-search#33", "replay discovery ref mismatch")
        require(replay.get("topic_ref") == "SocioProphet/slash-topics#26", "replay topic ref mismatch")
        missing_artifacts = sorted(REQUIRED_ARTIFACTS - set(as_list(replay.get("required_artifacts"), "mlops_replay_evidence.required_artifacts")))
        require(not missing_artifacts, f"missing replay artifacts: {missing_artifacts}")
        missing_receipts = sorted(REQUIRED_RECEIPTS - set(as_list(replay.get("required_lineage_receipts"), "mlops_replay_evidence.required_lineage_receipts")))
        require(not missing_receipts, f"missing lineage receipts: {missing_receipts}")
        metrics = replay.get("required_metrics")
        require(isinstance(metrics, dict), "required_metrics must be mapping")
        missing_ray = sorted(REQUIRED_RAY_METRICS - set(as_list(metrics.get("ray"), "required_metrics.ray")))
        missing_beam = sorted(REQUIRED_BEAM_METRICS - set(as_list(metrics.get("beam"), "required_metrics.beam")))
        require(not missing_ray, f"missing Ray metrics: {missing_ray}")
        require(not missing_beam, f"missing Beam metrics: {missing_beam}")
        replay_commands = set(as_list(replay.get("replay_commands"), "mlops_replay_evidence.replay_commands"))
        require("/lattice mlops ray run community_truth_demo --runtime prophet-ray-ml --dry-run" in replay_commands, "missing Ray replay command")
        require("/lattice dataops beam run community_truth_demo --runtime prophet-beam-dataops --dry-run" in replay_commands, "missing Beam replay command")
        surfaces = set(as_list(replay.get("required_consumer_surfaces"), "mlops_replay_evidence.required_consumer_surfaces"))
        missing_surfaces = sorted(REQUIRED_SURFACES - surfaces)
        require(not missing_surfaces, f"missing replay consumer surfaces: {missing_surfaces}")
        topics = replay.get("topic_refs")
        require(isinstance(topics, dict), "topic_refs must be mapping")
        for key, expected in REQUIRED_TOPICS.items():
            require(topics.get(key) == expected, f"topic_refs.{key} mismatch")
        replay_safety = replay.get("safety")
        require(isinstance(replay_safety, dict), "replay safety must be mapping")
        require(replay_safety.get("network") == "none", "replay network must be none")
        require(replay_safety.get("secrets") == "none", "replay secrets must be none")
        require(replay_safety.get("host_mutation") is False, "replay host_mutation must be false")

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
        commands = as_list(data.get("shell_commands"), "shell_commands")
        require(commands == REQUIRED_COMMANDS, "shell_commands must match ordered executable demo bundle")

        validation = data.get("validation_requirements")
        require(isinstance(validation, dict), "validation_requirements must be mapping")
        validation_refs = set(as_list(validation.get("required_tracking_refs"), "validation_requirements.required_tracking_refs"))
        missing_validation_refs = sorted(REQUIRED_REFS - validation_refs)
        require(not missing_validation_refs, f"validation refs missing: {missing_validation_refs}")
        for key in [
            "require_all_demo_path_steps",
            "require_all_readiness_checks",
            "require_shell_command_surface",
            "require_executable_command_bundle",
            "require_ordered_demo_commands",
            "require_replay_evidence_bundle",
            "require_lineage_receipts",
            "require_ray_and_beam_metric_expectations",
            "require_replay_evidence_search_index",
            "require_replay_evidence_topic_governance",
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
