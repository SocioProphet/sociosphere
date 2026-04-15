#!/usr/bin/env python3
"""Validate dependency graph entries against the canonical registry.

Checks for unknown repositories referenced by the dependency graph and for
direct dependency cycles. Returns a non-zero exit code when validation fails.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
DEP_GRAPH_FILE = REGISTRY_DIR / "dependency-graph.yaml"
CANONICAL_REPOS_FILE = REGISTRY_DIR / "canonical-repos.yaml"



def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}



def _known_repos(canonical: dict[str, Any]) -> set[str]:
    names = {
        repo.get("name")
        for repo in canonical.get("repositories", [])
        if isinstance(repo, dict) and repo.get("name")
    }
    names.add("all-repos")
    return names



def _detect_cycles(graph: dict[str, list[str]]) -> list[tuple[str, str]]:
    cycles: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for node, neighbours in graph.items():
        for neighbour in neighbours:
            if node in graph.get(neighbour, []):
                cycle = tuple(sorted((node, neighbour)))
                if cycle not in seen:
                    seen.add(cycle)
                    cycles.append((node, neighbour))
    return cycles



def validate(strict: bool = False) -> int:
    dep_data = _load_yaml(DEP_GRAPH_FILE)
    canonical = _load_yaml(CANONICAL_REPOS_FILE)
    dependencies = dep_data.get("dependencies", {})
    known = _known_repos(canonical)

    errors: list[str] = []
    warnings: list[str] = []
    depends_on_graph: dict[str, list[str]] = {}

    for repo, entry in dependencies.items():
        if repo not in known:
            message = f"repo '{repo}' in dependency-graph not in canonical-repos.yaml"
            (errors if strict else warnings).append(message)

        repo_dependencies: list[str] = []
        for dep in entry.get("depends_on", []):
            name = dep.get("name") if isinstance(dep, dict) else str(dep)
            if not name:
                continue
            repo_dependencies.append(name)
            if name not in known:
                message = f"dependency '{name}' (used by '{repo}') not in canonical-repos.yaml"
                (errors if strict else warnings).append(message)
        depends_on_graph[repo] = repo_dependencies

        for dependent in entry.get("dependents", []):
            name = dependent.get("name") if isinstance(dependent, dict) else str(dependent)
            if name and name not in known:
                message = f"dependent '{name}' (declared by '{repo}') not in canonical-repos.yaml"
                (errors if strict else warnings).append(message)

    errors.extend(f"direct cycle: {a} <-> {b}" for a, b in _detect_cycles(depends_on_graph))

    if errors:
        for error in errors:
            print(f"ERR: {error}", file=sys.stderr)
        return 1
    if warnings:
        for warning in warnings:
            print(f"WARN: {warning}", file=sys.stderr)
    return 0



def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    return validate(strict="--strict" in argv)


if __name__ == "__main__":
    raise SystemExit(main())
