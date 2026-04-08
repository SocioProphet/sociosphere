#!/usr/bin/env python3
"""check_topology.py – enforce workspace dependency-direction rules.

Rules (from docs/TOPOLOGY.md):
1. Submodule paths must live under third_party/ only.
2. No manifest component or adapter may have a URL pointing back at sociosphere itself.
3. Manifest third_party entries must use exact revs (not floating on a branch) in the lock.

Exit 0 on success, 1 on any violation.
Stdlib-only: no Python deps.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GITMODULES = ROOT / ".gitmodules"
LOCK_PATH = ROOT / "manifest" / "workspace.lock.json"
MANIFEST_PATH = ROOT / "manifest" / "workspace.toml"

# The sociosphere repo itself; components/adapters must not point here.
SELF_REPO_NAMES = {"sociosphere"}


def parse_gitmodules(path: Path) -> list[dict]:
    """Parse .gitmodules into a list of {name, path, url} dicts."""
    if not path.exists():
        return []

    entries: list[dict] = []
    current: dict = {}
    for line in path.read_text("utf-8").splitlines():
        line = line.strip()
        m = re.match(r'^\[submodule "(.+)"\]$', line)
        if m:
            if current:
                entries.append(current)
            current = {"name": m.group(1)}
        elif "=" in line and current is not None:
            key, _, val = line.partition("=")
            current[key.strip()] = val.strip()
    if current:
        entries.append(current)
    return entries


def load_lock() -> dict:
    if not LOCK_PATH.exists():
        return {}
    return json.loads(LOCK_PATH.read_text("utf-8"))


def load_manifest_raw() -> list[dict]:
    try:
        import tomllib
    except ImportError:
        print("ERR: Python 3.11+ required (tomllib missing)", file=sys.stderr)
        sys.exit(2)
    data = tomllib.loads(MANIFEST_PATH.read_text("utf-8"))
    return data.get("repos", [])


def check_submodule_paths(modules: list[dict]) -> list[str]:
    """Rule 1: submodule paths must be under third_party/."""
    violations: list[str] = []
    for mod in modules:
        p = mod.get("path", "")
        if not p.startswith("third_party/"):
            violations.append(
                f"SUBMODULE-PATH {mod.get('name')}: path '{p}' must be under third_party/"
            )
    return violations


def check_no_self_dependency(repos: list[dict]) -> list[str]:
    """Rule 2: components and adapters must not point back at sociosphere."""
    violations: list[str] = []
    for r in repos:
        role = r.get("role", "component")
        url = r.get("url") or ""
        if role in ("component", "adapter"):
            for name in SELF_REPO_NAMES:
                if name in url.lower():
                    violations.append(
                        f"SELF-DEP {r['name']} ({role}): url '{url}' points back at sociosphere"
                    )
    return violations


def check_third_party_pinned(repos: list[dict], lock: dict) -> list[str]:
    """Rule 3: third_party entries must be pinned to exact revs in the lock."""
    lock_index = {lr["name"]: lr for lr in lock.get("repos", [])}
    violations: list[str] = []
    for r in repos:
        if r.get("role") != "third_party":
            continue
        if not r.get("url"):
            continue  # local-only, not verifiable
        lr = lock_index.get(r["name"])
        if lr is None:
            violations.append(f"UNTRACKED-THIRD-PARTY {r['name']}: not in lock file")
            continue
        if not lr.get("rev"):
            violations.append(
                f"UNPINNED-THIRD-PARTY {r['name']}: third_party entry has no rev in lock"
            )
    return violations


def main() -> int:
    modules = parse_gitmodules(GITMODULES)
    repos = load_manifest_raw()
    lock = load_lock()

    all_violations: list[str] = []
    all_violations.extend(check_submodule_paths(modules))
    all_violations.extend(check_no_self_dependency(repos))
    all_violations.extend(check_third_party_pinned(repos, lock))

    if all_violations:
        for v in all_violations:
            print(f"FAIL: {v}", file=sys.stderr)
        return 1

    print(f"topology-check: OK ({len(modules)} submodule(s), {len(repos)} manifest repo(s) checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
