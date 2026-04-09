"""Tests for automation/propagation_handler.py."""

from unittest.mock import MagicMock, patch
import pytest

from automation.propagation_handler import PropagationHandler
from automation.rate_limiter import RateLimiter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_orchestrator(rebuild_ok=True, test_ok=True, deploy_ok=True):
    orch = MagicMock()
    orch.rebuild = MagicMock()
    orch.test = MagicMock(return_value=test_ok)
    orch.deploy = MagicMock(return_value=deploy_ok)
    orch.rollback = MagicMock()
    return orch


SAMPLE_REGISTRY = {
    "owner/source-repo": {
        "dependents": ["owner/dep-a", "owner/dep-b"],
    },
    "owner/isolated-repo": {
        "dependents": [],
    },
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPropagationHandler:
    def test_processes_code_change(self):
        orch = _make_orchestrator()
        handler = PropagationHandler(registry=SAMPLE_REGISTRY, devops_orchestrator=orch)

        event = {
            "repo": "owner/source-repo",
            "ref": "refs/heads/main",
            "payload": {
                "commits": [{"added": [], "modified": ["README.md"], "removed": []}]
            },
        }
        handler.handle(event)

        assert orch.rebuild.call_count == 2  # called for dep-a and dep-b
        assert orch.test.call_count == 0     # code change → no test step
        m = handler.get_metrics()
        assert m["rebuilds"] == 2
        assert m["dependents_triggered"] == 2

    def test_processes_deps_change(self):
        orch = _make_orchestrator()
        handler = PropagationHandler(registry=SAMPLE_REGISTRY, devops_orchestrator=orch)

        event = {
            "repo": "owner/source-repo",
            "ref": "refs/heads/main",
            "payload": {
                "commits": [
                    {"added": ["requirements.txt"], "modified": [], "removed": []}
                ]
            },
        }
        handler.handle(event)

        assert orch.test.call_count == 2  # deps change → tests run

    def test_processes_contracts_change(self):
        orch = _make_orchestrator()
        handler = PropagationHandler(registry=SAMPLE_REGISTRY, devops_orchestrator=orch)

        event = {
            "repo": "owner/source-repo",
            "ref": "refs/heads/main",
            "payload": {
                "commits": [
                    {"added": ["api/contract.yaml"], "modified": [], "removed": []}
                ]
            },
        }
        handler.handle(event)

        # contracts → rebuild + test + staging + prod
        assert orch.rebuild.call_count == 2
        assert orch.test.call_count == 2
        assert orch.deploy.call_count == 4  # staging + prod for each dependent

    def test_rollback_on_test_failure(self):
        orch = _make_orchestrator(test_ok=False)
        handler = PropagationHandler(registry=SAMPLE_REGISTRY, devops_orchestrator=orch)

        event = {
            "repo": "owner/source-repo",
            "ref": "refs/heads/main",
            "payload": {
                "commits": [
                    {"added": ["requirements.txt"], "modified": [], "removed": []}
                ]
            },
        }
        handler.handle(event)

        assert orch.rollback.call_count >= 1
        m = handler.get_metrics()
        assert m["rollbacks"] >= 1

    def test_unknown_repo_is_skipped(self):
        orch = _make_orchestrator()
        handler = PropagationHandler(registry=SAMPLE_REGISTRY, devops_orchestrator=orch)

        event = {"repo": "unknown/repo", "ref": "refs/heads/main", "payload": {}}
        handler.handle(event)

        orch.rebuild.assert_not_called()

    def test_no_dependents_is_a_noop(self):
        orch = _make_orchestrator()
        handler = PropagationHandler(registry=SAMPLE_REGISTRY, devops_orchestrator=orch)

        event = {
            "repo": "owner/isolated-repo",
            "ref": "refs/heads/main",
            "payload": {"commits": []},
        }
        handler.handle(event)

        orch.rebuild.assert_not_called()

    def test_event_log_records_entries(self):
        log = []
        handler = PropagationHandler(
            registry=SAMPLE_REGISTRY,
            devops_orchestrator=_make_orchestrator(),
            event_log=log,
        )

        event = {
            "repo": "owner/source-repo",
            "ref": "refs/heads/main",
            "payload": {"commits": []},
        }
        handler.handle(event)

        actions = [e["action"] for e in log]
        assert "received" in actions
        assert "propagation_success" in actions

    def test_rate_limiter_blocks_propagation(self):
        limiter = RateLimiter(hourly_limit=10, safety_buffer=0)
        limiter.metrics.calls_this_hour = 10  # fully exhausted
        orch = _make_orchestrator()
        handler = PropagationHandler(
            registry=SAMPLE_REGISTRY,
            devops_orchestrator=orch,
            rate_limiter=limiter,
        )

        event = {
            "repo": "owner/source-repo",
            "ref": "refs/heads/main",
            "payload": {"commits": []},
        }
        handler.handle(event)

        orch.rebuild.assert_not_called()

    def test_metrics_track_failures(self):
        orch = MagicMock()
        orch.rebuild = MagicMock(side_effect=RuntimeError("build error"))
        handler = PropagationHandler(registry=SAMPLE_REGISTRY, devops_orchestrator=orch)

        event = {
            "repo": "owner/source-repo",
            "ref": "refs/heads/main",
            "payload": {"commits": [{"added": [], "modified": ["src/main.py"], "removed": []}]},
        }
        handler.handle(event)

        m = handler.get_metrics()
        assert m["failures"] >= 1
