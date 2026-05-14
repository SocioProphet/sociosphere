#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as exc:  # noqa: BLE001
    raise SystemExit(f"ERROR: pyyaml required ({exc})")

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "registry" / "interpretability-harness-registration.yaml"
DEPENDENCIES = ROOT / "registry" / "interpretability-harness-dependency-edges.yaml"
CANONICAL = ROOT / "governance" / "interpretability-harness-canonical-sources.yaml"

REQUIRED_BOUND_MODES = {
    "receipt_integration": "hash_bound_reference",
    "authority_scope_analysis": "declared_scope_lattice_v1",
    "non_claim_analysis": "explicit_propagate_or_resolve_v1",
    "monitor_independence_analysis": "declared_monitor_independence_v1",
    "evidence_freshness_analysis": "declared_evidence_freshness_v1",
}

REQUIRED_FRAGMENTS = {
    "ModelArtifact",
    "SAEArtifact",
    "FeatureArtifact",
    "FeatureExplanation",
    "FeatureActivationSet",
    "SteeringIntervention",
    "CausalTriad",
    "AttributionGraph",
    "OffTargetAudit",
    "ManifoldBaseline",
    "ImplementabilityCurve",
    "RobustnessCertificate",
    "BenchmarkResult",
    "PublicInterpretabilityNote",
}

REQUIRED_REGISTRATION_NON_CLAIMS = {
    "does_not_promote_schemas_to_sourceos_spec",
    "does_not_claim_runtime_execution",
    "does_not_claim_runtime_evidence_integration",
    "does_not_claim_provider_api_integration",
    "does_not_claim_live_steering_execution",
    "does_not_claim_public_claim_promotion",
    "does_not_replace_superconscious_as_harness_owner",
    "does_not_replace_procybernetica_as_governance_doctrine_owner",
}

REQUIRED_DEPENDENCY_EDGES = {
    ("superconscious", "ProCybernetica", "governance_doctrine_reference", "active"),
    ("sociosphere", "superconscious", "doctrine_owner_reference", "active"),
    ("superconscious", "sourceos-spec", "schema_promotion_path", "pre_promotion"),
    ("superconscious", "agentplane", "future_runtime_evidence_integration", "deferred"),
    ("superconscious", "policy-fabric", "future_policy_decision_integration", "deferred"),
    ("superconscious", "ontogenesis", "future_ontology_promotion_path", "deferred"),
}

REQUIRED_CANONICAL_NAMESPACES = {
    "research/interpretability-harness": "superconscious",
    "research/interpretability-harness/provider-boundary": "superconscious",
    "research/interpretability-harness/moat": "superconscious",
    "schemas/interpretability-harness": "superconscious",
    "fixtures/interpretability-harness": "superconscious",
    "composition/interpretability-harness-release-bundle": "superconscious",
    "registry/interpretability-harness/neuronpedia-boundary": "superconscious",
    "governance/interpretability-harness": "ProCybernetica",
    "standards/interpretability-harness-schema-promotion": "sourceos-spec",
    "execution/interpretability-harness-runtime-evidence": "agentplane",
}

REQUIRED_BINDING_NON_CLAIMS = {
    "no_runtime_receipt_lookup",
    "no_runtime_non_claim_verification",
    "no_runtime_monitor_attestation",
    "no_timestamp_authenticity",
    "opaque_hashes_not_resolved",
    "no_runtime_provider_access",
    "no_runtime_feature_activation_claim",
    "no_live_steering_execution",
    "no_public_claim_promotion",
    "no_neuronpedia_release_substitution",
}


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"ERROR: missing required file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: expected mapping in {path}")
    return data


