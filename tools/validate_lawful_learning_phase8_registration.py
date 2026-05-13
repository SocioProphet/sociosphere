#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

try:
    import yaml  # type: ignore
except Exception as exc:  # noqa: BLE001
    raise SystemExit(f"ERROR: pyyaml required ({exc})")

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "registry" / "lawful-learning-registration.yaml"
DEPENDENCIES = ROOT / "registry" / "lawful-learning-dependency-edges.yaml"
CANONICAL = ROOT / "governance" / "lawful-learning-canonical-sources.yaml"

REQUIRED_BOUND_MODES = {
    "receipt_integration": "hash_bound_reference",
    "authority_scope_analysis": "declared_scope_lattice_v1",
    "non_claim_analysis": "explicit_propagate_or_resolve_v1",
    "monitor_independence_analysis": "declared_monitor_independence_v1",
    "evidence_freshness_analysis": "declared_evidence_freshness_v1",
}

REQUIRED_REGISTRATION_NON_CLAIMS = {
    "does_not_promote_schemas_to_sourceos_spec",
    "does_not_claim_runtime_execution",
    "does_not_claim_runtime_evidence_integration",
    "does_not_claim_tier2_verified_modes",
    "does_not_claim_cross_plane_evidence_resolution",
    "does_not_replace_superconscious_as_doctrine_owner",
}

REQUIRED_DEPENDENCY_EDGES = {
    ("superconscious", "sourceos-spec", "schema_promotion_path", "pre_promotion"),
    ("superconscious", "systems-learning-loops", "research_evidence_reference", "active"),
    ("systems-learning-loops", "sociosphere", "estate_registration_reference", "active"),
    ("sociosphere", "superconscious", "doctrine_owner_reference", "active"),
    ("superconscious", "agentplane", "future_runtime_evidence_integration", "deferred"),
}

REQUIRED_CANONICAL_NAMESPACES = {
    "research/lawful-learning": "superconscious",
    "research/lawful-learning/sources": "systems-learning-loops",
    "research/lawful-learning/claims": "systems-learning-loops",
    "research/lawful-learning/patterns": "systems-learning-loops",
    "ontology/lawful-learning": "systems-learning-loops",
    "standards/lawful-learning-schema-promotion": "sourceos-spec",
    "execution/lawful-learning-runtime-evidence": "agentplane",
}


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"ERROR: missing required file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: expected mapping in {path}")
    return data


def validate_registration() -> None:
    data = load_yaml(REGISTRATION)
    lane = data.get("lane", {})
    if lane.get("id") != "lawful-learning":
        raise SystemExit("ERROR: registration lane.id must be lawful-learning")
    if lane.get("owner_repo") != "SocioProphet/superconscious":
        raise SystemExit("ERROR: lawful-learning doctrine owner must be SocioProphet/superconscious")

    surfaces = data.get("surfaces", {})
    checker = surfaces.get("checker", {})
    if checker.get("ci_target") != "make lawful-learning-ci":
        raise SystemExit("ERROR: checker ci_target must be make lawful-learning-ci")

    schemas = surfaces.get("schemas", {})
    if schemas.get("promotion_target") != "SourceOS-Linux/sourceos-spec":
        raise SystemExit("ERROR: schema promotion target must be SourceOS-Linux/sourceos-spec")
    if schemas.get("promotion_state") != "repo_local_draft":
        raise SystemExit("ERROR: schema promotion_state must be repo_local_draft")

    binding = surfaces.get("tier2_binding", {})
    modes = binding.get("bound_modes", {})
    for key, expected in REQUIRED_BOUND_MODES.items():
        actual = modes.get(key)
        if actual != expected:
            raise SystemExit(f"ERROR: bound mode {key} expected {expected}, got {actual}")

    relationships = data.get("canonical_relationships", {})
    expected_relationships = {
        "doctrine_owner": "SocioProphet/superconscious",
        "evidence_pack_owner": "SocioProphet/systems-learning-loops",
        "registry_owner": "SocioProphet/sociosphere",
        "future_schema_standard_owner": "SourceOS-Linux/sourceos-spec",
        "runtime_evidence_owner": "SocioProphet/agentplane",
    }
    for key, expected in expected_relationships.items():
        if relationships.get(key) != expected:
            raise SystemExit(f"ERROR: canonical_relationships.{key} expected {expected}, got {relationships.get(key)}")

    missing_non_claims = REQUIRED_REGISTRATION_NON_CLAIMS - set(data.get("non_claims", []))
    if missing_non_claims:
        raise SystemExit(f"ERROR: registration missing non-claims: {sorted(missing_non_claims)}")


def validate_dependencies() -> None:
    data = load_yaml(DEPENDENCIES)
    seen = set()
    for edge in data.get("edges", []):
        seen.add((edge.get("from"), edge.get("to"), edge.get("type"), edge.get("state")))
        if edge.get("lane") != "lawful-learning":
            raise SystemExit(f"ERROR: dependency edge missing lane lawful-learning: {edge}")
    missing = REQUIRED_DEPENDENCY_EDGES - seen
    if missing:
        raise SystemExit(f"ERROR: missing required dependency edges: {sorted(missing)}")

    non_claims = set(data.get("non_claims", []))
    for required in [
        "does_not_create_runtime_dependency",
        "does_not_promote_schemas_to_sourceos_spec",
        "does_not_claim_phase9_runtime_integration",
        "does_not_change_dependency_graph_aggregate",
    ]:
        if required not in non_claims:
            raise SystemExit(f"ERROR: dependency pack missing non-claim {required}")


def validate_canonical_sources() -> None:
    data = load_yaml(CANONICAL)
    namespaces = data.get("namespaces", {})
    for namespace, expected_repo in REQUIRED_CANONICAL_NAMESPACES.items():
        entry = namespaces.get(namespace)
        if not isinstance(entry, dict):
            raise SystemExit(f"ERROR: missing canonical namespace {namespace}")
        if entry.get("canonical_repo") != expected_repo:
            raise SystemExit(
                f"ERROR: canonical namespace {namespace} expected repo {expected_repo}, got {entry.get('canonical_repo')}"
            )

    binding = data.get("binding_refs", {}).get("lawful_learning_trust_surface", {})
    if binding.get("repo") != "superconscious":
        raise SystemExit("ERROR: binding_refs.lawful_learning_trust_surface.repo must be superconscious")
    if "schemas/composition/lawful-learning-trust-surface-tier2-binding.v1.json" != binding.get("path"):
        raise SystemExit("ERROR: lawful-learning trust-surface binding path mismatch")

    non_claims = set(data.get("non_claims", []))
    for required in [
        "does_not_rewrite_governance_CANONICAL_SOURCES_yaml",
        "does_not_promote_schemas_to_sourceos_spec",
        "does_not_claim_runtime_execution",
        "does_not_claim_runtime_evidence_integration",
        "does_not_change_doctrine_owner",
    ]:
        if required not in non_claims:
            raise SystemExit(f"ERROR: canonical source pack missing non-claim {required}")


def main() -> None:
    validate_registration()
    validate_dependencies()
    validate_canonical_sources()
    print("OK: lawful-learning Phase 8 registration validates")


if __name__ == "__main__":
    main()
