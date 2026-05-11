#!/usr/bin/env python3
"""Validate SocioSphere proof apparatus control-plane artifacts.

This validator is intentionally dependency-light. It parses the proof apparatus
schemas, parses the proof workspace manifest, and validates any materialized
repo-local `proof-adapter.json` files found at the manifest's `local_path`
entries.

It does not prove mathematics. It validates controller metadata shape so proof
claims can fail closed before runner execution.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]

PROOF_MANIFEST = ROOT / "manifest" / "proof-workspace.toml"
CLAIM_SCHEMA = ROOT / "standards" / "proof-apparatus" / "claim-ledger.schema.json"
ADAPTER_SCHEMA = ROOT / "standards" / "proof-apparatus" / "proof-adapter.schema.json"

SEVERITY = {"E0", "E1", "E2", "E3", "E4", "E5", "E6", "E7"}
CLAIM_STATES = {
    "draft",
    "checked",
    "cross_checked",
    "diagnosed",
    "quarantined",
    "promoted",
    "archived",
}
GATE_STATUSES = {"pass", "fail", "skip", "blocked", "planned"}
GATE_KINDS = {
    "test",
    "proof_review",
    "fixture_check",
    "symbolic_check",
    "numeric_check",
    "claim_boundary_check",
    "non_claim_check",
    "obstruction_check",
}


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def load_toml(path: Path) -> dict[str, Any]:
    if tomllib is None:
        fail("Python tomllib is unavailable; use Python 3.11+ for TOML validation")
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError:
        fail(f"missing file: {path}")
    except Exception as exc:  # TOMLDecodeError type differs across runtimes
        fail(f"invalid TOML in {path}: {exc}")


def fail(message: str) -> None:
    print(f"proof-apparatus validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    proof_workspace = manifest.get("proof_workspace")
    require(isinstance(proof_workspace, dict), "manifest missing [proof_workspace]")
    require(proof_workspace.get("controller_repo") == "SocioProphet/sociosphere",
            "proof workspace controller_repo must be SocioProphet/sociosphere")
    require(proof_workspace.get("ledger_mode") == "required",
            "proof workspace ledger_mode must be required")
    require(proof_workspace.get("attestation_required") is True,
            "proof workspace attestation_required must be true")

    repos = manifest.get("repos")
    require(isinstance(repos, list) and repos, "manifest must contain [[repos]] entries")

    for repo in repos:
        require(isinstance(repo, dict), "repo entry must be a table")
        for field in ("name", "role", "domain", "url", "ref", "local_path"):
            require(field in repo, f"repo entry missing required field {field}")
        require(repo["role"] in {"domain-engine", "metatheory-engine", "finite-channel-engine", "analytic-number-theory-engine"},
                f"repo {repo['name']} has unsupported role {repo['role']}")
        require(isinstance(repo.get("owned_gates"), list), f"repo {repo['name']} missing owned_gates")
        require(isinstance(repo.get("primary_walls"), list), f"repo {repo['name']} missing primary_walls")

    return repos


def validate_adapter(path: Path, adapter: dict[str, Any]) -> None:
    for field in ("adapter_version", "repo", "domain", "claims", "gates", "non_claims"):
        require(field in adapter, f"{path} missing required field {field}")

    require(adapter["adapter_version"] == "0.1", f"{path} adapter_version must be 0.1")
    require(isinstance(adapter["repo"], str) and "/" in adapter["repo"], f"{path} repo must be owner/name")
    require(isinstance(adapter["domain"], str) and adapter["domain"], f"{path} domain must be nonempty")
    require(isinstance(adapter["claims"], list), f"{path} claims must be a list")
    require(isinstance(adapter["gates"], list), f"{path} gates must be a list")
    require(isinstance(adapter["non_claims"], list), f"{path} non_claims must be a list")

    for claim in adapter["claims"]:
        for field in ("claim_id", "state", "severity", "statement", "boundary", "owned_gates"):
            require(field in claim, f"{path} claim missing {field}")
        require(claim["state"] in CLAIM_STATES, f"{path} claim {claim['claim_id']} has invalid state")
        require(claim["severity"] in SEVERITY, f"{path} claim {claim['claim_id']} has invalid severity")
        require(isinstance(claim["boundary"], list), f"{path} claim {claim['claim_id']} boundary must be list")
        require(isinstance(claim["owned_gates"], list), f"{path} claim {claim['claim_id']} owned_gates must be list")

    for gate in adapter["gates"]:
        for field in ("gate_id", "kind", "status"):
            require(field in gate, f"{path} gate missing {field}")
        require(gate["kind"] in GATE_KINDS, f"{path} gate {gate['gate_id']} has invalid kind")
        require(gate["status"] in GATE_STATUSES, f"{path} gate {gate['gate_id']} has invalid status")

    for non_claim in adapter["non_claims"]:
        for field in ("non_claim_id", "statement"):
            require(field in non_claim, f"{path} non_claim missing {field}")


def main() -> int:
    load_json(CLAIM_SCHEMA)
    load_json(ADAPTER_SCHEMA)

    manifest = load_toml(PROOF_MANIFEST)
    repos = validate_manifest(manifest)

    checked_adapters = 0
    for repo in repos:
        adapter_path = ROOT / repo["local_path"] / "proof-adapter.json"
        if not adapter_path.exists():
            print(f"warning: materialized adapter not found: {adapter_path}")
            continue
        adapter = load_json(adapter_path)
        validate_adapter(adapter_path, adapter)
        checked_adapters += 1

    print(
        "proof-apparatus validation passed: "
        f"schemas=2 manifest_repos={len(repos)} adapters_checked={checked_adapters}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
