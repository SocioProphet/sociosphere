"""tests/test_metrics_collector.py — unit tests for MetricsCollector."""

from __future__ import annotations

import pytest
from pathlib import Path

from engines.metrics_collector import MetricsCollector


REGISTRY_DIR = Path(__file__).parent.parent / "registry"


@pytest.fixture
def collector() -> MetricsCollector:
    c = MetricsCollector(REGISTRY_DIR)
    c.load()
    return c


def test_repo_health_total_is_53(collector: MetricsCollector) -> None:
    health = collector.repo_health()
    assert health["total"] == 53


def test_repo_health_has_active_and_archived(collector: MetricsCollector) -> None:
    health = collector.repo_health()
    assert "active" in health["by_status"]
    assert "archived" in health["by_status"]


def test_role_distribution_nonempty(collector: MetricsCollector) -> None:
    dist = collector.role_distribution()
    assert len(dist) > 0
    assert sum(dist.values()) == 53


def test_language_distribution_nonempty(collector: MetricsCollector) -> None:
    dist = collector.language_distribution()
    assert len(dist) > 0
    assert sum(dist.values()) == 53


def test_dependency_stats_has_expected_keys(collector: MetricsCollector) -> None:
    stats = collector.dependency_stats()
    for key in [
        "total_edges",
        "by_type",
        "repos_with_dependencies",
        "repos_that_are_dependencies",
        "isolated_repos",
    ]:
        assert key in stats


def test_dependency_stats_edges_positive(collector: MetricsCollector) -> None:
    stats = collector.dependency_stats()
    assert stats["total_edges"] > 0


def test_propagation_coverage_keys(collector: MetricsCollector) -> None:
    cov = collector.propagation_coverage()
    assert "active_repos" in cov
    assert "repos_with_rules" in cov
    assert "coverage_pct" in cov


def test_propagation_coverage_pct_in_range(collector: MetricsCollector) -> None:
    cov = collector.propagation_coverage()
    assert 0.0 <= cov["coverage_pct"] <= 100.0


def test_devops_coverage_keys(collector: MetricsCollector) -> None:
    cov = collector.devops_coverage()
    for key in [
        "active_repos",
        "repos_with_devops_config",
        "coverage_pct",
        "deployable",
        "fips_required",
    ]:
        assert key in cov


def test_devops_coverage_pct_in_range(collector: MetricsCollector) -> None:
    cov = collector.devops_coverage()
    assert 0.0 <= cov["coverage_pct"] <= 100.0


def test_deduplication_progress_nonempty(collector: MetricsCollector) -> None:
    progress = collector.deduplication_progress()
    assert isinstance(progress, dict)
    assert "total_identified" in progress


def test_full_report_has_all_sections(collector: MetricsCollector) -> None:
    report = collector.full_report()
    for key in [
        "registry_version",
        "organization",
        "repo_health",
        "role_distribution",
        "language_distribution",
        "dependency_stats",
        "propagation_coverage",
        "devops_coverage",
        "deduplication_progress",
    ]:
        assert key in report


def test_full_report_organization(collector: MetricsCollector) -> None:
    report = collector.full_report()
    assert report["organization"] == "SocioProphet"


def test_full_report_registry_version(collector: MetricsCollector) -> None:
    report = collector.full_report()
    assert report["registry_version"] == "1.0.0"
