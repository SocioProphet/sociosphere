#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "protocol" / "agentic-workbench" / "v1"

SCHEMAS = [
    "workflow.schema.v0.1.json",
    "workflow_run.schema.v0.1.json",
    "step.schema.v0.1.json",
    "artifact_ref.schema.v0.1.json",
    "execution_envelope.schema.v0.1.json",
    "execution_record.schema.v0.1.json",
    "approval_request.schema.v0.1.json",
    "trust_profile.schema.v0.1.json",
    "policy_pack.schema.v0.1.json",
]

def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    items = []
    for name in SCHEMAS:
        path = BASE / name
        doc = json.loads(path.read_text("utf-8"))
        items.append({
            "$id": doc["$id"],
            "path": f"protocol/agentic-workbench/v1/{name}",
            "sha256": sha256_file(path),
            "title": doc["title"],
        })
    out = {"count": len(items), "items": items, "version": 1}
    (BASE / "index.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
