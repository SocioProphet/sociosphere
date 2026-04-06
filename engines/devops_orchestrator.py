"""engines/devops_orchestrator.py

Pipeline execution engine for the SocioProphet registry.

Reads registry/devops-automation.yaml and exposes methods to resolve
build/test/deploy steps for any repository.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


_REGISTRY_DIR = Path(__file__).parent.parent / "registry"


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class DevOpsOrchestrator:
    """Resolve and describe CI/CD pipelines for registered repositories."""

    def __init__(self, registry_dir: str | Path | None = None) -> None:
        self._dir = Path(registry_dir) if registry_dir else _REGISTRY_DIR
        self._config: dict[str, Any] = {}
        self._loaded = False

    # ── I/O ──────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load devops-automation.yaml into memory."""
        self._config = _load_yaml(self._dir / "devops-automation.yaml")
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    # ── Repository queries ────────────────────────────────────────────────────

    def get_repo_config(self, repo_id: str) -> dict[str, Any] | None:
        """Return the devops config for *repo_id*."""
        self._ensure_loaded()
        return self._config.get("repos", {}).get(repo_id)

    def all_repo_ids(self) -> list[str]:
        """Return all repo ids that have a devops config entry."""
        self._ensure_loaded()
        return list(self._config.get("repos", {}).keys())

    def deployable_repos(self) -> list[str]:
        """Return ids of repos that have deploy: true."""
        self._ensure_loaded()
        return [
            repo_id
            for repo_id, cfg in self._config.get("repos", {}).items()
            if cfg.get("deploy", False)
        ]

    def fips_required_repos(self) -> list[str]:
        """Return ids of repos that require FIPS validation."""
        self._ensure_loaded()
        return [
            repo_id
            for repo_id, cfg in self._config.get("repos", {}).items()
            if cfg.get("fips_required", False)
        ]

    # ── Pipeline resolution ───────────────────────────────────────────────────

    def resolve_ci_steps(self, repo_id: str) -> list[dict[str, Any]]:
        """
        Return the ordered list of CI steps for *repo_id*.

        If the repo has a build_template, steps from the template are used
        as a fallback for any missing fields.
        """
        self._ensure_loaded()
        cfg = self.get_repo_config(repo_id)
        if not cfg:
            return []
        return list(cfg.get("ci_steps", []))

    def resolve_deploy_steps(self, repo_id: str) -> list[dict[str, Any]]:
        """Return the ordered list of deploy steps for *repo_id*."""
        self._ensure_loaded()
        cfg = self.get_repo_config(repo_id)
        if not cfg or not cfg.get("deploy", False):
            return []
        return list(cfg.get("deploy_steps", []))

    def resolve_fips_validator(self, repo_id: str) -> str | None:
        """Return the FIPS validator command string for *repo_id*, or None."""
        self._ensure_loaded()
        cfg = self.get_repo_config(repo_id)
        if not cfg or not cfg.get("fips_required", False):
            return None
        return cfg.get("fips_validator")

    def build_template_for(self, repo_id: str) -> dict[str, Any] | None:
        """Return the language build template referenced by *repo_id*."""
        self._ensure_loaded()
        cfg = self.get_repo_config(repo_id)
        if not cfg:
            return None
        template_name = cfg.get("build_template")
        if not template_name:
            return None
        return self._config.get("language_build_templates", {}).get(template_name)

    # ── Pipeline stage queries ────────────────────────────────────────────────

    def pipeline_stages(self) -> list[dict[str, Any]]:
        """Return all defined pipeline stages."""
        self._ensure_loaded()
        return list(self._config.get("pipeline_stages", []))

    def stages_for_context(
        self,
        is_pr: bool = True,
        repo_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Return applicable pipeline stages for a given event context.

        Parameters
        ----------
        is_pr:
            True if the pipeline is being evaluated for a pull-request trigger;
            False for a push-to-main trigger.
        repo_id:
            If provided, stages that only apply to deployable or FIPS repos
            are filtered according to the repo's config.
        """
        self._ensure_loaded()
        is_deployable = (
            repo_id is not None and repo_id in self.deployable_repos()
        )
        is_fips = (
            repo_id is not None and repo_id in self.fips_required_repos()
        )

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

    # ── Summary ───────────────────────────────────────────────────────────────

    def summary(self) -> dict[str, Any]:
        """Return a high-level summary of the devops configuration."""
        self._ensure_loaded()
        all_ids = self.all_repo_ids()
        return {
            "total_repos_configured": len(all_ids),
            "deployable": len(self.deployable_repos()),
            "fips_required": len(self.fips_required_repos()),
            "pipeline_stages": len(self.pipeline_stages()),
            "language_templates": list(
                self._config.get("language_build_templates", {}).keys()
            ),
        }
