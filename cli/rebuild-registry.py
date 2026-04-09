#!/usr/bin/env python3
"""Validate canonical registry entries for completeness."""

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
CANONICAL_REPOS_FILE = REGISTRY_DIR / "canonical-repos.yaml"



def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}



def validate_repo_entry(repo: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    common_required = {"name", "status"}
    legacy_required = {"org", "layer", "purpose"}
    registry_required = {"id", "url", "role", "description"}

    for field in common_required:
        if not repo.get(field):
            errors.append(f"missing field: {field}")

    if not all(repo.get(field) for field in legacy_required) and not all(
        repo.get(field) for field in registry_required
    ):
        errors.append(
            "missing registry metadata: expected either org/layer/purpose or id/url/role/description"
        )

    if repo.get("status") not in {"active", "archived", "deprecated", "unknown"}:
        errors.append(f"invalid status: {repo.get('status')!r}")
    return errors



def run(check_only: bool = False) -> int:
    data = _load_yaml(CANONICAL_REPOS_FILE)
    repos = data.get("repositories", [])
    if not repos:
        print(f"ERR: no repositories found in {CANONICAL_REPOS_FILE.relative_to(ROOT)}", file=sys.stderr)
        return 1

    errors: dict[str, list[str]] = {}
    for repo in repos:
        name = repo.get("name", "__unknown__")
        repo_errors = validate_repo_entry(repo)
        if repo_errors:
            errors[name] = repo_errors

    if not check_only:
        total = len(repos)
        print(f"Registry: {CANONICAL_REPOS_FILE.relative_to(ROOT)}")
        print(f"  Total repos:           {total}")
        print(f"  Validation errors:     {len(errors)}")
        print(f"\nRegistry completeness: {round((total - len(errors)) / total * 100, 1) if total else 0}% ({total - len(errors)}/{total} valid entries)")

    if errors:
        for name, repo_errors in errors.items():
            for error in repo_errors:
                print(f"[{name}] {error}")
        return 1
    return 0



def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    return run(check_only="--check-only" in argv)


if __name__ == "__main__":
    raise SystemExit(main())
