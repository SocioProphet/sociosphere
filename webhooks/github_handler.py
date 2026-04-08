#!/usr/bin/env python3
"""
webhooks/github_handler.py

Minimal GitHub webhook event handler.

Receives GitHub push events, validates the HMAC signature, and triggers
the propagation engine when a push to the main branch is detected.

Usage (standalone HTTP server):
    python webhooks/github_handler.py [--port 8080] [--secret <shared-secret>]

Environment variables:
    WEBHOOK_SECRET   — shared secret for HMAC-SHA256 signature validation
    WEBHOOK_PORT     — port to listen on (default: 8080)

In production, run behind a reverse proxy (nginx / Caddy) with TLS.
"""
from __future__ import annotations

import hashlib
import hmac
import http.server
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import engines.propagation_engine as propagation_engine  # noqa: E402

DEFAULT_PORT = 8080
MAIN_REFS = {"refs/heads/main", "refs/heads/master"}


def _verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Validate the GitHub HMAC-SHA256 webhook signature."""
    if not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def handle_push_event(payload: dict) -> dict:
    """
    Process a GitHub push event.

    Returns a dict with 'status' and 'detail' keys.
    """
    ref = payload.get("ref", "")
    repo_info = payload.get("repository", {})
    repo_name = repo_info.get("name", "")

    if not repo_name:
        return {"status": "ignored", "detail": "missing repository name"}

    if ref not in MAIN_REFS:
        return {
            "status": "ignored",
            "detail": f"push to non-main ref '{ref}' — no propagation triggered",
        }

    print(f"Push event: {repo_name} → {ref}")
    rc = propagation_engine.propagate(repo_name, ref)
    if rc == 0:
        return {"status": "ok", "detail": f"propagation triggered for '{repo_name}'"}
    return {"status": "error", "detail": f"propagation failed for '{repo_name}' (rc={rc})"}


class _WebhookHandler(http.server.BaseHTTPRequestHandler):
    secret: str = ""

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/webhook":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        payload_bytes = self.rfile.read(content_length)

        # Validate signature if a secret is configured.
        if self.secret:
            sig = self.headers.get("X-Hub-Signature-256", "")
            if not _verify_signature(payload_bytes, sig, self.secret):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid signature"}')
                return

        event_type = self.headers.get("X-GitHub-Event", "")
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode())
            return

        if event_type == "push":
            result = handle_push_event(payload)
        else:
            result = {"status": "ignored", "detail": f"unsupported event '{event_type}'"}

        body = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:  # noqa: ANN001
        print(f"[webhook] {self.address_string()} — {fmt % args}")


def serve(port: int = DEFAULT_PORT, secret: str = "") -> None:
    """Start the webhook HTTP server."""
    _WebhookHandler.secret = secret

    with http.server.HTTPServer(("", port), _WebhookHandler) as httpd:
        print(f"Webhook server listening on port {port}")
        if secret:
            print("Signature validation: enabled")
        else:
            print("WARN: WEBHOOK_SECRET not set — signature validation disabled")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


def main(argv: list[str]) -> int:
    port = int(os.environ.get("WEBHOOK_PORT", DEFAULT_PORT))
    secret = os.environ.get("WEBHOOK_SECRET", "")

    # Parse CLI overrides.
    i = 1
    while i < len(argv):
        if argv[i] == "--port" and i + 1 < len(argv):
            port = int(argv[i + 1])
            i += 2
        elif argv[i] == "--secret" and i + 1 < len(argv):
            secret = argv[i + 1]
            i += 2
        else:
            i += 1

    serve(port=port, secret=secret)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
