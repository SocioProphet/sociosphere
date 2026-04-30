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
    "laneStatus",
    "deliveryEvidence",
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
ALLOWED_COPILOT_STATUS = {
    "copilot_assigned",
    "copilot_pr_open",
    "copilot_pr_merged",
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

    semantics = data.get("spec", {}).get("laneStatusSemantics", {})
    codex_semantics = semantics.get("codex", {})
    if codex_semantics.get("reviewTrigger") != "@codex review":
        return fail("Codex review trigger must be documented as '@codex review'")
    if codex_semantics.get("implementationTrigger") != "@codex Please take this...":
        return fail("Codex implementation trigger must be documented")
    if "verifiable GitHub PR, branch, commit, or merge" not in codex_semantics.get("deliveryRule", ""):
        return fail("Codex delivery rule must require verifiable GitHub artifacts")
    missing_codex_statuses = sorted(ALLOWED_CODEX_STATUS - set(codex_semantics.get("statuses", {})))
    if missing_codex_statuses:
        return fail(f"missing Codex statuses: {missing_codex_statuses}")

    items = data.get("spec", {}).get("workItems", [])
    if not items:
        return fail("spec.workItems must not be empty")
    repos = set()
    issue_refs = set()
    codex_statuses = set()
    copilot_statuses = set()
    for idx, item in enumerate(items):
        prefix = f"workItems[{idx}]"
        missing = sorted(REQUIRED_FIELDS - set(item))
        if missing:
            return fail(f"{prefix} missing fields: {missing}")
        lane = item["assignedLane"]
        lane_status = item["laneStatus"]
        if lane not in ALLOWED_LANES:
            return fail(f"{prefix}.assignedLane is invalid")
        if item["status"] not in ALLOWED_STATUS:
            return fail(f"{prefix}.status is invalid")
        if lane == "Codex":
            if lane_status not in ALLOWED_CODEX_STATUS:
                return fail(f"{prefix}.laneStatus is not an allowed Codex status")
            codex_statuses.add(lane_status)
            delivery = str(item["deliveryEvidence"])
            if lane_status in {"codex_engaged", "codex_findings_posted", "codex_unverified_output"} and "delivery" not in delivery.lower():
                return fail(f"{prefix}.deliveryEvidence must distinguish Codex engagement from delivery")
        if lane == "Copilot":
            if lane_status not in ALLOWED_COPILOT_STATUS:
                return fail(f"{prefix}.laneStatus is not an allowed Copilot status")
            copilot_statuses.add(lane_status)
        if not str(item["issueRef"]).startswith("https://github.com/"):
            return fail(f"{prefix}.issueRef must be a GitHub URL")
        if item["issueRef"] in issue_refs:
            return fail(f"duplicate issueRef: {item['issueRef']}")
        issue_refs.add(item["issueRef"])
        repos.add(item["repo"])
        if not str(item["expectedArtifact"]).strip():
            return fail(f"{prefix}.expectedArtifact is required")
        if not str(item["deliveryEvidence"]).strip():
            return fail(f"{prefix}.deliveryEvidence is required")
        if not str(item["acceptanceSummary"]).strip():
            return fail(f"{prefix}.acceptanceSummary is required")
    missing_repos = sorted(REQUIRED_REPOS - repos)
    if missing_repos:
        return fail(f"missing required repos: {missing_repos}")
    missing_codex_status_coverage = sorted(ALLOWED_CODEX_STATUS - codex_statuses)
    if missing_codex_status_coverage:
        return fail(f"work items must cover Codex statuses: {missing_codex_status_coverage}")
    if not copilot_statuses:
        return fail("work items must include Copilot lane statuses")
    print(f"OK: validated {len(items)} model-fabric agent work items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
