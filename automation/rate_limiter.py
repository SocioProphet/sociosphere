"""
Rate limiter for GitHub API calls.

Tracks the 5000 requests/hour GitHub API quota with a 500-call safety
buffer.  Supports adaptive backoff when usage exceeds 80 % and an
emergency stop at 95 %.
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# GitHub API limits
HOURLY_LIMIT = 5000
SAFETY_BUFFER = 500
AVAILABLE_QUOTA = HOURLY_LIMIT - SAFETY_BUFFER  # 4500

BACKOFF_THRESHOLD = 0.80   # 80 % → add delay
EMERGENCY_THRESHOLD = 0.95  # 95 % → stop all calls


@dataclass
class RateLimiterMetrics:
    calls_this_hour: int = 0
    calls_today: int = 0
    backoff_events: int = 0
    blocked_events: int = 0
    emergency_stops: int = 0
    hour_reset_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class RateLimiter:
    """Thread-safe GitHub API rate limiter.

    Usage::

        limiter = RateLimiter()
        if limiter.acquire(cost=5):
            # make API call
            ...
        else:
            # call was blocked
            ...
    """

    def __init__(
        self,
        hourly_limit: int = HOURLY_LIMIT,
        safety_buffer: int = SAFETY_BUFFER,
    ) -> None:
        self.hourly_limit = hourly_limit
        self.safety_buffer = safety_buffer
        self.available_quota = hourly_limit - safety_buffer

        self._lock = threading.Lock()
        self.metrics = RateLimiterMetrics()
        self._hour_start = time.monotonic()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def acquire(self, cost: int = 1) -> bool:
        """Try to consume *cost* API calls from the quota.

        Returns True if the call is allowed, False if it should be blocked.
        Applies a sleep delay when usage is between 80 % and 95 %.
        """
        with self._lock:
            self._maybe_reset_hour()

            usage = self._usage_fraction()

            if usage >= EMERGENCY_THRESHOLD:
                logger.error(
                    "Emergency stop: GitHub API usage at %.1f%% (hour calls=%d)",
                    usage * 100,
                    self.metrics.calls_this_hour,
                )
                self.metrics.emergency_stops += 1
                self.metrics.blocked_events += 1
                return False

            if self.metrics.calls_this_hour + cost > self.available_quota:
                logger.warning(
                    "Pre-emptive block: adding %d calls would exceed safe quota "
                    "(current=%d, limit=%d)",
                    cost,
                    self.metrics.calls_this_hour,
                    self.available_quota,
                )
                self.metrics.blocked_events += 1
                return False

            # Record the consumption before sleeping so that concurrent
            # threads see the updated count immediately.
            self.metrics.calls_this_hour += cost
            self.metrics.calls_today += cost

        # Adaptive backoff outside the lock to avoid blocking other threads.
        if usage >= BACKOFF_THRESHOLD:
            delay = self._backoff_delay(usage)
            logger.debug("Adaptive backoff %.3fs (usage=%.1f%%)", delay, usage * 100)
            self.metrics.backoff_events += 1
            time.sleep(delay)

        return True

    def remaining(self) -> int:
        """Return the number of calls remaining in the current hour window."""
        with self._lock:
            self._maybe_reset_hour()
            return max(0, self.available_quota - self.metrics.calls_this_hour)

    def usage_fraction(self) -> float:
        """Return current usage as a fraction of the available quota (0–1)."""
        with self._lock:
            self._maybe_reset_hour()
            return self._usage_fraction()

    def seconds_until_reset(self) -> float:
        """Return seconds until the next hourly quota reset."""
        elapsed = time.monotonic() - self._hour_start
        return max(0.0, 3600.0 - elapsed)

    def get_metrics(self) -> dict:
        """Return a snapshot of current metrics."""
        with self._lock:
            self._maybe_reset_hour()
            return {
                "calls_this_hour": self.metrics.calls_this_hour,
                "calls_today": self.metrics.calls_today,
                "remaining_this_hour": max(
                    0, self.available_quota - self.metrics.calls_this_hour
                ),
                "usage_pct": round(self._usage_fraction() * 100, 1),
                "backoff_events": self.metrics.backoff_events,
                "blocked_events": self.metrics.blocked_events,
                "emergency_stops": self.metrics.emergency_stops,
                "seconds_until_reset": round(self.seconds_until_reset(), 1),
                "hour_reset_at": self.metrics.hour_reset_at.isoformat(),
            }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _maybe_reset_hour(self) -> None:
        """Reset hourly counters if an hour has elapsed."""
        elapsed = time.monotonic() - self._hour_start
        if elapsed >= 3600:
            self._hour_start = time.monotonic()
            self.metrics.calls_this_hour = 0
            self.metrics.hour_reset_at = datetime.now(timezone.utc)
            logger.info("Hourly quota reset")

    def _usage_fraction(self) -> float:
        if self.available_quota == 0:
            return 1.0
        return self.metrics.calls_this_hour / self.available_quota

    @staticmethod
    def _backoff_delay(usage: float) -> float:
        """Return a sleep delay in seconds proportional to over-use."""
        # 80–95 % → linearly interpolate 0.01 s … 0.5 s
        t = (usage - BACKOFF_THRESHOLD) / (EMERGENCY_THRESHOLD - BACKOFF_THRESHOLD)
        return 0.01 + t * 0.49
