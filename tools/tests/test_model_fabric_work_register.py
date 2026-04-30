from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "examples" / "model-fabric-agent-work-register.example.json"

# Import ALLOWED_CODEX_STATUS from the validator to avoid duplication.
_spec = importlib.util.spec_from_file_location(
    "validate_model_fabric_work_register",
    ROOT / "tools" / "validate_model_fabric_work_register.py",
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
ALLOWED_CODEX_STATUS: frozenset[str] = frozenset(_mod.ALLOWED_CODEX_STATUS)

# Phrases that must appear in acceptanceSummary for unverified_output items.
_ENGAGEMENT_PHRASES = ("engagement evidence", "no verifiable")


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


def test_codex_items_have_valid_codex_status() -> None:
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    for item in data["spec"]["workItems"]:
        if item["assignedLane"] == "Codex":
            assert "codexStatus" in item, (
                f"Codex lane item {item['issueRef']} is missing codexStatus"
            )
            assert item["codexStatus"] in ALLOWED_CODEX_STATUS, (
                f"Codex lane item {item['issueRef']} has invalid codexStatus: {item['codexStatus']}"
            )


def test_codex_review_task_present() -> None:
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    codex_items = [i for i in data["spec"]["workItems"] if i["assignedLane"] == "Codex"]
    review_tasks = [
        i for i in codex_items
        if i.get("codexStatus") == "codex_findings_posted"
    ]
    assert review_tasks, "Register must include at least one Codex review task with codexStatus=codex_findings_posted"


def test_codex_unverified_output_documented() -> None:
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    unverified = [
        i for i in data["spec"]["workItems"]
        if i.get("codexStatus") == "codex_unverified_output"
    ]
    assert unverified, (
        "Register must include at least one codex_unverified_output item "
        "to illustrate engagement-vs-delivery distinction"
    )
    for item in unverified:
        summary = item["acceptanceSummary"].lower()
        assert any(phrase in summary for phrase in _ENGAGEMENT_PHRASES), (
            f"codex_unverified_output item {item['issueRef']} must clarify "
            f"that output is engagement evidence only (expected one of {_ENGAGEMENT_PHRASES})"
        )


def test_lane_semantics_present() -> None:
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    lane_semantics = data.get("spec", {}).get("laneSemantics", {})
    assert "Codex" in lane_semantics, "spec.laneSemantics must document the Codex lane"
    assert "Copilot" in lane_semantics, "spec.laneSemantics must document the Copilot lane"
    codex = lane_semantics["Codex"]
    assert "deliveryNote" in codex, "Codex laneSemantics must include a deliveryNote"
    assert "statuses" in codex, "Codex laneSemantics must include a statuses map"
    assert set(codex["statuses"].keys()) == ALLOWED_CODEX_STATUS, (
        "Codex laneSemantics.statuses must document exactly the allowed codexStatus values"
    )
