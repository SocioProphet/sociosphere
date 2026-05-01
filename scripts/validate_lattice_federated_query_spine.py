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
    "SocioProphet/memory-mesh",
    "SocioProphet/lampstand",
    "SocioProphet/ontogenesis",
    "SocioProphet/graphbrain-contract",
}
REQUIRED_RECORDS = {
    "FederatedQueryPlane",
    "FederatedQueryEvidence",
    "QueryRoutingDryRunPlan",
    "QueryRoutingEvidence",
}
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
REQUIRED_GOVERNANCE_SEQUENCE = [
    "slash-topic-scope",
    "newhope-membrane-admission",
    "memory-mesh-recall-policy",
    "lab-profile-selection",
    "physical-backend-route",
]
REQUIRED_LAB_PROFILE_REFS = {
    "lab://nlp-lab/default",
    "lab://embedding-lab/default",
    "lab://image-lab/default",
    "lab://speech-lab/default",
    "lab://vision-lab/default",
}
REQUIRED_BOUNDARIES = {
    "dry-run-only",
    "slash-topic-scope-required",
    "newhope-membrane-required",
    "memory-mesh-context-bound",
    "lab-profile-bound",
    "no-remote-query-execution",
    "no-local-index-read",
    "no-memory-writeback",
    "no-embedding-job",
    "no-lab-runtime-call",
    "no-sql-submission",
    "no-sparql-submission",
    "no-cypher-submission",
    "no-atomese-submission",
    "no-sherlock-query-submission",
    "no-topic-pack-read",
    "no-newhope-runtime-call",
    "no-lampstand-rpc-call",
}
REQUIRED_ROUTE_FAMILIES = {
    "drill-sql-route",
    "document-query-route",
    "annotation-query-route",
    "sparql-route",
    "ontology-query-route",
    "cypher-route",
    "graphbrain-route",
    "atomese-route",
    "sherlock-route",
    "slash-topics-route",
    "new-hope-route",
    "lampstand-route",
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
    require(REQUIRED_RECORDS.issubset(record_names), f"missing query records: {sorted(REQUIRED_RECORDS - record_names)}")
    roles = {item.get("repo"): str(item.get("role", "")) for item in producers if isinstance(item, dict)}
    require("public query/governance surface" in roles.get("SocioProphet/slash-topics", ""), "Slash Topics producer role must be public query/governance surface")
    require("internal membrane/runtime substrate" in roles.get("SocioProphet/new-hope", ""), "New Hope producer role must be internal membrane/runtime substrate")
    require("compatibility surface" in roles.get("SocioProphet/new-hope", ""), "New Hope producer role must preserve compatibility surface")

    surface_model = data.get("surface_model")
    require(isinstance(surface_model, dict), "surface_model must be object")
    public_surface = surface_model.get("public_query_surface")
    require(isinstance(public_surface, dict), "public_query_surface must be object")
    require(public_surface.get("repo") == "SocioProphet/slash-topics", "public query surface must be Slash Topics")
    require(public_surface.get("name") == "Slash Topics", "public query surface name mismatch")
    public_refs = set(public_surface.get("refs", []))
    require("slash-topic://" in public_refs, "Slash Topic scope ref missing")
    require("slash-topics://packs/" in public_refs, "Slash Topics pack ref missing")
    require("slash-topics://runtime/membranes/" in public_refs, "Slash Topics runtime alias ref missing")
    public_owns = set(public_surface.get("owns", []))
    for required in ["topic-scope", "topic-pack", "policy-membrane-reference", "deterministic-receipt", "public-lattice-query-adapter"]:
        require(required in public_owns, f"Slash Topics public surface missing {required}")

    runtime_substrate = surface_model.get("runtime_substrate")
    require(isinstance(runtime_substrate, dict), "runtime_substrate must be object")
    require(runtime_substrate.get("repo") == "SocioProphet/new-hope", "runtime substrate must be New Hope")
    require(runtime_substrate.get("name") == "New Hope", "runtime substrate name mismatch")
    runtime_refs = set(runtime_substrate.get("refs", []))
    require("newhope://membranes/" in runtime_refs, "New Hope membrane ref missing")
    require("newhope://protocol-packs/" in runtime_refs, "New Hope protocol-pack compatibility ref missing")
    runtime_owns = set(runtime_substrate.get("owns", []))
    for required in ["carrier", "receptor", "protocol", "membrane-decision", "replay", "provenance", "federation"]:
        require(required in runtime_owns, f"New Hope runtime substrate missing {required}")

    memory_attachment = surface_model.get("memory_attachment")
    require(isinstance(memory_attachment, dict), "memory_attachment must be object")
    require(memory_attachment.get("repo") == "SocioProphet/memory-mesh", "memory attachment must use Memory Mesh")
    require(memory_attachment.get("attaches_to") == "slash-topic-scope", "Memory Mesh must attach to Slash Topic scope")

    migration_policy = surface_model.get("migration_policy")
    require(isinstance(migration_policy, dict), "migration_policy must be object")
    require(migration_policy.get("recommendation") == "keep-slash-topics-as-public-surface-and-new-hope-as-runtime-substrate", "migration recommendation mismatch")
    require(migration_policy.get("future_alias", "").startswith("slash-topics://runtime/membranes/"), "future Slash Topics runtime alias missing")
    require(migration_policy.get("compatibility_ref", "").startswith("newhope://membranes/"), "New Hope compatibility ref missing")
    require(migration_policy.get("forbidden_model") == "ambiguous-peer-public-surfaces", "forbidden ambiguous peer model must be explicit")

    lab_sources = data.get("lab_profile_sources")
    require(isinstance(lab_sources, dict), "lab_profile_sources must be object")
    intended_refs = set(lab_sources.get("intended_capability_refs", []))
    confirmed_refs = {item.get("profile_ref") for item in lab_sources.get("confirmed_repos", []) if isinstance(item, dict)}
    require(REQUIRED_LAB_PROFILE_REFS.issubset(intended_refs | confirmed_refs), "missing required lab profile refs")

    lanes = data.get("query_lanes")
    require(isinstance(lanes, dict), "query_lanes must be object")
    require(REQUIRED_LANES.issubset(lanes), f"missing query lanes: {sorted(REQUIRED_LANES - set(lanes))}")
    languages = {item.get("language") for item in lanes.values() if isinstance(item, dict)}
    require(REQUIRED_LANGUAGES.issubset(languages), f"missing languages: {sorted(REQUIRED_LANGUAGES - languages)}")
    for lane_name, lane_doc in lanes.items():
        require(isinstance(lane_doc, dict), f"lane {lane_name} must be object")
        require(lane_doc.get("canonical_backend"), f"lane {lane_name} missing canonical_backend")
        require(lane_doc.get("backend_kind"), f"lane {lane_name} missing backend_kind")
        require(lane_doc.get("language"), f"lane {lane_name} missing language")
        caps = lane_doc.get("required_capabilities")
        require(isinstance(caps, list) and caps, f"lane {lane_name} must declare required_capabilities")

    envelope = data.get("governance_envelope")
    require(isinstance(envelope, dict), "governance_envelope must be object")
    require(envelope.get("canonical_sequence") == REQUIRED_GOVERNANCE_SEQUENCE, "governance sequence mismatch")
    required_refs = envelope.get("required_refs")
    require(isinstance(required_refs, dict), "governance required_refs must be object")
    require(required_refs.get("topic_scope_ref_prefix") == "slash-topic://", "Slash Topics scope prefix mismatch")
    require(required_refs.get("topic_pack_ref_prefix") == "slash-topics://packs/", "Slash Topics pack prefix mismatch")
    require(required_refs.get("membrane_ref_prefix") == "newhope://membranes/", "New Hope membrane prefix mismatch")
    require(required_refs.get("runtime_alias_ref_prefix") == "slash-topics://runtime/membranes/", "Slash Topics runtime alias prefix mismatch")
    require(required_refs.get("memory_profile_ref_prefix") == "memory-mesh://profiles/", "Memory Mesh profile prefix mismatch")
    require(required_refs.get("memory_event_ref") == "memory-mesh://events/query-route-dry-run", "Memory Mesh event ref mismatch")
    lab_refs = set(envelope.get("required_lab_profile_refs", []))
    require(REQUIRED_LAB_PROFILE_REFS.issubset(lab_refs), f"missing envelope lab refs: {sorted(REQUIRED_LAB_PROFILE_REFS - lab_refs)}")

    routing = data.get("routing_dry_run")
    require(isinstance(routing, dict), "routing_dry_run must be object")
    require(routing.get("canonical_record") == "QueryRoutingDryRunPlan", "routing canonical record mismatch")
    require(routing.get("evidence_record") == "QueryRoutingEvidence", "routing evidence record mismatch")
    boundaries = set(routing.get("required_boundaries", []))
    require(REQUIRED_BOUNDARIES.issubset(boundaries), f"missing route boundaries: {sorted(REQUIRED_BOUNDARIES - boundaries)}")
    families = set(routing.get("required_route_families", []))
    require(REQUIRED_ROUTE_FAMILIES.issubset(families), f"missing route families: {sorted(REQUIRED_ROUTE_FAMILIES - families)}")

    consumers = data.get("consumers")
    require(isinstance(consumers, list) and consumers, "consumers must be non-empty")
    consumer_repos = {item.get("repo") for item in consumers if isinstance(item, dict)}
    require(REQUIRED_CONSUMERS.issubset(consumer_repos), f"missing consumers: {sorted(REQUIRED_CONSUMERS - consumer_repos)}")
    consumed_records = {record for item in consumers if isinstance(item, dict) for record in item.get("consumes", [])}
    require("FederatedQueryPlane" in consumed_records, "FederatedQueryPlane must be consumed")
    require("QueryRoutingDryRunPlan" in consumed_records, "QueryRoutingDryRunPlan must be consumed")

    invariant_text = "\n".join(str(item) for item in data.get("invariants", []))
    for required in [
        "FederatedQueryPlane",
        "QueryRoutingDryRunPlan",
        "Slash Topics is the public query and governance surface",
        "New Hope is the internal membrane/runtime substrate",
        "New Hope must not be treated as a competing peer public product surface",
        "Slash Topics runtime aliases must preserve New Hope compatibility references",
        "Memory Mesh memory settings attach to Slash Topic scopes",
        "lab profile selection",
        "Sherlock",
        "Lampstand",
        "Ontology query",
        "PlatformAssetRecord",
    ]:
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
