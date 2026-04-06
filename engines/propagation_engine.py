#!/usr/bin/env python3
"""propagation_engine.py — PropagationEngine for the SocioProphet workspace registry.

Computes BFS cascade from change-propagation-rules.yaml.
Detects cycles in the dependency graph.
Exposes all_graph_nodes() and cascade_from(repo).

Stdlib + PyYAML only.
"""
from __future__ import annotations

import sys
from collections import deque
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


class PropagationEngine:
    """BFS cascade computation with cycle detection."""

    def __init__(self) -> None:
        rules_data = _load("change-propagation-rules.yaml")
        self._rules: list[dict] = rules_data.get("rules", [])
        # Build adjacency: trigger_repo -> [(target, action, rule_id)]
        self._adj: dict[str, list[tuple[str, str, str]]] = {}
        for rule in self._rules:
            src = rule["trigger_repo"]
            if src not in self._adj:
                self._adj[src] = []
            for cascade in rule.get("cascades", []):
                self._adj[src].append((cascade["target"], cascade["action"], rule["id"]))

        dep_data = _load("dependency-graph.yaml")
        self._edges: list[dict] = dep_data.get("edges", [])
        # Dependency adjacency: from -> [to]
        self._dep_adj: dict[str, list[str]] = {}
        for edge in self._edges:
            src = edge["from"]
            if src not in self._dep_adj:
                self._dep_adj[src] = []
            self._dep_adj[src].append(edge["to"])

    def all_graph_nodes(self) -> set[str]:
        """Return all repos that appear in propagation rules."""
        nodes: set[str] = set()
        for rule in self._rules:
            nodes.add(rule["trigger_repo"])
            for c in rule.get("cascades", []):
                nodes.add(c["target"])
        return nodes

    def cascade_from(self, repo: str, max_depth: int = 10) -> list[dict]:
        """BFS: compute full cascade of effects when `repo` merges to main."""
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(repo, 0)])
        result: list[dict] = []
        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            if current in visited:
                continue
            visited.add(current)
            for target, action, rule_id in self._adj.get(current, []):
                result.append({
                    "trigger": current,
                    "target": target,
                    "action": action,
                    "rule": rule_id,
                    "depth": depth + 1,
                })
                if target not in visited:
                    queue.append((target, depth + 1))
        return result

    def detect_cycles(self) -> list[list[str]]:
        """Detect cycles in the dependency graph using DFS."""
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[list[str]] = []

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in self._dep_adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(list(path[cycle_start:]) + [neighbor])
            path.pop()
            rec_stack.discard(node)

        all_nodes = set(self._dep_adj.keys())
        for edge in self._edges:
            all_nodes.add(edge["to"])
        for node in all_nodes:
            if node not in visited:
                dfs(node, [])
        return cycles

    def topological_order(self) -> list[str]:
        """Return nodes in topological order (dependencies before dependents)."""
        all_nodes: set[str] = set(self._dep_adj.keys())
        for edge in self._edges:
            all_nodes.add(edge["from"])
            all_nodes.add(edge["to"])

        in_degree: dict[str, int] = {n: 0 for n in all_nodes}
        for src, targets in self._dep_adj.items():
            for t in targets:
                in_degree[t] = in_degree.get(t, 0) + 1

        queue: deque[str] = deque(n for n in all_nodes if in_degree.get(n, 0) == 0)
        order: list[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in self._dep_adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return order

    def safe_merge_order(self) -> list[str]:
        """Return repos in topological dependency order — safe merge sequence."""
        return self.topological_order()


def main() -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="PropagationEngine CLI")
    p.add_argument("cmd", choices=["cascade", "cycles", "merge-order", "nodes"])
    p.add_argument("--repo", default=None, help="Repo name for cascade query")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()

    engine = PropagationEngine()

    if args.cmd == "cascade":
        if not args.repo:
            print("ERROR: --repo <name> required", file=sys.stderr)
            return 2
        result = engine.cascade_from(args.repo)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"Cascade from: {args.repo}")
            for item in result:
                print(f"  depth={item['depth']} [{item['action'].upper()}] {item['trigger']} -> {item['target']}  ({item['rule']})")
    elif args.cmd == "cycles":
        cycles = engine.detect_cycles()
        if cycles:
            print("CYCLES DETECTED:", file=sys.stderr)
            for c in cycles:
                print(f"  {' -> '.join(c)}", file=sys.stderr)
            return 1
        else:
            print("OK: no cycles detected")
    elif args.cmd == "merge-order":
        order = engine.safe_merge_order()
        if args.format == "json":
            print(json.dumps(order, indent=2))
        else:
            print("Safe merge order (dependencies first):")
            for i, repo in enumerate(order, 1):
                print(f"  {i:2d}. {repo}")
    elif args.cmd == "nodes":
        nodes = sorted(engine.all_graph_nodes())
        if args.format == "json":
            print(json.dumps(nodes, indent=2))
        else:
            for n in nodes:
                print(f"  {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
