#!/usr/bin/env python3
"""Validate the evidence fabric surface-integration registry slice."""

from __future__ import annotations

from pathlib import Path
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: python3 -m pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "evidence-fabric-surface-integrations.yaml"

REQUIRED_SURFACES = {
    "exodus-dashboard",
    "sociosphere-workspace",
    "email-ingest",
    "cloud-drive-ingest",
    "local-file-ingest",
    "sourceos-office-shell",
    "browser-and-terminal-capture",
    "notes-and-mobile-device-exports",
    "search-and-knowledge-projection",
    "proof-pack-export",
}

REQUIRED_PRINCIPLES = {
    "source systems are ingress only",
    "user-facing migration must be guided, explainable, and reversible",
    "raw evidence custody must precede parsing, chunking, and semantic projection",
    "email, documents, notes, media, console logs, browser exports, and cloud-drive objects use one broker path",
    "duplicate content collapses by hash while all source aliases remain preserved",
    "provider APIs and accounts are quarantine/ingress surfaces, not platform authority",
    "workspace UX should expose status, next actions, blockers, and proof packs",
    "no source-system deletion occurs before mirror parity, manifest parity, and cooling-off checks",
}

REQUIRED_METRICS = {
    "provider_control_surface_score",
    "exit_readiness_index",
    "migrated_blob_count",
    "migrated_unique_bytes",
    "duplicate_bytes_eliminated",
    "source_aliases_preserved",
    "blocked_objects_count",
    "open_format_conversion_count",
    "proof_pack_count",
    "source_deletion_eligible_count",
}

REQUIRED_WORKFLOW_PHRASES = {
    "connect source account or select local export",
    "preview provider topology and estimated size",
    "choose migration wave",
    "land raw content into canonical object store",
    "review dedupe and source aliases",
    "process text/log/document/media derivatives",
    "review blockers and next best actions",
    "export proof pack",
    "mark source provider as retained, downgraded, or deletion-eligible after cooling-off",
}


def fail(message: str) -> None:
    print(f"ERR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not REGISTRY.exists():
        fail(f"missing {REGISTRY.relative_to(ROOT)}")

    data = yaml.safe_load(REGISTRY.read_text())
    if not isinstance(data, dict):
        fail("surface integration registry must be a mapping")

    if data.get("program") != "evidence-fabric":
        fail("program must be evidence-fabric")

    principles = set(data.get("principles") or [])
    missing_principles = REQUIRED_PRINCIPLES - principles
    if missing_principles:
        fail(f"missing principles: {sorted(missing_principles)}")

    integrations = data.get("surface_integrations")
    if not isinstance(integrations, list):
        fail("surface_integrations must be a list")

    ids = {item.get("id") for item in integrations if isinstance(item, dict)}
    missing_surfaces = REQUIRED_SURFACES - ids
    if missing_surfaces:
        fail(f"missing required surfaces: {sorted(missing_surfaces)}")

    for item in integrations:
        for field in ("id", "owning_repo", "surface_type", "status", "user_value", "evidence_fabric_role", "phase"):
            if field not in item:
                fail(f"surface {item.get('id')} missing field {field}")
        roles = item.get("evidence_fabric_role")
        if not isinstance(roles, list) or not roles:
            fail(f"surface {item.get('id')} must define at least one evidence_fabric_role")

    metrics = set(data.get("exodus_acceleration_metrics") or [])
    missing_metrics = REQUIRED_METRICS - metrics
    if missing_metrics:
        fail(f"missing exodus metrics: {sorted(missing_metrics)}")

    workflows = set(data.get("minimum_user_workflows") or [])
    missing_workflows = REQUIRED_WORKFLOW_PHRASES - workflows
    if missing_workflows:
        fail(f"missing workflow steps: {sorted(missing_workflows)}")

    print("OK: evidence fabric surface integrations are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
