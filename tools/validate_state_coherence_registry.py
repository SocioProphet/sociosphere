#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry" / "state-coherence"

REQUIRED_REPO_REFS = {
    "github://SocioProphet/prophet-platform",
    "github://SocioProphet/sociosphere",
    "github://SourceOS-Linux/sourceos-syncd",
    "github://SourceOS-Linux/agent-machine",
    "github://SourceOS-Linux/BearBrowser",
    "github://SocioProphet/guardrail-fabric",
    "github://SocioProphet/agentplane",
    "github://SocioProphet/ontogenesis",
}

REQUIRED_SURFACES = {
    "release-proof-to-runtime-evidence",
    "gitops-readiness-to-local-demo-summary",
    "runtime-dry-run-to-agentplane-run-linkage",
    "runtime-dry-run-to-policyplane-decision-linkage",
    "agent-machine-node-profile-to-runtime-adapter",
    "immutable-update-readiness-to-demo-artifact-index",
    "sourceos-state-integrity-to-supporting-evidence-plane",
    "guardrail-decision-abi-to-policy-boundary",
    "operator-surfaces-to-sourceos-node-profile",
    "semantic-contracts-to-governed-evidence-plane",
    "state-coherence-summary-to-operator-artifacts",
    "state-coherence-html-to-browser-index",
}

REQUIRED_CHECKS = {
    "validate",
    "ci",
    "FogStack Local Demo",
    "FogStack Release Proof",
    "FogStack Release Proof Canonical Refs",
    "FogStack Wider Release Graph",
    "platform-contracts-check",
    "premerge-audit",
    "brokerage-validation",
    "platform-wave1-stubs",
    "workspace-operation-runtime",
}

REQUIRED_FOLLOW_ON_PRS = {426, 428}


def fail(path: Path, message: str) -> None:
    raise SystemExit(f"{path}: {message}")


def require_str(record: dict[str, Any], key: str, path: Path) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        fail(path, f"missing non-empty string field: {key}")
    return value


def require_list(record: dict[str, Any], key: str, path: Path) -> list[Any]:
    value = record.get(key)
    if not isinstance(value, list) or not value:
        fail(path, f"missing non-empty list field: {key}")
    return value


def require_operator_visibility(record: dict[str, Any], path: Path) -> None:
    visibility = record.get("operator_visibility")
    if not isinstance(visibility, dict):
        fail(path, "operator_visibility must be an object")
    if visibility.get("status") != "linked":
        fail(path, "operator_visibility.status must be linked")
    expected = {
        "state_coherence_markdown": "build/fogstack-local-demo/fogstack-local-demo.state-coherence.md",
        "state_coherence_html": "build/fogstack-local-demo/state-coherence.html",
        "browser_index": "build/fogstack-local-demo/index.html",
        "browser_index_link": "state-coherence.html",
    }
    for key, value in expected.items():
        if visibility.get(key) != value:
            fail(path, f"operator_visibility.{key} must be {value}")
    checks = set(visibility.get("checks", []))
    required = {"state_coherence_operator_artifacts_emitted", "state_coherence_index_linked"}
    if not required.issubset(checks):
        missing = sorted(required - checks)
        fail(path, f"operator_visibility.checks missing: {missing}")


