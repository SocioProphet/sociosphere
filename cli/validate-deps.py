#!/usr/bin/env python3
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
