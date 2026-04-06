"""Tests for automation/webhooks.py."""

import hashlib
import hmac
import json
import pytest

from automation.webhooks import create_app, validate_signature, event_queue


# ---------------------------------------------------------------------------
# Signature validation
# ---------------------------------------------------------------------------

class TestValidateSignature:
    def _make_sig(self, payload: bytes, secret: str) -> str:
        return "sha256=" + hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()

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


# ---------------------------------------------------------------------------
# Webhook handler
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    app = create_app(webhook_secret="test-secret")
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _sig_for(payload: bytes, secret: str = "test-secret") -> str:
    return "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()


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


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert "queue_depth" in data


class TestMetricsEndpoint:
    def test_metrics_keys(self, client):
        resp = client.get("/metrics")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "webhooks_received" in data
        assert "webhooks_valid" in data
        assert "queue_depth" in data


class TestWebhookEndpoint:
    def test_invalid_signature_returns_403(self, client):
        resp = client.post(
            "/webhook",
            data=b'{}',
            content_type="application/json",
            headers={
                "X-GitHub-Event": "push",
                "X-Hub-Signature-256": "sha256=bad",
            },
        )
        assert resp.status_code == 403

    def test_push_to_main_is_queued(self, client):
        payload = {
            "ref": "refs/heads/main",
            "repository": {"full_name": "owner/repo"},
            "commits": [],
        }
        resp = _post_push(client, payload)
        assert resp.status_code == 202
        data = resp.get_json()
        assert data["status"] == "queued"

    def test_push_to_non_main_is_ignored(self, client):
        payload = {
            "ref": "refs/heads/feature-branch",
            "repository": {"full_name": "owner/repo"},
            "commits": [],
        }
        resp = _post_push(client, payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ignored"

    def test_non_push_event_is_ignored(self, client):
        body = b'{"action": "opened"}'
        resp = client.post(
            "/webhook",
            data=body,
            content_type="application/json",
            headers={
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": _sig_for(body),
            },
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ignored"

    def test_no_secret_configured_accepts_all(self):
        """When no secret is configured, all requests are accepted."""
        app = create_app(webhook_secret="")
        app.config["TESTING"] = True
        with app.test_client() as c:
            payload = {
                "ref": "refs/heads/main",
                "repository": {"full_name": "owner/repo"},
                "commits": [],
            }
            body = json.dumps(payload).encode()
            resp = c.post(
                "/webhook",
                data=body,
                content_type="application/json",
                headers={"X-GitHub-Event": "push"},
            )
        assert resp.status_code == 202
