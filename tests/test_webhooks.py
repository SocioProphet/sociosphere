"""Unit tests for Flask and HTTP webhook handlers."""

from __future__ import annotations

import hashlib
import hmac
import json

import pytest

from automation.webhooks import create_app, validate_signature


class TestValidateSignature:
    def _make_sig(self, payload: bytes, secret: str) -> str:
        return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    def test_valid_signature(self):
        payload = b'{"key": "value"}'
        secret = "my-secret"
        sig = self._make_sig(payload, secret)
        assert validate_signature(payload, sig, secret) is True

    def test_invalid_signature(self):
        payload = b'{"key": "value"}'
        assert validate_signature(payload, "sha256=deadbeef", "my-secret") is False

    def test_missing_signature(self):
        assert validate_signature(b"data", None, "secret") is False

    def test_empty_signature(self):
        assert validate_signature(b"data", "", "secret") is False


@pytest.fixture
def client():
    app = create_app(webhook_secret="test-secret")
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client



def _sig_for(payload: bytes, secret: str = "test-secret") -> str:
    return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()



def _post_push(client, payload_dict: dict, secret: str = "test-secret"):
    body = json.dumps(payload_dict).encode()
    return client.post(
        "/webhook",
        data=body,
        content_type="application/json",
        headers={
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": _sig_for(body, secret),
        },
    )


class TestFlaskWebhookHandler:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert "queue_depth" in data

    def test_metrics_keys(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.get_json()
        assert "webhooks_received" in data
        assert "webhooks_valid" in data
        assert "queue_depth" in data

    def test_invalid_signature_returns_403(self, client):
        response = client.post(
            "/webhook",
            data=b"{}",
            content_type="application/json",
            headers={
                "X-GitHub-Event": "push",
                "X-Hub-Signature-256": "sha256=bad",
            },
        )
        assert response.status_code == 403

    def test_push_to_main_is_queued(self, client):
        payload = {
            "ref": "refs/heads/main",
            "repository": {"full_name": "owner/repo"},
            "commits": [],
        }
        response = _post_push(client, payload)
        assert response.status_code == 202
        assert response.get_json()["status"] == "queued"

    def test_push_to_non_main_is_ignored(self, client):
        payload = {
            "ref": "refs/heads/feature-branch",
            "repository": {"full_name": "owner/repo"},
            "commits": [],
        }
        response = _post_push(client, payload)
        assert response.status_code == 200
        assert response.get_json()["status"] == "ignored"

    def test_non_push_event_is_ignored(self, client):
        body = b'{"action": "opened"}'
        response = client.post(
            "/webhook",
            data=body,
            content_type="application/json",
            headers={
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": _sig_for(body),
            },
        )
        assert response.status_code == 200
        assert response.get_json()["status"] == "ignored"

    def test_no_secret_configured_accepts_all(self):
        app = create_app(webhook_secret="")
        app.config["TESTING"] = True
        with app.test_client() as test_client:
            payload = {
                "ref": "refs/heads/main",
                "repository": {"full_name": "owner/repo"},
                "commits": [],
            }
            body = json.dumps(payload).encode()
            response = test_client.post(
                "/webhook",
                data=body,
                content_type="application/json",
                headers={"X-GitHub-Event": "push"},
            )
        assert response.status_code == 202


class TestHttpWebhookHandler:
    def test_verify_signature_valid(self):
        from webhooks.github_handler import _verify_signature

        secret = "test-secret"
        payload = b'{"event": "push"}'
        sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
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

        payload = {"ref": "refs/heads/feature/xyz", "repository": {"name": "myrepo"}}
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

        payload = {"ref": "refs/heads/main", "repository": {"name": "sociosphere"}}
        result = github_handler.handle_push_event(payload)
        assert result["status"] == "ok"

    def test_handle_push_event_missing_repo_name(self):
        from webhooks.github_handler import handle_push_event

        result = handle_push_event({"ref": "refs/heads/main", "repository": {}})
        assert result["status"] == "ignored"
