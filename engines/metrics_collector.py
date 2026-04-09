"""Metrics collection helpers for registry health and automation status."""

from __future__ import annotations

import json
import sys
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
METRICS_FILE = METRICS_DIR / "registry-metrics.json"

CANONICAL_REPOS_FILE = REGISTRY_DIR / "canonical-repos.yaml"
ONTOLOGY_FILE = REGISTRY_DIR / "repository-ontology.yaml"
DEP_GRAPH_FILE = REGISTRY_DIR / "dependency-graph.yaml"
PROP_RULES_FILE = REGISTRY_DIR / "change-propagation-rules.yaml"
DEVOPS_FILE = REGISTRY_DIR / "devops-automation.yaml"
DEDUP_FILE = REGISTRY_DIR / "deduplication-map.yaml"
PROPAGATION_LOG = METRICS_DIR / "propagation-log.jsonl"
DEVOPS_LOG = METRICS_DIR / "devops-log.jsonl"
_REGISTRY_DIR = REGISTRY_DIR



def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}



def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events



def _repo_id(repo: dict[str, Any]) -> str | None:
    return repo.get("id") or repo.get("name")



def _dedup_groups(data: dict[str, Any]) -> list[dict[str, Any]]:
    duplicates = data.get("duplicates", {})
    if isinstance(duplicates, list):
        return [entry for entry in duplicates if isinstance(entry, dict)]
    if isinstance(duplicates, dict):
        groups: list[dict[str, Any]] = []
        for name, entry in duplicates.items():
            if not isinstance(entry, dict):
                continue
            group = dict(entry)
            group.setdefault("name", name)
            groups.append(group)
        return groups
    return []


