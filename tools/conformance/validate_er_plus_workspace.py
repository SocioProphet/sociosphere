#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = ROOT / "components" / "identity_is_prime_reference"
REGIS = ROOT / "components" / "regis_entity_graph"
MANIFEST = ROOT / "manifest" / "identity-prime-workspace.toml"

IDENTITY_REQUIRED = [
    "docs/70_ER_PLUS_INTRINSIC_GEOMETRY.md",
    "schemas/er_plus/ERPlusConfig.v0.1.json",
    "src/prime_er/edit_geometry.py",
    "src/prime_er/entity_geometry.py",
    "src/prime_er/behavior.py",
    "src/prime_er/neutrality.py",
    "tests/test_er_plus_geometry.py",
]

REGIS_REQUIRED = [
    "docs/architecture/er-plus-regis-graph-contract.md",
    "schemas/er_plus/ERPlusEvidenceBundle.v0.1.json",
    "fixtures/er_plus/er_plus_evidence_bundle.valid.json",
    "tools/validate_er_plus_evidence_bundle.py",
]

IDENTITY_CAPABILITIES = [
    "er_plus_record_geometry",
    "er_plus_entity_geometry",
    "er_plus_behavior_features",
    "er_plus_neutrality_replay",
]

REGIS_CAPABILITIES = [
    "er_plus_graph_contract",
    "er_plus_evidence_bundle",
    "er_plus_decision_ledger",
    "er_plus_validator",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def require_path(base: Path, rel: str) -> Path:
    path = base / rel
    if not path.exists():
        fail(f"missing required ER+ workspace artifact: {path}")
    return path


def require_manifest_capabilities() -> None:
    text = MANIFEST.read_text(encoding="utf-8")
    for capability in IDENTITY_CAPABILITIES + REGIS_CAPABILITIES:
        if capability not in text:
            fail(f"workspace overlay missing ER+ capability: {capability}")


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"top-level JSON must be object: {path}")
    return data


def main() -> None:
    require_path(ROOT, "manifest/identity-prime-workspace.toml")
    require_manifest_capabilities()

    for rel in IDENTITY_REQUIRED:
        require_path(IDENTITY, rel)
    for rel in REGIS_REQUIRED:
        require_path(REGIS, rel)

    identity_config = load_json(IDENTITY / "schemas/er_plus/ERPlusConfig.v0.1.json")
    if identity_config.get("properties", {}).get("schema_version", {}).get("const") != "er_plus.config.v0.1":
        fail("Identity ER+ config schema_version const mismatch")

    regis_schema = load_json(REGIS / "schemas/er_plus/ERPlusEvidenceBundle.v0.1.json")
    if regis_schema.get("properties", {}).get("schema_version", {}).get("const") != "regis.er_plus.evidence_bundle.v0.1":
        fail("Regis ER+ evidence bundle schema_version const mismatch")

    regis_fixture = load_json(REGIS / "fixtures/er_plus/er_plus_evidence_bundle.valid.json")
    if regis_fixture.get("schema_version") != "regis.er_plus.evidence_bundle.v0.1":
        fail("Regis ER+ evidence bundle fixture schema_version mismatch")

    certs = regis_fixture.get("certificates", {})
    for required_family in ("record_paths", "entity_paths", "behavioral_evidence", "local_expansion", "neutrality_replays"):
        if not certs.get(required_family):
            fail(f"Regis ER+ fixture missing non-empty certificate family: {required_family}")

    print("OK: Identity Prime ER+ workspace conformance validated")


if __name__ == "__main__":
    main()
