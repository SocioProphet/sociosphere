#!/usr/bin/env python3
"""Validate the Sociosphere Lattice federated query spine registry."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED_PRODUCERS = {
    "SocioProphet/prophet-platform",
    "SocioProphet/sherlock-search",
    "SocioProphet/slash-topics",
    "SocioProphet/new-hope",
    "SocioProphet/lampstand",
    "SocioProphet/ontogenesis",
    "SocioProphet/graphbrain-contract",
}
REQUIRED_RECORDS = {"FederatedQueryPlane", "FederatedQueryEvidence"}
REQUIRED_LANES = {
    "sql",
    "documents",
    "annotations",
    "sparql",
    "ontology",
    "cypher",
    "graphbrain",
    "atomese",
    "sherlock",
    "slash_topics",
    "new_hope",
    "lampstand",
}
REQUIRED_LANGUAGES = {
    "sql",
    "document-query",
    "annotation-query",
    "sparql",
    "ontology-query",
    "cypher",
    "graphbrain-hypergraph",
    "atomese",
    "sherlock-query",
    "slash-topic-query",
    "newhope-membrane-query",
    "lampstand-local-query",
}
REQUIRED_CONSUMERS = {"SocioProphet/prophet-cli", "SocioProphet/sherlock-search", "SocioProphet/sociosphere"}


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
    require(REQUIRED_RECORDS.issubset(record_names), f"missing query records: {sorted(REQUIRED_RECORDS - record_names)}")
    lanes = data.get("query_lanes")
    require(isinstance(lanes, dict), "query_lanes must be object")
    for lane in REQUIRED_LANES:
        require(lane in lanes, f"missing query lane {lane}")
    languages = {item.get("language") for item in lanes.values() if isinstance(item, dict)}
    require(REQUIRED_LANGUAGES.issubset(languages), f"missing languages: {sorted(REQUIRED_LANGUAGES - languages)}")
    for lane_name, lane_doc in lanes.items():
        require(isinstance(lane_doc, dict), f"lane {lane_name} must be object")
        require(lane_doc.get("canonical_backend"), f"lane {lane_name} missing canonical_backend")
        require(lane_doc.get("backend_kind"), f"lane {lane_name} missing backend_kind")
        require(lane_doc.get("language"), f"lane {lane_name} missing language")
        caps = lane_doc.get("required_capabilities")
        require(isinstance(caps, list) and caps, f"lane {lane_name} must declare required_capabilities")
    consumers = data.get("consumers")
    require(isinstance(consumers, list) and consumers, "consumers must be non-empty")
    consumer_repos = {item.get("repo") for item in consumers if isinstance(item, dict)}
    require(REQUIRED_CONSUMERS.issubset(consumer_repos), f"missing consumers: {sorted(REQUIRED_CONSUMERS - consumer_repos)}")
    consumed_records = {record for item in consumers if isinstance(item, dict) for record in item.get("consumes", [])}
    require("FederatedQueryPlane" in consumed_records, "FederatedQueryPlane must be consumed")
    invariant_text = "\n".join(str(item) for item in data.get("invariants", []))
    for required in ["FederatedQueryPlane", "Sherlock", "Slash Topics", "New Hope", "Lampstand", "Ontology query", "PlatformAssetRecord"]:
        require(required in invariant_text, f"missing invariant text for {required}")


def main() -> int:
    path = Path("registry/lattice-federated-query-spine.yaml")
    try:
        validate(path)
        print(f"PASS {path}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL {path}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
