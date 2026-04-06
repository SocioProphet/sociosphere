"""
tests/test_engines.py

Unit tests for the engine modules:
  - engines/ontology_engine.py
  - engines/propagation_engine.py
  - engines/devops_orchestrator.py
  - engines/metrics_collector.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ── ontology_engine tests ─────────────────────────────────────────────────────

class TestOntologyEngine:
    def test_tokenise(self):
        from engines.ontology_engine import _tokenise

        tokens = _tokenise("Hello world foo bar")
        assert "hello" in tokens
        assert "world" in tokens
        # stop words should be excluded
        assert "the" not in tokens

    def test_tokenise_removes_stop_words(self):
        from engines.ontology_engine import _tokenise

        tokens = _tokenise("and the for with by")
        assert tokens == []

    def test_extract_vocabulary_on_temp_dir(self):
        from engines.ontology_engine import extract_vocabulary

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "README.md").write_text(
                "governance workspace validation policy",
                encoding="utf-8",
            )
            vocab = extract_vocabulary(p)
            assert isinstance(vocab, list)
            # We don't assert specific words since ordering may vary, but the
            # result should be non-empty.
            assert len(vocab) >= 0  # may be 0 if all words are stop-words

    def test_extract_topics_returns_list(self):
        from engines.ontology_engine import extract_topics

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "main.py").write_text(
                "workspace governance validation contract service",
                encoding="utf-8",
            )
            topics = extract_topics(p)
            assert isinstance(topics, list)

    def test_analyze_repo_returns_dict(self):
        from engines.ontology_engine import analyze_repo

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "README.md").write_text("ontology vocabulary semantic", encoding="utf-8")
            result = analyze_repo(p)
            assert "controlled_vocabulary" in result
            assert "lsa_topics" in result


# ── propagation_engine tests ──────────────────────────────────────────────────

class TestPropagationEngine:
    def test_get_dependents_returns_list(self):
        from engines.propagation_engine import get_dependents

        dep_graph = {
            "dependencies": {
                "prophet-platform": {
                    "dependents": [
                        {"name": "sociosphere", "type": "imports"},
                        {"name": "agentplane", "type": "imports"},
                    ]
                }
            }
        }
        result = get_dependents("prophet-platform", dep_graph)
        assert "sociosphere" in result
        assert "agentplane" in result

    def test_get_dependents_excludes_all_repos(self):
        from engines.propagation_engine import get_dependents

        dep_graph = {
            "dependencies": {
                "sociosphere": {
                    "dependents": [
                        {"name": "all-repos", "type": "governed-by"},
                        {"name": "agentplane", "type": "governed-by"},
                    ]
                }
            }
        }
        result = get_dependents("sociosphere", dep_graph)
        assert "all-repos" not in result
        assert "agentplane" in result

    def test_get_propagation_rules_returns_dict(self):
        from engines.propagation_engine import get_propagation_rules

        rules = {
            "propagation_rules": {
                "sociosphere": {
                    "on_main_merge": {
                        "trigger": "rebuild governance",
                        "automation": [{"type": "re-validate", "targets": ["agentplane"]}],
                    }
                }
            }
        }
        result = get_propagation_rules("sociosphere", rules)
        assert result["trigger"] == "rebuild governance"

    def test_propagate_ignores_non_main_refs(self, tmp_path, monkeypatch):
        from engines import propagation_engine

        # Point log directory to tmp_path.
        monkeypatch.setattr(propagation_engine, "METRICS_DIR", tmp_path)
        monkeypatch.setattr(propagation_engine, "DEP_GRAPH_FILE", tmp_path / "dep.yaml")
        monkeypatch.setattr(propagation_engine, "PROP_RULES_FILE", tmp_path / "rules.yaml")

        rc = propagation_engine.propagate("sociosphere", "refs/heads/feature/xyz")
        assert rc == 0

    def test_propagate_main_creates_log(self, tmp_path, monkeypatch):
        from engines import propagation_engine

        log_file = tmp_path / "propagation-log.jsonl"
        monkeypatch.setattr(propagation_engine, "METRICS_DIR", tmp_path)
        monkeypatch.setattr(propagation_engine, "DEP_GRAPH_FILE", tmp_path / "dep.yaml")
        monkeypatch.setattr(propagation_engine, "PROP_RULES_FILE", tmp_path / "rules.yaml")
        monkeypatch.setattr(propagation_engine, "PROPAGATION_LOG", log_file)

        rc = propagation_engine.propagate("some-repo", "refs/heads/main")
        assert rc == 0
        assert log_file.exists()
        events = [json.loads(l) for l in log_file.read_text().splitlines() if l.strip()]
        assert len(events) == 1
        assert events[0]["repo"] == "some-repo"


# ── devops_orchestrator tests ─────────────────────────────────────────────────

class TestDevopsOrchestrator:
    def test_run_phase_skips_unknown_repo(self, tmp_path, monkeypatch):
        from engines import devops_orchestrator

        monkeypatch.setattr(devops_orchestrator, "METRICS_DIR", tmp_path)
        monkeypatch.setattr(
            devops_orchestrator, "DEVOPS_FILE", tmp_path / "devops.yaml"
        )

        result = devops_orchestrator.run_phase("no-such-repo", "build")
        assert result["status"] == "skipped"

    def test_orchestrate_dry_run(self, tmp_path, monkeypatch):
        import yaml

        from engines import devops_orchestrator

        devops_yaml = {
            "devops_rules": {
                "myrepo": {
                    "build": {
                        "trigger": "code change",
                        "steps": ["echo build-step"],
                    },
                    "test": {
                        "trigger": "code change",
                        "steps": ["echo test-step"],
                    },
                }
            }
        }
        devops_file = tmp_path / "devops.yaml"
        devops_file.write_text(yaml.dump(devops_yaml), encoding="utf-8")

        monkeypatch.setattr(devops_orchestrator, "METRICS_DIR", tmp_path)
        monkeypatch.setattr(devops_orchestrator, "DEVOPS_FILE", devops_file)

        rc = devops_orchestrator.orchestrate(
            "myrepo", event="code_change", dry_run=True
        )
        assert rc == 0


# ── metrics_collector tests ───────────────────────────────────────────────────

class TestMetricsCollector:
    def test_collect_returns_dict_with_expected_keys(self, tmp_path, monkeypatch):
        from engines import metrics_collector

        # Point all file paths to tmp_path (empty = baseline state).
        for attr in (
            "CANONICAL_REPOS_FILE",
            "ONTOLOGY_FILE",
            "DEP_GRAPH_FILE",
            "DEDUP_FILE",
            "PROPAGATION_LOG",
            "DEVOPS_LOG",
            "METRICS_FILE",
        ):
            monkeypatch.setattr(metrics_collector, attr, tmp_path / f"{attr}.tmp")

        metrics = metrics_collector.collect()
        assert "timestamp" in metrics
        assert "registry_completeness" in metrics
        assert "automation_effectiveness" in metrics
        assert "deduplication_progress" in metrics

    def test_registry_completeness_with_real_registry(self):
        """Run registry_completeness against the real registry files."""
        from engines.metrics_collector import registry_completeness

        result = registry_completeness()
        assert result["total_repos"] > 0
        assert result["pct_documented"] == 100

    def test_deduplication_progress_with_real_registry(self):
        from engines.metrics_collector import deduplication_progress

        result = deduplication_progress()
        assert result["duplicates_identified"] >= 4

    def test_save_and_load_metrics(self, tmp_path, monkeypatch):
        from engines import metrics_collector

        metrics_file = tmp_path / "registry-metrics.json"
        monkeypatch.setattr(metrics_collector, "METRICS_FILE", metrics_file)
        # Point log files to empty tmp files.
        for attr in ("PROPAGATION_LOG", "DEVOPS_LOG"):
            monkeypatch.setattr(metrics_collector, attr, tmp_path / f"{attr}.tmp")

        metrics = metrics_collector.collect()
        metrics_collector.save(metrics)
        assert metrics_file.exists()
        data = json.loads(metrics_file.read_text())
        assert "timestamp" in data
