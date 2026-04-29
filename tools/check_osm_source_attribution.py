#!/usr/bin/env python3
"""Check OSM attribution policy and optional mounted fixtures."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "standards/osm-source-attribution/policy.v0.json"


def error(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        error(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        error(f"bad json: {path}: {exc}")
    if not isinstance(data, dict):
        error(f"top-level JSON object required: {path}")
    return data


def nested(data: dict[str, Any], dotted: str) -> Any:
    value: Any = data
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def require(data: dict[str, Any], dotted: str, label: str) -> None:
    if not nested(data, dotted):
        error(f"{label} missing {dotted}")


def check_policy() -> None:
    policy = read_json(POLICY)
    for field in ["policy_version", "policy_id", "required_artifact_fields", "route_policy", "runtime_policy"]:
        if field not in policy:
            error(f"policy missing {field}")
    if policy["policy_version"] != "v0":
        error("policy_version must be v0")
    if nested(policy, "route_policy.default_status") != "advisory":
        error("route_policy.default_status must be advisory")


def check_fixtures() -> None:
    gaia_root = os.environ.get("GAIA_FIXTURE_ROOT")
    sherlock_root = os.environ.get("SHERLOCK_FIXTURE_ROOT")
    if not gaia_root or not sherlock_root:
        if os.environ.get("OSM_ATTRIBUTION_REQUIRE_FIXTURES") == "1":
            error("fixture roots required")
        print("fixture roots not set; policy-only check passed")
        return

    gaia = Path(gaia_root)
    sherlock = Path(sherlock_root)
    feature = read_json(gaia / "fixtures/geospatial/osm-road-feature-binding.sample.v1.json")
    layer = read_json(gaia / "fixtures/geospatial/osm-derived-map-tile-layer.sample.v1.json")
    graph = read_json(gaia / "fixtures/geospatial/osm-route-graph.sample.v1.json")
    search = read_json(sherlock / "examples/gaia-osm-derived-road-layer.sherlock-result.v1.json")

    for field in ["osm_ref.osm_type", "osm_ref.osm_id", "attribution.attribution_text", "provenance.source_refs"]:
        require(feature, field, "feature")
    for field in ["attribution.attribution_text", "attribution.license_refs", "provenance.source_refs"]:
        require(layer, field, "layer")
        require(graph, field, "route graph")
    if graph.get("safety_status") != "advisory":
        error("route graph fixture must be advisory")
    if not search.get("spatial_refs") or not search.get("provenance_refs"):
        error("Sherlock OSM result needs spatial_refs and provenance_refs")
    print("policy and fixture attribution checks passed")


def main() -> int:
    check_policy()
    check_fixtures()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
