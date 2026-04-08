#!/usr/bin/env python3
"""sociosphere runner (v0.2)

Workspace orchestration runner for the manifest+lock multi-repo workspace.

Commands:
  list            Show manifest repos and local materialisation status
  fetch           Clone missing repos and checkout locked revisions
  run             Run a task (build/test/lint/…) across selected repos
  lock-verify     Verify materialised git repos match their locked revisions (P0)
  check-manifest  Validate manifest role/path naming conventions (P1)
  inventory       Emit a JSON inventory of all workspace repos (P2)
  sbom            Emit a CycloneDX 1.4 JSON SBOM for the workspace (P2)

Stdlib-only: no Python deps beyond Python 3.11+.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
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


@dataclass(frozen=True)
class Repo:
    name: str
    role: str
    local_path: Path
    url: str | None = None
    ref: str | None = None
    rev: str | None = None


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
        print(f"- {r.name:28s} role={r.role:10s} status={status:7s} head={head or '-'} lock={lrev or '-'}{drift}")
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


# ---------------------------------------------------------------------------
# Manifest convention enforcement
# ---------------------------------------------------------------------------

_ROLE_PATH_PREFIXES: dict[str, str] = {
    "component": "components/",
    "adapter": "adapters/",
    "third_party": "third_party/",
}


def _check_manifest_conventions(repos: list[Repo]) -> list[str]:
    """Return warning strings for role/path convention violations."""
    warnings: list[str] = []
    for r in repos:
        expected = _ROLE_PATH_PREFIXES.get(r.role)
        if expected is None:
            continue
        rel = str(r.local_path.relative_to(ROOT)).replace("\\", "/")
        if not rel.startswith(expected):
            warnings.append(
                f"{r.name}: role={r.role} expects path prefix '{expected}', got '{rel}'"
            )
    return warnings


def cmd_check_manifest(args: argparse.Namespace) -> int:
    """Validate manifest role/path naming conventions."""
    repos = load_manifest()
    warnings = _check_manifest_conventions(repos)
    if warnings:
        for w in warnings:
            print(f"WARN {w}", file=sys.stderr)
        print(
            f"WARN: {len(warnings)} convention violation(s) (not yet a hard failure; fix paths in manifest/workspace.toml)",
            file=sys.stderr,
        )
    else:
        print("OK: manifest role/path conventions validated")
    return 0  # warn-only until all repos are migrated to canonical paths


# ---------------------------------------------------------------------------
# Lock verification (P0)
# ---------------------------------------------------------------------------


def cmd_lock_verify(args: argparse.Namespace) -> int:
    """Verify that materialised git repos are at the revision recorded in the lock file."""
    repos = load_manifest()
    lock = load_lock()

    checked = 0
    drifts: list[str] = []

    for r in repos:
        lrev = locked_rev(lock, r.name)
        if not lrev:
            # Lock has no rev for this repo (lock-update not yet run); skip silently.
            continue
        if not r.local_path.exists():
            # Not materialised locally; nothing to check.
            continue

        head = repo_head_rev(r.local_path)
        if head is None:
            continue

        checked += 1
        if head == lrev:
            print(f"OK    {r.name}: @ {head[:12]}")
        else:
            msg = f"{r.name}: HEAD={head[:12]} lock={lrev[:12]}"
            drifts.append(msg)
            print(f"DRIFT {msg}", file=sys.stderr)

    if not checked:
        print("OK: no locked+materialised repos to verify (run 'runner fetch' after setting lock revs)")
        return 0

    if drifts:
        print(
            f"FAIL: {len(drifts)} lock drift(s) detected — run 'runner fetch' to restore locked revisions",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {checked} repo(s) match lock file")
    return 0


# ---------------------------------------------------------------------------
# Inventory report (P2)
# ---------------------------------------------------------------------------


def cmd_inventory(args: argparse.Namespace) -> int:
    """Emit a JSON inventory of all workspace repos (name, role, rev, materialisation status)."""
    import datetime

    repos = load_manifest()
    lock = load_lock()
    lock_map: dict[str, Any] = {r["name"]: r for r in lock.get("repos", [])}

    components: list[dict[str, Any]] = []
    for r in repos:
        lr = lock_map.get(r.name, {})
        entry: dict[str, Any] = {
            "name": r.name,
            "role": r.role,
            "local_path": str(r.local_path.relative_to(ROOT)).replace("\\", "/"),
            "url": r.url,
            "rev": lr.get("rev"),
            "tree_hash": lr.get("tree_hash"),
            "retrieved_at": lr.get("retrieved_at"),
            "materialized": r.local_path.exists(),
        }
        if r.local_path.exists():
            head = repo_head_rev(r.local_path)
            if head:
                entry["head"] = head
        components.append(entry)

    report: dict[str, Any] = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "workspace": {"name": "sociosphere", "version": "0.1"},
        "repos": components,
    }

    out: str = getattr(args, "output", "-")
    if out == "-":
        print(json.dumps(report, indent=2))
    else:
        Path(out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"OK: inventory written to {out}")
    return 0


# ---------------------------------------------------------------------------
# SBOM generation (P2)
# ---------------------------------------------------------------------------


def cmd_sbom(args: argparse.Namespace) -> int:
    """Emit a CycloneDX 1.4 JSON SBOM for the workspace."""
    import datetime
    import uuid

    repos = load_manifest()
    lock = load_lock()
    lock_map: dict[str, Any] = {r["name"]: r for r in lock.get("repos", [])}

    components: list[dict[str, Any]] = []
    for r in repos:
        lr = lock_map.get(r.name, {})
        rev = lr.get("rev")
        comp: dict[str, Any] = {
            "type": "library",
            "bom-ref": f"sociosphere:{r.name}",
            "name": r.name,
            "version": rev[:12] if rev else "unresolved",
            "description": f"Workspace component; role={r.role}",
            "externalReferences": [],
        }
        if r.url:
            comp["externalReferences"].append({"type": "vcs", "url": r.url})
        if rev:
            comp["hashes"] = [{"alg": "SHA-1", "content": rev}]
        components.append(comp)

    sbom: dict[str, Any] = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "component": {
                "type": "application",
                "name": "sociosphere",
                "version": "0.1",
                "bom-ref": "sociosphere:workspace",
            },
        },
        "components": components,
    }

    out: str = getattr(args, "output", "-")
    if out == "-":
        print(json.dumps(sbom, indent=2))
    else:
        Path(out).write_text(json.dumps(sbom, indent=2), encoding="utf-8")
        print(f"OK: SBOM written to {out}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="runner")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list", help="Show manifest repos and local status")
    sp.set_defaults(fn=cmd_list)

    sp = sub.add_parser("fetch", help="Materialize missing repos (git clone) + checkout lock")
    sp.set_defaults(fn=cmd_fetch)

    sp = sub.add_parser("run", help="Run a task across selected repos")
    sp.add_argument("task", help="Task name (build/test/lint/fmt/...)")
    sp.add_argument("--all", action="store_true", help="Run against all repos with role=component")
    sp.add_argument("--only", action="append", help="Run only on named repo (repeatable)")
    sp.add_argument("--role", choices=["component", "adapter", "third_party", "tool"], help="Run on repos with this role")
    sp.set_defaults(fn=cmd_run)

    sp = sub.add_parser("lock-verify", help="Verify materialised repos match lock file revisions (P0)")
    sp.set_defaults(fn=cmd_lock_verify)

    sp = sub.add_parser("check-manifest", help="Validate manifest role/path naming conventions (P1)")
    sp.set_defaults(fn=cmd_check_manifest)

    sp = sub.add_parser("inventory", help="Emit JSON inventory of workspace repos (P2)")
    sp.add_argument("--output", default="-", metavar="FILE", help="Output file path (default: stdout)")
    sp.set_defaults(fn=cmd_inventory)

    sp = sub.add_parser("sbom", help="Emit CycloneDX 1.4 JSON SBOM for the workspace (P2)")
    sp.add_argument("--output", default="-", metavar="FILE", help="Output file path (default: stdout)")
    sp.set_defaults(fn=cmd_sbom)

    args = p.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
