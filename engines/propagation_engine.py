"""engines/propagation_engine.py

Cascade automation engine for the SocioProphet registry.

Reads registry/dependency-graph.yaml and
registry/change-propagation-rules.yaml, then computes which downstream
repositories are affected when a given repository changes.
"""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import yaml


_REGISTRY_DIR = Path(__file__).parent.parent / "registry"


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class PropagationEngine:
    """Compute and simulate change-cascade propagation."""

    def __init__(self, registry_dir: str | Path | None = None) -> None:
        self._dir = Path(registry_dir) if registry_dir else _REGISTRY_DIR
        self._edges: list[dict[str, Any]] = []
        self._rules: list[dict[str, Any]] = []
        self._dep_levels: dict[str, int] = {}
        self._adjacency: dict[str, list[str]] = defaultdict(list)
        self._reverse_adjacency: dict[str, list[str]] = defaultdict(list)
        self._loaded = False

    # ── I/O ──────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load dependency graph and propagation rules."""
        dep_raw = _load_yaml(self._dir / "dependency-graph.yaml")
        self._edges = dep_raw.get("edges", [])

        # Build adjacency maps
        for edge in self._edges:
            src = edge["from"]
            dst = edge["to"]
            self._adjacency[src].append(dst)
            self._reverse_adjacency[dst].append(src)

        # Flatten dependency levels
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

    # ── Dependency queries ────────────────────────────────────────────────────

    def dependencies_of(self, repo_id: str) -> list[str]:
        """Return direct dependencies (repos that *repo_id* depends on)."""
        self._ensure_loaded()
        return list(self._adjacency.get(repo_id, []))

    def dependents_of(self, repo_id: str) -> list[str]:
        """Return repos that directly depend on *repo_id*."""
        self._ensure_loaded()
        return list(self._reverse_adjacency.get(repo_id, []))

    def dependency_level(self, repo_id: str) -> int | None:
        """Return the topological level for *repo_id* (-1 = archived)."""
        self._ensure_loaded()
        return self._dep_levels.get(repo_id)

    # ── Propagation queries ───────────────────────────────────────────────────

    def get_rule(self, repo_id: str) -> dict[str, Any] | None:
        """Return the propagation rule whose trigger matches *repo_id*."""
        self._ensure_loaded()
        for rule in self._rules:
            if rule.get("trigger", {}).get("repo") == repo_id:
                return rule
        return None

    def all_rules(self) -> list[dict[str, Any]]:
        """Return all propagation rules."""
        self._ensure_loaded()
        return list(self._rules)

    # ── Cascade computation ───────────────────────────────────────────────────

    def compute_cascade(
        self,
        changed_repo: str,
        max_depth: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Compute the full propagation cascade when *changed_repo* changes.

        Returns a list of notification/action dicts ordered by depth, with
        cycle protection.  Each dict has keys:
          depth, repo, action, message, source_rule
        """
        self._ensure_loaded()

        results: list[dict[str, Any]] = []
        visited: set[str] = {changed_repo}
        queue: deque[tuple[str, int]] = deque()

        # Seed from explicit rule if one exists
        rule = self.get_rule(changed_repo)
        seed_targets: list[dict[str, Any]] = []
        if rule:
            seed_targets = rule.get("propagate_to", [])
            rule_max = rule.get("max_cascade_depth", max_depth)
            max_depth = min(max_depth, rule_max)

        # Also add reverse-adjacency (dependency graph) targets
        dependents = self.dependents_of(changed_repo)
        explicit_repos = {t["repo"] for t in seed_targets}
        for dep in dependents:
            if dep not in explicit_repos and dep not in visited:
                seed_targets.append(
                    {
                        "repo": dep,
                        "action": "notify",
                        "message": (
                            f"{changed_repo} changed — dependency update check"
                        ),
                    }
                )

        for target in seed_targets:
            repo = target["repo"]
            if repo not in visited:
                queue.append((repo, 1))
                results.append(
                    {
                        "depth": 1,
                        "repo": repo,
                        "action": target.get("action", "notify"),
                        "message": target.get("message", ""),
                        "auto_pr": target.get("auto_pr", False),
                        "pr_title": target.get("pr_title", ""),
                        "source_rule": rule["id"] if rule else "dependency_graph",
                    }
                )
                visited.add(repo)

        # BFS for deeper cascades
        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for downstream in self.dependents_of(current):
                if downstream not in visited:
                    visited.add(downstream)
                    results.append(
                        {
                            "depth": depth + 1,
                            "repo": downstream,
                            "action": "notify",
                            "message": (
                                f"Transitive change from {changed_repo} "
                                f"via {current}"
                            ),
                            "auto_pr": False,
                            "pr_title": "",
                            "source_rule": "transitive",
                        }
                    )
                    queue.append((downstream, depth + 1))

        return results

    def all_graph_nodes(self) -> set[str]:
        """Return all repo ids that appear in any dependency edge."""
        self._ensure_loaded()
        return set(self._adjacency.keys()) | set(self._reverse_adjacency.keys())

    def detect_cycles(self) -> list[list[str]]:
        """
        Detect dependency cycles in the graph.

        Returns a list of cycles (each cycle is a list of repo ids).
        Uses DFS with coloring (white/gray/black).
        """
        self._ensure_loaded()

        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = defaultdict(int)
        cycles: list[list[str]] = []

        def dfs(node: str, path: list[str]) -> None:
            color[node] = GRAY
            path.append(node)
            for neighbor in self._adjacency.get(node, []):
                if color[neighbor] == GRAY:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                elif color[neighbor] == WHITE:
                    dfs(neighbor, path)
            path.pop()
            color[node] = BLACK

        all_nodes = set(self._adjacency.keys()) | set(self._reverse_adjacency.keys())
        for node in sorted(all_nodes):
            if color[node] == WHITE:
                dfs(node, [])

        return cycles
