#!/usr/bin/env python3
"""cli/dedup-report.py

Report on repository deduplication status and consolidation progress.

Usage:
    python cli/dedup-report.py [--registry-dir PATH] [--format text|json]
                               [--status pending|in_progress|completed|dismissed]
"""

from __future__ import annotations

import argparse
import json
"""
cli/dedup-report.py

Display deduplication progress and blockers from
registry/deduplication-map.yaml.

Usage:
    python cli/dedup-report.py
    python cli/dedup-report.py --pending    # show only unresolved duplicates
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))


_REGISTRY_DIR = Path(__file__).parent.parent / "registry"


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report on SocioProphet repository deduplication"
    )
    parser.add_argument("--registry-dir", default=None)
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
    )
    parser.add_argument(
        "--status",
        choices=["pending", "in_progress", "completed", "dismissed"],
        default=None,
        help="Filter by deduplication status",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry_dir = (
        Path(args.registry_dir) if args.registry_dir else _REGISTRY_DIR
    )
    raw = _load_yaml(registry_dir / "deduplication-map.yaml")

    duplicates: list[dict[str, Any]] = raw.get("duplicates", [])
    summary: dict[str, Any] = raw.get("consolidation_summary", {})
    policy: dict[str, Any] = raw.get("policy", {})

    # Filter
    if args.status:
        duplicates = [d for d in duplicates if d.get("status") == args.status]

    if args.format == "json":
        print(
            json.dumps(
                {
                    "duplicates": duplicates,
                    "consolidation_summary": summary,
                    "policy": policy,
                },
                indent=2,
            )
        )
        return 0

    # Text output
    print("=== Repository Deduplication Report ===\n")

    # Summary table
    print("── Summary ─────────────────────────────────────────")
    for key, value in summary.items():
        print(f"  {key:<32} {value}")

    # Policy
    print("\n── Policy ──────────────────────────────────────────")
    for key, value in policy.items():
        print(f"  {key:<32} {value}")

    # Duplicate entries
    status_icons = {
        "pending": "⏳",
        "in_progress": "🔄",
        "completed": "✅",
        "dismissed": "🚫",
    }

    print(f"\n── Duplicate Entries ({len(duplicates)}) ────────────────────────")
    for dup in duplicates:
        icon = status_icons.get(dup.get("status", ""), "?")
        print(
            f"\n  {icon} [{dup['id']}] {dup['source']} → {dup['canonical']}  "
            f"({dup['status']})"
        )
        print(f"     Reason: {dup['reason'].strip()[:120]}")
        if dup.get("migration_notes"):
            print(f"     Notes:  {dup['migration_notes'].strip()[:120]}")
        if dup.get("completed_at"):
            print(f"     Completed: {dup['completed_at']}")
        if dup.get("dismissed_at"):
            print(f"     Dismissed: {dup['dismissed_at']} by {dup.get('dismissed_by', '?')}")

    print("\n=== End of deduplication report ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
DEDUP_FILE = REGISTRY_DIR / "deduplication-map.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(raw) or {}
    return {}


_STATUS_LABEL: dict[str, str] = {
    "resolved": "✅ RESOLVED",
    "merge_in_progress": "🔄 IN PROGRESS",
    "pending_consolidation": "⏳ PENDING",
    "pending_review": "❓ REVIEW NEEDED",
}


def report(pending_only: bool = False) -> int:
    data = _load_yaml(DEDUP_FILE)
    duplicates = data.get("duplicates", {})

    if not duplicates:
        print("No duplicate groups found in deduplication-map.yaml")
        return 0

    total = len(duplicates)
    resolved = sum(1 for d in duplicates.values() if d.get("status") == "resolved")
    in_progress = sum(
        1 for d in duplicates.values() if d.get("status") == "merge_in_progress"
    )
    pending = total - resolved - in_progress

    print("=" * 60)
    print("  DEDUPLICATION REPORT")
    print("=" * 60)
    print(f"\n  Total groups:    {total}")
    print(f"  Resolved:        {resolved}")
    print(f"  In progress:     {in_progress}")
    print(f"  Pending:         {pending}")
    pct = round(resolved / total * 100, 1) if total else 0
    print(f"  Completion:      {pct}%")

    for group_name, group in duplicates.items():
        status = group.get("status", "unknown")
        if pending_only and status == "resolved":
            continue

        label = _STATUS_LABEL.get(status, f"[{status}]")
        print(f"\n── {group_name} {label}")

        instances = group.get("instances", [])
        for inst in instances:
            org = inst.get("org", "?")
            repo = inst.get("repo", "?")
            lang = inst.get("language", "?")
            notes = f"  ({inst.get('notes', '')})" if inst.get("notes") else ""
            print(f"   • {org}/{repo} [{lang}]{notes}")

        canonical = group.get("canonical_home", "TBD")
        print(f"   Canonical home: {canonical}")

        action = group.get("owner_action", "")
        if action:
            print(f"   Action needed:  {action}")

        notes = group.get("notes", "")
        if notes:
            print(f"   Notes:          {notes}")

    print("\n" + "=" * 60)
    return 0


def main(argv: list[str]) -> int:
    pending_only = "--pending" in argv
    return report(pending_only=pending_only)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
