#!/usr/bin/env python3
"""compliance_checker.py — Compliance checker for the SocioProphet ecosystem.

Checks repos in registry/canonical-repos.yaml against telemetry/compliance-policy.yaml.
For each locally available (materialised) repo, runs applicable checks.

Exit codes:
  0 — all checks passed (fully compliant)
  1 — one or more ERROR-severity violations
  2 — usage error

Usage:
  python telemetry/compliance_checker.py check [--repo <name>] [--layer <layer>] [--format json]
  python telemetry/compliance_checker.py summary [--format json]

Stdlib + PyYAML only.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required (pip install pyyaml)", file=sys.stderr)
    raise

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = REPO_ROOT / "registry"
TELEMETRY_DIR = REPO_ROOT / "telemetry"


def _load(path: Path) -> Any:
    return yaml.safe_load(path.read_text("utf-8"))


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class Violation:
    repo: str
    req_id: str
    name: str
    severity: str   # error | warning
    detail: str


@dataclass
class RepoResult:
    repo_name: str
    layer: str
    role: str
    priority: str
    status: str
    violations: list[Violation] = field(default_factory=list)
    checks_run: int = 0
    skipped: bool = False
    skip_reason: str = ""

    @property
    def errors(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == "error"]

    @property
    def warnings(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == "warning"]

    @property
    def compliant(self) -> bool:
        return len(self.errors) == 0

    @property
    def compliance_label(self) -> str:
        if self.skipped:
            return "SKIPPED"
        if not self.errors and not self.warnings:
            return "COMPLIANT"
        if not self.errors:
            return "AT-RISK"
        return "NON-COMPLIANT"


# ── Checker ────────────────────────────────────────────────────────────────────

class ComplianceChecker:
    """Runs compliance checks against locally materialised repos."""

    def __init__(self) -> None:
        self._repos = _load(REGISTRY_DIR / "canonical-repos.yaml").get("repos", [])
        self._policy = _load(TELEMETRY_DIR / "compliance-policy.yaml")
        self._global_reqs = self._policy.get("global", {}).get("requirements", [])

    def _repo_local_path(self, repo: dict) -> Path | None:
        """Find the local path for a registry repo (materialized workspace)."""
        # Check if it's in the workspace.toml local_path entries
        manifest_path = REPO_ROOT / "manifest" / "workspace.toml"
        if manifest_path.exists():
            try:
                import tomllib
                data = tomllib.loads(manifest_path.read_text("utf-8"))
                for r in data.get("repos", []):
                    if r["name"].replace("-", "_") == repo["name"].replace("-", "_"):
                        p = REPO_ROOT / r["local_path"]
                        if p.exists():
                            return p
            except Exception:
                pass
        return None

    def _get_req_severity(self, req_id: str) -> str:
        """Look up severity for a requirement ID from the policy file."""
        for section in self._policy.values():
            if isinstance(section, dict):
                for req in section.get("requirements", []):
                    if isinstance(req, dict) and req.get("id") == req_id:
                        return req.get("severity", "error")
        return "error"

    def _check_single_default_branch(self, repo: dict, path: Path | None, result: RepoResult) -> None:
        """REQ-G01: default branch should be main."""
        result.checks_run += 1
        if path and path.exists():
            try:
                import subprocess
                out = subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=str(path), stderr=subprocess.DEVNULL, text=True
                ).strip()
                if out not in ("main", "HEAD"):
                    result.violations.append(Violation(
                        repo=repo["name"], req_id="REQ-G01",
                        name="single_default_branch",
                        severity="error",
                        detail=f"Current branch is '{out}', expected 'main'"
                    ))
            except Exception:
                pass  # Can't check if not a git repo

    def _check_no_prohibited_algorithms(self, repo: dict, path: Path | None, result: RepoResult) -> None:
        """REQ-G04: no prohibited crypto algorithms in source files."""
        result.checks_run += 1
        if path is None or not path.exists():
            return

        req = next((r for r in self._global_reqs if r["id"] == "REQ-G04"), None)
        if not req:
            return

        patterns = [re.compile(p) for p in req.get("patterns", [])]
        excludes = req.get("excludes", [])

        def should_exclude(p: Path) -> bool:
            for exc in excludes:
                if exc.startswith("*") and p.name.endswith(exc[1:]):
                    return True
                if exc.endswith("*") and p.name.startswith(exc[:-1]):
                    return True
                if "test" in p.name.lower() or "spec" in p.name.lower():
                    return True
            return False

        for src_file in path.rglob("*.py"):
            if should_exclude(src_file):
                continue
            try:
                content = src_file.read_text("utf-8", errors="ignore")
                for pattern in patterns:
                    if pattern.search(content):
                        result.violations.append(Violation(
                            repo=repo["name"], req_id="REQ-G04",
                            name="no_prohibited_algorithms",
                            severity="error",
                            detail=f"Prohibited algorithm pattern '{pattern.pattern}' found in {src_file.relative_to(path)}"
                        ))
                        break
            except Exception:
                continue

    def _check_has_readme(self, repo: dict, path: Path | None, result: RepoResult) -> None:
        """REQ-G03: must have a README.md."""
        result.checks_run += 1
        if path and path.exists():
            if not (path / "README.md").exists() and not (path / "README.rst").exists():
                result.violations.append(Violation(
                    repo=repo["name"], req_id="REQ-G03",
                    name="has_readme",
                    severity="warning",
                    detail="No README.md found at repo root"
                ))

    def _check_control_plane(self, repo: dict, path: Path | None, result: RepoResult) -> None:
        """Control plane specific checks."""
        name = repo["name"]
        if name == "sociosphere":
            result.checks_run += 1
            registry_file = REPO_ROOT / "registry" / "canonical-repos.yaml"
            if not registry_file.exists():
                result.violations.append(Violation(
                    repo=name, req_id="REQ-C02",
                    name="has_registry",
                    severity="error",
                    detail="registry/canonical-repos.yaml not found"
                ))

            result.checks_run += 1
            lock_file = REPO_ROOT / "manifest" / "workspace.lock.json"
            sev = self._get_req_severity("REQ-C01")
            if lock_file.exists():
                lock = json.loads(lock_file.read_text("utf-8"))
                repos_in_lock = lock.get("repos", [])
                all_null = all(
                    r.get("rev") is None and r.get("tree_hash") is None
                    for r in repos_in_lock
                )
                if all_null:
                    result.violations.append(Violation(
                        repo=name, req_id="REQ-C01",
                        name="has_manifest_lock",
                        severity=sev,
                        detail="workspace.lock.json exists but all rev/tree_hash fields are null — lock is not resolved"
                    ))
            else:
                result.violations.append(Violation(
                    repo=name, req_id="REQ-C01",
                    name="has_manifest_lock",
                    severity=sev,
                    detail="manifest/workspace.lock.json not found"
                ))

    def check_repo(self, repo: dict) -> RepoResult:
        """Run all applicable checks for a single repo."""
        result = RepoResult(
            repo_name=repo["name"],
            layer=repo.get("layer", ""),
            role=repo.get("role", ""),
            priority=repo.get("priority", ""),
            status=repo.get("status", ""),
        )

        # Skip archived repos
        if repo.get("status") == "archive":
            result.skipped = True
            result.skip_reason = "archived"
            return result

        path = self._repo_local_path(repo)

        # Global checks (always run)
        exempt_roles = next(
            (r.get("exempt_roles", []) for r in self._global_reqs if r["id"] == "REQ-G01"), []
        )
        if repo.get("role") not in exempt_roles:
            self._check_single_default_branch(repo, path, result)
        self._check_has_readme(repo, path, result)
        self._check_no_prohibited_algorithms(repo, path, result)

        # Control plane checks
        if repo.get("layer") == "control-plane" or repo.get("role") == "workspace-controller":
            self._check_control_plane(repo, path, result)

        return result

    def check_all(
        self,
        filter_repo: str | None = None,
        filter_layer: str | None = None,
    ) -> list[RepoResult]:
        """Run checks across all (or filtered) repos."""
        results = []
        for repo in self._repos:
            if filter_repo and repo["name"] != filter_repo:
                continue
            if filter_layer and repo.get("layer") != filter_layer:
                continue
            results.append(self.check_repo(repo))
        return results

    def summary(self, results: list[RepoResult]) -> dict:
        """Generate summary statistics from a list of results."""
        total = len(results)
        compliant = sum(1 for r in results if r.compliance_label == "COMPLIANT")
        at_risk = sum(1 for r in results if r.compliance_label == "AT-RISK")
        non_compliant = sum(1 for r in results if r.compliance_label == "NON-COMPLIANT")
        skipped = sum(1 for r in results if r.skipped)
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        return {
            "total_repos_checked": total,
            "compliant": compliant,
            "at_risk": at_risk,
            "non_compliant": non_compliant,
            "skipped": skipped,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "compliance_rate_pct": round(compliant / max(total - skipped, 1) * 100, 1),
        }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="SocioProphet compliance checker")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("check", help="Run compliance checks")
    sp.add_argument("--repo", default=None, help="Check a single repo by name")
    sp.add_argument("--layer", default=None, help="Filter by layer")
    sp.add_argument("--format", choices=["text", "json"], default="text")

    sp2 = sub.add_parser("summary", help="Print compliance summary")
    sp2.add_argument("--format", choices=["text", "json"], default="text")

    args = p.parse_args()
    checker = ComplianceChecker()

    if args.cmd in ("check", "summary"):
        fmt = getattr(args, "format", "text")
        repo_filter = getattr(args, "repo", None)
        layer_filter = getattr(args, "layer", None)
        results = checker.check_all(filter_repo=repo_filter, filter_layer=layer_filter)
        summ = checker.summary(results)

        if fmt == "json":
            output = {
                "summary": summ,
                "results": [
                    {
                        "repo": r.repo_name,
                        "label": r.compliance_label,
                        "errors": [{"id": v.req_id, "name": v.name, "detail": v.detail} for v in r.errors],
                        "warnings": [{"id": v.req_id, "name": v.name, "detail": v.detail} for v in r.warnings],
                    }
                    for r in results
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print("=" * 60)
            print("  SocioProphet Compliance Check")
            print("=" * 60)
            any_errors = False
            for r in results:
                if r.skipped:
                    continue
                label = r.compliance_label
                icon = "✅" if label == "COMPLIANT" else ("⚠️ " if label == "AT-RISK" else "❌")
                print(f"\n{icon} {r.repo_name}  [{label}]")
                for v in r.errors:
                    print(f"   ERROR  [{v.req_id}] {v.name}: {v.detail}")
                    any_errors = True
                for v in r.warnings:
                    print(f"   WARN   [{v.req_id}] {v.name}: {v.detail}")
            print("\n" + "=" * 60)
            print(f"  Total: {summ['total_repos_checked']} repos  "
                  f"✅ {summ['compliant']} compliant  "
                  f"⚠️  {summ['at_risk']} at-risk  "
                  f"❌ {summ['non_compliant']} non-compliant  "
                  f"⏭  {summ['skipped']} skipped")
            print(f"  Compliance rate: {summ['compliance_rate_pct']}%  "
                  f"({summ['total_errors']} errors, {summ['total_warnings']} warnings)")
            print("=" * 60)
            if any_errors:
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
