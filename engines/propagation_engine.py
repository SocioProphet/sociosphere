"""Propagation engine for dependency queries and cascade simulation."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
METRICS_DIR = ROOT / "metrics"
DEP_GRAPH_FILE = REGISTRY_DIR / "dependency-graph.yaml"
PROP_RULES_FILE = REGISTRY_DIR / "change-propagation-rules.yaml"
PROPAGATION_LOG = METRICS_DIR / "propagation-log.jsonl"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def get_dependents(repo_name: str, dep_graph: dict[str, Any]) -> list[str]:
    """Return dependent repos from webhook-style dependency graph payload."""
    entry = dep_graph.get("dependencies", {}).get(repo_name, {})
    deps = entry.get("dependents", [])
    result: list[str] = []
    for d in deps:
        name = d.get("name") if isinstance(d, dict) else str(d)
        if name and name != "all-repos":
            result.append(name)
    return result


def get_propagation_rules(repo_name: str, rules: dict[str, Any]) -> dict[str, Any]:
    return rules.get("propagation_rules", {}).get(repo_name, {}).get("on_main_merge", {})


def _log_event(event: dict[str, Any]) -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with PROPAGATION_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def simulate_automation(action_type: str, targets: list[str], repo: str) -> dict[str, Any]:
    return {
        "action": action_type,
        "targets": targets,
        "triggered_by": repo,
        "status": "triggered",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


def propagate(repo_name: str, ref: str = "refs/heads/main") -> int:
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

    actions_triggered: list[dict[str, Any]] = []
    for action in automation.get("automation", []):
        action_type = action.get("type", "unknown")
        targets = action.get("targets", [])
        actions_triggered.append(simulate_automation(action_type, targets, repo_name))

    event["actions_triggered"] = actions_triggered
    _log_event(event)
    return 0


class PropagationEngine:
    """Compute and validate dependency propagation."""

    def __init__(self, registry_dir: str | Path | None = None) -> None:
        self._dir = Path(registry_dir) if registry_dir else REGISTRY_DIR
        self._edges: list[dict[str, Any]] = []
        self._rules: list[dict[str, Any]] = []
        self._dep_levels: dict[str, int] = {}
        self._adjacency: dict[str, list[str]] = defaultdict(list)
        self._reverse_adjacency: dict[str, list[str]] = defaultdict(list)
        self._loaded = False

    def load(self) -> None:
        dep_raw = _load_yaml(self._dir / "dependency-graph.yaml")
        self._edges = dep_raw.get("edges", [])
        for edge in self._edges:
            src = edge["from"]
            dst = edge["to"]
            self._adjacency[src].append(dst)
            self._reverse_adjacency[dst].append(src)

        for level_str, repos in dep_raw.get("dependency_levels", {}).items():
            level = -1 if level_str == "archived" else int(level_str)
            for repo_id in repos:
                self._dep_levels[repo_id] = level

        rules_raw = _load_yaml(self._dir / "change-propagation-rules.yaml")
        self._rules = rules_raw.get("rules", [])
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def dependencies_of(self, repo_id: str) -> list[str]:
        self._ensure_loaded()
        return list(self._adjacency.get(repo_id, []))

    def dependents_of(self, repo_id: str) -> list[str]:
        self._ensure_loaded()
        return list(self._reverse_adjacency.get(repo_id, []))

    def dependency_level(self, repo_id: str) -> int | None:
        self._ensure_loaded()
        return self._dep_levels.get(repo_id)

    def get_rule(self, repo_id: str) -> dict[str, Any] | None:
        self._ensure_loaded()
        for rule in self._rules:
            if rule.get("trigger", {}).get("repo") == repo_id:
                return rule
        return None

    def all_rules(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return list(self._rules)

    def all_graph_nodes(self) -> set[str]:
        self._ensure_loaded()
        nodes: set[str] = set()
        for edge in self._edges:
            nodes.add(edge["from"])
            nodes.add(edge["to"])
        return nodes

    def compute_cascade(self, changed_repo: str, max_depth: int = 3) -> list[dict[str, Any]]:
        self._ensure_loaded()
        results: list[dict[str, Any]] = []
        visited: set[str] = {changed_repo}
        queue: deque[tuple[str, int, str]] = deque()

        rule = self.get_rule(changed_repo)
        seed_targets: list[dict[str, Any]] = list(rule.get("propagate_to", [])) if rule else []
        rule_max = rule.get("max_cascade_depth") if rule else None
        if isinstance(rule_max, int):
            max_depth = min(max_depth, rule_max)

        explicit = {t.get("repo") for t in seed_targets}
        for dep in self.dependents_of(changed_repo):
            if dep not in explicit:
                seed_targets.append({"repo": dep, "action": "notify", "message": f"{changed_repo} changed"})

        for target in seed_targets:
            repo = target.get("repo")
            if not repo or repo in visited:
                continue
            visited.add(repo)
            queue.append((repo, 1, rule.get("id", "dependency_graph") if rule else "dependency_graph"))
            results.append(
                {
                    "depth": 1,
                    "repo": repo,
                    "action": target.get("action", "notify"),
                    "message": target.get("message", ""),
                    "auto_pr": target.get("auto_pr", False),
                    "pr_title": target.get("pr_title", ""),
                    "source_rule": rule.get("id", "dependency_graph") if rule else "dependency_graph",
                }
            )

        while queue:
            current, depth, source_rule = queue.popleft()
            if depth >= max_depth:
                continue
            for downstream in self.dependents_of(current):
                if downstream in visited:
                    continue
                visited.add(downstream)
                nd = depth + 1
                queue.append((downstream, nd, source_rule))
                results.append(
                    {
                        "depth": nd,
                        "repo": downstream,
                        "action": "notify",
                        "message": f"Cascade from {current}",
                        "auto_pr": False,
                        "pr_title": "",
                        "source_rule": source_rule,
                    }
                )

        results.sort(key=lambda x: x["depth"])
        return results

    def detect_cycles(self) -> list[list[str]]:
        self._ensure_loaded()
        visited: set[str] = set()
        stack: set[str] = set()
        path: list[str] = []
        cycles: list[list[str]] = []

        def dfs(node: str) -> None:
            visited.add(node)
            stack.add(node)
            path.append(node)
            for neighbor in self._adjacency.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)
            stack.remove(node)
            path.pop()

        for node in list(self.all_graph_nodes()):
            if node not in visited:
                dfs(node)
        return cycles

    def merge_order(self) -> list[str]:
        self._ensure_loaded()
        by_level = sorted(self._dep_levels.items(), key=lambda kv: kv[1])
        return [repo for repo, _level in by_level if _level >= 0]


def main() -> int:
    parser = argparse.ArgumentParser(description="PropagationEngine CLI")
    parser.add_argument("cmd", choices=["cascade", "cycles", "merge-order", "nodes", "webhook"])
    parser.add_argument("--repo", default=None)
    parser.add_argument("--ref", default="refs/heads/main")
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    if args.cmd == "webhook":
        if not args.repo:
            print("ERROR: --repo is required", file=sys.stderr)
            return 2
        return propagate(args.repo, args.ref)

    engine = PropagationEngine()
    engine.load()

    if args.cmd == "cycles":
        cycles = engine.detect_cycles()
        if cycles:
            for cycle in cycles:
                print(" -> ".join(cycle), file=sys.stderr)
            return 1
        print("OK: no cycles detected")
        return 0

    if args.cmd == "merge-order":
        order = engine.merge_order()
        if args.format == "json":
            print(json.dumps(order, indent=2))
        else:
            for repo in order:
                print(repo)
        return 0

    if args.cmd == "nodes":
        nodes = sorted(engine.all_graph_nodes())
        if args.format == "json":
            print(json.dumps(nodes, indent=2))
        else:
            for node in nodes:
                print(node)
        return 0

    if not args.repo:
        print("ERROR: --repo is required for cascade", file=sys.stderr)
        return 2
    cascade = engine.compute_cascade(args.repo, max_depth=args.max_depth)
    if args.format == "json":
        print(json.dumps(cascade, indent=2))
    else:
        for item in cascade:
            print(f"d{item['depth']} {item['repo']} [{item['action']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
