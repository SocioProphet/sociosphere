#!/usr/bin/env python3
"""sociosphere runner (v0.3)

Canonical workspace runner for manifest+lock orchestration.

Commands:
  - list:            show manifest repos + whether materialized
  - fetch:           materialize missing repos (git clone) and checkout lock rev
  - lock-verify:     verify role validity plus manifest/lock/drift state
  - lock-update:     update lock revisions from currently-materialized repos
  - inventory:       print repo / revision / license supply-chain report
  - protocol:test:   execute protocol compatibility surface (fixture stub until vectors land)
  - validate-policy: validate workspace policy refs and hashes
  - validate-trust:  validate trust repo presence and trust metadata
  - trust-report:    emit a structured trust report for the workspace
  - run:             run a task (build/test/lint/etc.) across selected repos and emit structured artifacts
  - check-manifest:  validate manifest role/path naming conventions
  - sbom:            emit a CycloneDX 1.4 JSON SBOM for the workspace

Stdlib-only: no Python deps beyond Python 3.11+.
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
OVERRIDES_PATH = ROOT / "manifest" / "overrides.toml"
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
TOPOLOGY_PREFIXES = {
    "adapter": ("adapters/",),
    "docs": ("components/", "docs/"),
    "execution-plane": ("components/",),
    "library": ("components/",),
    "ontology": ("components/",),
    "protocol": ("third_party/", "protocol/", "components/"),
    "replay": ("components/",),
    "security": ("components/",),
    "standards": ("components/", "standards/"),
    "topic-pack": ("components/",),
    "component": ("components/",),
}

SHA256_RE_PREFIX = "sha256:"
TRUST_REPO_NAMES = {"agentplane", "mcp-a2a-zero-trust", "mcp_a2a_zero_trust"}


@dataclass(frozen=True)
class Repo:
    name: str
    role: str
    local_path: Path | None
    url: str | None = None
    ref: str | None = None
    rev: str | None = None
    license_hint: str | None = None
    required_capabilities: list[str] | None = None
    trust_zone: str | None = None
    trust_profile_ref: str | None = None
    required_grants: list[str] | None = None


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return SHA256_RE_PREFIX + h.hexdigest()


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


def load_manifest_raw() -> dict[str, Any]:
    return tomllib.loads(MANIFEST_PATH.read_text("utf-8"))


def load_overrides_raw() -> dict[str, Any]:
    if not OVERRIDES_PATH.exists():
        return {}
    return tomllib.loads(OVERRIDES_PATH.read_text("utf-8"))


def merge_manifest_and_overrides(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Merge overrides onto base.

    - workspace.* keys are shallow-merged.
    - workspace.policy is shallow-merged.
    - repos are merged by name.

    overrides.toml is optional and should be gitignored.
    """
    if not overrides:
        return base

    merged: dict[str, Any] = {k: v for k, v in base.items()}

    merged_workspace = dict(base.get("workspace", {}))
    merged_workspace.update(overrides.get("workspace", {}))
    if "policy" in base.get("workspace", {}) or "policy" in overrides.get("workspace", {}):
        policy = dict(base.get("workspace", {}).get("policy", {}))
        policy.update(overrides.get("workspace", {}).get("policy", {}))
        merged_workspace["policy"] = policy
    if merged_workspace:
        merged["workspace"] = merged_workspace

    by_name: dict[str, dict[str, Any]] = {}
    for r in base.get("repos", []):
        by_name[r["name"]] = dict(r)
    for r in overrides.get("repos", []):
        name = r["name"]
        current = dict(by_name.get(name, {"name": name}))
        current.update(r)
        by_name[name] = current
    merged["repos"] = list(by_name.values())
    return merged


def load_workspace_and_repos() -> tuple[dict[str, Any], list[Repo]]:
    data = merge_manifest_and_overrides(load_manifest_raw(), load_overrides_raw())
    workspace = data.get("workspace", {})

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
                license_hint=r.get("license_hint"),
                required_capabilities=r.get("required_capabilities"),
                trust_zone=r.get("trust_zone"),
                trust_profile_ref=r.get("trust_profile_ref"),
                required_grants=r.get("required_grants"),
            )
        )
    return workspace, repos


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


