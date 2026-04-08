#!/usr/bin/env python3
"""
fips-compliance-checker.py
==========================
Automated FIPS 140-2/140-3 compliance validation tool for the
SocioProphet/sociosphere workspace controller.

Checks:
  1. algo-scan       — Scan source code for disallowed cryptographic algorithms
  2. tls-version     — Validate TLS configuration (1.3+ minimum)
  3. audit-worm      — Check audit trail for WORM storage configuration
  4. hash-chain      — Verify audit log hash chain integrity
  5. nist-controls   — Spot-check NIST SP 800-53 control evidence files

Usage:
  python tools/validator/fips-compliance-checker.py [OPTIONS]

Options:
  --source-dir PATH   Root directory to scan for source files (default: .)
  --audit-log PATH    Path to audit log JSON Lines file to verify hash chain
  --evidence-dir PATH Directory containing NIST 800-53 evidence files
  --report PATH       Write JSON compliance report to this file (default: stdout)
  --fail-fast         Exit immediately on first failure
  --no-color          Disable ANSI color output

Exit codes:
  0   All checks passed
  1   One or more checks failed

Standards:
  FIPS 140-2/140-3   https://csrc.nist.gov/projects/cryptographic-module-validation-program/
  NIST SP 800-53     https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
  NIST SP 800-88     https://csrc.nist.gov/publications/detail/sp/800-88
  RFC 8446 (TLS 1.3) https://tools.ietf.org/html/rfc8446
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Algorithms explicitly disallowed by NIST SP 800-131A Rev. 2 and FIPS policy.
# Each entry is (pattern, description, standard_reference).
DISALLOWED_ALGO_PATTERNS: list[tuple[str, str, str]] = [
    (r"\bmd5\b", "MD5", "SP 800-131A Rev. 2 §9"),
    (r"\bsha[-_]?1\b", "SHA-1", "SP 800-131A Rev. 2 §9"),
    (r"\bsha1\b", "SHA-1", "SP 800-131A Rev. 2 §9"),
    (r"\bdes\b(?![-_]?3)", "DES", "SP 800-131A Rev. 2 §8"),
    (r"\b3des\b", "3DES/TDEA", "SP 800-131A Rev. 2 §8"),
    (r"\btdea\b", "TDEA/3DES", "SP 800-131A Rev. 2 §8"),
    (r"\btriple[-_]?des\b", "3DES", "SP 800-131A Rev. 2 §8"),
    (r"\brc4\b", "RC4", "SP 800-131A Rev. 2"),
    (r"\baes[-_.]?ecb\b", "AES-ECB", "FIPS 197 Note — ECB is non-authenticating"),
    (r"mode\s*[=:]\s*[\"']?ecb[\"']?", "AES-ECB (mode config)", "FIPS 197 Note"),
    (r"\barcfour\b", "RC4 (arcfour alias)", "SP 800-131A Rev. 2"),
]

# Files to skip during source scanning (build artifacts, lock files, etc.)
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "dist", "build", ".cache", ".tox",
}
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2",
    ".ttf", ".eot", ".pdf", ".zip", ".tar", ".gz", ".lock",
}

# Documentation files and the checker script itself legitimately enumerate
# disallowed algorithms in policy/educational context; skip them for
# source-code algorithm and TLS scans.
ALGO_SCAN_SKIP_EXTENSIONS = SKIP_EXTENSIONS | {".md", ".rst", ".txt", ".adoc"}
# Also skip this checker script itself (it holds the disallowed patterns as strings).
_SELF_PATH = Path(__file__).resolve()

# TLS configuration patterns to check (disallowed patterns).
DISALLOWED_TLS_PATTERNS: list[tuple[str, str]] = [
    (r"tls[-_\s]?1[\._]?[012]", "TLS version < 1.3 configured"),
    (r"ssl[-_\s]?[23]", "SSL 2/3 configured (deprecated)"),
    (r"sslv[23]", "SSLv2/SSLv3 configured"),
    (r"min[-_]version\s*[=:]\s*[\"']?tls1_[012][\"']?", "TLS min version < 1.3"),
    (r"TLSv1\.[012]", "TLS version < 1.3"),
    (r"PROTOCOL_TLS(?!v1_3|V1_3)", "Non-TLS-1.3 protocol hint"),
]

# Required NIST 800-53 control evidence file patterns.
NIST_CONTROL_EVIDENCE: dict[str, list[str]] = {
    "AC-2": ["glossary-fips", "GLOSSARY-FIPS"],
    "AC-3": ["zero-trust-govt-bindings", "FIPS-COMPLIANCE-GUIDE"],
    "IA-2": ["zero-trust-govt-bindings", "tritrpc-fips-spec"],
    "IA-5": ["FIPS-COMPLIANCE-GUIDE", "tritrpc-fips-spec"],
    "AU-2": ["FIPS-COMPLIANCE-GUIDE", "zero-trust-govt-bindings"],
    "AU-12": ["zero-trust-govt-bindings", "tritrpc-fips-spec"],
    "SC-7": ["zero-trust-govt-bindings", "tritrpc-fips-spec"],
    "SC-8": ["FIPS-COMPLIANCE-GUIDE", "tritrpc-fips-spec"],
    "SC-12": ["FIPS-COMPLIANCE-GUIDE", "zero-trust-govt-bindings"],
    "SI-7": ["tritrpc-fips-spec", "FIPS-COMPLIANCE-GUIDE"],
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """A single compliance finding (pass, fail, or warning)."""
    check_id: str
    status: str  # "pass" | "fail" | "warn"
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    detail: Optional[str] = None
    standard_ref: Optional[str] = None


@dataclass
class CheckResult:
    """Aggregated result for a single check."""
    check_id: str
    description: str
    status: str  # "pass" | "fail" | "warn" | "skip"
    findings: List[Finding] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------------------

_USE_COLOR = True


def _c(code: str, text: str) -> str:
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t: str) -> str:
    return _c("32", t)


def red(t: str) -> str:
    return _c("31", t)


def yellow(t: str) -> str:
    return _c("33", t)


def bold(t: str) -> str:
    return _c("1", t)


# ---------------------------------------------------------------------------
# Check 1: Algorithm scan
# ---------------------------------------------------------------------------

def check_algo_scan(source_dir: Path) -> CheckResult:
    """Scan source files for disallowed cryptographic algorithms."""
    result = CheckResult(
        check_id="algo-scan",
        description="Scan source code for disallowed cryptographic algorithms (MD5, SHA-1, DES, 3DES, RC4, ECB mode)",
        status="pass",
    )

    compiled = [
        (re.compile(pattern, re.IGNORECASE), desc, ref)
        for pattern, desc, ref in DISALLOWED_ALGO_PATTERNS
    ]

    for file_path in _walk_source_files(source_dir, skip_extensions=ALGO_SCAN_SKIP_EXTENSIONS):
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            for regex, algo_name, std_ref in compiled:
                if regex.search(line):
                    finding = Finding(
                        check_id="algo-scan",
                        status="fail",
                        message=f"Disallowed algorithm detected: {algo_name}",
                        file=str(file_path),
                        line=lineno,
                        detail=line.strip(),
                        standard_ref=std_ref,
                    )
                    result.findings.append(finding)
                    result.status = "fail"

    if result.status == "pass":
        result.evidence.append("No disallowed algorithm references found in source tree.")

    return result


def _walk_source_files(root: Path, skip_extensions: Optional[set] = None):
    """Yield source file paths, skipping build artifacts and binary files.

    Parameters
    ----------
    root:
        Directory to walk.
    skip_extensions:
        Set of lowercase file extensions to skip.  Defaults to
        ``SKIP_EXTENSIONS``.  Pass ``ALGO_SCAN_SKIP_EXTENSIONS`` to also
        exclude documentation files (.md, .rst, etc.) from algo/TLS scans.
    """
    if skip_extensions is None:
        skip_extensions = SKIP_EXTENSIONS
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune directories in-place to prevent descending into them.
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
        ]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix.lower() in skip_extensions:
                continue
            # Skip the checker script itself — it holds disallowed patterns
            # as string literals for detection purposes, not as usage.
            if fpath.resolve() == _SELF_PATH:
                continue
            yield fpath


# ---------------------------------------------------------------------------
# Check 2: TLS version validation
# ---------------------------------------------------------------------------

def check_tls_version(source_dir: Path) -> CheckResult:
    """Validate that no TLS version below 1.3 is configured."""
    result = CheckResult(
        check_id="tls-version",
        description="Validate TLS configuration (minimum TLS 1.3 per RFC 8446 and NIST SP 800-52 Rev. 2)",
        status="pass",
    )

    compiled = [
        (re.compile(pattern, re.IGNORECASE), desc)
        for pattern, desc in DISALLOWED_TLS_PATTERNS
    ]

    # Also look for explicit TLS 1.3 configurations as evidence.
    tls13_pattern = re.compile(r"tls[-_\s]?1[\._]?3|TLSv1_3|TLS1_3", re.IGNORECASE)
    tls13_found = False

    for file_path in _walk_source_files(source_dir, skip_extensions=ALGO_SCAN_SKIP_EXTENSIONS):
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if tls13_pattern.search(text):
            tls13_found = True
            result.evidence.append(f"TLS 1.3 configuration found in: {file_path}")

        for lineno, line in enumerate(text.splitlines(), start=1):
            for regex, desc in compiled:
                if regex.search(line):
                    finding = Finding(
                        check_id="tls-version",
                        status="fail",
                        message=desc,
                        file=str(file_path),
                        line=lineno,
                        detail=line.strip(),
                        standard_ref="RFC 8446, NIST SP 800-52 Rev. 2",
                    )
                    result.findings.append(finding)
                    result.status = "fail"

    if not tls13_found and result.status == "pass":
        result.status = "warn"
        result.findings.append(Finding(
            check_id="tls-version",
            status="warn",
            message="No explicit TLS 1.3 configuration found; verify TLS version is enforced externally.",
            standard_ref="RFC 8446",
        ))

    return result


# ---------------------------------------------------------------------------
# Check 3: Audit WORM storage
# ---------------------------------------------------------------------------

def check_audit_worm(source_dir: Path) -> CheckResult:
    """Check for WORM-compliant audit storage configuration."""
    result = CheckResult(
        check_id="audit-worm",
        description="Check audit trail for WORM storage configuration (NIST SP 800-88)",
        status="pass",
    )

    worm_patterns = [
        re.compile(r"\bworm\b", re.IGNORECASE),
        re.compile(r"object.?lock", re.IGNORECASE),
        re.compile(r"immutable.?blob", re.IGNORECASE),
        re.compile(r"append.?only", re.IGNORECASE),
        re.compile(r"write.?once", re.IGNORECASE),
        re.compile(r"immutableStorage", re.IGNORECASE),
        re.compile(r"wormCompliant", re.IGNORECASE),
    ]

    found_worm = False
    for file_path in _walk_source_files(source_dir):
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for pattern in worm_patterns:
            if pattern.search(text):
                found_worm = True
                result.evidence.append(f"WORM/immutable storage reference found in: {file_path}")
                break

    if not found_worm:
        result.status = "fail"
        result.findings.append(Finding(
            check_id="audit-worm",
            status="fail",
            message="No WORM-compliant audit storage configuration found. "
                    "Audit logs must use WORM storage (e.g., S3 Object Lock, Azure Immutable Blob).",
            standard_ref="NIST SP 800-88 Rev. 1",
        ))

    return result


# ---------------------------------------------------------------------------
# Check 4: Hash chain verification
# ---------------------------------------------------------------------------

def check_hash_chain(audit_log_path: Optional[Path]) -> CheckResult:
    """Verify the cryptographic hash chain of an audit log file."""
    result = CheckResult(
        check_id="hash-chain",
        description="Verify audit log hash chain integrity (NIST SP 800-88, AU-12)",
        status="pass",
    )

    if audit_log_path is None:
        result.status = "skip"
        result.evidence.append("No audit log path provided; skipping hash chain check.")
        return result

    if not audit_log_path.exists():
        result.status = "fail"
        result.findings.append(Finding(
            check_id="hash-chain",
            status="fail",
            message=f"Audit log file not found: {audit_log_path}",
            standard_ref="NIST SP 800-88 Rev. 1",
        ))
        return result

    records: list[dict] = []
    try:
        with audit_log_path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    result.findings.append(Finding(
                        check_id="hash-chain",
                        status="fail",
                        message=f"Invalid JSON on line {lineno}: {exc}",
                        file=str(audit_log_path),
                        line=lineno,
                    ))
                    result.status = "fail"
    except OSError as exc:
        result.status = "fail"
        result.findings.append(Finding(
            check_id="hash-chain",
            status="fail",
            message=f"Cannot read audit log: {exc}",
        ))
        return result

    if not records:
        result.status = "warn"
        result.findings.append(Finding(
            check_id="hash-chain",
            status="warn",
            message="Audit log is empty; no records to verify.",
        ))
        return result

    prev_hash: Optional[str] = None
    for idx, record in enumerate(records):
        record_id = record.get("event_id", f"record[{idx}]")

        # Verify record_hash field is present.
        stored_hash = record.get("record_hash")
        if not stored_hash:
            result.findings.append(Finding(
                check_id="hash-chain",
                status="fail",
                message=f"Record {record_id} missing 'record_hash' field.",
                file=str(audit_log_path),
                line=idx + 1,
            ))
            result.status = "fail"
            prev_hash = None
            continue

        # Recompute record hash (excluding the record_hash field itself).
        record_copy = {k: v for k, v in record.items() if k != "record_hash"}
        computed_hash = hashlib.sha256(
            json.dumps(record_copy, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        if computed_hash != stored_hash:
            result.findings.append(Finding(
                check_id="hash-chain",
                status="fail",
                message=f"Record {record_id} hash mismatch: stored={stored_hash}, computed={computed_hash}",
                file=str(audit_log_path),
                line=idx + 1,
                standard_ref="NIST SP 800-88 Rev. 1",
            ))
            result.status = "fail"

        # Verify previous_hash linkage.
        if idx > 0 and prev_hash is not None:
            record_prev_hash = record.get("previous_hash")
            if record_prev_hash != prev_hash:
                result.findings.append(Finding(
                    check_id="hash-chain",
                    status="fail",
                    message=(
                        f"Record {record_id} previous_hash mismatch: "
                        f"stored={record_prev_hash}, expected={prev_hash}"
                    ),
                    file=str(audit_log_path),
                    line=idx + 1,
                    standard_ref="NIST SP 800-88 Rev. 1",
                ))
                result.status = "fail"

        prev_hash = stored_hash

    if result.status == "pass":
        result.evidence.append(f"Hash chain verified across {len(records)} audit records.")

    return result


# ---------------------------------------------------------------------------
# Check 5: NIST 800-53 control evidence
# ---------------------------------------------------------------------------

def check_nist_controls(source_dir: Path) -> CheckResult:
    """Spot-check that required NIST SP 800-53 control evidence files exist."""
    result = CheckResult(
        check_id="nist-controls",
        description="Verify NIST SP 800-53 Rev. 5 control evidence files are present",
        status="pass",
    )

    # Collect all file names in the repository (case-insensitive).
    all_files_lower = set()
    for fpath in source_dir.rglob("*"):
        if fpath.is_file():
            all_files_lower.add(fpath.name.lower())

    for control, evidence_patterns in NIST_CONTROL_EVIDENCE.items():
        satisfied = False
        for pattern in evidence_patterns:
            if any(pattern.lower() in fname for fname in all_files_lower):
                satisfied = True
                result.evidence.append(
                    f"{control}: evidence pattern '{pattern}' found."
                )
                break

        if not satisfied:
            result.findings.append(Finding(
                check_id="nist-controls",
                status="fail",
                message=(
                    f"No evidence found for NIST SP 800-53 control {control}. "
                    f"Expected file matching one of: {evidence_patterns}"
                ),
                standard_ref=f"NIST SP 800-53 Rev. 5 {control}",
            ))
            result.status = "fail"

    return result


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(
    check_results: list[CheckResult],
    source_dir: Path,
    audit_log_path: Optional[Path],
) -> dict:
    """Build a structured JSON compliance report."""
    total = len(check_results)
    passed = sum(1 for r in check_results if r.status == "pass")
    failed = sum(1 for r in check_results if r.status == "fail")
    warned = sum(1 for r in check_results if r.status == "warn")
    skipped = sum(1 for r in check_results if r.status == "skip")

    overall = "pass" if failed == 0 else "fail"

    return {
        "report_id": _new_uuid(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "tools/validator/fips-compliance-checker.py v1.0.0",
        "scope": {
            "source_dir": str(source_dir.resolve()),
            "audit_log": str(audit_log_path.resolve()) if audit_log_path else None,
        },
        "summary": {
            "overall_status": overall,
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "warned": warned,
            "skipped": skipped,
        },
        "standards": [
            "FIPS 140-2/140-3",
            "NIST SP 800-53 Rev. 5",
            "NIST SP 800-88 Rev. 1",
            "NIST SP 800-131A Rev. 2",
            "RFC 8446 (TLS 1.3)",
        ],
        "checks": [
            {
                "check_id": r.check_id,
                "description": r.description,
                "status": r.status,
                "finding_count": len(r.findings),
                "evidence": r.evidence,
                "findings": [
                    {
                        "status": f.status,
                        "message": f.message,
                        "file": f.file,
                        "line": f.line,
                        "detail": f.detail,
                        "standard_ref": f.standard_ref,
                    }
                    for f in r.findings
                ],
            }
            for r in check_results
        ],
    }


def _new_uuid() -> str:
    """Generate a UUID v4 without requiring the uuid module."""
    import uuid
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

def print_summary(check_results: list[CheckResult]) -> None:
    print()
    print(bold("=== FIPS Compliance Check Results ==="))
    print()
    for result in check_results:
        status_str = {
            "pass": green("PASS"),
            "fail": red("FAIL"),
            "warn": yellow("WARN"),
            "skip": "SKIP",
        }.get(result.status, result.status.upper())

        print(f"  [{status_str}] {result.check_id}: {result.description}")
        for finding in result.findings:
            loc = ""
            if finding.file:
                loc = f" ({finding.file}"
                if finding.line:
                    loc += f":{finding.line}"
                loc += ")"
            f_status = red("✗") if finding.status == "fail" else yellow("!")
            print(f"         {f_status} {finding.message}{loc}")
        for ev in result.evidence:
            print(f"         {green('✓')} {ev}")
    print()

    total = len(check_results)
    failed = sum(1 for r in check_results if r.status == "fail")
    overall = red("FAILED") if failed else green("PASSED")
    print(bold(f"Overall: {overall} ({total - failed}/{total} checks passed)"))
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fips-compliance-checker",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("."),
        metavar="PATH",
        help="Root directory to scan for source files (default: .)",
    )
    parser.add_argument(
        "--audit-log",
        type=Path,
        default=None,
        metavar="PATH",
        help="Path to audit log JSON Lines file for hash chain verification",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Directory containing NIST 800-53 evidence files (default: --source-dir)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        metavar="PATH",
        help="Write JSON compliance report to this file (default: stdout)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Exit immediately on first check failure",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    global _USE_COLOR

    args = parse_args(argv)

    if args.no_color:
        _USE_COLOR = False

    source_dir: Path = args.source_dir.resolve()
    evidence_dir: Path = (args.evidence_dir or args.source_dir).resolve()

    print(bold(f"FIPS Compliance Checker — scanning {source_dir}"))
    print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()

    results: list[CheckResult] = []

    # Run checks.
    checks = [
        ("algo-scan", lambda: check_algo_scan(source_dir)),
        ("tls-version", lambda: check_tls_version(source_dir)),
        ("audit-worm", lambda: check_audit_worm(source_dir)),
        ("hash-chain", lambda: check_hash_chain(args.audit_log)),
        ("nist-controls", lambda: check_nist_controls(evidence_dir)),
    ]

    for check_id, check_fn in checks:
        print(f"  Running {check_id}...")
        try:
            check_result = check_fn()
        except Exception as exc:  # pylint: disable=broad-except
            check_result = CheckResult(
                check_id=check_id,
                description=check_id,
                status="fail",
                findings=[Finding(
                    check_id=check_id,
                    status="fail",
                    message=f"Unexpected error: {exc}",
                )],
            )

        results.append(check_result)

        if args.fail_fast and check_result.status == "fail":
            print(red(f"  FAIL: {check_id} — stopping (--fail-fast)"))
            break

    # Print human-readable summary.
    print_summary(results)

    # Build and output structured report.
    report = build_report(results, source_dir, args.audit_log)

    if args.report:
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Compliance report written to: {args.report}")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    # Exit 1 if any check failed.
    return 1 if any(r.status == "fail" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
