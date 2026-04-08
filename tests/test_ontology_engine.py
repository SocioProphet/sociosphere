"""tests/test_ontology_engine.py — unit tests for OntologyEngine."""

from __future__ import annotations

import pytest
from pathlib import Path

from engines.ontology_engine import OntologyEngine


REGISTRY_DIR = Path(__file__).parent.parent / "registry"


@pytest.fixture
def engine() -> OntologyEngine:
    e = OntologyEngine(REGISTRY_DIR)
    e.load()
    return e


def test_load_returns_53_repos(engine: OntologyEngine) -> None:
    assert len(engine.all_repos()) == 53


def test_get_repo_returns_known_repo(engine: OntologyEngine) -> None:
    repo = engine.get_repo("sociosphere")
    assert repo is not None
    assert repo["name"] == "sociosphere"
    assert repo["role"] == "orchestrator"


def test_get_repo_unknown_returns_none(engine: OntologyEngine) -> None:
    assert engine.get_repo("nonexistent-repo-xyz") is None


def test_repos_by_role_returns_correct_items(engine: OntologyEngine) -> None:
    adapters = engine.repos_by_role("adapter")
    ids = {r["id"] for r in adapters}
    assert "trit-to-trust" in ids
    assert "connector-github" in ids


def test_repos_by_status_active(engine: OntologyEngine) -> None:
    active = engine.repos_by_status("active")
    assert len(active) > 0
    for r in active:
        assert r["status"] == "active"


def test_repos_by_status_archived(engine: OntologyEngine) -> None:
    archived = engine.repos_by_status("archived")
    ids = {r["id"] for r in archived}
    assert "socios" in ids
    assert "tritrpc-notes-archive" in ids


def test_repos_by_tag(engine: OntologyEngine) -> None:
    ml_repos = engine.repos_by_tag("ml")
    assert len(ml_repos) > 0
    for r in ml_repos:
        assert "ml" in r["tags"]


def test_repos_by_language(engine: OntologyEngine) -> None:
    python_repos = engine.repos_by_language("Python")
    assert len(python_repos) > 0
    for r in python_repos:
        assert r["primary_language"] == "Python"


def test_all_roles_includes_expected(engine: OntologyEngine) -> None:
    roles = engine.all_roles()
    for expected in ["orchestrator", "component", "adapter", "protocol", "frontend"]:
        assert expected in roles


def test_get_role_definition(engine: OntologyEngine) -> None:
    defn = engine.get_role_definition("orchestrator")
    assert defn is not None
    assert "iri" in defn
    assert "description" in defn


def test_get_unknown_role_definition_returns_none(engine: OntologyEngine) -> None:
    assert engine.get_role_definition("nonexistent-role") is None


def test_all_relationships_nonempty(engine: OntologyEngine) -> None:
    rels = engine.all_relationships()
    assert len(rels) > 0
    assert "depends_on" in rels


def test_extract_tag_cloud(engine: OntologyEngine) -> None:
    cloud = engine.extract_tag_cloud()
    assert isinstance(cloud, dict)
    # Tags should be sorted by count descending
    counts = list(cloud.values())
    assert counts == sorted(counts, reverse=True)


def test_extract_role_summary(engine: OntologyEngine) -> None:
    summary = engine.extract_role_summary()
    assert isinstance(summary, dict)
    total = sum(summary.values())
    assert total == len(engine.all_repos())


def test_extract_language_summary(engine: OntologyEngine) -> None:
    summary = engine.extract_language_summary()
    assert isinstance(summary, dict)
    total = sum(summary.values())
    assert total == len(engine.all_repos())


def test_validate_repos_against_ontology_no_warnings(engine: OntologyEngine) -> None:
    warnings = engine.validate_repos_against_ontology()
    assert warnings == [], f"Unexpected ontology warnings: {warnings}"
