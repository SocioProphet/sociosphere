#!/usr/bin/env python3
"""
engines/propagation_engine.py

Listen for GitHub webhook events (push to main branch), identify the changed
repository, look up its dependents in registry/dependency-graph.yaml and
registry/change-propagation-rules.yaml, then trigger re-validation / re-build
/ re-test in downstream repos.

All propagation events are logged to metrics/propagation-log.jsonl.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
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
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
METRICS_DIR = ROOT / "metrics"
DEP_GRAPH_FILE = REGISTRY_DIR / "dependency-graph.yaml"
PROP_RULES_FILE = REGISTRY_DIR / "change-propagation-rules.yaml"
PROPAGATION_LOG = METRICS_DIR / "propagation-log.jsonl"


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file, returning an empty dict on failure."""
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(raw) or {}
    return {}


def get_dependents(repo_name: str, dep_graph: dict[str, Any]) -> list[str]:
    """Return the list of repos that depend on repo_name."""
    entry = dep_graph.get("dependencies", {}).get(repo_name, {})
    deps = entry.get("dependents", [])
    result: list[str] = []
    for d in deps:
        name = d.get("name") if isinstance(d, dict) else str(d)
        if name and name != "all-repos":
            result.append(name)
    return result


def get_propagation_rules(repo_name: str, rules: dict[str, Any]) -> dict[str, Any]:
    """Return the on_main_merge automation rules for repo_name."""
    return rules.get("propagation_rules", {}).get(repo_name, {}).get("on_main_merge", {})


def _log_event(event: dict[str, Any]) -> None:
    """Append a propagation event to the JSONL log."""
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with PROPAGATION_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def simulate_automation(action_type: str, targets: list[str], repo: str) -> dict[str, Any]:
    """
    Simulate (or in production, trigger) an automation action.

    Returns a result dict with status and details.
    """
    # In a real deployment this would call GitHub Actions / CI APIs.
    return {
        "action": action_type,
        "targets": targets,
        "triggered_by": repo,
        "status": "triggered",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


def propagate(repo_name: str, ref: str = "refs/heads/main") -> int:
    """
    Core propagation logic.

    Given a repository name and the ref that changed, look up dependents and
    automation rules, then trigger downstream actions.

    Returns 0 on success, non-zero on failure.
    """
    if not ref.endswith("/main"):
        print(f"INFO: skipping propagation for non-main ref '{ref}'")
        return 0

    dep_graph = _load_yaml(DEP_GRAPH_FILE)
    rules = _load_yaml(PROP_RULES_FILE)

    dependents = get_dependents(repo_name, dep_graph)
    automation = get_propagation_rules(repo_name, rules)

    event: dict[str, Any] = {
        "repo": repo_name,
        "ref": ref,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "dependents": dependents,
        "automation_trigger": automation.get("trigger", ""),
        "affected_repos": automation.get("affected_repos", []),
        "actions_triggered": [],
        "status": "success",
    }

    if not dependents and not automation:
        print(f"INFO: no propagation rules for '{repo_name}'")
        _log_event(event)
        return 0

    print(f"Propagating changes from '{repo_name}' …")
    print(f"  Dependents:     {dependents or '(none)'}")
    print(f"  Trigger:        {automation.get('trigger', '(none)')}")
    print(f"  Affected repos: {automation.get('affected_repos', '(none)')}")

    actions_triggered: list[dict[str, Any]] = []
    for action in automation.get("automation", []):
        action_type = action.get("type", "unknown")
        targets = action.get("targets", [])
        result = simulate_automation(action_type, targets, repo_name)
        actions_triggered.append(result)
        print(f"  → [{action_type}] targets={targets} — {result['status']}")

    event["actions_triggered"] = actions_triggered
    _log_event(event)
    print(f"OK: propagation complete ({len(actions_triggered)} action(s) triggered)")
    return 0


def main(argv: list[str]) -> int:
    """CLI entry point: propagate <repo-name> [<ref>]"""
    if len(argv) < 2:
        print("USAGE: propagation_engine.py <repo-name> [<git-ref>]", file=sys.stderr)
        print("  git-ref defaults to refs/heads/main", file=sys.stderr)
        return 2
    repo_name = argv[1]
    ref = argv[2] if len(argv) >= 3 else "refs/heads/main"
    return propagate(repo_name, ref)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
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
