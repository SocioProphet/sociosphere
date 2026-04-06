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
