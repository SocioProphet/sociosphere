#!/usr/bin/env python3
"""
engines/devops_orchestrator.py

Read registry/devops-automation.yaml and, on a code or dependency change,
execute the appropriate build / test / deploy steps for the affected repo.
Integrates with the FIPS validator for compliance checks.
"""
from __future__ import annotations

import subprocess
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
DEVOPS_FILE = REGISTRY_DIR / "devops-automation.yaml"
DEVOPS_LOG = METRICS_DIR / "devops-log.jsonl"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(raw) or {}
    return {}


def _log(entry: dict[str, Any]) -> None:
    import json

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with DEVOPS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def _run_step(step: str, cwd: Path, dry_run: bool = False) -> dict[str, Any]:
    """Execute a single automation step.  Returns a result dict."""
    if dry_run:
        return {"step": step, "status": "dry_run", "returncode": 0}
    result = subprocess.run(
        step,
        shell=True,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    return {
        "step": step,
        "returncode": result.returncode,
        "status": "ok" if result.returncode == 0 else "failed",
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
    }


def run_phase(
    repo_name: str,
    phase: str,
    cwd: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Run a specific phase (build | test | deploy) for a repository.

    Returns a summary dict with overall status and per-step results.
    """
    devops = _load_yaml(DEVOPS_FILE)
    repo_rules = devops.get("devops_rules", {}).get(repo_name)
    if repo_rules is None:
        return {
            "repo": repo_name,
            "phase": phase,
            "status": "skipped",
            "reason": f"no devops rules for '{repo_name}'",
        }

    phase_rules = repo_rules.get(phase)
    if phase_rules is None:
        return {
            "repo": repo_name,
            "phase": phase,
            "status": "skipped",
            "reason": f"no '{phase}' rules for '{repo_name}'",
        }

    work_dir = cwd or ROOT
    steps = phase_rules.get("steps", [])
    results: list[dict[str, Any]] = []
    failed = False

    print(f"Running {phase} for '{repo_name}' ({len(steps)} step(s)) …")
    for step in steps:
        print(f"  $ {step}")
        r = _run_step(step, work_dir, dry_run=dry_run)
        results.append(r)
        if r["returncode"] != 0:
            failed = True
            print(f"  FAIL (rc={r['returncode']})")
            if r.get("stderr"):
                print(f"  STDERR: {r['stderr'][:500]}")
            break
        else:
            print(f"  OK")

    summary: dict[str, Any] = {
        "repo": repo_name,
        "phase": phase,
        "trigger": phase_rules.get("trigger", ""),
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "status": "failed" if failed else "success",
        "steps": results,
    }
    _log(summary)
    return summary


def orchestrate(
    repo_name: str,
    event: str = "code_change",
    cwd: Path | None = None,
    dry_run: bool = False,
) -> int:
    """
    Decide which phases to run based on the event type, then execute them.

    event values:
      code_change       → build + test
      dependency_change → test
      test_success      → deploy
      all               → build + test + deploy
    """
    phases: list[str]
    if event == "code_change":
        phases = ["build", "test"]
    elif event == "dependency_change":
        phases = ["test"]
    elif event == "test_success":
        phases = ["deploy"]
    elif event == "all":
        phases = ["build", "test", "deploy"]
    else:
        phases = ["build", "test"]

    overall_ok = True
    for phase in phases:
        result = run_phase(repo_name, phase, cwd=cwd, dry_run=dry_run)
        if result.get("status") == "failed":
            print(f"FAIL: {phase} phase failed for '{repo_name}' — stopping")
            overall_ok = False
            break

    status = "success" if overall_ok else "failed"
    print(f"{'OK' if overall_ok else 'FAIL'}: orchestration {status} for '{repo_name}'")
    return 0 if overall_ok else 1


def main(argv: list[str]) -> int:
    """CLI entry point: devops_orchestrator.py <repo> [<event>] [--dry-run]"""
    if len(argv) < 2:
        print(
            "USAGE: devops_orchestrator.py <repo-name> [<event>] [--dry-run]",
            file=sys.stderr,
        )
        print("  event: code_change | dependency_change | test_success | all", file=sys.stderr)
        return 2

    repo_name = argv[1]
    event = argv[2] if len(argv) >= 3 and not argv[2].startswith("--") else "code_change"
    dry_run = "--dry-run" in argv

    return orchestrate(repo_name, event=event, dry_run=dry_run)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
