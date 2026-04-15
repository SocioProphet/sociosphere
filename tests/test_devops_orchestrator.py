"""tests/test_devops_orchestrator.py — unit tests for DevOpsOrchestrator."""

from __future__ import annotations

import pytest
from pathlib import Path

from engines.devops_orchestrator import DevOpsOrchestrator


REGISTRY_DIR = Path(__file__).parent.parent / "registry"


@pytest.fixture
def orch() -> DevOpsOrchestrator:
    o = DevOpsOrchestrator(REGISTRY_DIR)
    o.load()
    return o


def test_all_repo_ids_nonempty(orch: DevOpsOrchestrator) -> None:
    ids = orch.all_repo_ids()
    assert len(ids) > 0


def test_get_repo_config_known(orch: DevOpsOrchestrator) -> None:
    cfg = orch.get_repo_config("sociosphere")
    assert cfg is not None
    assert "ci_steps" in cfg


def test_get_repo_config_unknown_returns_none(orch: DevOpsOrchestrator) -> None:
    assert orch.get_repo_config("nonexistent-xyz") is None


def test_deployable_repos_all_have_deploy_true(orch: DevOpsOrchestrator) -> None:
    for repo_id in orch.deployable_repos():
        cfg = orch.get_repo_config(repo_id)
        assert cfg is not None
        assert cfg.get("deploy", False) is True


def test_fips_repos_all_have_fips_required_true(orch: DevOpsOrchestrator) -> None:
    for repo_id in orch.fips_required_repos():
        cfg = orch.get_repo_config(repo_id)
        assert cfg is not None
        assert cfg.get("fips_required", False) is True


def test_prophet_platform_is_deployable(orch: DevOpsOrchestrator) -> None:
    assert "prophet-platform" in orch.deployable_repos()


def test_prophet_platform_is_fips(orch: DevOpsOrchestrator) -> None:
    assert "prophet-platform" in orch.fips_required_repos()


def test_resolve_ci_steps_sociosphere(orch: DevOpsOrchestrator) -> None:
    steps = orch.resolve_ci_steps("sociosphere")
    assert len(steps) > 0
    names = [s["name"] for s in steps]
    assert "ui-check" in names


def test_resolve_ci_steps_unknown_returns_empty(orch: DevOpsOrchestrator) -> None:
    assert orch.resolve_ci_steps("nonexistent") == []


def test_resolve_deploy_steps_deployable(orch: DevOpsOrchestrator) -> None:
    steps = orch.resolve_deploy_steps("prophet-platform")
    assert len(steps) > 0


def test_resolve_deploy_steps_non_deployable_returns_empty(
    orch: DevOpsOrchestrator,
) -> None:
    steps = orch.resolve_deploy_steps("fips-compliance")
    assert steps == []


def test_resolve_fips_validator_fips_repo(orch: DevOpsOrchestrator) -> None:
    validator = orch.resolve_fips_validator("prophet-platform")
    assert validator is not None
    assert "fips" in validator.lower()


def test_resolve_fips_validator_non_fips_returns_none(
    orch: DevOpsOrchestrator,
) -> None:
    validator = orch.resolve_fips_validator("sociosphere")
    assert validator is None


def test_build_template_for_known_language(orch: DevOpsOrchestrator) -> None:
    template = orch.build_template_for("sociosphere")
    assert template is not None


def test_pipeline_stages_nonempty(orch: DevOpsOrchestrator) -> None:
    stages = orch.pipeline_stages()
    assert len(stages) > 0


def test_stages_for_context_pr(orch: DevOpsOrchestrator) -> None:
    stages = orch.stages_for_context(is_pr=True, repo_id="prophet-platform")
    ids = {s["id"] for s in stages}
    assert "lint" in ids
    assert "test" in ids
    # deploy stage should not appear on PR
    assert "deploy" not in ids


def test_stages_for_context_push_main_deployable(orch: DevOpsOrchestrator) -> None:
    stages = orch.stages_for_context(is_pr=False, repo_id="prophet-platform")
    ids = {s["id"] for s in stages}
    assert "deploy" in ids
    assert "build_image" in ids


def test_stages_for_context_push_main_non_deployable(
    orch: DevOpsOrchestrator,
) -> None:
    stages = orch.stages_for_context(is_pr=False, repo_id="fips-compliance")
    ids = {s["id"] for s in stages}
    assert "deploy" not in ids
    assert "build_image" not in ids


def test_summary_keys(orch: DevOpsOrchestrator) -> None:
    summary = orch.summary()
    for key in [
        "total_repos_configured",
        "deployable",
        "fips_required",
        "pipeline_stages",
        "language_templates",
    ]:
        assert key in summary
