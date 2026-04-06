#!/usr/bin/env python3
"""Generate reproducible branch inventory and merge-wave planning artifacts.

This script is intentionally conservative: it only uses branch refs available
in the current local clone. If remotes are not configured/fetched, the
inventory will reflect that limitation explicitly.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class BranchRef:
    scope: str
    name: str
    short_name: str
    sha: str
    committer_date: str
    author: str
    subject: str
    upstream: str


def run_git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def list_branch_refs() -> list[BranchRef]:
    fmt = "%(refname)|%(refname:short)|%(objectname)|%(committerdate:iso8601)|%(authorname)|%(subject)|%(upstream:short)"
    out = run_git(["for-each-ref", "refs/heads", "refs/remotes", f"--format={fmt}"])
    branches: list[BranchRef] = []
    if not out:
        return branches

    for row in out.splitlines():
        refname, short_name, sha, cdate, author, subject, upstream = row.split("|", 6)
        scope = "remote" if refname.startswith("refs/remotes/") else "local"
        branches.append(
            BranchRef(
                scope=scope,
                name=refname,
                short_name=short_name,
                sha=sha,
                committer_date=cdate,
                author=author,
                subject=subject,
                upstream=upstream,
            )
        )
    return branches


def ahead_behind(branch: str, upstream: str) -> tuple[str, str]:
    if not upstream:
        return ("", "")
    try:
        out = run_git(["rev-list", "--left-right", "--count", f"{branch}...{upstream}"])
    except subprocess.CalledProcessError:
        return ("", "")
    left, right = out.split()
    return left, right


def files_changed(base: str, branch: str) -> set[str]:
    if base == branch:
        return set()
    try:
        out = run_git(["diff", "--name-only", f"{base}...{branch}"])
    except subprocess.CalledProcessError:
        return set()
    if not out:
        return set()
    return {line for line in out.splitlines() if line}


def classify_risk(overlap_count: int, file_count: int) -> str:
    if file_count == 0:
        return "empty"
    if overlap_count == 0 and file_count <= 10:
        return "low"
    if overlap_count <= 5 and file_count <= 40:
        return "medium"
    return "high"


def write_catalog(path: Path, branches: Iterable[BranchRef]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            [
                "scope",
                "short_name",
                "refname",
                "tip_sha",
                "committer_date",
                "author",
                "subject",
                "upstream",
                "ahead",
                "behind",
            ]
        )
        for b in branches:
            ahead, behind = ahead_behind(b.short_name, b.upstream)
            writer.writerow(
                [
                    b.scope,
                    b.short_name,
                    b.name,
                    b.sha,
                    b.committer_date,
                    b.author,
                    b.subject,
                    b.upstream,
                    ahead,
                    behind,
                ]
            )


def build_wave_data(branches: list[BranchRef], base_branch: str) -> dict:
    base_files = files_changed(base_branch, base_branch)
    _ = base_files
    branch_files: dict[str, set[str]] = {}
    for b in branches:
        if b.short_name == base_branch:
            continue
        branch_files[b.short_name] = files_changed(base_branch, b.short_name)

    wave_a: list[dict] = []
    wave_b: list[dict] = []
    wave_c: list[dict] = []

    names = list(branch_files.keys())
    overlap_counts = {name: 0 for name in names}
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            overlap = len(branch_files[left].intersection(branch_files[right]))
            if overlap > 0:
                overlap_counts[left] += overlap
                overlap_counts[right] += overlap

    for name in names:
        file_count = len(branch_files[name])
        overlap = overlap_counts[name]
        risk = classify_risk(overlap, file_count)
        payload = {
            "branch": name,
            "files_changed": file_count,
            "overlap_score": overlap,
            "risk": risk,
        }
        if risk == "low":
            wave_a.append(payload)
        elif risk == "medium":
            wave_b.append(payload)
        else:
            wave_c.append(payload)

    for wave in (wave_a, wave_b, wave_c):
        wave.sort(key=lambda x: (x["overlap_score"], x["files_changed"], x["branch"]))

    return {
        "base_branch": base_branch,
        "total_candidates": len(names),
        "waves": {
            "wave_a_low_risk": wave_a,
            "wave_b_medium_risk": wave_b,
            "wave_c_high_risk": wave_c,
        },
    }


def write_merge_wave_plan(path: Path, wave_data: dict, remotes: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("# Generated Merge Wave Plan\n\n")
        f.write("This file is generated by `tools/branch_integration_audit.py`.\n\n")
        f.write(f"- Base branch: `{wave_data['base_branch']}`\n")
        f.write(f"- Candidate branches: `{wave_data['total_candidates']}`\n")
        f.write(f"- Remotes configured: `{', '.join(remotes) if remotes else 'none'}`\n\n")

        if wave_data["total_candidates"] == 0:
            f.write(
                "## No merge candidates detected\n\n"
                "Only the base branch is present in this clone. Add/fetch remotes to evaluate all branches.\n"
            )
            return

        for section, title in [
            ("wave_a_low_risk", "Wave A — Low risk"),
            ("wave_b_medium_risk", "Wave B — Medium risk"),
            ("wave_c_high_risk", "Wave C — High risk"),
        ]:
            f.write(f"## {title}\n\n")
            items = wave_data["waves"][section]
            if not items:
                f.write("No branches in this wave.\n\n")
                continue
            f.write("| Branch | Files changed vs base | Overlap score | Risk |\n")
            f.write("|---|---:|---:|---|\n")
            for item in items:
                f.write(
                    f"| `{item['branch']}` | {item['files_changed']} | {item['overlap_score']} | {item['risk']} |\n"
                )
            f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-branch", default="work", help="Branch used as integration base")
    parser.add_argument(
        "--catalog-path",
        default="workbench/backlog/branch-catalog.tsv",
        help="Output path for branch catalog TSV",
    )
    parser.add_argument(
        "--wave-plan-path",
        default="governance/merge-wave-plan.md",
        help="Output path for generated wave plan markdown",
    )
    parser.add_argument(
        "--summary-path",
        default="docs/branch-integration-plan.md",
        help="Output path for integration summary markdown",
    )
    args = parser.parse_args()

    branches = list_branch_refs()
    remotes_raw = run_git(["remote"]) if True else ""
    remotes = [line for line in remotes_raw.splitlines() if line]

    write_catalog(Path(args.catalog_path), branches)
    wave_data = build_wave_data(branches, args.base_branch)
    write_merge_wave_plan(Path(args.wave_plan_path), wave_data, remotes)

    summary = {
        "date_utc": run_git(["show", "-s", "--format=%cI", "HEAD"]),
        "base_branch": args.base_branch,
        "branch_count": len(branches),
        "remote_count": len(remotes),
        "catalog_path": args.catalog_path,
        "wave_plan_path": args.wave_plan_path,
        "remotes": remotes,
    }
    summary_path = Path(args.summary_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8") as f:
        f.write("# Branch Integration Evaluation and Execution\n\n")
        f.write("This document is generated by `tools/branch_integration_audit.py`.\n\n")
        f.write(f"- Base branch: `{summary['base_branch']}`\n")
        f.write(f"- Branch refs discovered: `{summary['branch_count']}`\n")
        f.write(f"- Remotes configured: `{summary['remote_count']}`\n")
        f.write(f"- Branch catalog: `{summary['catalog_path']}`\n")
        f.write(f"- Wave plan: `{summary['wave_plan_path']}`\n\n")

        if not remotes:
            f.write(
                "## Execution status\n\n"
                "No git remotes are configured in this checkout, so only local refs can be evaluated.\n"
                "To move forward, add the authoritative remote and rerun:\n\n"
                "```bash\n"
                "git remote add origin <url>\n"
                "git fetch origin --prune --tags\n"
                "python3 tools/branch_integration_audit.py --base-branch work\n"
                "```\n"
            )
        else:
            f.write(
                "## Execution status\n\n"
                "Remotes are configured and refs were audited. Review generated artifacts for merge wave execution.\n"
            )

        f.write("\n## Machine summary\n\n")
        f.write("```json\n")
        f.write(json.dumps(summary, indent=2))
        f.write("\n```\n")


if __name__ == "__main__":
    main()
