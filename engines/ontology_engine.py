#!/usr/bin/env python3
"""ontology_engine.py — OntologyEngine for the SocioProphet workspace registry.

Queries canonical-repos.yaml and repository-ontology.yaml to answer:
  - Which repos have a given role / tag / layer?
  - Which repos govern / depend on a given repo?
  - What is the full ontological description of a repo?

Stdlib + PyYAML only.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required (pip install pyyaml)", file=sys.stderr)
    raise

REGISTRY_DIR = Path(__file__).resolve().parents[1] / "registry"


def _load(filename: str) -> Any:
    return yaml.safe_load((REGISTRY_DIR / filename).read_text("utf-8"))


class OntologyEngine:
    """Role/tag/layer query engine for the canonical-repos registry."""

    def __init__(self) -> None:
        data = _load("canonical-repos.yaml")
        self._repos: list[dict] = data.get("repos", [])
        ont = _load("repository-ontology.yaml")
        self._roles: dict[str, dict] = {r["id"]: r for r in ont.get("roles", [])}
        self._layers: dict[str, dict] = {la["id"]: la for la in ont.get("layers", [])}
        self._bindings: list[dict] = ont.get("semantic_bindings", [])
        # Index repos by name
        self._by_name: dict[str, dict] = {r["name"]: r for r in self._repos}

    # ── Repo queries ──────────────────────────────────────────────────────────

    def all_repos(self) -> list[dict]:
        return list(self._repos)

    def repo(self, name: str) -> dict | None:
        return self._by_name.get(name)

    def repos_by_layer(self, layer: str) -> list[dict]:
        return [r for r in self._repos if r.get("layer") == layer]

    def repos_by_role(self, role: str) -> list[dict]:
        return [r for r in self._repos if r.get("role") == role]

    def repos_by_tag(self, tag: str) -> list[dict]:
        return [r for r in self._repos if tag in r.get("tags", [])]

    def repos_by_priority(self, priority: str) -> list[dict]:
        return [r for r in self._repos if r.get("priority") == priority]

    def repos_with_open_prs(self) -> list[dict]:
        return [r for r in self._repos if r.get("open_prs", 0) > 0]

    def dedup_candidates(self) -> list[dict]:
        return [r for r in self._repos if r.get("dedup_candidate")]

    def single_branch_exempt(self) -> list[dict]:
        return [r for r in self._repos if r.get("single_branch_exempt")]

    # ── Relationship queries ──────────────────────────────────────────────────

    def dependents_of(self, name: str) -> list[str]:
        """Return repos that declare a depends_on edge to `name`."""
        return [
            b["subject"]
            for b in self._bindings
            if b.get("predicate") == "depends_on" and b.get("object") == name
        ]

    def dependencies_of(self, name: str) -> list[str]:
        """Return repos that `name` depends on."""
        return [
            b["object"]
            for b in self._bindings
            if b.get("predicate") == "depends_on" and b.get("subject") == name
        ]

    def governed_by(self, name: str) -> list[str]:
        """Return standards repos that govern `name`."""
        return [
            b["object"]
            for b in self._bindings
            if b.get("predicate") == "governed_by" and b.get("subject") == name
        ]

    def governs(self, name: str) -> list[str]:
        """Return repos governed by `name`."""
        return [
            b["subject"]
            for b in self._bindings
            if b.get("predicate") == "governed_by" and b.get("object") == name
        ]

    # ── Validation ────────────────────────────────────────────────────────────

    def validate_all_roles(self) -> list[str]:
        """Validate every repo role is declared in the ontology."""
        known = set(self._roles.keys())
        errors: list[str] = []
        for r in self._repos:
            role = r.get("role", "")
            if role and role not in known:
                errors.append(f"{r['name']}: unknown role '{role}'")
        return errors

    def validate_all_layers(self) -> list[str]:
        """Validate every repo layer is declared in the ontology."""
        known = set(self._layers.keys())
        errors: list[str] = []
        for r in self._repos:
            layer = r.get("layer", "")
            if layer and layer not in known:
                errors.append(f"{r['name']}: unknown layer '{layer}'")
        return errors

    # ── Summary ───────────────────────────────────────────────────────────────

    def summary(self) -> dict:
        layers: dict[str, int] = {}
        roles: dict[str, int] = {}
        priorities: dict[str, int] = {}
        statuses: dict[str, int] = {}
        total_open_prs = 0
        for r in self._repos:
            layers[r.get("layer", "unknown")] = layers.get(r.get("layer", "unknown"), 0) + 1
            roles[r.get("role", "unknown")] = roles.get(r.get("role", "unknown"), 0) + 1
            priorities[r.get("priority", "unknown")] = priorities.get(r.get("priority", "unknown"), 0) + 1
            statuses[r.get("status", "unknown")] = statuses.get(r.get("status", "unknown"), 0) + 1
            total_open_prs += r.get("open_prs", 0)
        return {
            "total_repos": len(self._repos),
            "total_open_prs": total_open_prs,
            "by_layer": layers,
            "by_role": roles,
            "by_priority": priorities,
            "by_status": statuses,
            "dedup_candidates": len(self.dedup_candidates()),
        }


def main() -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="OntologyEngine CLI")
    p.add_argument("cmd", choices=["summary", "validate", "list", "repo", "layer", "role", "tag"])
    p.add_argument("--arg", default=None, help="Argument for repo/layer/role/tag queries")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()

    engine = OntologyEngine()

    if args.cmd == "summary":
        result = engine.summary()
    elif args.cmd == "validate":
        role_errors = engine.validate_all_roles()
        layer_errors = engine.validate_all_layers()
        result = {"role_errors": role_errors, "layer_errors": layer_errors, "ok": not (role_errors or layer_errors)}
        if result["ok"]:
            print("OK: all roles and layers valid")
        else:
            for e in role_errors + layer_errors:
                print(f"ERROR: {e}", file=sys.stderr)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    elif args.cmd == "list":
        result = [{"name": r["name"], "layer": r.get("layer"), "role": r.get("role"), "status": r.get("status"), "open_prs": r.get("open_prs", 0)} for r in engine.all_repos()]
    elif args.cmd == "repo":
        if not args.arg:
            print("ERROR: --arg <repo-name> required", file=sys.stderr)
            return 2
        result = engine.repo(args.arg)
        if result is None:
            print(f"ERROR: repo '{args.arg}' not found", file=sys.stderr)
            return 1
    elif args.cmd == "layer":
        if not args.arg:
            print("ERROR: --arg <layer> required", file=sys.stderr)
            return 2
        result = [r["name"] for r in engine.repos_by_layer(args.arg)]
    elif args.cmd == "role":
        if not args.arg:
            print("ERROR: --arg <role> required", file=sys.stderr)
            return 2
        result = [r["name"] for r in engine.repos_by_role(args.arg)]
    elif args.cmd == "tag":
        if not args.arg:
            print("ERROR: --arg <tag> required", file=sys.stderr)
            return 2
        result = [r["name"] for r in engine.repos_by_tag(args.arg)]
    else:
        return 2

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if isinstance(result, dict):
            for k, v in result.items():
                print(f"  {k}: {v}")
        elif isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    print(f"  {item.get('name', item)}")
                else:
                    print(f"  {item}")
        else:
            print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
