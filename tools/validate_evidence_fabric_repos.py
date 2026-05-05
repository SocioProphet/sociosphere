#!/usr/bin/env python3
"""Validate the evidence fabric repo-family registry slice."""

from __future__ import annotations

from pathlib import Path
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: python3 -m pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "evidence-fabric-repos.yaml"

REQUIRED_REPOS = {
    "evidence-contracts",
    "evidence-broker",
    "evidence-storage-infra",
    "evidence-connectors-gdrive",
    "evidence-connectors-icloud",
    "evidence-validator",
}

REQUIRED_ARCHITECTURE_RULES = {
    "source systems are ingress only",
    "raw object identity is content-addressed by SHA-256",
    "source aliases are preserved, not collapsed away",
    "Postgres owns metadata, provenance, routing, and processing state",
    "chunking and enrichment are derivative, never primary custody",
    "graph and semantic projection target SHIR and standards-knowledge later",
    "TriTRPC provides deterministic transport only, not evidence semantics",
    "Sociosphere registers topology and workspace control",
    "SourceOS/SociOS enforce local path and mount boundaries",
}


def fail(message: str) -> None:
    print(f"ERR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not REGISTRY.exists():
        fail(f"missing {REGISTRY.relative_to(ROOT)}")

    data = yaml.safe_load(REGISTRY.read_text())
    if not isinstance(data, dict):
        fail("registry must be a mapping")

    if data.get("program") != "evidence-fabric":
        fail("program must be evidence-fabric")

    repos = data.get("planned_repositories")
    if not isinstance(repos, list):
        fail("planned_repositories must be a list")

    ids = {repo.get("id") for repo in repos if isinstance(repo, dict)}
    missing = REQUIRED_REPOS - ids
    extra_empty = {repo.get("id") for repo in repos if not repo.get("purpose")}

    if missing:
        fail(f"missing planned repositories: {sorted(missing)}")
    if extra_empty:
        fail(f"repositories missing purpose: {sorted(extra_empty)}")

    for repo in repos:
        for field in ("id", "name", "org", "layer", "status", "role", "purpose"):
            if field not in repo:
                fail(f"repo {repo.get('id')} missing field {field}")
        if repo.get("org") != "SocioProphet":
            fail(f"repo {repo.get('id')} must be in SocioProphet org")
        if repo.get("status") != "planned":
            fail(f"repo {repo.get('id')} must be planned until created")

    rules = set(data.get("architecture_rules") or [])
    missing_rules = REQUIRED_ARCHITECTURE_RULES - rules
    if missing_rules:
        fail(f"missing architecture rules: {sorted(missing_rules)}")

    acceptance = data.get("phase_1_acceptance") or []
    if len(acceptance) < 5:
        fail("phase_1_acceptance must contain at least five gates")

    print("OK: evidence fabric repo registry is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
