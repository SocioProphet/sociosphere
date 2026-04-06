"""
DevOps Orchestrator.

Reads ``devops-automation.yaml`` from the registry, executes build /
test / deploy / rollback steps for a given repo, integrates with FIPS
validation, and handles timeouts + retries with exponential backoff.
"""

import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:  # pragma: no cover
    _YAML_AVAILABLE = False

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0
DEFAULT_TIMEOUT = 300  # seconds


class DevOpsOrchestrator:
    """Executes build/test/deploy pipelines for a repo.

    Parameters
    ----------
    automation_config:
        A dict loaded from ``devops-automation.yaml``.  Keys are repo
        names; values contain ``build``, ``test``, ``deploy``, and
        optional ``fips_validate`` step lists.
    rate_limiter:
        Optional rate limiter; each step consumes one API call unit.
    dry_run:
        When True, log steps but do not execute shell commands.
    """

    def __init__(
        self,
        automation_config: Optional[Dict[str, Any]] = None,
        rate_limiter=None,
        dry_run: bool = False,
    ) -> None:
        self.config: Dict[str, Any] = automation_config or {}
        self.rate_limiter = rate_limiter
        self.dry_run = dry_run

        self._metrics: dict = {
            "builds": 0,
            "tests_run": 0,
            "deploys": 0,
            "rollbacks": 0,
            "failures": 0,
            "retries": 0,
        }

    # ------------------------------------------------------------------
    # Class-level factory
    # ------------------------------------------------------------------

    @classmethod
    def from_yaml(cls, path: str, **kwargs) -> "DevOpsOrchestrator":
        """Load automation config from a YAML file and return an instance."""
        if not _YAML_AVAILABLE:
            raise RuntimeError("pyyaml is not installed")
        with open(path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh) or {}
        return cls(automation_config=config, **kwargs)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def rebuild(self, repo: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Run the build steps for *repo*.  Returns True on success."""
        steps = self._steps_for(repo, "build")
        return self._run_steps(repo, "build", steps, timeout=timeout)

    def test(self, repo: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Run the test steps for *repo*.  Returns True on success."""
        steps = self._steps_for(repo, "test")
        result = self._run_steps(repo, "test", steps, timeout=timeout)
        self._metrics["tests_run"] += 1
        return result

    def deploy(
        self,
        repo: str,
        environment: str = "staging",
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bool:
        """Run the deploy steps for *repo* targeting *environment*."""
        steps = self._steps_for(repo, f"deploy_{environment}") or self._steps_for(
            repo, "deploy"
        )
        result = self._run_steps(repo, f"deploy:{environment}", steps, timeout=timeout)
        if result:
            self._metrics["deploys"] += 1
        return result

    def rollback(self, repo: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Run the rollback steps for *repo*."""
        steps = self._steps_for(repo, "rollback")
        result = self._run_steps(repo, "rollback", steps, timeout=timeout)
        if result:
            self._metrics["rollbacks"] += 1
        return result

    def fips_validate(self, repo: str) -> bool:
        """Run the FIPS validation step if configured."""
        steps = self._steps_for(repo, "fips_validate")
        if not steps:
            logger.debug("No FIPS validation configured for %s", repo)
            return True
        return self._run_steps(repo, "fips_validate", steps)

    def get_metrics(self) -> dict:
        return dict(self._metrics)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _steps_for(self, repo: str, phase: str) -> List[str]:
        repo_cfg = self.config.get(repo, {})
        return list(repo_cfg.get(phase, []))

    def _run_steps(
        self,
        repo: str,
        phase: str,
        steps: List[str],
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bool:
        if not steps:
            logger.debug("No %s steps configured for %s", phase, repo)
            return True

        if self.rate_limiter:
            self.rate_limiter.acquire(cost=1)

        self._metrics["builds" if phase == "build" else "builds"] += 0  # no-op counter

        for step in steps:
            if not self._run_step(repo, phase, step, timeout=timeout):
                self._metrics["failures"] += 1
                return False

        return True

    def _run_step(
        self,
        repo: str,
        phase: str,
        step: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bool:
        """Execute a single shell step with retry logic."""
        for attempt in range(1, MAX_RETRIES + 1):
            logger.info("[%s] %s (attempt %d): %s", repo, phase, attempt, step)

            if self.dry_run:
                logger.debug("[dry-run] skipping execution")
                return True

            try:
                result = subprocess.run(
                    step,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                if result.returncode == 0:
                    logger.debug("Step succeeded:\n%s", result.stdout[:500])
                    return True

                logger.warning(
                    "Step failed (exit %d):\n%s",
                    result.returncode,
                    result.stderr[:500],
                )
            except subprocess.TimeoutExpired:
                logger.warning("Step timed out after %ds", timeout)
            except Exception as exc:
                logger.exception("Step raised an exception: %s", exc)

            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY ** attempt
                self._metrics["retries"] += 1
                logger.info("Retrying in %.1fs …", delay)
                time.sleep(delay)

        return False
