#!/usr/bin/env python3
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
