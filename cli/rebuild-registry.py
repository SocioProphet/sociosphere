#!/usr/bin/env python3
"""cli/rebuild-registry.py

Rebuild and validate the full registry from the YAML source files.

Usage:
    python cli/rebuild-registry.py [--registry-dir PATH] [--verbose]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.ontology_engine import OntologyEngine
from engines.propagation_engine import PropagationEngine
from engines.devops_orchestrator import DevOpsOrchestrator
from engines.metrics_collector import MetricsCollector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild and validate the SocioProphet registry"
    )
    parser.add_argument(
        "--registry-dir",
        default=None,
        help="Path to the registry/ directory (default: auto-detected)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry_dir = args.registry_dir
    verbose = args.verbose

    print("=== SocioProphet Registry Rebuild ===\n")

    # ── 1. Load ontology ──────────────────────────────────────────────────────
    print("[1/4] Loading ontology engine …")
    engine = OntologyEngine(registry_dir)
    engine.load()
    repos = engine.all_repos()
    print(f"      Loaded {len(repos)} repositories")
    warnings = engine.validate_repos_against_ontology()
    if warnings:
        for w in warnings:
            print(f"      WARN: {w}")
    else:
        print("      All roles validated against ontology ✓")

    if verbose:
        print("      Role summary:", engine.extract_role_summary())
        print("      Language summary:", engine.extract_language_summary())

    # ── 2. Load dependency graph ──────────────────────────────────────────────
    print("\n[2/4] Loading propagation engine …")
    prop = PropagationEngine(registry_dir)
    prop.load()
    cycles = prop.detect_cycles()
    if cycles:
        print(f"      ERROR: {len(cycles)} dependency cycle(s) detected!")
        for cycle in cycles:
            print(f"        cycle: {' -> '.join(cycle)}")
        return 1
    print("      No dependency cycles detected ✓")
    if verbose:
        total_rules = len(prop.all_rules())
        print(f"      Propagation rules: {total_rules}")

    # ── 3. Load DevOps config ─────────────────────────────────────────────────
    print("\n[3/4] Loading DevOps orchestrator …")
    orch = DevOpsOrchestrator(registry_dir)
    summary = orch.summary()
    print(f"      Repos with devops config: {summary['total_repos_configured']}")
    print(f"      Deployable repos:         {summary['deployable']}")
    print(f"      FIPS-required repos:      {summary['fips_required']}")

    # ── 4. Collect metrics ────────────────────────────────────────────────────
    print("\n[4/4] Collecting metrics …")
    collector = MetricsCollector(registry_dir)
    report = collector.full_report()
    health = report["repo_health"]
    print(f"      Total repos:    {health['total']}")
    print(f"      By status:      {health['by_status']}")
    prop_cov = report["propagation_coverage"]
    print(
        f"      Propagation coverage: "
        f"{prop_cov['repos_with_rules']} / {prop_cov['active_repos']} "
        f"({prop_cov['coverage_pct']}%)"
    )
    devops_cov = report["devops_coverage"]
    print(
        f"      DevOps coverage: "
        f"{devops_cov['repos_with_devops_config']} / {devops_cov['active_repos']} "
        f"({devops_cov['coverage_pct']}%)"
    )

    print("\n=== Registry rebuild complete ✓ ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
