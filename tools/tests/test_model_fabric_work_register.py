from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "examples" / "model-fabric-agent-work-register.example.json"

REQUIRED_CODEX_STATUSES = {
    "codex_dispatched",
    "codex_engaged",
    "codex_findings_posted",
    "codex_pr_open",
    "codex_pr_merged",
    "codex_unverified_output",
}


def test_model_fabric_work_register_validator_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_model_fabric_work_register.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "OK: validated" in result.stdout


def test_register_tracks_codex_and_copilot_lanes() -> None:
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    lanes = {item["assignedLane"] for item in data["spec"]["workItems"]}
    repos = {item["repo"] for item in data["spec"]["workItems"]}

    assert lanes == {"Codex", "Copilot"}
    assert "SocioProphet/prophet-platform" in repos
    assert "SocioProphet/homebrew-prophet" in repos


def test_codex_lane_semantics_are_explicit() -> None:
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    codex = data["spec"]["laneStatusSemantics"]["codex"]

    assert codex["reviewTrigger"] == "@codex review"
    assert codex["implementationTrigger"] == "@codex Please take this..."
    assert "verifiable GitHub PR, branch, commit, or merge" in codex["deliveryRule"]
    assert set(codex["statuses"]) == REQUIRED_CODEX_STATUSES


def test_work_items_cover_codex_statuses_and_delivery_evidence() -> None:
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    items = data["spec"]["workItems"]
    codex_statuses = {
        item["laneStatus"] for item in items if item["assignedLane"] == "Codex"
    }

    assert REQUIRED_CODEX_STATUSES <= codex_statuses
    for item in items:
        assert item["deliveryEvidence"].strip()
        if item["assignedLane"] == "Codex" and item["laneStatus"] in {
            "codex_engaged",
            "codex_findings_posted",
            "codex_unverified_output",
        }:
            assert "delivery" in item["deliveryEvidence"].lower()
