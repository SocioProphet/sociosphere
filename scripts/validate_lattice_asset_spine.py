#!/usr/bin/env python3
"""Validate the Sociosphere Lattice platform asset spine registry."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REQUIRED_CONSUMERS = {
    "SocioProphet/sherlock-search",
    "SocioProphet/slash-topics",
    "SocioProphet/new-hope",
    "SocioProphet/contractforge",
    "SocioProphet/policy-fabric",
    "SocioProphet/graphbrain-contract",
}
REQUIRED_PRODUCERS = {"SourceOS-Linux/sourceos-boot", "SocioProphet/lattice-forge"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def minimal_yaml_load(path: Path) -> dict:
    if yaml is not None:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must decode to object")
        return data
    raise RuntimeError("PyYAML is required for registry validation")


def validate(path: Path) -> None:
    data = minimal_yaml_load(path)
    require(data.get("schema_version") == 1, "schema_version must be 1")
    require(data.get("canonical_identity") == "PlatformAssetRecord", "canonical_identity must be PlatformAssetRecord")
    require(data.get("owner_repo") == "SocioProphet/prophet-platform", "owner_repo mismatch")

    producers = data.get("producer_surfaces")
    require(isinstance(producers, list) and producers, "producer_surfaces must be non-empty")
    producer_repos = {item.get("repo") for item in producers if isinstance(item, dict)}
    require(REQUIRED_PRODUCERS.issubset(producer_repos), f"missing producers: {sorted(REQUIRED_PRODUCERS - producer_repos)}")

    consumers = data.get("consumers")
    require(isinstance(consumers, list) and consumers, "consumers must be non-empty")
    consumer_repos = {item.get("repo") for item in consumers if isinstance(item, dict)}
    require(REQUIRED_CONSUMERS.issubset(consumer_repos), f"missing consumers: {sorted(REQUIRED_CONSUMERS - consumer_repos)}")

    invariants = data.get("invariants")
    require(isinstance(invariants, list) and invariants, "invariants must be non-empty")
    invariant_text = "\n".join(str(item) for item in invariants)
    require("PlatformAssetRecord.assetId" in invariant_text, "assetId invariant missing")


def main(argv: list[str] | None = None) -> int:
    path = Path(argv[0]) if argv else Path("registry/lattice-platform-asset-spine.yaml")
    try:
        validate(path)
        print(f"PASS {path}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL {path}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
