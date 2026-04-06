#!/usr/bin/env python3
"""cli/validate-deps.py

Validate the dependency graph for cycles, orphaned repos, and
missing propagation rules.

Usage:
    python cli/validate-deps.py [--registry-dir PATH] [--strict]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.propagation_engine import PropagationEngine
from engines.ontology_engine import OntologyEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the SocioProphet dependency graph"
    )
    parser.add_argument("--registry-dir", default=None)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on warnings (not just errors)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    print("=== Dependency Graph Validation ===\n")

    # ── Load engines ──────────────────────────────────────────────────────────
    prop = PropagationEngine(args.registry_dir)
    prop.load()
    onto = OntologyEngine(args.registry_dir)
    onto.load()

    all_repo_ids = {r["id"] for r in onto.all_repos()}
    active_repo_ids = {r["id"] for r in onto.repos_by_status("active")}

    # ── Cycle detection ───────────────────────────────────────────────────────
    print("[1/4] Checking for dependency cycles …")
    cycles = prop.detect_cycles()
    if cycles:
        for cycle in cycles:
            errors.append(f"Cycle detected: {' -> '.join(cycle)}")
        print(f"      ERROR: {len(cycles)} cycle(s) found")
    else:
        print("      No cycles ✓")

    # ── Unknown repos in graph ────────────────────────────────────────────────
    print("\n[2/4] Checking for unknown repos in dependency edges …")
    unknown: set[str] = set()
    for repo_id in prop.all_graph_nodes():
        if repo_id not in all_repo_ids:
            unknown.add(repo_id)
    if unknown:
        for repo_id in sorted(unknown):
            warnings.append(
                f"Repo '{repo_id}' appears in dependency graph but not in "
                "canonical-repos.yaml"
            )
        print(f"      WARN: {len(unknown)} unknown repo(s) in graph")
    else:
        print("      All repos in graph are registered ✓")

    # ── Orphaned active repos (no deps, no dependents) ────────────────────────
    print("\n[3/4] Checking for isolated active repos …")
    all_graph_nodes = prop.all_graph_nodes()
    isolated = active_repo_ids - all_graph_nodes
    # Some repos are intentionally standalone (documentation, testing top-level, tooling)
    intentionally_isolated = {
        "architecture-docs", "api-specs", "onboarding-docs", "runbooks",
        "integration-tests", "e2e-tests", "load-tests",
        "workspace-runner",
    }
    truly_isolated = isolated - intentionally_isolated
    if truly_isolated:
        for repo_id in sorted(truly_isolated):
            warnings.append(
                f"Active repo '{repo_id}' has no entries in the dependency graph"
            )
        print(f"      WARN: {len(truly_isolated)} isolated active repo(s)")
    else:
        print("      No unexpected isolated repos ✓")

    # ── Propagation rule coverage ─────────────────────────────────────────────
    print("\n[4/4] Checking propagation rule coverage …")
    rules_by_repo = {r.get("trigger", {}).get("repo") for r in prop.all_rules()}
    # Only check repos with dependents (they are the ones that need rules)
    has_dependents = {
        repo_id
        for repo_id in active_repo_ids
        if prop.dependents_of(repo_id)
    }
    uncovered = has_dependents - rules_by_repo
    if uncovered:
        for repo_id in sorted(uncovered):
            warnings.append(
                f"Repo '{repo_id}' has dependents but no propagation rule"
            )
        print(f"      WARN: {len(uncovered)} repo(s) missing propagation rules")
    else:
        print("      All repos with dependents have propagation rules ✓")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n--- Summary ---")
    if errors:
        print(f"  ERRORS:   {len(errors)}")
        for e in errors:
            print(f"    ✗ {e}")
    if warnings:
        print(f"  WARNINGS: {len(warnings)}")
        for w in warnings:
            print(f"    ⚠ {w}")
    if not errors and not warnings:
        print("  All checks passed ✓")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""
cli/validate-deps.py

Verify that the dependency graph in registry/dependency-graph.yaml is
internally consistent:
  - Every named dependent/dependency exists in canonical-repos.yaml
  - No circular dependencies (direct cycles)

Usage:
    python cli/validate-deps.py
    python cli/validate-deps.py --strict   # fail on missing repo entries too
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
DEP_GRAPH_FILE = REGISTRY_DIR / "dependency-graph.yaml"
CANONICAL_REPOS_FILE = REGISTRY_DIR / "canonical-repos.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(raw) or {}
    return {}


def _known_repos(canonical: dict[str, Any]) -> set[str]:
    """Return the set of all repo names in canonical-repos.yaml."""
    repos = canonical.get("repositories", [])
    names: set[str] = set()
    for r in repos:
        name = r.get("name")
        if name:
            names.add(name)
    # Always include the sentinel used for "all repos in the org".
    names.add("all-repos")
    return names


def _detect_cycles(graph: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Simple cycle detection for direct (length-2) cycles."""
    cycles: list[tuple[str, str]] = []
    for node, neighbours in graph.items():
        for nb in neighbours:
            if node in graph.get(nb, []):
                pair = tuple(sorted([node, nb]))
                if pair not in {tuple(sorted(c)) for c in cycles}:
                    cycles.append((node, nb))
    return cycles


def validate(strict: bool = False) -> int:
    dep_data = _load_yaml(DEP_GRAPH_FILE)
    canonical = _load_yaml(CANONICAL_REPOS_FILE)

    dependencies = dep_data.get("dependencies", {})
    known = _known_repos(canonical)

    errors: list[str] = []
    warnings: list[str] = []

    # Build adjacency list for cycle detection.
    depends_on_graph: dict[str, list[str]] = {}

    for repo, entry in dependencies.items():
        if repo not in known and repo != "all-repos":
            msg = f"repo '{repo}' in dependency-graph not in canonical-repos.yaml"
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)

        dep_list: list[str] = []
        for dep in entry.get("depends_on", []):
            name = dep.get("name") if isinstance(dep, dict) else str(dep)
            if not name:
                continue
            dep_list.append(name)
            if name not in known and name != "all-repos":
                msg = f"dependency '{name}' (used by '{repo}') not in canonical-repos.yaml"
                if strict:
                    errors.append(msg)
                else:
                    warnings.append(msg)

        for dep in entry.get("dependents", []):
            name = dep.get("name") if isinstance(dep, dict) else str(dep)
            if not name:
                continue
            if name not in known and name != "all-repos":
                msg = f"dependent '{name}' (of '{repo}') not in canonical-repos.yaml"
                if strict:
                    errors.append(msg)
                else:
                    warnings.append(msg)

        depends_on_graph[repo] = dep_list

    cycles = _detect_cycles(depends_on_graph)
    for a, b in cycles:
        errors.append(f"circular dependency detected: {a} ↔ {b}")

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  WARN: {w}")

    if errors:
        print("Errors:")
        for e in errors:
            print(f"  ERR: {e}")
        print(f"\nFAIL: {len(errors)} dependency validation error(s)")
        return 1

    total_repos = len(dependencies)
    total_deps = sum(
        len(v.get("depends_on", [])) + len(v.get("dependents", []))
        for v in dependencies.values()
    )
    print(f"OK: dependency graph valid")
    print(f"  Repos with dependency entries: {total_repos}")
    print(f"  Total dependency links:        {total_deps}")
    if warnings:
        print(f"  Warnings (non-fatal):          {len(warnings)}")
    return 0


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    return validate(strict=strict)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
