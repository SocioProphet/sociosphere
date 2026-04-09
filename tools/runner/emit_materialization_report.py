#!/usr/bin/env python3
"""Emit a materialization report from sociosphere manifest + lock.

Usage:
  python tools/runner/emit_materialization_report.py
"""

from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except Exception as e:  # pragma: no cover
    raise SystemExit("Python 3.11+ required (tomllib missing)")

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "manifest" / "workspace.toml"
LOCK_PATH = ROOT / "manifest" / "workspace.lock.json"


def load_manifest() -> dict:
    return tomllib.loads(MANIFEST_PATH.read_text("utf-8"))


def load_lock() -> dict:
    if not LOCK_PATH.exists():
        return {}
    return json.loads(LOCK_PATH.read_text("utf-8"))


def locked_rev(lock: dict, name: str):
    for r in lock.get("repos", []):
        if r.get("name") == name:
            return r.get("rev")
    return None


def classify_repo(repo: dict, lock: dict) -> dict:
    name = repo["name"]
    local_path = repo.get("local_path")
    url = repo.get("url")
    lrev = locked_rev(lock, name)
    status = "local_only"
    if url and lrev:
        status = "remote_locked"
    elif url and not lrev:
        status = "remote_unlocked"
    elif not url and lrev:
        status = "lock_without_remote"
    return {
        "name": name,
        "role": repo.get("role", "component"),
        "local_path": local_path,
        "url": url,
        "lock_rev": lrev,
        "status": status,
    }


def main() -> int:
    manifest = load_manifest()
    lock = load_lock()
    rows = [classify_repo(r, lock) for r in manifest.get("repos", [])]
    report = {
        "kind": "MaterializationReport",
        "workspace": manifest.get("workspace", {}).get("name"),
        "repos": rows,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
