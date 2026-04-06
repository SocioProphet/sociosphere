"""
tests/test_cli.py

Unit tests for the CLI tools:
  - cli/rebuild-registry.py  (imports as module)
  - cli/validate-deps.py
  - cli/dedup-report.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _import_cli(name: str):
    """Load a CLI script as a module without executing __main__ code."""
    script = ROOT / "cli" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── rebuild-registry tests ────────────────────────────────────────────────────

class TestRebuildRegistry:
    def test_validate_repo_entry_passes_complete_entry(self):
        mod = _import_cli("rebuild-registry")
        repo = {
            "name": "sociosphere",
            "org": "SocioProphet",
            "layer": "control-plane",
            "purpose": "Workspace controller",
            "status": "active",
        }
        errors = mod.validate_repo_entry(repo)
        assert errors == []

    def test_validate_repo_entry_catches_missing_field(self):
        mod = _import_cli("rebuild-registry")
        repo = {"name": "incomplete"}
        errors = mod.validate_repo_entry(repo)
        assert any("org" in e for e in errors)

    def test_validate_repo_entry_catches_bad_status(self):
        mod = _import_cli("rebuild-registry")
        repo = {
            "name": "x",
            "org": "y",
            "layer": "z",
            "purpose": "p",
            "status": "bad-value",
        }
        errors = mod.validate_repo_entry(repo)
        assert any("status" in e for e in errors)

    def test_run_with_real_registry(self):
        mod = _import_cli("rebuild-registry")
        rc = mod.run()
        assert rc == 0


# ── validate-deps tests ───────────────────────────────────────────────────────

class TestValidateDeps:
    def test_detect_cycles_finds_direct_cycle(self):
        mod = _import_cli("validate-deps")
        graph = {"a": ["b"], "b": ["a"]}
        cycles = mod._detect_cycles(graph)
        assert len(cycles) > 0

    def test_detect_cycles_no_cycles(self):
        mod = _import_cli("validate-deps")
        graph = {"a": ["b"], "b": ["c"], "c": []}
        cycles = mod._detect_cycles(graph)
        assert cycles == []

    def test_validate_with_real_registry(self):
        mod = _import_cli("validate-deps")
        rc = mod.validate(strict=False)
        assert rc == 0


# ── dedup-report tests ────────────────────────────────────────────────────────

class TestDedupReport:
    def test_report_exits_ok(self, capsys):
        mod = _import_cli("dedup-report")
        rc = mod.report(pending_only=False)
        assert rc == 0
        out = capsys.readouterr().out
        assert "DEDUPLICATION REPORT" in out

    def test_report_shows_speechlab(self, capsys):
        mod = _import_cli("dedup-report")
        mod.report(pending_only=False)
        out = capsys.readouterr().out
        assert "speechlab" in out.lower()

    def test_report_pending_only_hides_resolved(self, capsys, tmp_path, monkeypatch):
        import yaml

        mod = _import_cli("dedup-report")
        dedup_yaml = {
            "duplicates": {
                "resolved_group": {
                    "instances": [
                        {"org": "OrgA", "repo": "x"},
                        {"org": "OrgB", "repo": "x"},
                    ],
                    "canonical_home": "OrgA/x",
                    "status": "resolved",
                },
                "pending_group": {
                    "instances": [
                        {"org": "OrgA", "repo": "y"},
                        {"org": "OrgB", "repo": "y"},
                    ],
                    "canonical_home": "TBD",
                    "status": "pending_consolidation",
                },
            }
        }
        dedup_file = tmp_path / "dedup.yaml"
        dedup_file.write_text(yaml.dump(dedup_yaml), encoding="utf-8")
        monkeypatch.setattr(mod, "DEDUP_FILE", dedup_file)

        mod.report(pending_only=True)
        out = capsys.readouterr().out
        assert "pending_group" in out
        # resolved group should be hidden when --pending flag is set
        assert "resolved_group" not in out
