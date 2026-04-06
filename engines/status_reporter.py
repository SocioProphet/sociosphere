#!/usr/bin/env python3
"""status_reporter.py — StatusReporter for the SocioProphet workspace.

Generates a human/machine-readable status report of the full ecosystem:
  - Registry summary (repos by layer/role/priority/status)
  - Open PRs per repo
  - Compliance summary
  - Deduplication status
  - Critical path items

Reads: registry/*, status/ecosystem-status.yaml, telemetry/compliance-policy.yaml
Stdlib + PyYAML only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required (pip install pyyaml)", file=sys.stderr)
    raise

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO_ROOT / "registry"
STATUS_DIR = REPO_ROOT / "status"
TELEMETRY_DIR = REPO_ROOT / "telemetry"


def _load(path: Path) -> Any:
    return yaml.safe_load(path.read_text("utf-8"))


def _load_optional(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return yaml.safe_load(path.read_text("utf-8"))


class StatusReporter:
    """Aggregate status reporter for the SocioProphet ecosystem."""

    def __init__(self) -> None:
        self._repos = _load(REGISTRY_DIR / "canonical-repos.yaml").get("repos", [])
        self._dedup = _load(REGISTRY_DIR / "deduplication-map.yaml").get("entries", [])
        self._propagation_rules = _load(REGISTRY_DIR / "change-propagation-rules.yaml").get("rules", [])
        self._ecosystem_status = _load_optional(STATUS_DIR / "ecosystem-status.yaml", {})
        self._pr_register = _load_optional(STATUS_DIR / "pr-register.yaml", {})
        self._compliance_policy = _load_optional(TELEMETRY_DIR / "compliance-policy.yaml", {})

    def generate_report(self) -> dict:
        """Generate a full ecosystem status report."""
        now = datetime.now(timezone.utc).isoformat()

        # ── Registry summary ─────────────────────────────────────────────────
        total_repos = len(self._repos)
        by_layer: dict[str, list[str]] = {}
        by_priority: dict[str, list[str]] = {}
        by_status: dict[str, list[str]] = {}
        total_open_prs = 0
        repos_needing_prs: list[str] = []

        for r in self._repos:
            layer = r.get("layer", "unknown")
            priority = r.get("priority", "unknown")
            status = r.get("status", "unknown")
            name = r["name"]
            open_prs = r.get("open_prs", 0)

            by_layer.setdefault(layer, []).append(name)
            by_priority.setdefault(priority, []).append(name)
            by_status.setdefault(status, []).append(name)
            total_open_prs += open_prs

            # Flag P0/P1 active repos with no PRs as needing attention
            if open_prs == 0 and priority in ("P0", "P1") and status == "active" and not r.get("single_branch_exempt"):
                repos_needing_prs.append(name)

        # ── Deduplication summary ─────────────────────────────────────────────
        dedup_summary: dict[str, int] = {}
        for entry in self._dedup:
            s = entry.get("consolidation_status", "unknown")
            dedup_summary[s] = dedup_summary.get(s, 0) + 1

        # ── Critical path ─────────────────────────────────────────────────────
        critical_path = [
            {"repo": "prophet-platform-standards", "pr": "#1 (draft)", "reason": "ADR foundation — blocks all standards compliance"},
            {"repo": "sociosphere", "pr": "this branch", "reason": "Registry foundation — blocks automation and compliance tooling"},
            {"repo": "socioprophet-standards-storage", "pr": "#13 (draft)", "reason": "Shared schemas — blocks agentplane and TriTRPC slice work"},
            {"repo": "agentplane", "pr": "#12 (draft)", "reason": "Slice layout — blocks TriTRPC#20 local-hybrid slice"},
            {"repo": "TriTRPC", "pr": "#20 (draft)", "reason": "Transport slice — blocks receipt path integration"},
        ]

        # ── High-priority gaps ────────────────────────────────────────────────
        gaps = []
        for name in repos_needing_prs:
            gaps.append({"repo": name, "gap": "Active P0/P1 repo with no open PRs — needs architectural PR"})

        # Known specific gaps
        gaps += [
            {"repo": "agentplane", "gap": "Receipt builder (receipt path consumer) — no PR exists yet"},
            {"repo": "manifest/workspace.lock.json", "gap": "All fields are null — lock is not real, reproducible builds impossible"},
            {"repo": "gaia-world-model", "gap": "5 open issues, 0 PRs — critical data-plane component with no PR work"},
        ]

        return {
            "generated_at": now,
            "registry": {
                "total_repos": total_repos,
                "total_open_prs": total_open_prs,
                "by_layer": {k: len(v) for k, v in by_layer.items()},
                "by_priority": {k: len(v) for k, v in by_priority.items()},
                "by_status": {k: len(v) for k, v in by_status.items()},
            },
            "deduplication": dedup_summary,
            "critical_path": critical_path,
            "high_priority_gaps": gaps,
            "propagation_rules_count": len(self._propagation_rules),
        }

    def print_dashboard(self) -> None:
        """Print a human-readable status dashboard to stdout."""
        report = self.generate_report()
        reg = report["registry"]

        print("=" * 70)
        print("  SocioProphet Ecosystem Status Dashboard")
        print(f"  Generated: {report['generated_at']}")
        print("=" * 70)

        print(f"\n📦 REGISTRY  ({reg['total_repos']} repos, {reg['total_open_prs']} open PRs)\n")
        print("  By Layer:")
        for layer, count in sorted(reg["by_layer"].items()):
            print(f"    {layer:<22} {count}")
        print("\n  By Priority:")
        for pri in ["P0", "P1", "P2", "P3"]:
            count = reg["by_priority"].get(pri, 0)
            print(f"    {pri}  {count}")
        print("\n  By Status:")
        for status, count in sorted(reg["by_status"].items()):
            print(f"    {status:<15} {count}")

        print("\n🔗 DEDUPLICATION")
        for status, count in sorted(report["deduplication"].items()):
            print(f"    {status:<15} {count}")

        print("\n⛔ CRITICAL PATH (must merge in this order):")
        for i, item in enumerate(report["critical_path"], 1):
            print(f"  {i}. [{item['repo']}] {item['pr']}")
            print(f"     {item['reason']}")

        print("\n⚠️  HIGH-PRIORITY GAPS:")
        for item in report["high_priority_gaps"]:
            print(f"  • [{item['repo']}] {item['gap']}")

        print("\n" + "=" * 70)


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="StatusReporter CLI")
    p.add_argument("cmd", choices=["dashboard", "report"])
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args()

    reporter = StatusReporter()

    if args.cmd == "dashboard":
        reporter.print_dashboard()
    elif args.cmd == "report":
        report = reporter.generate_report()
        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            reporter.print_dashboard()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
