from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "examples" / "model-fabric-agent-work-register.example.json"


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
