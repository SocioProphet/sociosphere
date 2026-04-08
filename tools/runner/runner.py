#!/usr/bin/env python3
"""sociosphere runner (v0.2)

Canonical workspace runner for manifest+lock orchestration.

Commands:
  - list: show manifest repos + whether materialized
  - fetch: materialize missing repos (git clone) and checkout lock rev
  - lock-verify: verify role validity plus manifest/lock/drift state
  - protocol:test: execute protocol compatibility surface (fixture stub until vectors land)
  - run: run a task (build/test/lint/etc.) across selected repos and emit structured artifacts

Stdlib-only: no Python deps.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import tomllib  # py>=3.11
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # py<3.11 fallback

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "manifest" / "workspace.toml"
LOCK_PATH = ROOT / "manifest" / "workspace.lock.json"
ARTIFACTS_ROOT = ROOT / "artifacts" / "workspace"
VALID_ROLES = {
    "adapter",
    "component",
    "docs",
    "execution-plane",
    "library",
    "ontology",
    "protocol",
    "replay",
    "security",
    "standards",
    "tool",
    "topic-pack",
}


@dataclass(frozen=True)
class Repo:
    name: str
    role: str
    local_path: Path | None
    url: str | None = None
    ref: str | None = None
    rev: str | None = None


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _run(cmd: list[str], cwd: Path | None = None, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        capture_output=capture,
    )


def _capture(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=str(cwd) if cwd else None, text=True).strip()


def load_manifest() -> list[Repo]:
    data = tomllib.loads(MANIFEST_PATH.read_text("utf-8"))
    repos: list[Repo] = []
    for r in data.get("repos", []):
        lp_raw = r.get("local_path")
        lp = (ROOT / lp_raw) if lp_raw else None
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


def repo_is_git(p: Path | None) -> bool:
    if p is None:
        return False
    return (p / ".git").exists()


def repo_head_rev(p: Path | None) -> str | None:
    if not repo_is_git(p):
        return None
    try:
        return _capture(["git", "rev-parse", "HEAD"], cwd=p)
    except Exception:
        return None


def materialized_status(p: Path | None) -> str:
    if p is None:
        return "REMOTE"
    if not p.exists():
        return "MISSING"
    if repo_is_git(p):
        return "GIT"
    return "LOCAL"


def role_errors(repos: Iterable[Repo]) -> list[str]:
    errs: list[str] = []
    for r in repos:
        if r.role not in VALID_ROLES:
            errs.append(f"{r.name}: invalid role '{r.role}'")
    return errs


def artifact_run_dir() -> Path:
    run_dir = ARTIFACTS_ROOT / now_iso().replace(":", "-")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def inventory_payload(repos: list[Repo], lock: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for r in repos:
        head = repo_head_rev(r.local_path)
        lrev = locked_rev(lock, r.name)
        rows.append(
            {
                "name": r.name,
                "role": r.role,
                "localPath": str(r.local_path) if r.local_path else None,
                "url": r.url,
                "ref": r.ref,
                "rev": r.rev,
                "headRev": head,
                "status": materialized_status(r.local_path),
                "lockDrift": bool(lrev and head and lrev != head),
            }
        )
    return {
        "kind": "WorkspaceInventoryArtifact",
        "workspace": {"name": "sociosphere", "version": "0.2"},
        "generatedAt": now_iso(),
        "manifestDigest": sha256_path(MANIFEST_PATH),
        "lockDigest": sha256_path(LOCK_PATH) if LOCK_PATH.exists() else "",
        "runnerVersion": "0.2",
        "repos": rows,
    }


def cmd_list(args: argparse.Namespace) -> int:
    repos = load_manifest()
    lock = load_lock()
    errs = role_errors(repos)

    for r in repos:
        head = repo_head_rev(r.local_path) if r.local_path and r.local_path.exists() else None
        lrev = locked_rev(lock, r.name)
        status = materialized_status(r.local_path)
        drift = ""
        if lrev and head and head != lrev:
            drift = " (LOCK DRIFT)"
        print(f"- {r.name:28s} role={r.role:10s} status={status:7s} head={head or '-'} lock={lrev or '-'}{drift}")

    if args.json_out:
        payload = inventory_payload(repos, lock)
        if errs:
            payload["messages"] = errs
        write_json(Path(args.json_out), payload)
        print(f"[list] wrote {args.json_out}")

    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    repos = load_manifest()
    lock = load_lock()
    errs = role_errors(repos)
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2

    for r in repos:
        if r.local_path is None:
            if r.url:
                print(f"SKIP {r.name}: remote-only entry (no local_path)")
            else:
                print(f"SKIP {r.name}: no local_path and no url", file=sys.stderr)
            continue

        r.local_path.parent.mkdir(parents=True, exist_ok=True)

        if r.local_path.exists():
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


def detect_task_command(repo_path: Path, task: str) -> tuple[str, list[str]]:
    if (repo_path / "Makefile").exists():
        return ("make", ["make", task])
    if (repo_path / "justfile").exists():
        return ("just", ["just", task])
    if (repo_path / "Taskfile.yml").exists() or (repo_path / "Taskfile.yaml").exists():
        return ("task", ["task", task])
    sh = repo_path / "scripts" / f"{task}.sh"
    py = repo_path / "scripts" / f"{task}.py"
    if sh.exists():
        return ("script", ["bash", str(sh)])
    if py.exists():
        return ("script", [sys.executable, str(py)])
    return ("none", [])


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


def cmd_lock_verify(args: argparse.Namespace) -> int:
    repos = load_manifest()
    lock = load_lock()
    msgs = role_errors(repos)
    unresolved: list[str] = []
    drifted: list[str] = []

    for r in repos:
        lrev = locked_rev(lock, r.name)
        status = materialized_status(r.local_path)
        if status == "MISSING" and not (r.url or lrev or r.rev):
            unresolved.append(r.name)
        head = repo_head_rev(r.local_path) if status != "MISSING" else None
        if lrev and head and lrev != head:
            drifted.append(r.name)

    result = "pass" if not (msgs or unresolved or drifted) else "fail"
    payload = {
        "kind": "LockVerificationArtifact",
        "generatedAt": now_iso(),
        "result": result,
        "unresolvedRepos": unresolved,
        "driftedRepos": drifted,
        "messages": msgs,
    }
    if args.json_out:
        write_json(Path(args.json_out), payload)
        print(f"[lock-verify] wrote {args.json_out}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result == "pass" else 2


def cmd_protocol_test(args: argparse.Namespace) -> int:
    fixtures_dir = ROOT / "protocol" / "fixtures"
    msgs: list[str] = []
    result = "pass"
    if not fixtures_dir.exists():
        msgs.append("protocol fixtures directory missing; stub surface only")
        result = "warn"
    payload = {
        "kind": "ProtocolCompatibilityArtifact",
        "generatedAt": now_iso(),
        "fixtureSet": "protocol/fixtures",
        "target": "workspace",
        "result": result,
        "messages": msgs,
    }
    if args.json_out:
        write_json(Path(args.json_out), payload)
        print(f"[protocol:test] wrote {args.json_out}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    repos = load_manifest()
    errs = role_errors(repos)
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2

    targets = iter_targets(repos, args.only, args.role, args.all)
    if not targets:
        print("No targets selected. Use --all or --only <name> or --role <role>.", file=sys.stderr)
        return 2

    run_dir = artifact_run_dir() if args.artifact_dir == "auto" else Path(args.artifact_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    rc = 0
    for r in targets:
        started = now_iso()
        stdout_ref = None
        stderr_ref = None
        if r.local_path is None:
            print(f"REMOTE-ONLY {r.name}: no local_path to run '{args.task}'", file=sys.stderr)
            rc = 2
            payload = {
                "kind": "TaskRunArtifact",
                "generatedAt": now_iso(),
                "repo": {"name": r.name, "role": r.role},
                "task": args.task,
                "contractType": "none",
                "command": [],
                "startedAt": started,
                "finishedAt": now_iso(),
                "exitCode": 2,
                "stdoutRef": stdout_ref,
                "stderrRef": stderr_ref,
            }
            write_json(run_dir / f"task-run-{r.name}.json", payload)
            continue

        if not r.local_path.exists():
            print(f"MISSING {r.name}: {r.local_path} (run fetch first)", file=sys.stderr)
            rc = 2
            payload = {
                "kind": "TaskRunArtifact",
                "generatedAt": now_iso(),
                "repo": {"name": r.name, "role": r.role},
                "task": args.task,
                "contractType": "none",
                "command": [],
                "startedAt": started,
                "finishedAt": now_iso(),
                "exitCode": 2,
                "stdoutRef": stdout_ref,
                "stderrRef": stderr_ref,
            }
            write_json(run_dir / f"task-run-{r.name}.json", payload)
            continue

        contract_type, cmd = detect_task_command(r.local_path, args.task)
        if not cmd:
            print(f"NO TASK CONTRACT for {r.name}: can't run '{args.task}'", file=sys.stderr)
            rc = 2
            payload = {
                "kind": "TaskRunArtifact",
                "generatedAt": now_iso(),
                "repo": {"name": r.name, "role": r.role},
                "task": args.task,
                "contractType": contract_type,
                "command": cmd,
                "startedAt": started,
                "finishedAt": now_iso(),
                "exitCode": 2,
                "stdoutRef": stdout_ref,
                "stderrRef": stderr_ref,
            }
            write_json(run_dir / f"task-run-{r.name}.json", payload)
            continue

        print(f"\n== {r.name}: {args.task} ==")
        cp = _run(cmd, cwd=r.local_path, check=False, capture=True)
        if cp.stdout:
            print(cp.stdout, end="")
        if cp.stderr:
            print(cp.stderr, end="", file=sys.stderr)

        stdout_path = run_dir / f"{r.name}-{args.task}.stdout.log"
        stderr_path = run_dir / f"{r.name}-{args.task}.stderr.log"
        stdout_path.write_text(cp.stdout or "", encoding="utf-8")
        stderr_path.write_text(cp.stderr or "", encoding="utf-8")
        stdout_ref = str(stdout_path)
        stderr_ref = str(stderr_path)

        payload = {
            "kind": "TaskRunArtifact",
            "generatedAt": now_iso(),
            "repo": {"name": r.name, "role": r.role},
            "task": args.task,
            "contractType": contract_type,
            "command": cmd,
            "startedAt": started,
            "finishedAt": now_iso(),
            "exitCode": cp.returncode,
            "stdoutRef": stdout_ref,
            "stderrRef": stderr_ref,
        }
        write_json(run_dir / f"task-run-{r.name}.json", payload)
        if cp.returncode != 0:
            rc = cp.returncode or 1
            print(f"FAIL {r.name}: exit {cp.returncode}", file=sys.stderr)

    return rc


def main() -> int:
    p = argparse.ArgumentParser(prog="runner")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list", help="Show manifest repos and local status")
    sp.add_argument("--json-out", help="Optional path to write a WorkspaceInventoryArtifact")
    sp.set_defaults(fn=cmd_list)

    sp = sub.add_parser("fetch", help="Materialize missing repos (git clone) + checkout lock")
    sp.set_defaults(fn=cmd_fetch)

    sp = sub.add_parser("lock-verify", help="Verify manifest/lock consistency and role validity")
    sp.add_argument("--json-out", help="Optional path to write a LockVerificationArtifact")
    sp.set_defaults(fn=cmd_lock_verify)

    sp = sub.add_parser("protocol:test", help="Run protocol fixture compatibility checks (stub surface)")
    sp.add_argument("--json-out", help="Optional path to write a ProtocolCompatibilityArtifact")
    sp.set_defaults(fn=cmd_protocol_test)

    sp = sub.add_parser("run", help="Run a task across selected repos")
    sp.add_argument("task", help="Task name (build/test/lint/fmt/...) ")
    sp.add_argument("--all", action="store_true", help="Run against all repos with role=component")
    sp.add_argument("--only", action="append", help="Run only on named repo (repeatable)")
    sp.add_argument("--role", choices=sorted(VALID_ROLES), help="Run on repos with this role")
    sp.add_argument("--artifact-dir", default="auto", help="Artifact output directory (default: auto under artifacts/workspace)")
    sp.set_defaults(fn=cmd_run)

    args = p.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
