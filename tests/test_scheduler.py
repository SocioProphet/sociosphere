"""Tests for automation/scheduler.py."""

import queue
import time
import pytest

pytest.importorskip("apscheduler", reason="apscheduler not installed")

from automation.rate_limiter import RateLimiter
from automation.scheduler import RegistryScheduler


@pytest.fixture
def limiter():
    return RateLimiter(hourly_limit=5000, safety_buffer=500)


@pytest.fixture
def eq():
    return queue.Queue()


@pytest.fixture
def scheduler(limiter, eq):
    called = {"propagation": [], "rebuild": [], "deep_scan": []}

    def propagation_handler(event):
        called["propagation"].append(event)

    def rebuild_fn():
        called["rebuild"].append(True)

    def deep_scan_fn():
        called["deep_scan"].append(True)

    sched = RegistryScheduler(
        rate_limiter=limiter,
        event_queue=eq,
        propagation_handler=propagation_handler,
        registry_rebuild_fn=rebuild_fn,
        deep_scan_fn=deep_scan_fn,
    )
    yield sched, called
    if sched._scheduler.running:
        sched.shutdown(wait=False)


class TestSchedulerJobs:
    def test_jobs_registered(self, scheduler):
        sched, _ = scheduler
        job_ids = {job.id for job in sched._scheduler.get_jobs()}
        assert "process_queue" in job_ids
        assert "registry_rebuild" in job_ids
        assert "deep_scan" in job_ids

    def test_process_queue_drains_events(self, scheduler):
        sched, called = scheduler
        sched._scheduler.start()

        # Put a test event in the queue
        sched.event_queue.put({"repo": "test/repo", "ref": "refs/heads/main"})

        # Manually invoke the queue processor
        sched._process_queue()

        assert len(called["propagation"]) == 1
        assert called["propagation"][0]["repo"] == "test/repo"

    def test_registry_rebuild_job(self, scheduler):
        sched, called = scheduler
        sched._run_registry_rebuild()
        assert len(called["rebuild"]) == 1

    def test_deep_scan_job(self, scheduler):
        sched, called = scheduler
        sched._run_deep_scan()
        assert len(called["deep_scan"]) == 1

    def test_metrics_track_jobs_run(self, scheduler):
        sched, _ = scheduler
        sched._run_registry_rebuild()
        m = sched.get_metrics()
        assert m["jobs_run"] >= 1

    def test_queue_skipped_when_api_usage_high(self, scheduler):
        sched, called = scheduler
        # Fill the rate limiter to > 80 %
        sched.rate_limiter.metrics.calls_this_hour = int(
            sched.rate_limiter.available_quota * 0.85
        )
        sched.event_queue.put({"repo": "test/repo"})
        sched._process_queue()
        # Event should not have been processed
        assert len(called["propagation"]) == 0

    def test_on_demand_trigger_adds_job(self, scheduler):
        sched, _ = scheduler
        sched._scheduler.start()
        sched.trigger_propagation("owner/my-repo")
        jobs = sched._scheduler.get_jobs()
        assert any("on_demand_owner/my-repo" in j.id for j in jobs)


class TestSchedulerRetry:
    def test_propagation_failure_records_metric(self, scheduler):
        sched, _ = scheduler

        def failing_handler(event):
            raise RuntimeError("boom")

        sched.propagation_handler = failing_handler

        # _exponential_retry would sleep; override to a no-op for speed
        sched._exponential_retry = lambda *a, **kw: None
        sched._run_propagation({"repo": "test/repo"})

        m = sched.get_metrics()
        assert m["jobs_failed"] >= 1
