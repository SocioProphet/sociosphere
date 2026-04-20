#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / "protocol" / "workspace-fabric" / "v0"
FIX = WF / "fixtures"

REQUEST = FIX / "mount-registration-request.example.json"
LEASE = FIX / "mount-registration-lease.example.json"
EVENT = FIX / "evidence-event.example.json"

REQ_SCHEMA = WF / "mount-registration-request.schema.json"
LEASE_SCHEMA = WF / "mount-registration-lease.schema.json"
EVENT_SCHEMA = WF / "evidence-event.schema.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_keys(obj: dict, keys: list[str], label: str) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        raise SystemExit(f"{label} missing keys: {missing}")


def main() -> int:
    for path in [REQUEST, LEASE, EVENT, REQ_SCHEMA, LEASE_SCHEMA, EVENT_SCHEMA]:
        if not path.exists():
            raise SystemExit(f"missing required file: {path}")

    req = load(REQUEST)
    lease = load(LEASE)
    event = load(EVENT)
    req_schema = load(REQ_SCHEMA)
    lease_schema = load(LEASE_SCHEMA)
    event_schema = load(EVENT_SCHEMA)

    require_keys(req, req_schema["required"], "request fixture")
    require_keys(lease, lease_schema["required"], "lease fixture")
    require_keys(event, event_schema["required"], "event fixture")

    require_keys(req["workspace"], ["cell", "id", "principal"], "request.workspace")
    require_keys(req["mount"], ["id", "backend", "authority_mode"], "request.mount")
    require_keys(lease["workspace"], ["cell", "id"], "lease.workspace")
    require_keys(lease["mount"], ["id", "backend", "authority_mode"], "lease.mount")
    require_keys(event, ["workspace_ref", "mount_ref", "dataset_ref", "correlation_id"], "event envelope")

    if req["workspace"]["id"] != lease["workspace"]["id"]:
        raise SystemExit("workspace id mismatch between request and lease")
    if req["mount"]["id"] != lease["mount"]["id"]:
        raise SystemExit("mount id mismatch between request and lease")
    if req["mount"]["authority_mode"] != lease["mount"]["authority_mode"]:
        raise SystemExit("authority mode mismatch between request and lease")
    if event["workspace_ref"] != req["workspace"]["id"]:
        raise SystemExit("event workspace_ref does not match request workspace id")
    if event["mount_ref"] != req["mount"]["id"]:
        raise SystemExit("event mount_ref does not match request mount id")

    dataset_ids = [d["id"] for d in req["datasets"]]
    if event["dataset_ref"] not in dataset_ids:
        raise SystemExit("event dataset_ref not found in request datasets")
    if lease["approved"]["datasets"][0] not in dataset_ids:
        raise SystemExit("lease approved dataset not found in request datasets")

    request_adapter_roles = {f"{a['kind']}:{a['role']}" for a in req["adapters"]}
    lease_adapter_roles = set(lease["approved"]["adapters"])
    if not lease_adapter_roles.issubset(request_adapter_roles):
        raise SystemExit("lease adapter approvals are not a subset of request adapters")

    print("workspace-fabric fixtures: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
