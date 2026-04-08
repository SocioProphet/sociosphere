"""
Metrics Collector.

Tracks API call usage, propagation success/failure rates, average
latency, cost-per-repo, and deduplication progress.  Generates daily
reports and emits alerts on anomalies.
"""

import logging
import threading
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Alert thresholds
API_ALERT_THRESHOLD = 0.90       # 90 % usage → alert
PROPAGATION_FAILURE_ALERT = 0.10  # > 10 % failure rate → alert


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MetricsCollector:
    """Collects, aggregates, and reports automation metrics.

    Parameters
    ----------
    rate_limiter:
        Optional :class:`~automation.rate_limiter.RateLimiter` for API
        usage data.
    alert_fn:
        Callable invoked when an anomaly is detected.  Receives a single
        dict with ``level`` and ``message`` keys.  Defaults to logging.
    """

    def __init__(
        self,
        rate_limiter=None,
        alert_fn: Optional[Callable[[dict], None]] = None,
    ) -> None:
        self.rate_limiter = rate_limiter
        self.alert_fn = alert_fn or self._default_alert

        self._lock = threading.Lock()

        # Propagation tracking
        self._propagation_events: List[dict] = []
        self._propagation_success = 0
        self._propagation_failure = 0

        # Per-repo cost (arbitrary unit: # API calls spent on that repo)
        self._repo_costs: Dict[str, int] = {}

        # Deduplication progress
        self._dedup_total = 0
        self._dedup_resolved = 0

        # Sprint tracking
        self._sprint_start: datetime = datetime.now(timezone.utc)

        # Daily report storage
        self._daily_reports: List[dict] = []

    # ------------------------------------------------------------------
    # Recording methods
    # ------------------------------------------------------------------

    def record_propagation(
        self,
        repo: str,
        success: bool,
        latency_seconds: float,
    ) -> None:
        """Record a single propagation outcome."""
        with self._lock:
            if success:
                self._propagation_success += 1
            else:
                self._propagation_failure += 1

            self._propagation_events.append(
                {
                    "repo": repo,
                    "success": success,
                    "latency_seconds": latency_seconds,
                    "timestamp": _now_iso(),
                }
            )

        failure_rate = self._failure_rate()
        if failure_rate > PROPAGATION_FAILURE_ALERT:
            self.alert_fn(
                {
                    "level": "warning",
                    "message": (
                        f"Propagation failure rate {failure_rate:.1%} "
                        f"exceeds threshold {PROPAGATION_FAILURE_ALERT:.0%}"
                    ),
                }
            )

    def record_api_call(self, repo: str, cost: int = 1) -> None:
        """Record that *cost* API calls were consumed for *repo*."""
        with self._lock:
            self._repo_costs[repo] = self._repo_costs.get(repo, 0) + cost

        if self.rate_limiter:
            usage = self.rate_limiter.usage_fraction()
            if usage > API_ALERT_THRESHOLD:
                self.alert_fn(
                    {
                        "level": "critical",
                        "message": (
                            f"GitHub API usage at {usage:.1%} — "
                            "approaching quota limit"
                        ),
                    }
                )

    def record_dedup_progress(self, total: int, resolved: int) -> None:
        """Update deduplication progress counters."""
        with self._lock:
            self._dedup_total = total
            self._dedup_resolved = resolved

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return a current metrics snapshot."""
        with self._lock:
            total = self._propagation_success + self._propagation_failure
            avg_latency = (
                sum(e["latency_seconds"] for e in self._propagation_events) /
                len(self._propagation_events)
                if self._propagation_events
                else 0.0
            )
            summary = {
                "propagation": {
                    "total": total,
                    "success": self._propagation_success,
                    "failure": self._propagation_failure,
                    "success_rate_pct": round(
                        (self._propagation_success / total * 100) if total else 0.0, 1
                    ),
                    "avg_latency_seconds": round(avg_latency, 2),
                },
                "deduplication": {
                    "total": self._dedup_total,
                    "resolved": self._dedup_resolved,
                    "pct": round(
                        (self._dedup_resolved / self._dedup_total * 100)
                        if self._dedup_total
                        else 0.0,
                        1,
                    ),
                },
                "top_repos_by_api_cost": sorted(
                    self._repo_costs.items(), key=lambda kv: kv[1], reverse=True
                )[:10],
                "sprint_start": self._sprint_start.isoformat(),
                "generated_at": _now_iso(),
            }

        if self.rate_limiter:
            summary["api_usage"] = self.rate_limiter.get_metrics()

        return summary

    def generate_daily_report(self) -> dict:
        """Generate and store a daily report snapshot."""
        report = self.get_summary()
        report["report_type"] = "daily"
        with self._lock:
            self._daily_reports.append(report)
        logger.info("Daily report generated: %s", report)
        return report

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _failure_rate(self) -> float:
        total = self._propagation_success + self._propagation_failure
        if total == 0:
            return 0.0
        return self._propagation_failure / total

    @staticmethod
    def _default_alert(alert: dict) -> None:
        level = alert.get("level", "info").upper()
        msg = alert.get("message", "")
        logger.log(
            logging.CRITICAL if level == "CRITICAL" else logging.WARNING,
            "ALERT [%s]: %s",
            level,
            msg,
        )
