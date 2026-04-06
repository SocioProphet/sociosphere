"""
Propagation handler.

Receives push events from the webhook queue, looks up the source repo
in the registry, identifies all dependent repos, and triggers the
appropriate DevOps action for each dependent.

Actions triggered per dependent
--------------------------------
- Code changed    → rebuild
- Deps changed    → test
- Contracts changed → deploy to staging then prod (if staging passes)

All events are logged immutably, and failures trigger auto-rollback.
"""

import logging
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Core handler
# ---------------------------------------------------------------------------

class PropagationHandler:
    """Processes push events and cascades changes to dependent repos.

    Parameters
    ----------
    registry:
        A dict mapping ``repo_full_name`` → repo metadata (including
        ``dependents`` list).
    devops_orchestrator:
        A :class:`~automation.devops_orchestrator.DevOpsOrchestrator`
        (or duck-typed equivalent) used to run build/test/deploy steps.
    rate_limiter:
        Shared :class:`~automation.rate_limiter.RateLimiter` instance.
    event_log:
        Optional list that receives immutable event log entries.  If not
        provided, a module-level list is used.
    """

    def __init__(
        self,
        registry: Optional[Dict] = None,
        devops_orchestrator=None,
        rate_limiter=None,
        event_log: Optional[List] = None,
    ) -> None:
        self.registry = registry or {}
        self.orchestrator = devops_orchestrator
        self.rate_limiter = rate_limiter
        self.event_log: List[dict] = event_log if event_log is not None else []

        self._metrics: dict = {
            "events_received": 0,
            "dependents_triggered": 0,
            "rebuilds": 0,
            "tests_run": 0,
            "deploys_staging": 0,
            "deploys_prod": 0,
            "rollbacks": 0,
            "failures": 0,
        }

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def handle(self, event: dict) -> None:
        """Process a single push event."""
        self._metrics["events_received"] += 1
        repo = event.get("repo", "")
        received_at = event.get("received_at", _now_iso())

        self._log(
            action="received",
            repo=repo,
            details={"ref": event.get("ref", ""), "received_at": received_at},
        )

        repo_meta = self.registry.get(repo)
        if repo_meta is None:
            logger.info("Repo %s not found in registry — skipping propagation", repo)
            return

        dependents = repo_meta.get("dependents", [])
        if not dependents:
            logger.debug("No dependents for %s", repo)
            return

        change_type = self._classify_change(event)

        for dependent in dependents:
            self._propagate_to(
                source_repo=repo,
                dependent=dependent,
                change_type=change_type,
                event=event,
            )

    def get_metrics(self) -> dict:
        return dict(self._metrics)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _propagate_to(
        self,
        source_repo: str,
        dependent: str,
        change_type: str,
        event: dict,
    ) -> None:
        self._metrics["dependents_triggered"] += 1
        logger.info("Propagating %s change from %s → %s", change_type, source_repo, dependent)

        if self.rate_limiter:
            if not self.rate_limiter.acquire(cost=10):
                logger.warning("Rate limiter blocked propagation to %s", dependent)
                return

        success = True

        try:
            if change_type in ("code", "deps", "contracts"):
                self._trigger_rebuild(dependent, source_repo)

            if change_type in ("deps", "contracts"):
                test_ok = self._trigger_tests(dependent, source_repo)
                if not test_ok:
                    self._rollback(dependent, source_repo, "test failure")
                    return

            if change_type == "contracts":
                staging_ok = self._deploy_staging(dependent, source_repo)
                if not staging_ok:
                    self._rollback(dependent, source_repo, "staging failure")
                    return

                self._deploy_prod(dependent, source_repo)

            self._log(
                action="propagation_success",
                repo=source_repo,
                details={"dependent": dependent, "change_type": change_type},
            )

        except Exception as exc:
            success = False
            self._metrics["failures"] += 1
            logger.exception(
                "Propagation from %s to %s failed: %s", source_repo, dependent, exc
            )
            self._log(
                action="propagation_failure",
                repo=source_repo,
                details={"dependent": dependent, "error": str(exc)},
            )
            self._rollback(dependent, source_repo, str(exc))

    def _trigger_rebuild(self, repo: str, source: str) -> None:
        self._metrics["rebuilds"] += 1
        logger.info("Triggering rebuild for %s (source: %s)", repo, source)
        if self.orchestrator:
            self.orchestrator.rebuild(repo)
        self._log("rebuild", repo, {"source": source})

    def _trigger_tests(self, repo: str, source: str) -> bool:
        self._metrics["tests_run"] += 1
        logger.info("Triggering tests for %s (source: %s)", repo, source)
        if self.orchestrator:
            return self.orchestrator.test(repo)
        return True

    def _deploy_staging(self, repo: str, source: str) -> bool:
        self._metrics["deploys_staging"] += 1
        logger.info("Deploying %s to staging (source: %s)", repo, source)
        if self.orchestrator:
            return self.orchestrator.deploy(repo, environment="staging")
        return True

    def _deploy_prod(self, repo: str, source: str) -> None:
        self._metrics["deploys_prod"] += 1
        logger.info("Deploying %s to prod (source: %s)", repo, source)
        if self.orchestrator:
            self.orchestrator.deploy(repo, environment="prod")
        self._log("deploy_prod", repo, {"source": source})

    def _rollback(self, repo: str, source: str, reason: str) -> None:
        self._metrics["rollbacks"] += 1
        logger.warning("Rolling back %s (reason: %s)", repo, reason)
        if self.orchestrator:
            self.orchestrator.rollback(repo)
        self._log("rollback", repo, {"source": source, "reason": reason})

    def _log(self, action: str, repo: str, details: Optional[dict] = None) -> None:
        entry = {
            "timestamp": _now_iso(),
            "action": action,
            "repo": repo,
            "details": details or {},
        }
        self.event_log.append(entry)

    @staticmethod
    def _classify_change(event: dict) -> str:
        """Classify the type of change from the push event payload."""
        payload = event.get("payload", {})
        commits = payload.get("commits", [])
        changed_files: List[str] = []
        for commit in commits:
            changed_files.extend(commit.get("added", []))
            changed_files.extend(commit.get("modified", []))
            changed_files.extend(commit.get("removed", []))

        paths = " ".join(changed_files).lower()

        if any(kw in paths for kw in ("contract", "api", "schema", "spec")):
            return "contracts"
        if any(kw in paths for kw in ("requirements", "package.json", "go.mod", "deps")):
            return "deps"
        return "code"