class MetricsCollector:
    """Aggregate and report metrics across registry files."""

    def __init__(self, registry_dir: str | Path | None = None) -> None:
        self._dir = Path(registry_dir) if registry_dir else _REGISTRY_DIR
        self._data: dict[str, dict[str, Any]] = {}
        self._loaded = False

    def load(self) -> None:
        if yaml is None:
            raise RuntimeError("PyYAML is required for metrics collection")
        self._data["canonical-repos"] = _load_yaml(self._dir / "canonical-repos.yaml")
        self._data["repository-ontology"] = _load_yaml(self._dir / "repository-ontology.yaml")
        self._data["dependency-graph"] = _load_yaml(self._dir / "dependency-graph.yaml")
        self._data["change-propagation-rules"] = _load_yaml(self._dir / "change-propagation-rules.yaml")
        self._data["devops-automation"] = _load_yaml(self._dir / "devops-automation.yaml")
        self._data["deduplication-map"] = _load_yaml(self._dir / "deduplication-map.yaml")
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def _repos(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        repos = self._data["canonical-repos"].get("repositories", [])
        return [repo for repo in repos if isinstance(repo, dict)]

    def _repo_ids(self) -> set[str]:
        return {repo_id for repo in self._repos() if (repo_id := _repo_id(repo))}

    def repo_health(self) -> dict[str, Any]:
        totals: dict[str, int] = {}
        repos = self._repos()
        for repo in repos:
            status = repo.get("status", "unknown")
            totals[status] = totals.get(status, 0) + 1
        return {"total": len(repos), "by_status": totals}

    def role_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for repo in self._repos():
            role = repo.get("role", "unknown")
            dist[role] = dist.get(role, 0) + 1
        return dict(sorted(dist.items(), key=lambda kv: kv[1], reverse=True))

    def language_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for repo in self._repos():
            lang = repo.get("primary_language") or "null"
            dist[lang] = dist.get(lang, 0) + 1
        return dict(sorted(dist.items(), key=lambda kv: kv[1], reverse=True))

    def dependency_stats(self) -> dict[str, Any]:
        self._ensure_loaded()
        edges = self._data["dependency-graph"].get("edges", [])
        edge_types: dict[str, int] = {}
        all_repos: set[str] = set()
        has_deps: set[str] = set()
        is_dep: set[str] = set()

        for edge in edges:
            if not isinstance(edge, dict):
                continue
            src = edge.get("from")
            dst = edge.get("to")
            etype = edge.get("type", "unknown")
            edge_types[etype] = edge_types.get(etype, 0) + 1
            if src:
                all_repos.add(src)
                has_deps.add(src)
            if dst:
                all_repos.add(dst)
                is_dep.add(dst)

        return {
            "total_edges": len([edge for edge in edges if isinstance(edge, dict)]),
            "by_type": edge_types,
            "repos_with_dependencies": len(has_deps),
            "repos_that_are_dependencies": len(is_dep),
            "isolated_repos": len(self._repo_ids() - all_repos),
        }

    def propagation_coverage(self) -> dict[str, Any]:
        self._ensure_loaded()
        active_ids = {
            repo_id
            for repo in self._repos()
            if repo.get("status") == "active" and (repo_id := _repo_id(repo))
        }
        rules = self._data["change-propagation-rules"].get("rules", [])
        repos_with_rules = {
            rule.get("trigger", {}).get("repo")
            for rule in rules
            if isinstance(rule, dict)
        }
        repos_with_rules.discard(None)
        covered = len(active_ids & repos_with_rules)
        return {
            "active_repos": len(active_ids),
            "repos_with_rules": len(repos_with_rules),
            "coverage_pct": round(covered / max(len(active_ids), 1) * 100, 1),
        }

    def devops_coverage(self) -> dict[str, Any]:
        self._ensure_loaded()
        active_ids = {
            repo_id
            for repo in self._repos()
            if repo.get("status") == "active" and (repo_id := _repo_id(repo))
        }
        devops_repos = set(self._data["devops-automation"].get("repos", {}).keys())
        deployable = sum(
            1
            for cfg in self._data["devops-automation"].get("repos", {}).values()
            if isinstance(cfg, dict) and cfg.get("deploy", False)
        )
        fips_required = sum(
            1
            for cfg in self._data["devops-automation"].get("repos", {}).values()
            if isinstance(cfg, dict) and cfg.get("fips_required", False)
        )
        covered = len(active_ids & devops_repos)
        return {
            "active_repos": len(active_ids),
            "repos_with_devops_config": covered,
            "coverage_pct": round(covered / max(len(active_ids), 1) * 100, 1),
            "deployable": deployable,
            "fips_required": fips_required,
        }

    def deduplication_progress(self) -> dict[str, Any]:
        self._ensure_loaded()
        summary = self._data["deduplication-map"].get("consolidation_summary")
        if isinstance(summary, dict) and summary:
            return dict(summary)

        groups = _dedup_groups(self._data["deduplication-map"])
        total = len(groups)
        completed = sum(1 for group in groups if group.get("status") in {"completed", "resolved"})
        in_progress = sum(1 for group in groups if group.get("status") in {"in_progress", "merge_in_progress"})
        pending = sum(
            1
            for group in groups
            if group.get("status") in {"pending", "pending_consolidation", "pending_review"}
        )
        dismissed = sum(1 for group in groups if group.get("status") == "dismissed")
        return {
            "total_identified": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "dismissed": dismissed,
        }

    def full_report(self) -> dict[str, Any]:
        self._ensure_loaded()
        canonical = self._data["canonical-repos"]
        return {
            "registry_version": canonical.get("version"),
            "organization": canonical.get("organization"),
            "repo_health": self.repo_health(),
            "role_distribution": self.role_distribution(),
            "language_distribution": self.language_distribution(),
            "dependency_stats": self.dependency_stats(),
            "propagation_coverage": self.propagation_coverage(),
            "devops_coverage": self.devops_coverage(),
            "deduplication_progress": self.deduplication_progress(),
        }



def registry_completeness() -> dict[str, Any]:
    repos_data = _load_yaml(CANONICAL_REPOS_FILE)
    repos = repos_data.get("repositories", [])
    total = len([repo for repo in repos if isinstance(repo, dict)])

    ontology_data = _load_yaml(ONTOLOGY_FILE)
    ontologies = ontology_data.get("ontologies", {})
    ontology_count = len(ontologies) if isinstance(ontologies, dict) else len(ontologies or [])

    dep_data = _load_yaml(DEP_GRAPH_FILE)
    deps = dep_data.get("dependencies")
    if isinstance(deps, dict):
        dep_count = len(deps)
    else:
        dep_count = len(dep_data.get("edges", []))

    return {
        "total_repos": total,
        "documented_repos": total,
        "ontology_complete": ontology_count,
        "dependencies_mapped": dep_count,
        "pct_documented": 100 if total > 0 else 0,
        "pct_ontology": round(ontology_count / total * 100, 1) if total > 0 else 0,
        "pct_deps": round(dep_count / total * 100, 1) if total > 0 else 0,
    }



def automation_effectiveness() -> dict[str, Any]:
    prop_events = _load_jsonl(PROPAGATION_LOG)
    devops_events = _load_jsonl(DEVOPS_LOG)

    prop_total = len(prop_events)
    prop_success = sum(1 for event in prop_events if event.get("status") == "success")
    devops_total = len(devops_events)
    devops_success = sum(1 for event in devops_events if event.get("status") == "success")
    actions_total = sum(len(event.get("actions_triggered", [])) for event in prop_events)

    return {
        "propagations_triggered": prop_total,
        "propagations_successful": prop_success,
        "propagation_success_pct": round(prop_success / prop_total * 100, 1) if prop_total > 0 else 0,
        "devops_runs_total": devops_total,
        "devops_runs_successful": devops_success,
        "devops_success_pct": round(devops_success / devops_total * 100, 1) if devops_total > 0 else 0,
        "total_actions_triggered": actions_total,
    }



def deduplication_progress() -> dict[str, Any]:
    data = _load_yaml(DEDUP_FILE)
    summary = data.get("consolidation_summary")
    if isinstance(summary, dict) and summary:
        total = summary.get("total_identified", 0)
        completed = summary.get("completed", 0)
        in_progress = summary.get("in_progress", 0)
        pending = summary.get("pending", 0)
        dismissed = summary.get("dismissed", 0)
    else:
        groups = _dedup_groups(data)
        total = len(groups)
        completed = sum(1 for group in groups if group.get("status") in {"completed", "resolved"})
        in_progress = sum(1 for group in groups if group.get("status") in {"in_progress", "merge_in_progress"})
        pending = sum(
            1
            for group in groups
            if group.get("status") in {"pending", "pending_consolidation", "pending_review"}
        )
        dismissed = sum(1 for group in groups if group.get("status") == "dismissed")

    return {
        "duplicates_identified": total,
        "duplicates_resolved": completed,
        "duplicates_in_progress": in_progress,
        "duplicates_pending": pending,
        "duplicates_dismissed": dismissed,
        "completion_pct": round(completed / total * 100, 1) if total > 0 else 0,
    }



def collect() -> dict[str, Any]:
    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "registry_completeness": registry_completeness(),
        "automation_effectiveness": automation_effectiveness(),
        "deduplication_progress": deduplication_progress(),
    }