def require_equal(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise SystemExit(f"ERROR: {label} expected {expected!r}, got {actual!r}")


def validate_registration() -> None:
    data = load_yaml(REGISTRATION)
    lane = data.get("lane", {})
    require_equal("registration lane.id", lane.get("id"), "interpretability-harness")
    require_equal("registration lane.owner_repo", lane.get("owner_repo"), "SocioProphet/superconscious")
    require_equal("registration lane.status", lane.get("status"), "registered")

    surfaces = data.get("surfaces", {})
    schemas = surfaces.get("schemas", {})
    require_equal("schemas repo", schemas.get("repo"), "SocioProphet/superconscious")
    require_equal("schemas path", schemas.get("path"), "schemas/interpretability/")
    require_equal("schemas promotion_state", schemas.get("promotion_state"), "repo_local_draft")
    require_equal("schemas promotion_target", schemas.get("promotion_target"), "SourceOS-Linux/sourceos-spec")

    checker = surfaces.get("checker", {})
    require_equal("checker path", checker.get("path"), "scripts/check-interpretability-harness.py")
    require_equal("checker ci_target", checker.get("ci_target"), "make interpretability-harness-ci")

    binding = surfaces.get("tier2_binding", {})
    require_equal("tier2 binding path", binding.get("path"), "schemas/composition/interpretability-harness-tier2-binding.v1.json")
    require_equal("tier2 binding composition_id", binding.get("composition_id"), "superconscious.interpretability_harness.release_bundle")
    require_equal("tier2 binding fragment_count", binding.get("fragment_count"), 14)
    if set(binding.get("required_fragments", [])) != REQUIRED_FRAGMENTS:
        raise SystemExit("ERROR: tier2 binding required_fragments must match the exact 14-fragment harness boundary")
    for key, expected in REQUIRED_BOUND_MODES.items():
        require_equal(f"bound mode {key}", binding.get("bound_modes", {}).get(key), expected)

    governance = surfaces.get("governance_doctrine", {})
    require_equal("governance doctrine repo", governance.get("repo"), "SocioProphet/ProCybernetica")
    governance_paths = set(governance.get("paths", []))
    for required_path in [
        "docs/governance-fabric/TIER2_COMPOSITION_INVARIANTS.md",
        "docs/governance-fabric/INTERPRETABILITY_HARNESS_RELEASE_COMPOSITION.md",
    ]:
        if required_path not in governance_paths:
            raise SystemExit(f"ERROR: governance_doctrine missing path {required_path}")

    boundary = surfaces.get("registry_source_boundary", {})
    require_equal("registry source provider", boundary.get("provider"), "neuronpedia")
    require_equal("registry source access_mode", boundary.get("access_mode"), "registry_only")
    forbidden_uses = set(boundary.get("forbidden_uses", []))
    for required in ["live_runtime_replay", "feature_steering_authority", "public_claim_promotion"]:
        if required not in forbidden_uses:
            raise SystemExit(f"ERROR: registry_source_boundary missing forbidden use {required}")

    relationships = data.get("canonical_relationships", {})
    expected_relationships = {
        "doctrine_owner": "SocioProphet/superconscious",
        "governance_doctrine_owner": "SocioProphet/ProCybernetica",
        "registry_owner": "SocioProphet/sociosphere",
        "future_schema_standard_owner": "SourceOS-Linux/sourceos-spec",
        "future_runtime_evidence_owner": "SocioProphet/agentplane",
        "future_policy_decision_owner": "SocioProphet/policy-fabric",
        "future_ontology_owner": "SocioProphet/ontogenesis",
    }
    for key, expected in expected_relationships.items():
        require_equal(f"canonical_relationships.{key}", relationships.get(key), expected)

    missing_non_claims = REQUIRED_REGISTRATION_NON_CLAIMS - set(data.get("non_claims", []))
    if missing_non_claims:
        raise SystemExit(f"ERROR: registration missing non-claims: {sorted(missing_non_claims)}")


def validate_dependencies() -> None:
    data = load_yaml(DEPENDENCIES)
    seen = set()
    for edge in data.get("edges", []):
        if edge.get("lane") != "interpretability-harness":
            raise SystemExit(f"ERROR: dependency edge missing lane interpretability-harness: {edge}")
        seen.add((edge.get("from"), edge.get("to"), edge.get("type"), edge.get("state")))
    missing = REQUIRED_DEPENDENCY_EDGES - seen
    if missing:
        raise SystemExit(f"ERROR: missing required dependency edges: {sorted(missing)}")

    non_claims = set(data.get("non_claims", []))
    for required in [
        "does_not_create_runtime_dependency",
        "does_not_promote_schemas_to_sourceos_spec",
        "does_not_claim_agentplane_runtime_integration",
        "does_not_claim_policy_fabric_admission_integration",
        "does_not_claim_ontogenesis_vocabulary_promotion",
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
        require_equal(f"canonical namespace {namespace} repo", entry.get("canonical_repo"), expected_repo)

    bundle = data.get("binding_refs", {}).get("interpretability_harness_release_bundle", {})
    require_equal("binding ref repo", bundle.get("repo"), "superconscious")
    require_equal("binding ref path", bundle.get("path"), "schemas/composition/interpretability-harness-tier2-binding.v1.json")
    missing_binding_non_claims = REQUIRED_BINDING_NON_CLAIMS - set(bundle.get("non_claims", []))
    if missing_binding_non_claims:
        raise SystemExit(f"ERROR: binding ref missing non-claims: {sorted(missing_binding_non_claims)}")

    non_claims = set(data.get("non_claims", []))
    for required in [
        "does_not_rewrite_governance_CANONICAL_SOURCES_yaml",
        "does_not_promote_schemas_to_sourceos_spec",
        "does_not_claim_runtime_execution",
        "does_not_claim_runtime_evidence_integration",
        "does_not_claim_provider_api_integration",
        "does_not_change_harness_owner",
        "does_not_change_governance_doctrine_owner",
    ]:
        if required not in non_claims:
            raise SystemExit(f"ERROR: canonical source pack missing non-claim {required}")


def main() -> None:
    validate_registration()
    validate_dependencies()
    validate_canonical_sources()
    print("OK: interpretability harness estate registration validates")


if __name__ == "__main__":
    main()