def topology_errors(repos: Iterable[Repo]) -> list[str]:
    errs: list[str] = []
    for r in repos:
        if r.local_path is None:
            continue
        allowed = TOPOLOGY_PREFIXES.get(r.role)
        if not allowed:
            continue
        rel = r.local_path.relative_to(ROOT).as_posix()
        if not any(rel.startswith(prefix) for prefix in allowed):
            errs.append(
                f"{r.name}: role '{r.role}' path '{rel}' violates topology (allowed prefixes: {', '.join(allowed)})"
            )
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
        "workspace": {"name": "sociosphere", "version": "0.3"},
        "generatedAt": now_iso(),
        "manifestDigest": sha256_path(MANIFEST_PATH),
        "lockDigest": sha256_path(LOCK_PATH) if LOCK_PATH.exists() else "",
        "runnerVersion": "0.3",
        "repos": rows,
    }


def detect_duplicate_repo_names(repos: Iterable[Repo]) -> list[str]:
    seen: dict[str, int] = {}
    for r in repos:
        seen[r.name] = seen.get(r.name, 0) + 1
    return sorted([name for name, count in seen.items() if count > 1])


def detect_duplicate_repo_urls(repos: Iterable[Repo]) -> list[str]:
    seen: dict[str, list[str]] = {}
    for r in repos:
        if r.url:
            seen.setdefault(r.url, []).append(r.name)
    out: list[str] = []
    for url, names in seen.items():
        if len(names) > 1:
            out.append(f"{url} -> {', '.join(sorted(names))}")
    return sorted(out)


