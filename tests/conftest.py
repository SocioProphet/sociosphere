"""Shared pytest fixtures for the automation test suite."""

import queue
import pytest

from automation.rate_limiter import RateLimiter


@pytest.fixture
def rate_limiter():
    """A fresh RateLimiter with a small quota for fast tests."""
    return RateLimiter(hourly_limit=100, safety_buffer=10)


@pytest.fixture
def event_queue():
    return queue.Queue()


@pytest.fixture
def sample_push_event():
    return {
        "event": "push",
        "ref": "refs/heads/main",
        "repo": "SocioProphet/sociosphere",
        "payload": {
            "ref": "refs/heads/main",
            "repository": {"full_name": "SocioProphet/sociosphere"},
            "commits": [
                {
                    "id": "abc123",
                    "message": "Update README",
                    "added": [],
                    "modified": ["README.md"],
                    "removed": [],
                }
            ],
        },
        "received_at": "2026-04-06T00:00:00+00:00",
    }