def print_dashboard(metrics: dict[str, Any]) -> None:
    rc = metrics["registry_completeness"]
    ae = metrics["automation_effectiveness"]
    dp = metrics["deduplication_progress"]

    print("=" * 60)
    print("  SOCIOSPHERE METRICS DASHBOARD")
    print(f"  Generated: {metrics['timestamp']}")
    print("=" * 60)
    print("\n── Registry Completeness ──────────────────────────────────")
    print(f"  Total repos:          {rc['total_repos']}")
    print(f"  Documented:           {rc['documented_repos']}/{rc['total_repos']} ({rc['pct_documented']}%)")
    print(f"  Ontology complete:    {rc['ontology_complete']}/{rc['total_repos']} ({rc['pct_ontology']}%)")
    print(f"  Dependencies mapped:  {rc['dependencies_mapped']}/{rc['total_repos']} ({rc['pct_deps']}%)")
    print("\n── Automation Effectiveness ───────────────────────────────")
    print(f"  Propagations triggered:   {ae['propagations_triggered']}")
    print(f"  Propagations successful:  {ae['propagations_successful']} ({ae['propagation_success_pct']}%)")
    print(f"  Total actions triggered:  {ae['total_actions_triggered']}")
    print(f"  DevOps runs:              {ae['devops_runs_total']}")
    print(f"  DevOps success rate:      {ae['devops_runs_successful']}/{ae['devops_runs_total']} ({ae['devops_success_pct']}%)")
    print("\n── Deduplication Progress ─────────────────────────────────")
    print(f"  Duplicates identified:  {dp['duplicates_identified']}")
    print(f"  Resolved:               {dp['duplicates_resolved']}")
    print(f"  In progress:            {dp['duplicates_in_progress']}")
    print(f"  Pending:                {dp['duplicates_pending']}")
    print(f"  Completion:             {dp['completion_pct']}%")
    print("\n" + "=" * 60)



def save(metrics: dict[str, Any]) -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")



def run(print_output: bool = True, save_output: bool = True) -> int:
    metrics = collect()
    if print_output:
        print_dashboard(metrics)
    if save_output:
        save(metrics)
    return 0



def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    quiet = "--quiet" in argv
    no_save = "--no-save" in argv
    return run(print_output=not quiet, save_output=not no_save)


if __name__ == "__main__":
    raise SystemExit(main())
