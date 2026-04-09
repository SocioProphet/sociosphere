"""
Auto-merge handler for Phase A PRs.

On deployment, detects Phase A PRs #1 and #2, validates their readiness
(checks pass, no merge conflicts), merges them in sequence, and waits
for CI before proceeding.
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Wait between merges to allow CI to run
CI_WAIT_SECONDS = 120

# Retry config
MAX_MERGE_RETRIES = 3
RETRY_BACKOFF_BASE = 5.0


class AutoMergeHandler:
    """Detects and merges Phase A PRs via the GitHub API client.

    Parameters
    ----------
    github_client:
        An object that implements the minimal GitHub API surface used
        here.  In tests this is replaced by a mock.  In production use
        a :class:`github.Github` (PyGitHub) instance.
    repo_full_name:
        The ``owner/repo`` string, e.g. ``SocioProphet/sociosphere``.
    rate_limiter:
        Shared :class:`~automation.rate_limiter.RateLimiter` instance.
    phase_a_pr_numbers:
        The PR numbers that form Phase A, in merge order.
    ci_wait_seconds:
        How long to wait after each merge for CI to run (default 120 s).
    """

    def __init__(
        self,
        github_client,
        repo_full_name: str,
        rate_limiter=None,
        phase_a_pr_numbers: Optional[list] = None,
        ci_wait_seconds: int = CI_WAIT_SECONDS,
    ) -> None:
        self.gh = github_client
        self.repo_full_name = repo_full_name
        self.rate_limiter = rate_limiter
        self.phase_a_pr_numbers = phase_a_pr_numbers or [1, 2]
        self.ci_wait_seconds = ci_wait_seconds

        self._metrics: dict = {
            "prs_merged": 0,
            "prs_failed": 0,
            "prs_skipped": 0,
        }

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> bool:
        """Detect and merge all Phase A PRs in order.

        Returns True if all PRs were merged successfully.
        """
        logger.info(
            "Auto-merge handler starting for %s (PRs: %s)",
            self.repo_full_name,
            self.phase_a_pr_numbers,
        )

        repo = self._get_repo()
        if repo is None:
            logger.error("Could not access repo %s", self.repo_full_name)
            return False

        for i, pr_number in enumerate(self.phase_a_pr_numbers):
            pr = self._get_pr(repo, pr_number)
            if pr is None:
                logger.warning("PR #%d not found — skipping", pr_number)
                self._metrics["prs_skipped"] += 1
                continue

            if self._is_merged(pr):
                logger.info("PR #%d already merged — skipping", pr_number)
                self._metrics["prs_skipped"] += 1
                continue

            if not self._is_ready(pr):
                logger.warning(
                    "PR #%d is not ready (conflicts or failing checks)", pr_number
                )
                self._metrics["prs_failed"] += 1
                return False

            success = self._merge_with_retry(pr, pr_number)
            if not success:
                self._metrics["prs_failed"] += 1
                return False

            self._metrics["prs_merged"] += 1

            if i < len(self.phase_a_pr_numbers) - 1:
                logger.info(
                    "Waiting %ds for CI after merging PR #%d …",
                    self.ci_wait_seconds,
                    pr_number,
                )
                time.sleep(self.ci_wait_seconds)

        logger.info(
            "Auto-merge complete: merged=%d failed=%d skipped=%d",
            self._metrics["prs_merged"],
            self._metrics["prs_failed"],
            self._metrics["prs_skipped"],
        )
        return True

    def get_metrics(self) -> dict:
        return dict(self._metrics)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_repo(self):
        try:
            if self.rate_limiter:
                self.rate_limiter.acquire(cost=1)
            return self.gh.get_repo(self.repo_full_name)
        except Exception as exc:
            logger.exception("Failed to get repo: %s", exc)
            return None

    def _get_pr(self, repo, pr_number: int):
        try:
            if self.rate_limiter:
                self.rate_limiter.acquire(cost=1)
            return repo.get_pull(pr_number)
        except Exception as exc:
            logger.exception("Failed to get PR #%d: %s", pr_number, exc)
            return None

    @staticmethod
    def _is_merged(pr) -> bool:
        return getattr(pr, "merged", False)

    def _is_ready(self, pr) -> bool:
        """Check that a PR has no conflicts and all checks pass."""
        # mergeable_state: 'clean' → ready, 'blocked' → checks pending,
        # 'dirty' → merge conflict, 'unknown' → still being computed.
        state = getattr(pr, "mergeable_state", "unknown")
        if state == "clean":
            return True
        if state == "unknown":
            # GitHub is still computing — wait briefly and retry once
            time.sleep(3)
            if self.rate_limiter:
                self.rate_limiter.acquire(cost=1)
            try:
                pr.update()
            except Exception:
                pass
            state = getattr(pr, "mergeable_state", "unknown")
        return state == "clean"

    def _merge_with_retry(self, pr, pr_number: int) -> bool:
        for attempt in range(1, MAX_MERGE_RETRIES + 1):
            try:
                if self.rate_limiter:
                    self.rate_limiter.acquire(cost=2)
                pr.merge(
                    merge_method="squash",
                    commit_message=f"Auto-merge Phase A PR #{pr_number}",
                )
                logger.info("PR #%d merged (attempt %d)", pr_number, attempt)
                return True
            except Exception as exc:
                logger.warning(
                    "Merge attempt %d/%d for PR #%d failed: %s",
                    attempt,
                    MAX_MERGE_RETRIES,
                    pr_number,
                    exc,
                )
                if attempt < MAX_MERGE_RETRIES:
                    delay = RETRY_BACKOFF_BASE ** attempt
                    time.sleep(delay)

        logger.error("All merge attempts failed for PR #%d", pr_number)
        return False
