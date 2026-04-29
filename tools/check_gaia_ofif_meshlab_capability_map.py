#!/usr/bin/env python3
"""Validate the GAIA / OFIF / MeshLab capability map registry.

This is a dependency-light governance check. It ensures the machine-readable
program registry has the minimum fields SocioSphere needs for readiness and
change-propagation reasoning.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/gaia-ofif-meshlab-capability-map.v1.json"

REQUIRED_TOP = [
    "registry_version",
    "capability_program",
    "status",
    "updated_at",
    "authority",
    "source_of_truth",
    "repositories",
    "validation_lanes",
    "readiness_states",
    "blocked_items",
]

REQUIRED_REPOS = {
    "prophet-platform",
    "gaia-world-model",
    "orion-field-intelligence",
    "sherlock-search",
    "lattice-forge",
    "lampstand",
    "meshrush",
    "agentplane",
    "nlboot",
}

REQUIRED_LANES = {
    "gaia-contract-fixtures",
    "sherlock-geospatial-results",
    "meshrush-crystallization-fixtures",
    "agentplane-meshrush-candidate",
    "lattice-runtime-admission",
    "smart-spaces-domain-home",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        fail(f"missing registry: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail("registry top level must be an object")
    return value


def require_fields(doc: Dict[str, Any], fields: Iterable[str], scope: str) -> None:
    missing = [field for field in fields if field not in doc]
    if missing:
        fail(f"{scope} missing fields: {', '.join(missing)}")


def main() -> int:
    doc = load_json(REGISTRY)
    require_fields(doc, REQUIRED_TOP, "capability map")
    if doc.get("registry_version") != "v1":
        fail("registry_version must be v1")
    if doc.get("capability_program") != "gaia-ofif-meshlab-control-tower":
        fail("unexpected capability_program")

    repos = doc.get("repositories")
    if not isinstance(repos, list) or not repos:
        fail("repositories must be a non-empty array")
    repo_names = {repo.get("name") for repo in repos if isinstance(repo, dict)}
    missing_repos = REQUIRED_REPOS - repo_names
    if missing_repos:
        fail(f"missing required repositories: {', '.join(sorted(missing_repos))}")
    for repo in repos:
        if not isinstance(repo, dict):
            fail("repository entries must be objects")
        require_fields(repo, ["name", "role", "readiness"], f"repository {repo}")

    lanes = doc.get("validation_lanes")
    if not isinstance(lanes, list) or not lanes:
        fail("validation_lanes must be a non-empty array")
    lane_ids = {lane.get("id") for lane in lanes if isinstance(lane, dict)}
    missing_lanes = REQUIRED_LANES - lane_ids
    if missing_lanes:
        fail(f"missing required validation lanes: {', '.join(sorted(missing_lanes))}")
    for lane in lanes:
        if not isinstance(lane, dict):
            fail("validation lane entries must be objects")
        require_fields(lane, ["id", "repo", "required", "state"], f"validation lane {lane}")

    readiness = doc.get("readiness_states")
    if not isinstance(readiness, dict) or "blocked" not in readiness or "executable" not in readiness:
        fail("readiness_states must include blocked and executable")

    blocked = doc.get("blocked_items")
    if not isinstance(blocked, list):
        fail("blocked_items must be an array")

    print("GAIA / OFIF / MeshLab capability map passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