def require_follow_on_evidence(record: dict[str, Any], path: Path) -> None:
    follow_on = require_list(record, "follow_on_evidence", path)
    by_pr: dict[int, dict[str, Any]] = {}
    for entry in follow_on:
        if not isinstance(entry, dict):
            fail(path, "follow_on_evidence entries must be objects")
        pr_number = entry.get("prophet_platform_pr")
        if isinstance(pr_number, int):
            by_pr[pr_number] = entry

    missing = sorted(REQUIRED_FOLLOW_ON_PRS - set(by_pr))
    if missing:
        fail(path, f"follow_on_evidence missing PRs: {missing}")

    expected_commits = {
        426: "e6e38cf32e2cdb7cc281d9f69fde9ec81af351ff",
        428: "97626e52adf3271072b44b21d3055120886be912",
    }
    for pr_number, expected_commit in expected_commits.items():
        entry = by_pr[pr_number]
        if entry.get("merged_commit") != expected_commit:
            fail(path, f"follow_on_evidence PR {pr_number} merged_commit must be {expected_commit}")
        if not isinstance(entry.get("purpose"), str) or not entry["purpose"]:
            fail(path, f"follow_on_evidence PR {pr_number} purpose must be non-empty")
        checks = set(entry.get("checks", []))
        if not REQUIRED_CHECKS.issubset(checks):
            missing_checks = sorted(REQUIRED_CHECKS - checks)
            fail(path, f"follow_on_evidence PR {pr_number} missing checks: {missing_checks}")


def validate_record(path: Path) -> None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(path, f"invalid JSON: {exc}")

    if not isinstance(record, dict):
        fail(path, "record must be a JSON object")

    if record.get("kind") != "SociosphereStateCoherenceRecord":
        fail(path, "kind must be SociosphereStateCoherenceRecord")
    if record.get("schema_version") != "v0.1":
        fail(path, "schema_version must be v0.1")
    if record.get("status") not in {"proposed", "merged", "superseded"}:
        fail(path, "status must be proposed, merged, or superseded")

    for key in (
        "record_id",
        "subject_ref",
        "subject_commit",
        "posture",
        "demo_boundary",
        "production_boundary",
        "canonical_demo_command",
        "emitted_summary",
        "emitted_section",
    ):
        require_str(record, key, path)

    if record["posture"] != "compressed-estate-demo-coherence":
        fail(path, "posture must be compressed-estate-demo-coherence")
    if record["demo_boundary"] != "bounded-local-non-mutating":
        fail(path, "demo_boundary must be bounded-local-non-mutating")
    if record["canonical_demo_command"] != "make fogstack-local-demo-full":
        fail(path, "canonical_demo_command must be make fogstack-local-demo-full")
    if record["emitted_section"] != "state_coherence":
        fail(path, "emitted_section must be state_coherence")

    require_operator_visibility(record, path)
    require_follow_on_evidence(record, path)

    repo_refs = set(require_list(record, "repo_refs", path))
    if not REQUIRED_REPO_REFS.issubset(repo_refs):
        missing = sorted(REQUIRED_REPO_REFS - repo_refs)
        fail(path, f"missing required repo_refs: {missing}")

    integration_surfaces = set(require_list(record, "integration_surfaces", path))
    if not REQUIRED_SURFACES.issubset(integration_surfaces):
        missing = sorted(REQUIRED_SURFACES - integration_surfaces)
        fail(path, f"missing required integration_surfaces: {missing}")

    validation_evidence = record.get("validation_evidence")
    if not isinstance(validation_evidence, dict):
        fail(path, "validation_evidence must be an object")
    if validation_evidence.get("prophet_platform_pr") != 420:
        fail(path, "validation_evidence.prophet_platform_pr must be 420")
    if validation_evidence.get("merged_commit") != record.get("subject_commit"):
        fail(path, "validation_evidence.merged_commit must match subject_commit")
    checks = set(validation_evidence.get("checks", []))
    if not REQUIRED_CHECKS.issubset(checks):
        missing = sorted(REQUIRED_CHECKS - checks)
        fail(path, f"missing validation checks: {missing}")

    acceptance = require_list(record, "acceptance", path)
    if len(acceptance) < 3:
        fail(path, "acceptance must contain at least three statements")


def main() -> int:
    if not REGISTRY_DIR.exists():
        fail(REGISTRY_DIR, "registry directory missing")
    records = sorted(REGISTRY_DIR.glob("*.json"))
    if not records:
        fail(REGISTRY_DIR, "no state coherence records found")
    for record in records:
        validate_record(record)
    print(f"validated {len(records)} state coherence record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
