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
#!/usr/bin/env python3
"""
engines/metrics_collector.py

Measure and report the health of the Repository Intelligence system:
  - Registry completeness (% of repos documented)
  - Automation success rates (% propagations successful)
  - Deduplication progress (% duplicates resolved)

Outputs to metrics/registry-metrics.json and prints a dashboard to stdout.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
METRICS_DIR = ROOT / "metrics"
METRICS_FILE = METRICS_DIR / "registry-metrics.json"

CANONICAL_REPOS_FILE = REGISTRY_DIR / "canonical-repos.yaml"
ONTOLOGY_FILE = REGISTRY_DIR / "repository-ontology.yaml"
DEP_GRAPH_FILE = REGISTRY_DIR / "dependency-graph.yaml"
DEDUP_FILE = REGISTRY_DIR / "deduplication-map.yaml"
PROPAGATION_LOG = METRICS_DIR / "propagation-log.jsonl"
DEVOPS_LOG = METRICS_DIR / "devops-log.jsonl"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(raw) or {}
    return {}


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


# ── metric collection ────────────────────────────────────────────────────────

def registry_completeness() -> dict[str, Any]:
    """Measure how many repos are in the canonical registry and ontology."""
    repos_data = _load_yaml(CANONICAL_REPOS_FILE)
    repos = repos_data.get("repositories", [])
    total = len(repos)

    ontology_data = _load_yaml(ONTOLOGY_FILE)
    ontologies = ontology_data.get("ontologies", {})
    ontology_count = len(ontologies)

    dep_data = _load_yaml(DEP_GRAPH_FILE)
    deps = dep_data.get("dependencies", {})
    dep_count = len(deps)

    return {
        "total_repos": total,
        "documented_repos": total,  # all repos in canonical-repos.yaml are documented
        "ontology_complete": ontology_count,
        "dependencies_mapped": dep_count,
        "pct_documented": 100 if total > 0 else 0,
        "pct_ontology": round(ontology_count / total * 100, 1) if total > 0 else 0,
        "pct_deps": round(dep_count / total * 100, 1) if total > 0 else 0,
    }


def automation_effectiveness() -> dict[str, Any]:
    """Measure propagation and DevOps automation success rates."""
    prop_events = _load_jsonl(PROPAGATION_LOG)
    devops_events = _load_jsonl(DEVOPS_LOG)

    prop_total = len(prop_events)
    prop_success = sum(1 for e in prop_events if e.get("status") == "success")

    devops_total = len(devops_events)
    devops_success = sum(1 for e in devops_events if e.get("status") == "success")

    actions_total = sum(len(e.get("actions_triggered", [])) for e in prop_events)

    return {
        "propagations_triggered": prop_total,
        "propagations_successful": prop_success,
        "propagation_success_pct": (
            round(prop_success / prop_total * 100, 1) if prop_total > 0 else 0
        ),
        "devops_runs_total": devops_total,
        "devops_runs_successful": devops_success,
        "devops_success_pct": (
            round(devops_success / devops_total * 100, 1) if devops_total > 0 else 0
        ),
        "total_actions_triggered": actions_total,
    }


def deduplication_progress() -> dict[str, Any]:
    """Measure deduplication consolidation progress."""
    dedup_data = _load_yaml(DEDUP_FILE)
    duplicates = dedup_data.get("duplicates", {})

    total = len(duplicates)
    resolved = sum(1 for d in duplicates.values() if d.get("status") == "resolved")
    in_progress = sum(
        1 for d in duplicates.values() if d.get("status") == "merge_in_progress"
    )
    pending = sum(
        1 for d in duplicates.values()
        if d.get("status") in ("pending_consolidation", "pending_review")
    )

    return {
        "duplicates_identified": total,
        "duplicates_resolved": resolved,
        "duplicates_in_progress": in_progress,
        "duplicates_pending": pending,
        "completion_pct": round(resolved / total * 100, 1) if total > 0 else 0,
    }


# ── dashboard ─────────────────────────────────────────────────────────────────

def collect() -> dict[str, Any]:
    """Collect all metrics and return a structured dashboard dict."""
    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "registry_completeness": registry_completeness(),
        "automation_effectiveness": automation_effectiveness(),
        "deduplication_progress": deduplication_progress(),
    }


def print_dashboard(metrics: dict[str, Any]) -> None:
    """Print a human-readable metrics dashboard to stdout."""
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
    """Save metrics to metrics/registry-metrics.json."""
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )


def run(print_output: bool = True, save_output: bool = True) -> int:
    """Collect metrics, print dashboard, and save to file."""
    metrics = collect()
    if print_output:
        print_dashboard(metrics)
    if save_output:
        save(metrics)
        print(f"OK: metrics saved to {METRICS_FILE.relative_to(ROOT)}")
    return 0


def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv
    no_save = "--no-save" in argv
    return run(print_output=not quiet, save_output=not no_save)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
