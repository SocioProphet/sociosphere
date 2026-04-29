#!/usr/bin/env python3
"""Generate a minimal EMVI proof-slice demo artifact from merged fixtures.

This is intentionally lightweight and stdlib-only. It does not execute the real
shell or services; it composes the already-governed fixture inputs into a single
artifact so downstream implementation has a stable shape to target.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "protocol" / "emvi-proof-slice" / "v0"
ACTIONSPEC_PATH = PROTO / "fixtures" / "actionspec.example.json"
EVENTS_PATH = PROTO / "fixtures" / "events.example.jsonl"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def build_demo_artifact() -> dict[str, Any]:
    actionspec = load_json(ACTIONSPEC_PATH)
    events = load_jsonl(EVENTS_PATH)
    return {
        "kind": "EMVIProofSliceDemoArtifact",
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "protocolRef": "protocol/emvi-proof-slice/v0",
        "actionSpec": actionspec,
        "events": events,
        "summary": {
            "eventCount": len(events),
            "targetIds": sorted({tid for row in events for tid in row.get("target_ids", [])}),
            "serviceFamilies": sorted({row.get("service_family", "") for row in events if row.get("service_family")}),
            "correlationIds": sorted({row.get("correlation_id", "") for row in events if row.get("correlation_id")}),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="-", help="Output path or '-' for stdout")
    args = parser.parse_args()

    artifact = build_demo_artifact()
    payload = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.output == "-":
        print(payload, end="")
    else:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        print(f"OK: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
