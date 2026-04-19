#!/usr/bin/env python3
"""Minimal validator for EMVI proof-slice fixture files.

This intentionally avoids third-party dependencies so it can run in a bare
workspace checkout. It does not implement full JSON Schema validation; instead it
checks the required structural invariants for the current fixture examples.
"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTO = ROOT / "protocol" / "emvi-proof-slice" / "v0"

ACTIONSPEC_PATH = PROTO / "fixtures" / "actionspec.example.json"
EVENTS_PATH = PROTO / "fixtures" / "events.example.jsonl"

REQUIRED_ACTIONSPEC_KEYS = {
    "id",
    "intent",
    "action_class",
    "targets",
    "service_families",
    "placement",
    "preview_required",
    "confirmation_required",
    "rollback_expected",
    "policy_status",
    "provenance_sink",
}

REQUIRED_EVENT_KEYS = {
    "event_id",
    "event_type",
    "timestamp",
    "correlation_id",
    "actor",
    "target_ids",
    "service_family",
    "status",
    "placement",
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)



def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"could not parse JSON from {path}: {exc}")



def validate_actionspec() -> None:
    if not ACTIONSPEC_PATH.exists():
        fail(f"missing fixture: {ACTIONSPEC_PATH}")
    obj = load_json(ACTIONSPEC_PATH)
    if not isinstance(obj, dict):
        fail("ActionSpec fixture is not a JSON object")
    missing = REQUIRED_ACTIONSPEC_KEYS - set(obj.keys())
    if missing:
        fail(f"ActionSpec fixture missing keys: {sorted(missing)}")
    if not isinstance(obj["targets"], list) or not obj["targets"]:
        fail("ActionSpec targets must be a non-empty list")
    for idx, target in enumerate(obj["targets"]):
        if not isinstance(target, dict):
            fail(f"ActionSpec target #{idx} is not an object")
        if "id" not in target or "kind" not in target:
            fail(f"ActionSpec target #{idx} missing id/kind")
    if not isinstance(obj["service_families"], list) or not obj["service_families"]:
        fail("ActionSpec service_families must be a non-empty list")



def validate_events() -> None:
    if not EVENTS_PATH.exists():
        fail(f"missing fixture: {EVENTS_PATH}")
    lines = EVENTS_PATH.read_text(encoding="utf-8").splitlines()
    if not lines:
        fail("events fixture is empty")
    correlation_ids: set[str] = set()
    action_spec_ids: set[str] = set()
    for idx, line in enumerate(lines, start=1):
        try:
            obj = json.loads(line)
        except Exception as exc:
            fail(f"events fixture line {idx} is not valid JSON: {exc}")
        if not isinstance(obj, dict):
            fail(f"events fixture line {idx} is not a JSON object")
        missing = REQUIRED_EVENT_KEYS - set(obj.keys())
        if missing:
            fail(f"events fixture line {idx} missing keys: {sorted(missing)}")
        if not isinstance(obj["target_ids"], list):
            fail(f"events fixture line {idx} target_ids is not a list")
        correlation_ids.add(str(obj["correlation_id"]))
        if "action_spec_id" in obj:
            action_spec_ids.add(str(obj["action_spec_id"]))
    if len(correlation_ids) != 1:
        fail(f"events fixture should use one correlation_id, found: {sorted(correlation_ids)}")
    if "act_0001" not in action_spec_ids:
        fail("events fixture does not reference expected action_spec_id act_0001")



def main() -> None:
    validate_actionspec()
    validate_events()
    print("OK: EMVI proof-slice fixtures validated")


if __name__ == "__main__":
    main()
