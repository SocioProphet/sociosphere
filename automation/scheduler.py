"""
APScheduler-based job scheduler for autonomous registry management.

Jobs
----
- Every 1 minute  : drain the webhook event queue
- Every 1 hour    : registry rebuild (≈200 API calls)
- Every day 02:00 : deep scan       (≈800 API calls)
- On-demand       : trigger propagation for a specific repo
"""

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

logger = logging.getLogger(__name__)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.jobstores.memory import MemoryJobStore
    from apscheduler.executors.pool import ThreadPoolExecutor
    _APSCHEDULER_AVAILABLE = True
except ImportError:  # pragma: no cover
    _APSCHEDULER_AVAILABLE = False
    BackgroundScheduler = None  # type: ignore[assignment,misc]

from automation.rate_limiter import RateLimiter

# API call cost estimates
COST_REGISTRY_REBUILD = 200
COST_DEEP_SCAN = 800
COST_PROCESS_EVENT = 10
COST_PROPAGATION = 50
ON_DEMAND_DELAY_SECONDS = 1

# Adaptive scheduling threshold
BACKOFF_USAGE_THRESHOLD = 0.80


class RegistryScheduler:
    """Wraps APScheduler with registry-specific jobs and adaptive backoff.

    Parameters
    ----------
    rate_limiter:
        Shared :class:`~automation.rate_limiter.RateLimiter` instance.
    event_queue:
        A :class:`queue.Queue` populated by the webhook handler.
    propagation_handler:
        Callable that receives a single event dict and processes it.
    registry_rebuild_fn:
        Callable invoked for hourly registry rebuilds.
    deep_scan_fn:
        Callable invoked for daily deep scans.
    """

    def __init__(
        self,
        rate_limiter: RateLimiter,
        event_queue=None,
        propagation_handler: Optional[Callable] = None,
        registry_rebuild_fn: Optional[Callable] = None,
        deep_scan_fn: Optional[Callable] = None,
    ) -> None:
        if not _APSCHEDULER_AVAILABLE:
            raise RuntimeError(
                "APScheduler is not installed. "
                "Run: pip install apscheduler"
            )

        self.rate_limiter = rate_limiter
        self.event_queue = event_queue
        self.propagation_handler = propagation_handler or self._noop_handler
        self.registry_rebuild_fn = registry_rebuild_fn or self._default_rebuild
        self.deep_scan_fn = deep_scan_fn or self._default_deep_scan

        self._metrics: dict = {
            "jobs_run": 0,
            "jobs_failed": 0,
            "jobs_skipped": 0,
            "events_processed": 0,
            "rebuilds_run": 0,
            "deep_scans_run": 0,
        }

        jobstores = {"default": MemoryJobStore()}
        executors = {"default": ThreadPoolExecutor(max_workers=4)}
        self._scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            timezone="UTC",
        )
        self._register_jobs()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background scheduler."""
        self._scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self, wait: bool = True) -> None:
        """Stop the scheduler."""
        self._scheduler.shutdown(wait=wait)
        logger.info("Scheduler stopped")

    def trigger_propagation(self, repo_full_name: str) -> None:
        """On-demand: schedule an immediate propagation for *repo_full_name*."""
        self._scheduler.add_job(
            self._run_propagation,
            "date",
            run_date=datetime.now(timezone.utc) + timedelta(seconds=ON_DEMAND_DELAY_SECONDS),
            args=[{"repo": repo_full_name, "on_demand": True}],
            id=f"on_demand_{repo_full_name}_{int(time.time())}",
            misfire_grace_time=60,
        )
        logger.info("Queued on-demand propagation for %s", repo_full_name)

    def get_metrics(self) -> dict:
        return dict(self._metrics)

    # ------------------------------------------------------------------
    # Job registration
    # ------------------------------------------------------------------

    def _register_jobs(self) -> None:
        # Process webhook queue every minute
        self._scheduler.add_job(
            self._process_queue,
            "interval",
            minutes=1,
            id="process_queue",
            misfire_grace_time=30,
        )

        # Hourly registry rebuild
        self._scheduler.add_job(
            self._run_registry_rebuild,
            "interval",
            hours=1,
            id="registry_rebuild",
            misfire_grace_time=300,
        )

        # Daily deep scan at 02:00 UTC
        self._scheduler.add_job(
            self._run_deep_scan,
            "cron",
            hour=2,
            minute=0,
            id="deep_scan",
            misfire_grace_time=600,
        )

    # ------------------------------------------------------------------
    # Job implementations
    # ------------------------------------------------------------------

    def _process_queue(self) -> None:
        if self.event_queue is None:
            return

        processed = 0
        while not self.event_queue.empty():
            if self.rate_limiter.usage_fraction() >= BACKOFF_USAGE_THRESHOLD:
                logger.warning(
                    "Skipping queue processing: API usage > %.0f%%",
                    BACKOFF_USAGE_THRESHOLD * 100,
                )
                self._metrics["jobs_skipped"] += 1
                break

            if not self.rate_limiter.acquire(cost=COST_PROCESS_EVENT):
                self._metrics["jobs_skipped"] += 1
                break

            try:
                event = self.event_queue.get_nowait()
            except Exception:
                break

            self._run_propagation(event)
            processed += 1

        if processed:
            logger.info("Processed %d queued events", processed)

    def _run_propagation(self, event: dict) -> None:
        self._metrics["jobs_run"] += 1
        try:
            self.propagation_handler(event)
            self._metrics["events_processed"] += 1
        except Exception as exc:
            self._metrics["jobs_failed"] += 1
            logger.exception("Propagation failed for event %s: %s", event, exc)
            self._exponential_retry(self._run_propagation, event)

    def _run_registry_rebuild(self) -> None:
        if self.rate_limiter.usage_fraction() >= BACKOFF_USAGE_THRESHOLD:
            logger.warning("Skipping registry rebuild: API usage > 80%%")
            self._metrics["jobs_skipped"] += 1
            return

        if not self.rate_limiter.acquire(cost=COST_REGISTRY_REBUILD):
            self._metrics["jobs_skipped"] += 1
            return

        self._metrics["jobs_run"] += 1
        try:
            self.registry_rebuild_fn()
            self._metrics["rebuilds_run"] += 1
            logger.info("Registry rebuild complete")
        except Exception as exc:
            self._metrics["jobs_failed"] += 1
            logger.exception("Registry rebuild failed: %s", exc)

    def _run_deep_scan(self) -> None:
        if self.rate_limiter.usage_fraction() >= BACKOFF_USAGE_THRESHOLD:
            logger.warning("Skipping deep scan: API usage > 80%%")
            self._metrics["jobs_skipped"] += 1
            return

        if not self.rate_limiter.acquire(cost=COST_DEEP_SCAN):
            self._metrics["jobs_skipped"] += 1
            return

        self._metrics["jobs_run"] += 1
        try:
            self.deep_scan_fn()
            self._metrics["deep_scans_run"] += 1
            logger.info("Deep scan complete")
        except Exception as exc:
            self._metrics["jobs_failed"] += 1
            logger.exception("Deep scan failed: %s", exc)

    # ------------------------------------------------------------------
    # Retry helper
    # ------------------------------------------------------------------

    def _exponential_retry(
        self,
        fn: Callable,
        arg: dict,
        max_retries: int = 3,
        base_delay: float = 2.0,
    ) -> None:
        for attempt in range(1, max_retries + 1):
            delay = base_delay ** attempt
            logger.info("Retry %d/%d in %.1fs", attempt, max_retries, delay)
            time.sleep(delay)
            try:
                fn(arg)
                return
            except Exception as exc:
                logger.warning("Retry %d failed: %s", attempt, exc)
        logger.error("All retries exhausted for %s", arg)

    # ------------------------------------------------------------------
    # Default no-op implementations
    # ------------------------------------------------------------------

    @staticmethod
    def _noop_handler(event: dict) -> None:
        logger.debug("No propagation handler registered; event=%s", event)

    @staticmethod
    def _default_rebuild() -> None:
        logger.info("[stub] Registry rebuild job ran")

    @staticmethod
    def _default_deep_scan() -> None:
        logger.info("[stub] Deep scan job ran")
