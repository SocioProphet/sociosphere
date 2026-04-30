#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "model-fabric-agent-work-register.example.json"
REQUIRED_FIELDS = {
    "repo",
    "issueRef",
    "assignedLane",
    "workstream",
    "expectedArtifact",
    "status",
    "acceptanceSummary",
}
ALLOWED_LANES = {"Codex", "Copilot"}
ALLOWED_STATUS = {"open", "in-progress", "blocked", "closed"}
ALLOWED_CODEX_STATUS = {
    "codex_dispatched",
    "codex_engaged",
    "codex_findings_posted",
    "codex_pr_open",
    "codex_pr_merged",
    "codex_unverified_output",
}
REQUIRED_REPOS = {
    "SocioProphet/prophet-platform",
    "SocioProphet/model-router",
    "SocioProphet/guardrail-fabric",
    "SocioProphet/model-governance-ledger",
    "SocioProphet/agent-registry",
    "SocioProphet/homebrew-prophet",
    "SocioProphet/sociosphere",
}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if not EXAMPLE.exists():
        return fail(f"missing {EXAMPLE}")
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    if data.get("apiVersion") != "sociosphere.socioprophet.dev/v1":
        return fail("apiVersion must be sociosphere.socioprophet.dev/v1")
    if data.get("kind") != "AgentWorkRegister":
        return fail("kind must be AgentWorkRegister")
    items = data.get("spec", {}).get("workItems", [])
    if not items:
        return fail("spec.workItems must not be empty")
    repos = set()
    issue_refs = set()
    for idx, item in enumerate(items):
        prefix = f"workItems[{idx}]"
        missing = sorted(REQUIRED_FIELDS - set(item))
        if missing:
            return fail(f"{prefix} missing fields: {missing}")
        if item["assignedLane"] not in ALLOWED_LANES:
            return fail(f"{prefix}.assignedLane is invalid")
        if item["status"] not in ALLOWED_STATUS:
            return fail(f"{prefix}.status is invalid")
        if item["assignedLane"] == "Codex":
            if "codexStatus" not in item:
                return fail(f"{prefix} is a Codex lane item but is missing required field: codexStatus")
            if item["codexStatus"] not in ALLOWED_CODEX_STATUS:
                return fail(
                    f"{prefix}.codexStatus '{item['codexStatus']}' is invalid; "
                    f"must be one of {sorted(ALLOWED_CODEX_STATUS)}"
                )
        if not str(item["issueRef"]).startswith("https://github.com/"):
            return fail(f"{prefix}.issueRef must be a GitHub URL")
        if item["issueRef"] in issue_refs:
            return fail(f"duplicate issueRef: {item['issueRef']}")
        issue_refs.add(item["issueRef"])
        repos.add(item["repo"])
        if not str(item["expectedArtifact"]).strip():
            return fail(f"{prefix}.expectedArtifact is required")
        if not str(item["acceptanceSummary"]).strip():
            return fail(f"{prefix}.acceptanceSummary is required")
    missing_repos = sorted(REQUIRED_REPOS - repos)
    if missing_repos:
        return fail(f"missing required repos: {missing_repos}")
    print(f"OK: validated {len(items)} model-fabric agent work items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
