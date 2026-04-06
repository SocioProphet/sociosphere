"""
tests/test_registry.py

Unit tests for registry YAML files and the registry CLI tools.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

REGISTRY_DIR = ROOT / "registry"


# ── helpers ───────────────────────────────────────────────────────────────────

def _load_yaml(path: Path):
    if not HAS_YAML:
        pytest.skip("PyYAML not installed")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# ── canonical-repos.yaml tests ────────────────────────────────────────────────

class TestCanonicalRepos:
    FILE = REGISTRY_DIR / "canonical-repos.yaml"

    def test_file_exists(self):
        assert self.FILE.exists(), f"Missing: {self.FILE.relative_to(ROOT)}"

    def test_has_repositories_key(self):
        data = _load_yaml(self.FILE)
        assert "repositories" in data

    def test_repositories_non_empty(self):
        data = _load_yaml(self.FILE)
        assert len(data["repositories"]) > 0

    def test_required_fields_present(self):
        data = _load_yaml(self.FILE)
        required = ["name", "org", "layer", "purpose", "status"]
        for repo in data["repositories"]:
            for field in required:
                assert field in repo, (
                    f"Repo '{repo.get('name')}' missing field '{field}'"
                )

    def test_sociosphere_entry_exists(self):
        data = _load_yaml(self.FILE)
        names = {r["name"] for r in data["repositories"]}
        assert "sociosphere" in names

    def test_core_repos_present(self):
        data = _load_yaml(self.FILE)
        names = {r["name"] for r in data["repositories"]}
        expected = {
            "sociosphere",
            "prophet-platform",
            "TriTRPC",
            "agentplane",
            "new-hope",
        }
        missing = expected - names
        assert not missing, f"Missing core repos: {missing}"

    def test_status_values_valid(self):
        data = _load_yaml(self.FILE)
        valid = {"active", "archived", "deprecated", "unknown"}
        for repo in data["repositories"]:
            assert repo.get("status") in valid, (
                f"Invalid status '{repo.get('status')}' for repo '{repo.get('name')}'"
            )


# ── repository-ontology.yaml tests ───────────────────────────────────────────

class TestRepositoryOntology:
    FILE = REGISTRY_DIR / "repository-ontology.yaml"

    def test_file_exists(self):
        assert self.FILE.exists(), f"Missing: {self.FILE.relative_to(ROOT)}"

    def test_has_ontologies_key(self):
        data = _load_yaml(self.FILE)
        assert "ontologies" in data

    def test_ontologies_non_empty(self):
        data = _load_yaml(self.FILE)
        assert len(data["ontologies"]) > 0

    def test_sociosphere_ontology_has_vocabulary(self):
        data = _load_yaml(self.FILE)
        onto = data["ontologies"].get("sociosphere", {})
        assert "controlled_vocabulary" in onto
        assert len(onto["controlled_vocabulary"]) > 0


# ── dependency-graph.yaml tests ───────────────────────────────────────────────

class TestDependencyGraph:
    FILE = REGISTRY_DIR / "dependency-graph.yaml"

    def test_file_exists(self):
        assert self.FILE.exists(), f"Missing: {self.FILE.relative_to(ROOT)}"

    def test_has_dependencies_key(self):
        data = _load_yaml(self.FILE)
        assert "dependencies" in data

    def test_sociosphere_has_depends_on(self):
        data = _load_yaml(self.FILE)
        entry = data["dependencies"].get("sociosphere", {})
        assert "depends_on" in entry

    def test_sociosphere_depends_on_prophet_platform(self):
        data = _load_yaml(self.FILE)
        deps = data["dependencies"].get("sociosphere", {}).get("depends_on", [])
        names = [d["name"] if isinstance(d, dict) else d for d in deps]
        assert "prophet-platform" in names


# ── change-propagation-rules.yaml tests ──────────────────────────────────────

class TestChangePropagationRules:
    FILE = REGISTRY_DIR / "change-propagation-rules.yaml"

    def test_file_exists(self):
        assert self.FILE.exists(), f"Missing: {self.FILE.relative_to(ROOT)}"

    def test_has_propagation_rules_key(self):
        data = _load_yaml(self.FILE)
        assert "propagation_rules" in data

    def test_sociosphere_rule_has_trigger(self):
        data = _load_yaml(self.FILE)
        rule = data["propagation_rules"].get("sociosphere", {}).get("on_main_merge", {})
        assert "trigger" in rule

    def test_sociosphere_rule_has_automation(self):
        data = _load_yaml(self.FILE)
        rule = data["propagation_rules"].get("sociosphere", {}).get("on_main_merge", {})
        assert "automation" in rule
        assert len(rule["automation"]) > 0


# ── devops-automation.yaml tests ─────────────────────────────────────────────

class TestDevopsAutomation:
    FILE = REGISTRY_DIR / "devops-automation.yaml"

    def test_file_exists(self):
        assert self.FILE.exists(), f"Missing: {self.FILE.relative_to(ROOT)}"

    def test_has_devops_rules_key(self):
        data = _load_yaml(self.FILE)
        assert "devops_rules" in data

    def test_sociosphere_has_build_and_test(self):
        data = _load_yaml(self.FILE)
        rules = data["devops_rules"].get("sociosphere", {})
        assert "build" in rules
        assert "test" in rules


# ── deduplication-map.yaml tests ─────────────────────────────────────────────

class TestDeduplicationMap:
    FILE = REGISTRY_DIR / "deduplication-map.yaml"

    def test_file_exists(self):
        assert self.FILE.exists(), f"Missing: {self.FILE.relative_to(ROOT)}"

    def test_has_duplicates_key(self):
        data = _load_yaml(self.FILE)
        assert "duplicates" in data

    def test_speechlab_duplicate_listed(self):
        data = _load_yaml(self.FILE)
        assert "speechlab" in data["duplicates"]

    def test_each_duplicate_has_instances(self):
        data = _load_yaml(self.FILE)
        for name, entry in data["duplicates"].items():
            assert "instances" in entry, f"Duplicate '{name}' missing 'instances'"
            assert len(entry["instances"]) >= 2, (
                f"Duplicate '{name}' should have at least 2 instances"
            )