def validate_workspace_policy(workspace: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    policy = workspace.get("policy")
    if not policy:
        errors.append("missing [workspace.policy] block")
        return errors, warnings

    pack_ref = policy.get("policy_pack_ref")
    if not pack_ref:
        errors.append("workspace.policy.policy_pack_ref missing")
    else:
        pack_path = ROOT / pack_ref
        if not pack_path.exists():
            errors.append(f"policy pack ref missing: {pack_ref}")
        else:
            expect = policy.get("policy_pack_hash")
            actual = sha256_path(pack_path)
            if not expect:
                warnings.append("workspace.policy.policy_pack_hash missing")
            elif expect != actual:
                errors.append(f"policy pack hash mismatch: expected {expect}, got {actual}")

    trust_ref = policy.get("trust_profile_ref")
    if not trust_ref:
        errors.append("workspace.policy.trust_profile_ref missing")
    else:
        trust_path = ROOT / trust_ref
        if not trust_path.exists():
            errors.append(f"trust profile ref missing: {trust_ref}")

    if policy.get("ledger_mode") not in {"required", "best_effort", "off", None}:
        errors.append("workspace.policy.ledger_mode invalid")
    if not policy.get("default_quorum_rule"):
        warnings.append("workspace.policy.default_quorum_rule missing")
    return errors, warnings


def validate_trust_workspace(workspace: dict[str, Any], repos: list[Repo]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    policy_errors, policy_warnings = validate_workspace_policy(workspace)
    errors.extend(policy_errors)
    warnings.extend(policy_warnings)

    names = {r.name for r in repos}
    if "agentplane" not in names:
        errors.append("required trust repo missing: agentplane")
    if not (names & {"mcp-a2a-zero-trust", "mcp_a2a_zero_trust"}):
        errors.append("required trust repo missing: mcp-a2a-zero-trust")

    for r in repos:
        if r.trust_zone == "control" and not r.trust_profile_ref:
            errors.append(f"{r.name}: trust_zone=control requires trust_profile_ref")
        if r.trust_profile_ref:
            p = ROOT / r.trust_profile_ref
            if not p.exists():
                errors.append(f"{r.name}: trust profile ref missing: {r.trust_profile_ref}")

    duplicate_names = detect_duplicate_repo_names(repos)
    duplicate_urls = detect_duplicate_repo_urls(repos)
    if duplicate_names:
        warnings.append("duplicate repo names: " + ", ".join(duplicate_names))
    if duplicate_urls:
        warnings.extend([f"duplicate repo urls: {row}" for row in duplicate_urls])

    return errors, warnings


def trust_report_payload(workspace: dict[str, Any], repos: list[Repo]) -> dict[str, Any]:
    policy_errors, policy_warnings = validate_workspace_policy(workspace)
    trust_errors, trust_warnings = validate_trust_workspace(workspace, repos)

    trust_repos = [
        {
            "name": r.name,
            "role": r.role,
            "localPath": str(r.local_path.relative_to(ROOT)) if r.local_path else None,
            "url": r.url,
            "trustZone": r.trust_zone,
            "trustProfileRef": r.trust_profile_ref,
            "requiredGrants": r.required_grants or [],
            "requiredCapabilities": r.required_capabilities or [],
        }
        for r in repos
        if r.name in TRUST_REPO_NAMES or r.trust_zone == "control" or r.trust_profile_ref
    ]

    return {
        "kind": "TrustReportArtifact",
        "generatedAt": now_iso(),
        "workspace": {
            "name": workspace.get("name", "sociosphere"),
            "version": workspace.get("version", "0.3"),
            "policy": workspace.get("policy", {}),
        },
        "result": "pass" if not (policy_errors or trust_errors) else "fail",
        "policyErrors": policy_errors,
        "trustErrors": trust_errors,
        "warnings": sorted(set(policy_warnings + trust_warnings)),
        "trustRepos": trust_repos,
    }


def cmd_validate_policy(args: argparse.Namespace) -> int:
    workspace, _ = load_workspace_and_repos()
    errors, warnings = validate_workspace_policy(workspace)
    payload = {
        "kind": "PolicyValidationArtifact",
        "generatedAt": now_iso(),
        "result": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
    }
    if args.json_out:
        write_json(Path(args.json_out), payload)
        print(f"[validate-policy] wrote {args.json_out}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not errors else 2


def cmd_validate_trust(args: argparse.Namespace) -> int:
    workspace, repos = load_workspace_and_repos()
    errors, warnings = validate_trust_workspace(workspace, repos)
    payload = {
        "kind": "TrustValidationArtifact",
        "generatedAt": now_iso(),
        "result": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
    }
    if args.json_out:
        write_json(Path(args.json_out), payload)
        print(f"[validate-trust] wrote {args.json_out}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not errors else 2


def cmd_trust_report(args: argparse.Namespace) -> int:
    workspace, repos = load_workspace_and_repos()
    payload = trust_report_payload(workspace, repos)
    out = getattr(args, "output", "-")
    if out == "-":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        write_json(Path(out), payload)
        print(f"[trust-report] wrote {out}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    _, repos = load_workspace_and_repos()
    lock = load_lock()
    errs = role_errors(repos) + topology_errors(repos)

    for r in repos:
        head = repo_head_rev(r.local_path) if r.local_path and r.local_path.exists() else None
        lrev = locked_rev(lock, r.name)
        status = materialized_status(r.local_path)
        drift = ""
        if lrev and head and head != lrev:
            drift = " (LOCK DRIFT)"
        print(f"- {r.name:28s} role={r.role:14s} status={status:7s} head={head or '-'} lock={lrev or '-'}{drift}")

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
    _, repos = load_workspace_and_repos()
    lock = load_lock()
    errs = role_errors(repos) + topology_errors(repos)
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
    _, repos = load_workspace_and_repos()
    lock = load_lock()
    msgs = role_errors(repos) + topology_errors(repos)
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


def cmd_lock_update(args: argparse.Namespace) -> int:
    _, repos = load_workspace_and_repos()
    lock = load_lock()

    if not lock:
        lock = {"workspace": {"name": "sociosphere", "version": "0.1"}, "repos": []}

    lock_index: dict[str, Any] = {r["name"]: r for r in lock.get("repos", [])}
    now = now_iso()
    updated = 0

    for r in repos:
        if not r.url:
            continue

        if r.local_path is None or not r.local_path.exists() or not repo_is_git(r.local_path):
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
                "local_path": str(r.local_path.relative_to(ROOT)) if r.local_path else None,
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
    _, repos = load_workspace_and_repos()
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
                "local_path": str(r.local_path.relative_to(ROOT)) if r.local_path else None,
                "materialized": r.local_path.exists() if r.local_path else False,
            }
        )

    if getattr(args, "json", False):
        print(json.dumps(records, indent=2))
    else:
        header = f"{'name':36s} {'role':14s} {'rev':10s} {'license':8s} url"
        print(header)
        print("-" * len(header))
        for rec in records:
            rev_short = (rec["rev"] or "-")[:9]
            lic = rec["license_hint"] or "-"
            print(f"{rec['name']:36s} {rec['role']:14s} {rev_short:10s} {lic:8s} {rec['url'] or '(local)'}")
    return 0


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


def cmd_sbom(args: argparse.Namespace) -> int:
    import uuid

    _, repos = load_workspace_and_repos()
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
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
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


def cmd_run(args: argparse.Namespace) -> int:
    workspace, repos = load_workspace_and_repos()

    errs = role_errors(repos)
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2

    policy_errors, _ = validate_workspace_policy(workspace)
    trust_errors, _ = validate_trust_workspace(workspace, repos)
    if policy_errors or trust_errors:
        for e in policy_errors + trust_errors:
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


def cmd_check_manifest(args: argparse.Namespace) -> int:
    _, repos = load_workspace_and_repos()
    warnings: list[str] = []

    role_path_prefixes: dict[str, str] = {
        "component": "components/",
        "adapter": "adapters/",
        "third_party": "third_party/",
    }

    for r in repos:
        if r.local_path is None:
            continue
        expected = role_path_prefixes.get(r.role)
        if expected is None:
            continue
        rel = str(r.local_path.relative_to(ROOT)).replace("\\", "/")
        if not rel.startswith(expected):
            warnings.append(f"{r.name}: role={r.role} expects path prefix '{expected}', got '{rel}'")

    if warnings:
        for w in warnings:
            print(f"WARN {w}", file=sys.stderr)
        print(f"WARN: {len(warnings)} convention violation(s)", file=sys.stderr)
    else:
        print("OK: manifest role/path conventions validated")
    return 0


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

    sp = sub.add_parser("lock-update", help="Update lock revisions from materialized repos (run fetch first)")
    sp.set_defaults(fn=cmd_lock_update)

    sp = sub.add_parser("inventory", help="Print supply-chain inventory (name/role/rev/license/url)")
    sp.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    sp.add_argument("--output", default="-", metavar="FILE", help="Output file path (default: stdout)")
    sp.set_defaults(fn=cmd_inventory)

    sp = sub.add_parser("protocol:test", help="Run protocol fixture compatibility checks (stub surface)")
    sp.add_argument("--json-out", help="Optional path to write a ProtocolCompatibilityArtifact")
    sp.set_defaults(fn=cmd_protocol_test)

    sp = sub.add_parser("validate-policy", help="Validate workspace policy refs and hashes")
    sp.add_argument("--json-out", help="Optional path to write a PolicyValidationArtifact")
    sp.set_defaults(fn=cmd_validate_policy)

    sp = sub.add_parser("validate-trust", help="Validate trust repo presence and trust metadata")
    sp.add_argument("--json-out", help="Optional path to write a TrustValidationArtifact")
    sp.set_defaults(fn=cmd_validate_trust)

    sp = sub.add_parser("trust-report", help="Emit a structured trust report for the workspace")
    sp.add_argument("--output", default="-", metavar="FILE", help="Output file path (default: stdout)")
    sp.set_defaults(fn=cmd_trust_report)

    sp = sub.add_parser("run", help="Run a task across selected repos")
    sp.add_argument("task", help="Task name (build/test/lint/fmt/...)")
    sp.add_argument("--all", action="store_true", help="Run against all repos with role=component")
    sp.add_argument("--only", action="append", help="Run only on named repo (repeatable)")
    sp.add_argument("--role", choices=sorted(VALID_ROLES), help="Run on repos with this role")
    sp.add_argument("--artifact-dir", default="auto", help="Artifact output directory (default: auto under artifacts/workspace)")
    sp.set_defaults(fn=cmd_run)

    sp = sub.add_parser("check-manifest", help="Validate manifest role/path naming conventions")
    sp.set_defaults(fn=cmd_check_manifest)

    sp = sub.add_parser("sbom", help="Emit CycloneDX 1.4 JSON SBOM for the workspace")
    sp.add_argument("--output", default="-", metavar="FILE", help="Output file path (default: stdout)")
    sp.set_defaults(fn=cmd_sbom)

    args = p.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
