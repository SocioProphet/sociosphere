#!/usr/bin/env python3
"""cli/measure-success.py

Measure and report the health and success metrics of the registry layer.

Usage:
    python cli/measure-success.py [--registry-dir PATH] [--format text|json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.metrics_collector import MetricsCollector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure SocioProphet registry health and success metrics"
    )
    parser.add_argument("--registry-dir", default=None)
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    collector = MetricsCollector(args.registry_dir)
    report = collector.full_report()

    if args.format == "json":
        print(json.dumps(report, indent=2))
        return 0

    # Text output
    print("=== SocioProphet Registry Success Metrics ===\n")
    print(
        f"Registry version: {report['registry_version']}  "
        f"| Organization: {report['organization']}"
    )

    print("\n── Repository Health ───────────────────────────────")
    health = report["repo_health"]
    print(f"  Total repos: {health['total']}")
    for status, count in health["by_status"].items():
        bar = "█" * count
        print(f"  {status:<12} {count:>3}  {bar}")

    print("\n── Role Distribution ───────────────────────────────")
    for role, count in report["role_distribution"].items():
        bar = "█" * count
        print(f"  {role:<22} {count:>3}  {bar}")

    print("\n── Language Distribution ───────────────────────────")
    for lang, count in report["language_distribution"].items():
        bar = "█" * count
        print(f"  {lang:<22} {count:>3}  {bar}")

    print("\n── Dependency Graph ────────────────────────────────")
    dep = report["dependency_stats"]
    print(f"  Total edges:                  {dep['total_edges']}")
    print(f"  Repos with dependencies:      {dep['repos_with_dependencies']}")
    print(f"  Repos that are dependencies:  {dep['repos_that_are_dependencies']}")
    print(f"  Isolated repos:               {dep['isolated_repos']}")
    print(f"  Edge types: {dep['by_type']}")

    print("\n── Propagation Coverage ────────────────────────────")
    prop = report["propagation_coverage"]
    print(
        f"  {prop['repos_with_rules']} / {prop['active_repos']} "
        f"active repos covered  ({prop['coverage_pct']}%)"
    )

    print("\n── DevOps Coverage ─────────────────────────────────")
    devops = report["devops_coverage"]
    print(
        f"  {devops['repos_with_devops_config']} / {devops['active_repos']} "
        f"active repos covered  ({devops['coverage_pct']}%)"
    )
    print(f"  Deployable repos:  {devops['deployable']}")
    print(f"  FIPS-required:     {devops['fips_required']}")

    print("\n── Deduplication Progress ──────────────────────────")
    dedup = report["deduplication_progress"]
    if dedup:
        for key, value in dedup.items():
            print(f"  {key:<30} {value}")
    else:
        print("  No deduplication data available")

    print("\n=== End of report ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
