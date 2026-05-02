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
REGISTRY = ROOT / "registry" / "lattice-operating-model.yaml"
REQUIRED_ENVS = {"local-dev", "ci-fixture", "demo", "staging", "production", "tenant-sandbox"}
REQUIRED_STATES = {"fixture", "demo-ready", "staging-candidate", "release-candidate", "stable", "deprecated", "rollback-required", "retired"}
REQUIRED_OWNERS = {
    "product_owner": "SocioProphet/prophet-platform",
    "topology_owner": "SocioProphet/sociosphere",
    "policy_owner": "SocioProphet/policy-fabric",
    "execution_owner": "SocioProphet/agentplane",
    "runtime_owner": "SocioProphet/lattice-forge",
    "shell_owner": "SocioProphet/cloudshell-fog",
    "search_owner": "SocioProphet/sherlock-search",
    "topic_owner": "SocioProphet/slash-topics",
    "membrane_owner": "SocioProphet/new-hope",
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
        return fail("PyYAML is required for operating model validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeOperatingModelRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = data.get("umbrella")
        require(isinstance(umbrella, dict), "umbrella must be mapping")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella issue mismatch")
        require(umbrella.get("work_order") == "work-order-0", "work order mismatch")

        envs = as_list(data.get("environments"), "environments")
        env_ids = {env.get("id") for env in envs if isinstance(env, dict)}
        require(env_ids == REQUIRED_ENVS, f"environment ids mismatch: {env_ids}")
        for env in envs:
            require(isinstance(env, dict), "environment must be mapping")
            for key in ["purpose", "data_posture", "execution_posture", "promotion_allowed"]:
                require(key in env, f"environment {env.get('id')} missing {key}")

        states = set(as_list(data.get("lifecycle_states"), "lifecycle_states"))
        require(REQUIRED_STATES <= states, "lifecycle states incomplete")

        release = data.get("release_flow")
        require(isinstance(release, dict), "release_flow must be mapping")
        release_sequence = as_list(release.get("sequence"), "release_flow.sequence")
        require(release_sequence[0] == "fixture-validation", "release flow must start with fixture-validation")
        require(release_sequence[-1] == "stable-release", "release flow must end with stable-release")
        gates = set(as_list(release.get("required_gates"), "release_flow.required_gates"))
        for gate in ["ci-success", "policy-fabric-decision", "sociosphere-topology-registration", "runtime-evidence-present", "rollback-plan-present", "owner-approval-present"]:
            require(gate in gates, f"release gate missing {gate}")

        rollback = data.get("rollback_flow")
        require(isinstance(rollback, dict), "rollback_flow must be mapping")
        as_list(rollback.get("triggers"), "rollback_flow.triggers")
        rollback_artifacts = set(as_list(rollback.get("required_artifacts"), "rollback_flow.required_artifacts"))
        for artifact in ["rollback-receipt", "previous-release-ref", "policy-decision-ref", "incident-or-change-ref"]:
            require(artifact in rollback_artifacts, f"rollback artifact missing {artifact}")
        require(rollback.get("owner_repo") == "SocioProphet/sociosphere", "rollback owner mismatch")

        incident = data.get("incident_path")
        require(isinstance(incident, dict), "incident_path must be mapping")
        incident_states = as_list(incident.get("states"), "incident_path.states")
        require(incident_states == ["detected", "triaged", "contained", "remediated", "reviewed", "closed"], "incident states mismatch")
        receipts = set(as_list(incident.get("required_receipts"), "incident_path.required_receipts"))
        for receipt in ["incident-receipt", "policy-impact-receipt", "runtime-impact-receipt", "tenant-impact-receipt", "post-incident-review"]:
            require(receipt in receipts, f"incident receipt missing {receipt}")

        owners = data.get("ownership")
        require(isinstance(owners, dict), "ownership must be mapping")
        for key, expected in REQUIRED_OWNERS.items():
            require(owners.get(key) == expected, f"ownership.{key} mismatch")

        rules = data.get("operating_rules")
        require(isinstance(rules, dict), "operating_rules must be mapping")
        for key in [
            "policy_fabric_required_for_authoritative_actions",
            "agentplane_required_for_execution",
            "sociosphere_required_for_topology",
            "runtime_release_requires_manifest",
            "stable_release_requires_external_evidence",
            "dry_run_may_use_fixture_evidence",
            "production_requires_tenant_scope",
            "no_parallel_metadata_spines",
        ]:
            require(rules.get(key) is True, f"operating_rules.{key} must be true")

        validation = data.get("validation_requirements")
        require(isinstance(validation, dict), "validation_requirements must be mapping")
        for key in [
            "require_environments",
            "require_lifecycle_states",
            "require_release_flow",
            "require_rollback_flow",
            "require_incident_path",
            "require_ownership",
            "require_operating_rules",
            "require_policy_before_authoritative_action",
            "require_agentplane_before_execution",
        ]:
            require(validation.get(key) is True, f"validation_requirements.{key} must be true")
    except Exception as exc:
        return fail(str(exc))
    print("OK: validated Lattice operating model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
