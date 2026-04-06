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
