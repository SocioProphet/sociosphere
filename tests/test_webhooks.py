"""
tests/test_webhooks.py

Unit tests for the GitHub webhook handler.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TestWebhookHandler:
    def test_verify_signature_valid(self):
        from webhooks.github_handler import _verify_signature

        secret = "test-secret"
        payload = b'{"event": "push"}'
        sig = "sha256=" + hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        assert _verify_signature(payload, sig, secret) is True

    def test_verify_signature_invalid(self):
        from webhooks.github_handler import _verify_signature

        assert _verify_signature(b"payload", "sha256=bad", "secret") is False

    def test_verify_signature_missing_prefix(self):
        from webhooks.github_handler import _verify_signature

        assert _verify_signature(b"payload", "nosigprefix", "secret") is False

    def test_handle_push_event_non_main_ref(self, tmp_path, monkeypatch):
        from webhooks import github_handler
        from engines import propagation_engine

        log_file = tmp_path / "propagation-log.jsonl"
        monkeypatch.setattr(propagation_engine, "METRICS_DIR", tmp_path)
        monkeypatch.setattr(propagation_engine, "PROPAGATION_LOG", log_file)
        monkeypatch.setattr(propagation_engine, "DEP_GRAPH_FILE", tmp_path / "d.yaml")
        monkeypatch.setattr(propagation_engine, "PROP_RULES_FILE", tmp_path / "r.yaml")

        payload = {
            "ref": "refs/heads/feature/xyz",
            "repository": {"name": "myrepo"},
        }
        result = github_handler.handle_push_event(payload)
        assert result["status"] == "ignored"

    def test_handle_push_event_main_ref(self, tmp_path, monkeypatch):
        from webhooks import github_handler
        from engines import propagation_engine

        log_file = tmp_path / "propagation-log.jsonl"
        monkeypatch.setattr(propagation_engine, "METRICS_DIR", tmp_path)
        monkeypatch.setattr(propagation_engine, "PROPAGATION_LOG", log_file)
        monkeypatch.setattr(propagation_engine, "DEP_GRAPH_FILE", tmp_path / "d.yaml")
        monkeypatch.setattr(propagation_engine, "PROP_RULES_FILE", tmp_path / "r.yaml")

        payload = {
            "ref": "refs/heads/main",
            "repository": {"name": "sociosphere"},
        }
        result = github_handler.handle_push_event(payload)
        assert result["status"] == "ok"

    def test_handle_push_event_missing_repo_name(self):
        from webhooks.github_handler import handle_push_event

        result = handle_push_event({"ref": "refs/heads/main", "repository": {}})
        assert result["status"] == "ignored"
