"""Tests for automation/rate_limiter.py."""

import time
import pytest

from automation.rate_limiter import RateLimiter, BACKOFF_THRESHOLD, EMERGENCY_THRESHOLD


# ---------------------------------------------------------------------------
# Basic quota tracking
# ---------------------------------------------------------------------------

def test_acquire_within_quota():
    rl = RateLimiter(hourly_limit=100, safety_buffer=10)  # available=90
    assert rl.acquire(cost=5) is True


def test_remaining_decreases_after_acquire():
    rl = RateLimiter(hourly_limit=100, safety_buffer=10)
    before = rl.remaining()
    rl.acquire(cost=10)
    assert rl.remaining() == before - 10


def test_acquire_blocked_when_quota_exceeded():
    rl = RateLimiter(hourly_limit=20, safety_buffer=5)  # available=15
    # Use up all available quota
    rl.acquire(cost=15)
    # This should be blocked
    assert rl.acquire(cost=1) is False


def test_blocked_events_counter_increments():
    rl = RateLimiter(hourly_limit=10, safety_buffer=5)  # available=5
    rl.acquire(cost=5)
    rl.acquire(cost=1)  # blocked
    assert rl.get_metrics()["blocked_events"] >= 1


# ---------------------------------------------------------------------------
# Emergency stop
# ---------------------------------------------------------------------------

def test_emergency_stop_at_95_pct():
    rl = RateLimiter(hourly_limit=100, safety_buffer=0)  # available=100
    # Manually set calls_this_hour to 96 (> 95 %)
    rl.metrics.calls_this_hour = 96
    result = rl.acquire(cost=1)
    assert result is False
    assert rl.get_metrics()["emergency_stops"] >= 1


# ---------------------------------------------------------------------------
# Usage fraction
# ---------------------------------------------------------------------------

def test_usage_fraction_zero_at_start():
    rl = RateLimiter()
    assert rl.usage_fraction() == 0.0


def test_usage_fraction_after_calls():
    rl = RateLimiter(hourly_limit=100, safety_buffer=0)
    rl.acquire(cost=50)
    assert abs(rl.usage_fraction() - 0.50) < 0.01


# ---------------------------------------------------------------------------
# Metrics snapshot
# ---------------------------------------------------------------------------

def test_get_metrics_keys():
    rl = RateLimiter()
    m = rl.get_metrics()
    for key in (
        "calls_this_hour",
        "remaining_this_hour",
        "usage_pct",
        "blocked_events",
        "emergency_stops",
        "seconds_until_reset",
    ):
        assert key in m, f"missing key: {key}"


# ---------------------------------------------------------------------------
# Hourly reset
# ---------------------------------------------------------------------------

def test_hourly_reset(monkeypatch):
    rl = RateLimiter(hourly_limit=100, safety_buffer=0)
    rl.acquire(cost=50)
    assert rl.metrics.calls_this_hour == 50

    # Simulate an hour passing
    monkeypatch.setattr(rl, "_hour_start", rl._hour_start - 3601)
    assert rl.remaining() == 100  # reset occurred


# ---------------------------------------------------------------------------
# Seconds until reset
# ---------------------------------------------------------------------------

def test_seconds_until_reset_positive():
    rl = RateLimiter()
    secs = rl.seconds_until_reset()
    assert 0 < secs <= 3600
