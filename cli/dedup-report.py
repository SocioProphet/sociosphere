#!/usr/bin/env python3
"""Display deduplication progress from registry/deduplication-map.yaml."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
DEDUP_FILE = REGISTRY_DIR / "deduplication-map.yaml"

_STATUS_LABEL = {
    "resolved": "✅ RESOLVED",
    "completed": "✅ RESOLVED",
    "merge_in_progress": "🔄 IN PROGRESS",
    "in_progress": "🔄 IN PROGRESS",
    "pending_consolidation": "⏳ PENDING",
    "pending": "⏳ PENDING",
    "pending_review": "❓ REVIEW NEEDED",
    "dismissed": "🚫 DISMISSED",
}



def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}



def report(pending_only: bool = False) -> int:
    data = _load_yaml(DEDUP_FILE)
    duplicates = data.get("duplicates", {})
    if not isinstance(duplicates, dict) or not duplicates:
        print("No duplicate groups found in deduplication-map.yaml")
        return 0

    groups = {
        name: entry
        for name, entry in duplicates.items()
        if isinstance(entry, dict)
        and (not pending_only or entry.get("status") != "resolved")
    }

    total = len(groups)
    resolved = sum(1 for entry in groups.values() if entry.get("status") in {"resolved", "completed"})
    in_progress = sum(1 for entry in groups.values() if entry.get("status") in {"merge_in_progress", "in_progress"})
    pending = total - resolved - in_progress

    print("=" * 60)
    print("  DEDUPLICATION REPORT")
    print("=" * 60)
    print(f"\n  Total groups:    {total}")
    print(f"  Resolved:        {resolved}")
    print(f"  In progress:     {in_progress}")
    print(f"  Pending/review:  {pending}")

    for name, entry in groups.items():
        label = _STATUS_LABEL.get(entry.get("status", ""), entry.get("status", "UNKNOWN"))
        print(f"\n[{name}] {label}")
        print(f"  Canonical: {entry.get('canonical_home', 'TBD')}")
        for instance in entry.get("instances", []):
            print(f"  - {instance.get('org', '?')}/{instance.get('repo', '?')}")
        if entry.get("owner_action"):
            print(f"  Action: {entry['owner_action']}")
        if entry.get("notes"):
            print(f"  Notes: {entry['notes']}")

    return 0



def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    return report(pending_only="--pending" in argv)


if __name__ == "__main__":
    raise SystemExit(main())
