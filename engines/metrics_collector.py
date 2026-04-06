"""engines/metrics_collector.py

Continuous tracking engine for the SocioProphet registry.

Collects and aggregates metrics across the registry:
- Repository health (active vs archived vs deprecated)
- Dependency graph statistics
- Propagation rule coverage
- DevOps pipeline coverage
- Deduplication progress
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


_REGISTRY_DIR = Path(__file__).parent.parent / "registry"


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class MetricsCollector:
    """Aggregate and report metrics across the registry layer."""

    def __init__(self, registry_dir: str | Path | None = None) -> None:
        self._dir = Path(registry_dir) if registry_dir else _REGISTRY_DIR
        self._data: dict[str, dict[str, Any]] = {}
        self._loaded = False

    # ── I/O ──────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load all registry YAML files."""
        self._data["canonical-repos"] = _load_yaml(
            self._dir / "canonical-repos.yaml"
        )
        self._data["repository-ontology"] = _load_yaml(
            self._dir / "repository-ontology.yaml"
        )
        self._data["dependency-graph"] = _load_yaml(
            self._dir / "dependency-graph.yaml"
        )
        self._data["change-propagation-rules"] = _load_yaml(
            self._dir / "change-propagation-rules.yaml"
        )
        self._data["devops-automation"] = _load_yaml(
            self._dir / "devops-automation.yaml"
        )
        self._data["deduplication-map"] = _load_yaml(
            self._dir / "deduplication-map.yaml"
        )
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    # ── Repository metrics ────────────────────────────────────────────────────

    def repo_health(self) -> dict[str, Any]:
        """Return a breakdown of repos by status."""
        self._ensure_loaded()
        repos = self._data["canonical-repos"].get("repositories", [])
        totals: dict[str, int] = {}
        for repo in repos:
            status = repo.get("status", "unknown")
            totals[status] = totals.get(status, 0) + 1
        return {
            "total": len(repos),
            "by_status": totals,
        }

    def role_distribution(self) -> dict[str, int]:
        """Return a count of repos per role."""
        self._ensure_loaded()
        repos = self._data["canonical-repos"].get("repositories", [])
        dist: dict[str, int] = {}
        for repo in repos:
            role = repo.get("role", "unknown")
            dist[role] = dist.get(role, 0) + 1
        return dict(sorted(dist.items(), key=lambda kv: kv[1], reverse=True))

    def language_distribution(self) -> dict[str, int]:
        """Return a count of repos per primary language."""
        self._ensure_loaded()
        repos = self._data["canonical-repos"].get("repositories", [])
        dist: dict[str, int] = {}
        for repo in repos:
            lang = repo.get("primary_language") or "null"
            dist[lang] = dist.get(lang, 0) + 1
        return dict(sorted(dist.items(), key=lambda kv: kv[1], reverse=True))

    # ── Dependency metrics ────────────────────────────────────────────────────

    def dependency_stats(self) -> dict[str, Any]:
        """Return high-level dependency graph statistics."""
        self._ensure_loaded()
        edges = self._data["dependency-graph"].get("edges", [])
        edge_types: dict[str, int] = {}
        for edge in edges:
            etype = edge.get("type", "unknown")
            edge_types[etype] = edge_types.get(etype, 0) + 1

        all_repos: set[str] = set()
        has_deps: set[str] = set()
        is_dep: set[str] = set()
        for edge in edges:
            all_repos.add(edge["from"])
            all_repos.add(edge["to"])
            has_deps.add(edge["from"])
            is_dep.add(edge["to"])

        return {
            "total_edges": len(edges),
            "by_type": edge_types,
            "repos_with_dependencies": len(has_deps),
            "repos_that_are_dependencies": len(is_dep),
            "isolated_repos": len(
                self._get_all_repo_ids() - all_repos
            ),
        }

    def _get_all_repo_ids(self) -> set[str]:
        repos = self._data["canonical-repos"].get("repositories", [])
        return {r["id"] for r in repos}

    # ── Propagation metrics ───────────────────────────────────────────────────

    def propagation_coverage(self) -> dict[str, Any]:
        """Report what fraction of active repos have explicit propagation rules."""
        self._ensure_loaded()
        repos = self._data["canonical-repos"].get("repositories", [])
        active = [r for r in repos if r.get("status") == "active"]
        rules = self._data["change-propagation-rules"].get("rules", [])
        repos_with_rules = {r.get("trigger", {}).get("repo") for r in rules}
        covered = sum(1 for r in active if r["id"] in repos_with_rules)
        return {
            "active_repos": len(active),
            "repos_with_rules": len(repos_with_rules),
            "coverage_pct": round(covered / max(len(active), 1) * 100, 1),
        }

    # ── DevOps metrics ────────────────────────────────────────────────────────

    def devops_coverage(self) -> dict[str, Any]:
        """Report what fraction of active repos have devops config."""
        self._ensure_loaded()
        repos = self._data["canonical-repos"].get("repositories", [])
        active = [r for r in repos if r.get("status") == "active"]
        devops_repos = set(
            self._data["devops-automation"].get("repos", {}).keys()
        )
        covered = sum(1 for r in active if r["id"] in devops_repos)
        deployable = sum(
            1 for cfg in self._data["devops-automation"].get("repos", {}).values()
            if cfg.get("deploy", False)
        )
        fips_required = sum(
            1 for cfg in self._data["devops-automation"].get("repos", {}).values()
            if cfg.get("fips_required", False)
        )
        return {
            "active_repos": len(active),
            "repos_with_devops_config": covered,
            "coverage_pct": round(covered / max(len(active), 1) * 100, 1),
            "deployable": deployable,
            "fips_required": fips_required,
        }

    # ── Deduplication metrics ─────────────────────────────────────────────────

    def deduplication_progress(self) -> dict[str, Any]:
        """Return current deduplication consolidation progress."""
        self._ensure_loaded()
        summary = self._data["deduplication-map"].get("consolidation_summary", {})
        return dict(summary)

    # ── Full report ───────────────────────────────────────────────────────────

    def full_report(self) -> dict[str, Any]:
        """Return a comprehensive metrics report across all dimensions."""
        self._ensure_loaded()
        return {
            "registry_version": self._data["canonical-repos"].get("version"),
            "organization": self._data["canonical-repos"].get("organization"),
            "repo_health": self.repo_health(),
            "role_distribution": self.role_distribution(),
            "language_distribution": self.language_distribution(),
            "dependency_stats": self.dependency_stats(),
            "propagation_coverage": self.propagation_coverage(),
            "devops_coverage": self.devops_coverage(),
            "deduplication_progress": self.deduplication_progress(),
        }
