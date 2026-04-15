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
        for repo in data["repositories"]:
            assert "name" in repo, f"Repo entry missing field 'name': {repo}"
            assert "status" in repo, f"Repo '{repo.get('name')}' missing field 'status'"
            assert (
                all(field in repo for field in ("org", "layer", "purpose"))
                or all(field in repo for field in ("id", "url", "role", "description"))
            ), f"Repo '{repo.get('name')}' is missing required metadata"

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
            "tritrpc",
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


class TestWorkspaceManifest:
    FILE = ROOT / "manifest" / "workspace.toml"

    def test_manifest_is_valid_toml(self):
        import tomllib

        data = tomllib.loads(self.FILE.read_text(encoding="utf-8"))
        repos = data.get("repos", [])
        assert repos
        names = {repo["name"] for repo in repos}
        assert "socioprophet_integration" in names


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

    @staticmethod
    def _sociosphere_dependencies(data):
        if "dependencies" in data:
            deps = data["dependencies"].get("sociosphere", {}).get("depends_on", [])
            return [d["name"] if isinstance(d, dict) else d for d in deps]
        return [edge["to"] for edge in data.get("edges", []) if edge.get("from") == "sociosphere"]

    def test_file_exists(self):
        assert self.FILE.exists(), f"Missing: {self.FILE.relative_to(ROOT)}"

    def test_has_dependencies_key(self):
        data = _load_yaml(self.FILE)
        assert "dependencies" in data or "edges" in data

    def test_sociosphere_has_depends_on(self):
        data = _load_yaml(self.FILE)
        assert self._sociosphere_dependencies(data)

    def test_sociosphere_depends_on_core_protocols(self):
        data = _load_yaml(self.FILE)
        deps = self._sociosphere_dependencies(data)
        # Dependency IDs are normalized to lowercase in the current registry helpers.
        assert "tritrpc" in deps


# ── change-propagation-rules.yaml tests ──────────────────────────────────────

class TestChangePropagationRules:
    FILE = REGISTRY_DIR / "change-propagation-rules.yaml"

    @staticmethod
    def _sociosphere_rule(data):
        if "propagation_rules" in data:
            return data["propagation_rules"].get("sociosphere", {}).get("on_main_merge", {})
        for rule in data.get("rules", []):
            trigger_repo = rule.get("trigger", {}).get("repo")
            if trigger_repo == "sociosphere":
                return rule
        return {}

    def test_file_exists(self):
        assert self.FILE.exists(), f"Missing: {self.FILE.relative_to(ROOT)}"

    def test_has_propagation_rules_key(self):
        data = _load_yaml(self.FILE)
        assert "propagation_rules" in data or "rules" in data

    def test_sociosphere_rule_has_trigger(self):
        data = _load_yaml(self.FILE)
        rule = self._sociosphere_rule(data)
        assert "trigger" in rule or "id" in rule

    def test_sociosphere_rule_has_automation(self):
        data = _load_yaml(self.FILE)
        rule = self._sociosphere_rule(data)
        automation = rule.get("automation") or rule.get("propagate_to", [])
        assert automation


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
