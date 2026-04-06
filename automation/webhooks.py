"""
Flask webhook handler for GitHub events.

Listens on port 5000, validates HMAC-SHA256 signatures, queues push
events for asynchronous processing, and exposes /health and /metrics
endpoints.
"""

import hashlib
import hmac
import json
import logging
import os
import queue
import threading
import time
from datetime import datetime, timezone
from typing import Optional

from flask import Flask, Response, jsonify, request

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Thread-safe event queue shared across the application
# ---------------------------------------------------------------------------
event_queue: queue.Queue = queue.Queue()

# ---------------------------------------------------------------------------
# Simple in-process metrics store
# ---------------------------------------------------------------------------
_metrics: dict = {
    "webhooks_received": 0,
    "webhooks_valid": 0,
    "webhooks_invalid_sig": 0,
    "webhooks_queued": 0,
    "webhooks_ignored": 0,
    "uptime_start": datetime.now(timezone.utc).isoformat(),
}
_metrics_lock = threading.Lock()


def _inc(key: str, delta: int = 1) -> None:
    with _metrics_lock:
        _metrics[key] = _metrics.get(key, 0) + delta


# ---------------------------------------------------------------------------
# Signature validation
# ---------------------------------------------------------------------------

def validate_signature(
    payload: bytes,
    header_sig: Optional[str],
    secret: str,
) -> bool:
    """Return True if *header_sig* matches the HMAC-SHA256 of *payload*."""
    if not header_sig:
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, header_sig)


# ---------------------------------------------------------------------------
# Flask application factory
# ---------------------------------------------------------------------------

def create_app(
    webhook_secret: Optional[str] = None,
    rate_limiter=None,
) -> Flask:
    """Create and configure the Flask webhook application.

    Parameters
    ----------
    webhook_secret:
        GitHub webhook secret used to validate HMAC-SHA256 signatures.
        Falls back to the ``GITHUB_WEBHOOK_SECRET`` environment variable.
    rate_limiter:
        Optional :class:`~automation.rate_limiter.RateLimiter` instance
        used to record inbound event processing costs.
    """
    app = Flask(__name__)
    secret = webhook_secret or os.environ.get("GITHUB_WEBHOOK_SECRET", "")

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify(
            {
                "status": "ok",
                "queue_depth": event_queue.qsize(),
                "uptime_start": _metrics["uptime_start"],
            }
        )

    @app.route("/metrics", methods=["GET"])
    def metrics():
        with _metrics_lock:
            snapshot = dict(_metrics)
        snapshot["queue_depth"] = event_queue.qsize()
        if rate_limiter is not None:
            snapshot["rate_limiter"] = rate_limiter.get_metrics()
        return jsonify(snapshot)

    @app.route("/webhook", methods=["POST"])
    def webhook():
        _inc("webhooks_received")

        # Validate signature when a secret is configured
        if secret:
            sig = request.headers.get("X-Hub-Signature-256")
            if not validate_signature(request.data, sig, secret):
                _inc("webhooks_invalid_sig")
                logger.warning("Webhook signature validation failed")
                return jsonify({"error": "Invalid signature"}), 403

        _inc("webhooks_valid")

        event_type = request.headers.get("X-GitHub-Event", "unknown")
        try:
            payload = request.get_json(force=True) or {}
        except Exception:
            payload = {}

        # Only queue push events targeting the main branch
        if event_type == "push":
            ref = payload.get("ref", "")
            if ref in ("refs/heads/main", "refs/heads/master"):
                entry = {
                    "event": event_type,
                    "ref": ref,
                    "repo": (payload.get("repository") or {}).get("full_name", ""),
                    "payload": payload,
                    "received_at": datetime.now(timezone.utc).isoformat(),
                }
                event_queue.put(entry)
                _inc("webhooks_queued")
                logger.info("Queued push event for %s", entry["repo"])
                return jsonify({"status": "queued"}), 202
            else:
                _inc("webhooks_ignored")
                return jsonify({"status": "ignored", "reason": "not main branch"}), 200

        _inc("webhooks_ignored")
        return jsonify({"status": "ignored", "reason": f"event={event_type}"}), 200

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    port = int(os.environ.get("WEBHOOK_PORT", "5000"))
    logger.info("Starting webhook handler on port %d", port)
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
