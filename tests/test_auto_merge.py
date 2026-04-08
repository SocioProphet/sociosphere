"""Tests for automation/auto_merge_handler.py."""

from unittest.mock import MagicMock, patch
import pytest

from automation.auto_merge_handler import AutoMergeHandler
from automation.rate_limiter import RateLimiter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pr(
    number: int,
    merged: bool = False,
    mergeable_state: str = "clean",
):
    pr = MagicMock()
    pr.number = number
    pr.merged = merged
    pr.mergeable_state = mergeable_state
    pr.merge = MagicMock()
    pr.update = MagicMock()
    return pr


def _make_repo(prs: dict):
    repo = MagicMock()
    repo.get_pull = lambda n: prs[n]
    return repo


def _make_gh(repo):
    gh = MagicMock()
    gh.get_repo = MagicMock(return_value=repo)
    return gh


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAutoMergeHandler:
    def test_merges_both_prs_in_order(self):
        pr1 = _make_pr(1)
        pr2 = _make_pr(2)
        repo = _make_repo({1: pr1, 2: pr2})
        gh = _make_gh(repo)

        handler = AutoMergeHandler(
            gh,
            "owner/repo",
            phase_a_pr_numbers=[1, 2],
            ci_wait_seconds=0,
        )
        result = handler.run()

        assert result is True
        pr1.merge.assert_called_once()
        pr2.merge.assert_called_once()
        m = handler.get_metrics()
        assert m["prs_merged"] == 2
        assert m["prs_failed"] == 0

    def test_skips_already_merged_pr(self):
        pr1 = _make_pr(1, merged=True)
        pr2 = _make_pr(2)
        repo = _make_repo({1: pr1, 2: pr2})
        gh = _make_gh(repo)

        handler = AutoMergeHandler(
            gh,
            "owner/repo",
            phase_a_pr_numbers=[1, 2],
            ci_wait_seconds=0,
        )
        result = handler.run()

        assert result is True
        pr1.merge.assert_not_called()
        pr2.merge.assert_called_once()
        m = handler.get_metrics()
        assert m["prs_skipped"] == 1
        assert m["prs_merged"] == 1

    def test_returns_false_on_merge_conflict(self):
        pr1 = _make_pr(1, mergeable_state="dirty")
        repo = _make_repo({1: pr1})
        gh = _make_gh(repo)

        handler = AutoMergeHandler(
            gh,
            "owner/repo",
            phase_a_pr_numbers=[1],
            ci_wait_seconds=0,
        )
        result = handler.run()

        assert result is False
        pr1.merge.assert_not_called()
        m = handler.get_metrics()
        assert m["prs_failed"] == 1

    def test_retries_on_merge_failure(self):
        pr1 = _make_pr(1)
        # First two merge attempts raise, third succeeds
        pr1.merge = MagicMock(
            side_effect=[Exception("rate limited"), Exception("timeout"), None]
        )
        repo = _make_repo({1: pr1})
        gh = _make_gh(repo)

        handler = AutoMergeHandler(
            gh,
            "owner/repo",
            phase_a_pr_numbers=[1],
            ci_wait_seconds=0,
        )
        # Patch sleep to speed up test
        with patch("automation.auto_merge_handler.time.sleep"):
            result = handler.run()

        assert result is True
        assert pr1.merge.call_count == 3

    def test_returns_false_when_repo_not_found(self):
        gh = MagicMock()
        gh.get_repo = MagicMock(side_effect=Exception("not found"))

        handler = AutoMergeHandler(gh, "owner/repo", phase_a_pr_numbers=[1])
        result = handler.run()

        assert result is False

    def test_skips_missing_pr_number(self):
        pr2 = _make_pr(2)
        repo = MagicMock()
        repo.get_pull = MagicMock(
            side_effect=lambda n: pr2 if n == 2 else (_ for _ in ()).throw(
                Exception("not found")
            )
        )
        gh = _make_gh(repo)

        handler = AutoMergeHandler(
            gh,
            "owner/repo",
            phase_a_pr_numbers=[1, 2],
            ci_wait_seconds=0,
        )
        with patch("automation.auto_merge_handler.time.sleep"):
            result = handler.run()

        assert result is True
        pr2.merge.assert_called_once()
        m = handler.get_metrics()
        assert m["prs_skipped"] == 1

    def test_rate_limiter_is_called(self):
        pr1 = _make_pr(1)
        repo = _make_repo({1: pr1})
        gh = _make_gh(repo)
        limiter = RateLimiter(hourly_limit=100, safety_buffer=0)

        handler = AutoMergeHandler(
            gh,
            "owner/repo",
            rate_limiter=limiter,
            phase_a_pr_numbers=[1],
            ci_wait_seconds=0,
        )
        with patch("automation.auto_merge_handler.time.sleep"):
            handler.run()

        # Some API calls should have been recorded
        assert limiter.metrics.calls_this_hour > 0
