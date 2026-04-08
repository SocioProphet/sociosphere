#!/usr/bin/env python3
"""sociosphere runner (v0.2)

Bootstrap runner for our manifest+lock workspace.

Commands:
  - list:         show manifest repos + whether materialized
  - fetch:        materialize missing repos (git clone) and checkout lock rev
  - run:          run a task (build/test/lint/etc.) across selected components
  - lock-verify:  verify lock is consistent with manifest and (if materialized)
                  that no repo has drifted from its pinned revision
  - lock-update:  update lock revisions from currently-materialized repos
  - inventory:    print repo / revision / license report

Stdlib-only: no Python deps.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import tomllib  # py>=3.11
except Exception as e:  # pragma: no cover
    print("ERROR: Python 3.11+ required (tomllib missing)", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "manifest" / "workspace.toml"
LOCK_PATH = ROOT / "manifest" / "workspace.lock.json"

VALID_ROLES = {"component", "adapter", "third_party", "governance", "docs", "tool"}


@dataclass(frozen=True)
class Repo:
    name: str
    role: str
    local_path: Path
    url: str | None = None
    ref: str | None = None
    rev: str | None = None
    license_hint: str | None = None


def _run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=check)


def _capture(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=str(cwd) if cwd else None, text=True).strip()


def load_manifest() -> list[Repo]:
    data = tomllib.loads(MANIFEST_PATH.read_text("utf-8"))
    repos: list[Repo] = []
    for r in data.get("repos", []):
        lp = ROOT / r["local_path"]
        repos.append(
            Repo(
                name=r["name"],
                role=r.get("role", "component"),
                local_path=lp,
                url=r.get("url"),
                ref=r.get("ref"),
                rev=r.get("rev"),
                license_hint=r.get("license_hint"),
            )
        )
    return repos


def load_lock() -> dict[str, Any]:
    if not LOCK_PATH.exists():
        return {}
    return json.loads(LOCK_PATH.read_text("utf-8"))


def locked_rev(lock: dict[str, Any], name: str) -> str | None:
    for r in lock.get("repos", []):
        if r.get("name") == name:
            return r.get("rev")
    return None


def repo_is_git(p: Path) -> bool:
    return (p / ".git").exists()


def repo_head_rev(p: Path) -> str | None:
    if not repo_is_git(p):
        return None
    try:
        return _capture(["git", "rev-parse", "HEAD"], cwd=p)
    except Exception:
        return None


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_list(args: argparse.Namespace) -> int:
    repos = load_manifest()
    lock = load_lock()

    for r in repos:
        exists = r.local_path.exists()
        head = repo_head_rev(r.local_path) if exists else None
        lrev = locked_rev(lock, r.name)
        status = "MISSING"
        if exists:
            status = "LOCAL"
            if repo_is_git(r.local_path):
                status = "GIT"
        drift = ""
        if lrev and head and head != lrev:
            drift = " (LOCK DRIFT)"
        print(f"- {r.name:36s} role={r.role:12s} status={status:7s} head={head or '-'} lock={lrev or '-'}{drift}")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    repos = load_manifest()
    lock = load_lock()

    for r in repos:
        r.local_path.parent.mkdir(parents=True, exist_ok=True)

        if r.local_path.exists():
            # already materialized
            continue

        if not r.url:
            print(f"SKIP {r.name}: no url and path missing ({r.local_path})", file=sys.stderr)
            continue

        print(f"CLONE {r.name} -> {r.local_path}")
        _run(["git", "clone", r.url, str(r.local_path)])

        lrev = locked_rev(lock, r.name) or r.rev
        if lrev:
            print(f"CHECKOUT {r.name} @ {lrev}")
            _run(["git", "checkout", lrev], cwd=r.local_path)

    return 0


def cmd_lock_verify(args: argparse.Namespace) -> int:
    """Verify the lock file is consistent with the manifest.

    Checks performed:
    1. Every manifest repo appears in the lock.
    2. Every repo with a URL has a non-null rev in the lock.
    3. No stale entries exist in the lock (present in lock, absent from manifest).
    4. For materialized git repos: HEAD matches the pinned lock rev.

    Returns 0 on success, 1 on any verification failure.
    """
    repos = load_manifest()
    lock = load_lock()

    if not lock:
        print("ERR: lock file missing or empty", file=sys.stderr)
        return 1

    lock_index: dict[str, Any] = {r["name"]: r for r in lock.get("repos", [])}
    manifest_names = {r.name for r in repos}
    rc = 0

    for r in repos:
        lr = lock_index.get(r.name)
        if lr is None:
            print(f"MISSING-FROM-LOCK {r.name}: not in workspace.lock.json", file=sys.stderr)
            rc = 1
            continue

        # Repos with a remote URL must be pinned
        if r.url and not lr.get("rev"):
            print(f"UNPINNED {r.name}: url={r.url} but lock.rev is null (run lock-update)", file=sys.stderr)
            rc = 1
            continue

        # Drift check: only for materialized git repos
        if lr.get("rev") and r.local_path.exists() and repo_is_git(r.local_path):
            head = repo_head_rev(r.local_path)
            if head and head != lr["rev"]:
                print(f"DRIFT {r.name}: HEAD={head} lock={lr['rev']}", file=sys.stderr)
                rc = 1
                continue

        print(f"OK {r.name}")

    # Stale-entry check
    for lr in lock.get("repos", []):
        if lr["name"] not in manifest_names:
            print(f"STALE {lr['name']}: in lock but not in manifest (remove or add to manifest)", file=sys.stderr)
            rc = 1

    if rc == 0:
        print("lock-verify: all checks passed")
    return rc


def cmd_lock_update(args: argparse.Namespace) -> int:
    """Update the lock file with HEAD revisions from materialized repos.

    For each manifest repo that has a URL:
    - If the repo is materialized as a git checkout, capture its HEAD and write to lock.
    - If not materialized, emit a warning (run fetch first).

    Run `runner fetch` before this command to ensure repos are materialized.
    """
    repos = load_manifest()
    lock = load_lock()

    if not lock:
        lock = {"workspace": {"name": "sociosphere", "version": "0.1"}, "repos": []}

    lock_index: dict[str, Any] = {r["name"]: r for r in lock.get("repos", [])}
    now = _now_utc()
    updated = 0

    for r in repos:
        if not r.url:
            continue  # local-only repos are not pinnable from remote

        if not r.local_path.exists() or not repo_is_git(r.local_path):
            print(f"SKIP {r.name}: not materialized (run fetch first)", file=sys.stderr)
            continue

        head = repo_head_rev(r.local_path)
        if not head:
            print(f"SKIP {r.name}: can't read HEAD", file=sys.stderr)
            continue

        lr = lock_index.get(r.name)
        if lr is None:
            entry: dict[str, Any] = {
                "name": r.name,
                "role": r.role,
                "url": r.url,
                "ref": r.ref,
                "rev": head,
                "local_path": str(r.local_path.relative_to(ROOT)),
                "tree_hash": None,
                "retrieved_at": now,
            }
            lock.setdefault("repos", []).append(entry)
            lock_index[r.name] = entry
        else:
            lr["rev"] = head
            lr["url"] = r.url
            lr["retrieved_at"] = now

        print(f"PINNED {r.name} @ {head}")
        updated += 1

    lock["generated_at"] = now
    LOCK_PATH.write_text(json.dumps(lock, indent=2) + "\n", "utf-8")
    print(f"lock-update: {updated} entries written to {LOCK_PATH}")
    return 0


def cmd_inventory(args: argparse.Namespace) -> int:
    """Print a supply-chain inventory: name / role / rev / license / url."""
    repos = load_manifest()
    lock = load_lock()

    records = []
    for r in repos:
        lrev = locked_rev(lock, r.name)
        records.append(
            {
                "name": r.name,
                "role": r.role,
                "rev": lrev,
                "license_hint": r.license_hint,
                "url": r.url,
                "local_path": str(r.local_path.relative_to(ROOT)),
                "materialized": r.local_path.exists(),
            }
        )

    if getattr(args, "json", False):
        print(json.dumps(records, indent=2))
    else:
        header = f"{'name':36s} {'role':12s} {'rev':10s} {'license':8s} url"
        print(header)
        print("-" * len(header))
        for rec in records:
            rev_short = (rec["rev"] or "-")[:9]
            lic = rec["license_hint"] or "-"
            print(f"{rec['name']:36s} {rec['role']:12s} {rev_short:10s} {lic:8s} {rec['url'] or '(local)'}")
    return 0


def detect_task_command(repo_path: Path, task: str) -> list[str] | None:
    """Return a command list for executing `task` inside `repo_path`."""

    if (repo_path / "Makefile").exists():
        return ["make", task]

    if (repo_path / "justfile").exists():
        return ["just", task]

    # Taskfile.yml (requires `task` binary)
    if (repo_path / "Taskfile.yml").exists() or (repo_path / "Taskfile.yaml").exists():
        return ["task", task]

    # scripts/ convention
    sh = repo_path / "scripts" / f"{task}.sh"
    py = repo_path / "scripts" / f"{task}.py"
    if sh.exists():
        return ["bash", str(sh)]
    if py.exists():
        return [sys.executable, str(py)]

    return None


def iter_targets(repos: Iterable[Repo], only: list[str] | None, role: str | None, all_components: bool) -> list[Repo]:
    out: list[Repo] = []

    if only:
        wanted = set(only)
        for r in repos:
            if r.name in wanted:
                out.append(r)
        return out

    if all_components:
        return [r for r in repos if r.role == "component"]

    if role:
        return [r for r in repos if r.role == role]

    return []


def cmd_run(args: argparse.Namespace) -> int:
    repos = load_manifest()
    targets = iter_targets(repos, args.only, args.role, args.all)

    if not targets:
        print("No targets selected. Use --all or --only <name> or --role <role>.", file=sys.stderr)
        return 2

    rc = 0
    for r in targets:
        if not r.local_path.exists():
            print(f"MISSING {r.name}: {r.local_path} (run fetch first)", file=sys.stderr)
            rc = 2
            continue

        cmd = detect_task_command(r.local_path, args.task)
        if not cmd:
            print(f"NO TASK CONTRACT for {r.name}: can't run '{args.task}'", file=sys.stderr)
            rc = 2
            continue

        print(f"\n== {r.name}: {args.task} ==")
        try:
            _run(cmd, cwd=r.local_path, check=True)
        except subprocess.CalledProcessError as e:
            print(f"FAIL {r.name}: exit {e.returncode}", file=sys.stderr)
            rc = e.returncode or 1

    return rc


def main() -> int:
    p = argparse.ArgumentParser(prog="runner")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list", help="Show manifest repos and local status")
    sp.set_defaults(fn=cmd_list)

    sp = sub.add_parser("fetch", help="Materialize missing repos (git clone) + checkout lock")
    sp.set_defaults(fn=cmd_fetch)

    sp = sub.add_parser("lock-verify", help="Verify lock is consistent with manifest; check for drift")
    sp.set_defaults(fn=cmd_lock_verify)

    sp = sub.add_parser("lock-update", help="Update lock revisions from materialized repos (run fetch first)")
    sp.set_defaults(fn=cmd_lock_update)

    sp = sub.add_parser("inventory", help="Print supply-chain inventory (name/role/rev/license/url)")
    sp.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    sp.set_defaults(fn=cmd_inventory)

    sp = sub.add_parser("run", help="Run a task across selected repos")
    sp.add_argument("task", help="Task name (build/test/lint/fmt/...) ")
    sp.add_argument("--all", action="store_true", help="Run against all repos with role=component")
    sp.add_argument("--only", action="append", help="Run only on named repo (repeatable)")
    sp.add_argument(
        "--role",
        choices=sorted(VALID_ROLES),
        help="Run on repos with this role",
    )
    sp.set_defaults(fn=cmd_run)

    args = p.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
