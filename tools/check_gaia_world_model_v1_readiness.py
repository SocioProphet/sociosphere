#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_TOP = ["registry_id", "version", "status", "updated_at", "baseline", "readiness_lanes", "non_claims"]
REQUIRED_BASELINE_PRS = {
    "SocioProphet/socioprophet#294",
    "SocioProphet/prophet-platform#259",
    "SocioProphet/gaia-world-model#13",
}
REQUIRED_LANES = {
    "deployable_map_demo",
    "bounded_live_osm_ingestion",
    "production_tile_layer_serving",
    "eo_satellite_adapter",
    "lidar_dem_terrain",
    "weather_reanalysis_time",
    "fusion_semantics",
    "gaia_world_model_api",
    "runtime_admission",
    "deployment_operations",
}
ALLOWED_STATES = {"open", "planning", "fixture_planning", "fixture_runtime_pending", "candidate_only", "done"}


def fail(message: str) -> None:
    print(f"ERR: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path}: invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path}: expected top-level object")
    return data


def require_keys(obj: dict, keys: list[str], where: str) -> None:
    missing = [key for key in keys if key not in obj]
    if missing:
        fail(f"{where}: missing required keys: {', '.join(missing)}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "registry/gaia_world_model_v1_readiness.v1.json"
    if not path.exists():
        fail("missing registry/gaia_world_model_v1_readiness.v1.json")
    data = load_json(path)
    require_keys(data, REQUIRED_TOP, "registry")

    baseline = data["baseline"]
    if not isinstance(baseline, dict):
        fail("baseline must be object")
    require_keys(baseline, ["current_slice", "target", "baseline_prs"], "baseline")
    if baseline["current_slice"] != "GAIA Workbench v0":
        fail("baseline.current_slice must remain GAIA Workbench v0")
    if baseline["target"] != "GAIA World Model v1":
        fail("baseline.target must be GAIA World Model v1")
    missing_prs = sorted(REQUIRED_BASELINE_PRS - set(baseline.get("baseline_prs", [])))
    if missing_prs:
        fail(f"baseline missing PR refs: {', '.join(missing_prs)}")

    lanes = data["readiness_lanes"]
    if not isinstance(lanes, list) or not lanes:
        fail("readiness_lanes must be non-empty array")
    seen = set()
    for idx, lane in enumerate(lanes):
        if not isinstance(lane, dict):
            fail(f"readiness_lanes[{idx}] must be object")
        require_keys(lane, ["lane", "state", "required_repos", "required_checks"], f"readiness_lanes[{idx}]")
        if lane["state"] not in ALLOWED_STATES:
            fail(f"{lane['lane']}: invalid state {lane['state']!r}")
        if not isinstance(lane["required_repos"], list) or not lane["required_repos"]:
            fail(f"{lane['lane']}: required_repos must be non-empty array")
        if not isinstance(lane["required_checks"], list) or not lane["required_checks"]:
            fail(f"{lane['lane']}: required_checks must be non-empty array")
        seen.add(lane["lane"])
    missing_lanes = sorted(REQUIRED_LANES - seen)
    if missing_lanes:
        fail(f"missing readiness lanes: {', '.join(missing_lanes)}")

    non_claims = data["non_claims"]
    if not isinstance(non_claims, list) or len(non_claims) < 3:
        fail("non_claims must contain at least three guardrails")
    required_phrase = "Do not claim live OSM ingestion until bounded live extract is validated and served."
    if required_phrase not in non_claims:
        fail("non_claims must guard against premature live OSM ingestion claims")

    print("OK: GAIA World Model v1 readiness registry is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
