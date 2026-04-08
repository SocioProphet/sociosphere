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
"""
cli/rebuild-registry.py

Scan the canonical-repos.yaml, verify each entry is populated, and report
completeness.  In a connected environment this can be extended to call the
GitHub API and auto-discover new repos.

Usage:
    python cli/rebuild-registry.py [--check-only]
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "registry"
CANONICAL_REPOS_FILE = REGISTRY_DIR / "canonical-repos.yaml"

REQUIRED_FIELDS = ["name", "org", "layer", "purpose", "status"]


def _load_yaml(path: Path):
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(raw) or {}
    return {}


def validate_repo_entry(repo: dict) -> list[str]:
    """Return a list of validation errors for a repository entry."""
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if not repo.get(field):
            errors.append(f"missing field: {field}")
    if repo.get("status") not in ("active", "archived", "deprecated", "unknown"):
        errors.append(f"invalid status: {repo.get('status')!r}")
    return errors


def run(check_only: bool = False) -> int:
    data = _load_yaml(CANONICAL_REPOS_FILE)
    repos = data.get("repositories", [])

    if not repos:
        print(
            f"ERR: no repositories found in {CANONICAL_REPOS_FILE.relative_to(ROOT)}",
            file=sys.stderr,
        )
        return 1

    total = len(repos)
    errors: dict[str, list[str]] = {}

    for repo in repos:
        name = repo.get("name", "__unknown__")
        errs = validate_repo_entry(repo)
        if errs:
            errors[name] = errs

    has_missing_purpose = sum(1 for r in repos if not r.get("purpose"))
    has_missing_owners = sum(1 for r in repos if not r.get("owners"))
    has_missing_topics = sum(1 for r in repos if not r.get("topics"))

    print(f"Registry: {CANONICAL_REPOS_FILE.relative_to(ROOT)}")
    print(f"  Total repos:           {total}")
    print(f"  Validation errors:     {len(errors)}")
    print(f"  Missing purpose:       {has_missing_purpose}")
    print(f"  Missing owners:        {has_missing_owners}")
    print(f"  Missing topics:        {has_missing_topics}")

    if errors:
        print("\nValidation errors:")
        for name, errs in errors.items():
            for e in errs:
                print(f"  [{name}] {e}")

    pct = round((total - len(errors)) / total * 100, 1) if total else 0
    print(f"\nRegistry completeness: {pct}% ({total - len(errors)}/{total} valid entries)")

    if errors:
        return 1

    print("OK: registry rebuild complete — all entries valid")
    return 0


def main(argv: list[str]) -> int:
    check_only = "--check-only" in argv
    return run(check_only=check_only)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
