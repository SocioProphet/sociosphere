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
    for repo_id in list(prop._adjacency.keys()) + list(prop._reverse_adjacency.keys()):
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
    all_graph_nodes = (
        set(prop._adjacency.keys()) | set(prop._reverse_adjacency.keys())
    )
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
