#!/usr/bin/env python3
"""Source exposure validator for Sociosphere.

The validator is intentionally stdlib-only. It is designed to catch
high-confidence publication blockers without turning natural-language docs into
false-positive noise.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SEVERITIES = ("block", "warn", "info")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def load_policy(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text("utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"policy not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"policy is not valid JSON: {path}: {exc}") from None

    if not isinstance(data, dict):
        raise SystemExit("policy root must be an object")
    if not data.get("schema_version"):
        raise SystemExit("policy.schema_version missing")
    for rule in data.get("content_rules", []):
        try:
            re.compile(rule["pattern"])
        except re.error as exc:
            raise SystemExit(f"invalid regex for rule {rule.get('id', '<unknown>')}: {exc}") from None
    return data


def git_tracked_files(root: Path) -> list[Path] | None:
    try:
        cp = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=str(root),
            check=True,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception:
        return None

    if not cp.stdout:
        return []
    files: list[Path] = []
    for raw in cp.stdout.split(b"\0"):
        if raw:
            files.append(root / raw.decode("utf-8", errors="replace"))
    return files


def walk_files(root: Path, ignored_dirs: set[str]) -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignored_dirs]
        base = Path(dirpath)
        for filename in filenames:
            out.append(base / filename)
    return out


def is_ignored(path: Path, root: Path, ignored_dirs: set[str]) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    return any(part in ignored_dirs for part in rel.parts)


def rel_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def path_findings(path: Path, root: Path, policy: dict[str, Any]) -> list[dict[str, Any]]:
    rel = rel_path(path, root)
    name = path.name
    suffixes = tuple(str(s).lower() for s in policy.get("blocked_path_suffixes", []))
    names = {str(n) for n in policy.get("blocked_path_names", [])}
    findings: list[dict[str, Any]] = []

    if name in names:
        findings.append(
            {
                "rule_id": "blocked-path-name",
                "severity": "block",
                "path": rel,
                "line": None,
                "message": f"blocked publication path name: {name}",
            }
        )

    lower = rel.lower()
    for suffix in suffixes:
        if lower.endswith(suffix):
            findings.append(
                {
                    "rule_id": "blocked-path-suffix",
                    "severity": "block",
                    "path": rel,
                    "line": None,
                    "message": f"blocked publication path suffix: {suffix}",
                }
            )
            break

    return findings


def content_findings(path: Path, root: Path, policy: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    max_bytes = int(policy.get("max_file_bytes", 1048576))
    try:
        stat = path.stat()
    except OSError:
        return [], True

    if stat.st_size > max_bytes:
        return [], True

    try:
        raw = path.read_bytes()
    except OSError:
        return [], True

    if b"\0" in raw:
        return [], True

    text = raw.decode("utf-8", errors="replace")
    rules = [
        {
            **rule,
            "_compiled": re.compile(rule["pattern"]),
        }
        for rule in policy.get("content_rules", [])
    ]

    findings: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for rule in rules:
            if rule["_compiled"].search(line):
                severity = rule.get("severity", "warn")
                if severity not in SEVERITIES:
                    severity = "warn"
                findings.append(
                    {
                        "rule_id": rule.get("id", "unnamed-rule"),
                        "severity": severity,
                        "path": rel_path(path, root),
                        "line": line_no,
                        "message": rule.get("description", "source exposure rule matched"),
                    }
                )
    return findings, False


def build_report(root: Path, policy_path: Path) -> dict[str, Any]:
    policy = load_policy(policy_path)
    ignored_dirs = set(policy.get("ignored_dirs", []))
    tracked = git_tracked_files(root)
    candidates = tracked if tracked is not None else walk_files(root, ignored_dirs)

    findings: list[dict[str, Any]] = []
    skipped = 0
    scanned = 0

    for path in candidates:
        if is_ignored(path, root, ignored_dirs):
            skipped += 1
            continue
        if not path.exists() or not path.is_file():
            skipped += 1
            continue

        findings.extend(path_findings(path, root, policy))
        content_matches, was_skipped = content_findings(path, root, policy)
        if was_skipped:
            skipped += 1
        else:
            scanned += 1
            findings.extend(content_matches)

    counts = {
        "files_scanned": scanned,
        "files_skipped": skipped,
        "block": sum(1 for f in findings if f["severity"] == "block"),
        "warn": sum(1 for f in findings if f["severity"] == "warn"),
        "info": sum(1 for f in findings if f["severity"] == "info"),
    }

    return {
        "schema_version": "sociosphere.source-exposure-report/v1",
        "generated_at": now_iso(),
        "root": str(root),
        "policy": {
            "path": str(policy_path),
            "schema_version": policy.get("schema_version"),
        },
        "result": "fail" if counts["block"] else "pass",
        "counts": counts,
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate source exposure publication safety.")
    parser.add_argument("--root", default=".", help="Repository/workspace root to scan.")
    parser.add_argument(
        "--policy",
        default="standards/source-exposure/policy.v0.json",
        help="Source exposure policy JSON.",
    )
    parser.add_argument(
        "--json-out",
        default="artifacts/source-exposure/source-exposure-report.json",
        help="Report output path. Use '-' for stdout only.",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    policy_path = (root / args.policy).resolve() if not Path(args.policy).is_absolute() else Path(args.policy)
    report = build_report(root, policy_path)

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_out == "-":
        print(rendered, end="")
    else:
        out = (root / args.json_out).resolve() if not Path(args.json_out).is_absolute() else Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, "utf-8")
        print(f"[source-exposure] wrote {out}")
        print(
            f"[source-exposure] result={report['result']} "
            f"block={report['counts']['block']} warn={report['counts']['warn']} "
            f"files_scanned={report['counts']['files_scanned']}"
        )

    return 0 if report["result"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
