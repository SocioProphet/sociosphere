#!/usr/bin/env python3
"""Validate the Sociosphere Lattice placement spine registry."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED_PRODUCERS = {
    "SocioProphet/prophet-platform",
    "SocioProphet/cloudshell-fog",
    "SociOS-Linux/cloudshell-fog",
    "SourceOS-Linux/dnote",
}
REQUIRED_RECORDS = {
    "BYOCPlacementPlan",
    "UnifiedNotebookShellPlacementPlan",
    "M2TopoLVMPlacementPlan",
    "PlacementDryRunReport",
}
REQUIRED_CONSUMERS = {"SocioProphet/sherlock-search", "SocioProphet/prophet-cli", "SocioProphet/sociosphere"}
REQUIRED_LANES = {"byoc", "cloudshell_fog", "command_line_notebook", "m2_topolvm", "placement_decision"}
REQUIRED_DECISION_CHECKS = {
    "byoc-compute-targets",
    "byoc-storage-targets",
    "byoc-io-bindings",
    "cloudshell-fog-terminal-path",
    "m2-topolvm-safety-boundary",
    "notebook-adapter-launch-coverage",
    "promotion-target-coverage",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(path: Path) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), "registry must decode to object")
    require(data.get("schema_version") == 1, "schema_version must be 1")
    require(data.get("canonical_identity") == "PlatformAssetRecord", "canonical identity mismatch")
    producers = data.get("producer_surfaces")
    require(isinstance(producers, list) and producers, "producer_surfaces must be non-empty")
    producer_repos = {item.get("repo") for item in producers if isinstance(item, dict)}
    require(REQUIRED_PRODUCERS.issubset(producer_repos), f"missing producers: {sorted(REQUIRED_PRODUCERS - producer_repos)}")
    record_names = {record for item in producers if isinstance(item, dict) for record in item.get("records", [])}
    require(REQUIRED_RECORDS.issubset(record_names), f"missing records: {sorted(REQUIRED_RECORDS - record_names)}")
    lanes = data.get("placement_lanes")
    require(isinstance(lanes, dict), "placement_lanes must be object")
    for key in REQUIRED_LANES:
        require(key in lanes, f"missing placement lane {key}")
    decision = lanes.get("placement_decision")
    require(isinstance(decision, dict), "placement_decision must be object")
    require(decision.get("canonical_record") == "PlacementDryRunReport", "placement decision canonical record mismatch")
    checks = set(decision.get("required_checks", []))
    require(REQUIRED_DECISION_CHECKS.issubset(checks), f"missing decision checks: {sorted(REQUIRED_DECISION_CHECKS - checks)}")
    consumers = data.get("consumers")
    require(isinstance(consumers, list) and consumers, "consumers must be non-empty")
    consumer_repos = {item.get("repo") for item in consumers if isinstance(item, dict)}
    require(REQUIRED_CONSUMERS.issubset(consumer_repos), f"missing consumers: {sorted(REQUIRED_CONSUMERS - consumer_repos)}")
    consumed_records = {record for item in consumers if isinstance(item, dict) for record in item.get("consumes", [])}
    require("PlacementDryRunReport" in consumed_records, "PlacementDryRunReport must be consumed")
    invariant_text = "\n".join(str(item) for item in data.get("invariants", []))
    require("side-effect-free" in invariant_text, "side-effect-free invariant missing")
    require("PlacementDryRunReport" in invariant_text, "PlacementDryRunReport invariant missing")
    require("PlatformAssetRecord" in invariant_text, "PlatformAssetRecord invariant missing")


def main() -> int:
    path = Path("registry/lattice-placement-spine.yaml")
    try:
        validate(path)
        print(f"PASS {path}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL {path}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
