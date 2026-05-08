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
REGISTRY = ROOT / "registry" / "governed-intelligence-rollout.yaml"

REQUIRED_LOOP = [
    "Observe",
    "Anchor",
    "Normalize",
    "Propose",
    "Explain",
    "Verify",
    "Govern",
    "Act",
    "Receipt",
    "Learn",
]
REQUIRED_OBJECTS = {
    "Entity",
    "Anchor",
    "Evidence",
    "Claim",
    "ProofCertificate",
    "ExplanationTrace",
    "VectorCandidate",
    "PolicyDecision",
    "ActionProposal",
    "ActionAdmission",
    "RuntimeReceipt",
    "LearningEvent",
    "Revocation",
    "SlashTopicProfile",
}
REQUIRED_STATUSES = {
    "not_started",
    "schema_stubbed",
    "adapter_in_progress",
    "contract_tests_present",
    "vertical_slice_ready",
}
REQUIRED_REPOS = {
    "SocioProphet/sociosphere",
    "SocioProphet/ontogenesis",
    "SocioProphet/holmes",
    "SocioProphet/sherlock-search",
    "SocioProphet/gaia-world-model",
    "SocioProphet/guardrail-fabric",
    "SocioProphet/agentplane",
}
REQUIRED_MEMBRANES = {
    "/architecture/governed-intelligence",
    "/sherlock/evidence-answers",
    "/holmes/proof-claims",
    "/gaia/world-claims",
    "/agents/action-admission",
    "/policy/claim-action-admission",
    "/ontogenesis/schema-contracts",
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
        return fail("PyYAML is required for governed intelligence rollout validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")

    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be a mapping")
        require(
            data.get("kind") == "GovernedIntelligenceRolloutRegistration",
            "kind mismatch",
        )
        require(data.get("version") == "0.1.0", "version mismatch")

        loop = data.get("canonical_platform_loop")
        require(loop == REQUIRED_LOOP, "canonical_platform_loop mismatch")

        membranes = set(as_list(data.get("slash_topic_membranes"), "slash_topic_membranes"))
        require(REQUIRED_MEMBRANES <= membranes, "required slash-topic membranes missing")

        adoption = data.get("adoption_status_projection")
        require(isinstance(adoption, dict), "adoption_status_projection must be mapping")
        allowed_statuses = set(as_list(adoption.get("allowed_statuses"), "adoption_status_projection.allowed_statuses"))
        require(REQUIRED_STATUSES == allowed_statuses, "adoption statuses mismatch")

        repos = as_list(adoption.get("repos"), "adoption_status_projection.repos")
        seen_repos: set[str] = set()
        for item in repos:
            require(isinstance(item, dict), "adoption repo entry must be mapping")
            repo = item.get("repo")
            require(isinstance(repo, str) and repo, "adoption repo missing repo")
            require(repo not in seen_repos, f"duplicate adoption repo entry: {repo}")
            seen_repos.add(repo)
            status = item.get("status")
            require(status in REQUIRED_STATUSES, f"invalid status {status!r} for {repo}")
        require(REQUIRED_REPOS <= seen_repos, "required repos missing from adoption projection")

        matrix = as_list(data.get("canonical_object_matrix"), "canonical_object_matrix")
        object_names = set()
        for row in matrix:
            require(isinstance(row, dict), "canonical_object_matrix row must be mapping")
            obj = row.get("object")
            require(isinstance(obj, str) and obj, "canonical object missing name")
            require(obj not in object_names, f"duplicate canonical object: {obj}")
            object_names.add(obj)
            source_repo = row.get("source_of_truth_repo")
            require(isinstance(source_repo, str) and source_repo.startswith("SocioProphet/"), f"invalid source_of_truth_repo for {obj}")
            consumers = as_list(row.get("consuming_repos"), f"consuming_repos for {obj}")
            require(all(isinstance(repo, str) and repo.startswith("SocioProphet/") for repo in consumers), f"invalid consuming_repos for {obj}")
        require(REQUIRED_OBJECTS == object_names, "canonical objects mismatch")

        child_issues = as_list(data.get("child_rollout_issues"), "child_rollout_issues")
        child_repos = set()
        for item in child_issues:
            require(isinstance(item, dict), "child issue entry must be mapping")
            repo = item.get("repo")
            issue = item.get("issue")
            require(isinstance(repo, str) and repo.startswith("SocioProphet/"), "invalid child issue repo")
            require(isinstance(issue, int) and issue > 0, f"invalid child issue id for {repo}")
            child_repos.add(repo)
        require((REQUIRED_REPOS - {"SocioProphet/sociosphere"}) <= child_repos, "missing required child rollout issues")

        rollup = data.get("workspace_mesh_rollup")
        require(isinstance(rollup, dict), "workspace_mesh_rollup must be mapping")
        status_counts = rollup.get("status_counts")
        require(isinstance(status_counts, dict), "workspace_mesh_rollup.status_counts must be mapping")
        require(REQUIRED_STATUSES <= set(status_counts), "workspace rollup status_counts missing required statuses")
        membrane_rollups = as_list(rollup.get("membrane_rollups"), "workspace_mesh_rollup.membrane_rollups")
        require(any(item.get("membrane") == "/architecture/governed-intelligence" for item in membrane_rollups if isinstance(item, dict)), "missing architecture membrane rollup")

        non_goals = as_list(data.get("non_goals"), "non_goals")
        require(len(non_goals) >= 3, "non_goals must include at least three entries")
    except Exception as exc:
        return fail(str(exc))

    print("OK: validated governed intelligence rollout registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
