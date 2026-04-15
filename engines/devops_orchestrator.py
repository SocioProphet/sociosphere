"""DevOps orchestration helpers for registry-backed CI metadata."""

from __future__ import annotations

import subprocess
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
DEVOPS_FILE = REGISTRY_DIR / "devops-automation.yaml"
DEVOPS_LOG = METRICS_DIR / "devops-log.jsonl"
_REGISTRY_DIR = REGISTRY_DIR



def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


class DevOpsOrchestrator:
    """Resolve CI and deployment metadata from registry/devops-automation.yaml."""

    def __init__(self, registry_dir: str | Path | None = None) -> None:
        self._dir = Path(registry_dir) if registry_dir else _REGISTRY_DIR
        self._config: dict[str, Any] = {}
        self._loaded = False

    def load(self) -> None:
        self._config = _load_yaml(self._dir / "devops-automation.yaml")
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def get_repo_config(self, repo_id: str) -> dict[str, Any] | None:
        self._ensure_loaded()
        return self._config.get("repos", {}).get(repo_id)

    def all_repo_ids(self) -> list[str]:
        self._ensure_loaded()
        return list(self._config.get("repos", {}).keys())

    def deployable_repos(self) -> list[str]:
        self._ensure_loaded()
        return [
            repo_id
            for repo_id, cfg in self._config.get("repos", {}).items()
            if cfg.get("deploy", False)
        ]

    def fips_required_repos(self) -> list[str]:
        self._ensure_loaded()
        return [
            repo_id
            for repo_id, cfg in self._config.get("repos", {}).items()
            if cfg.get("fips_required", False)
        ]

    def resolve_ci_steps(self, repo_id: str) -> list[dict[str, Any]]:
        self._ensure_loaded()
        cfg = self.get_repo_config(repo_id)
        if not cfg:
            return []
        return list(cfg.get("ci_steps", []))

    def resolve_deploy_steps(self, repo_id: str) -> list[dict[str, Any]]:
        self._ensure_loaded()
        cfg = self.get_repo_config(repo_id)
        if not cfg or not cfg.get("deploy", False):
            return []
        return list(cfg.get("deploy_steps", []))

    def resolve_fips_validator(self, repo_id: str) -> str | None:
        self._ensure_loaded()
        cfg = self.get_repo_config(repo_id)
        if not cfg or not cfg.get("fips_required", False):
            return None
        return cfg.get("fips_validator")

    def build_template_for(self, repo_id: str) -> dict[str, Any] | None:
        self._ensure_loaded()
        cfg = self.get_repo_config(repo_id)
        if not cfg:
            return None
        template_name = cfg.get("build_template")
        if not template_name:
            return None
        return self._config.get("language_build_templates", {}).get(template_name)

    def pipeline_stages(self) -> list[dict[str, Any]]:
        self._ensure_loaded()
        return list(self._config.get("pipeline_stages", []))

    def stages_for_context(
        self,
        is_pr: bool = True,
        repo_id: str | None = None,
    ) -> list[dict[str, Any]]:
        self._ensure_loaded()
        is_deployable = repo_id is not None and repo_id in self.deployable_repos()
        is_fips = repo_id is not None and repo_id in self.fips_required_repos()

        result: list[dict[str, Any]] = []
        for stage in self.pipeline_stages():
            if is_pr and not stage.get("runs_on_pr", False):
                continue
            if not is_pr and not stage.get("runs_on_push_main", False):
                continue
            if stage.get("applies_to_deployable_only") and not is_deployable:
                continue
            if stage.get("applies_to_fips_required_only") and not is_fips:
                continue
            result.append(stage)
        return result

    def summary(self) -> dict[str, Any]:
        self._ensure_loaded()
        return {
            "total_repos_configured": len(self.all_repo_ids()),
            "deployable": len(self.deployable_repos()),
            "fips_required": len(self.fips_required_repos()),
            "pipeline_stages": len(self.pipeline_stages()),
            "language_templates": list(
                self._config.get("language_build_templates", {}).keys()
            ),
        }



def _log(entry: dict[str, Any]) -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with DEVOPS_LOG.open("a", encoding="utf-8") as fh:
        import json

        fh.write(json.dumps(entry) + "\n")



def _run_step(step: str, cwd: Path, dry_run: bool = False) -> dict[str, Any]:
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
    """Run build/test/deploy steps for a repo from the devops_rules section."""

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

    for step in steps:
        result = _run_step(step, work_dir, dry_run=dry_run)
        results.append(result)
        if result["returncode"] != 0:
            failed = True
            break

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
    """Execute the appropriate phases for an event type."""

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

    for phase in phases:
        result = run_phase(repo_name, phase, cwd=cwd, dry_run=dry_run)
        if result.get("status") == "failed":
            return 1
    return 0



def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    if len(argv) < 2:
        print(
            "USAGE: devops_orchestrator.py <repo-name> [<event>] [--dry-run]",
            file=sys.stderr,
        )
        return 2

    repo_name = argv[1]
    event = argv[2] if len(argv) >= 3 and not argv[2].startswith("--") else "code_change"
    dry_run = "--dry-run" in argv
    return orchestrate(repo_name, event=event, dry_run=dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
