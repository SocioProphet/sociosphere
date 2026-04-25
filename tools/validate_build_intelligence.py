from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATUS_DIR = ROOT / "status" / "build-intelligence"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "recorded_at",
    "controller_repo",
    "subject_repo",
    "status",
    "scope",
    "merged_tranches",
    "active_tranches",
    "test_and_workflow_surfaces",
    "software_review",
    "running_backlog",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERR: {message}")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} did not parse to an object")
    return data


def require_non_empty_list(record: dict[str, Any], key: str, rel: str) -> None:
    value = record.get(key)
    if not isinstance(value, list) or not value:
        fail(f"{rel} requires non-empty list at {key}")


def validate_record(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    record = load_yaml(path)
    missing = sorted(REQUIRED_TOP_LEVEL - set(record))
    if missing:
        fail(f"{rel} missing required keys: {', '.join(missing)}")

    if record["schema_version"] != "sociosphere.build-intelligence/v0.1":
        fail(f"{rel} has unsupported schema_version={record['schema_version']!r}")
    if record["controller_repo"] != "SocioProphet/sociosphere":
        fail(f"{rel} must be controlled by SocioProphet/sociosphere")
    if not str(record["subject_repo"]).startswith("SocioProphet/"):
        fail(f"{rel} subject_repo must be a SocioProphet repo")

    require_non_empty_list(record, "merged_tranches", rel)
    require_non_empty_list(record, "active_tranches", rel)
    require_non_empty_list(record, "running_backlog", rel)

    for tranche in record["merged_tranches"]:
        if not isinstance(tranche, dict):
            fail(f"{rel} merged_tranches entries must be objects")
        for key in ("pr", "title", "merge_commit", "artifacts"):
            if key not in tranche:
                fail(f"{rel} merged tranche missing {key}")
        if not isinstance(tranche["artifacts"], list) or not tranche["artifacts"]:
            fail(f"{rel} merged tranche PR {tranche.get('pr')} requires artifacts")

    for tranche in record["active_tranches"]:
        if not isinstance(tranche, dict):
            fail(f"{rel} active_tranches entries must be objects")
        for key in ("pr", "title", "branch", "state", "files_changed", "pending_gates"):
            if key not in tranche:
                fail(f"{rel} active tranche missing {key}")
        if tranche["state"] not in {"open", "draft", "merged", "blocked"}:
            fail(f"{rel} active tranche PR {tranche.get('pr')} has invalid state={tranche['state']!r}")

    review = record.get("software_review", {})
    if not isinstance(review, dict):
        fail(f"{rel} software_review must be an object")
    for key in ("correctness", "weaknesses", "next_hardening"):
        if not isinstance(review.get(key), list) or not review[key]:
            fail(f"{rel} software_review.{key} must be a non-empty list")


def main() -> int:
    if not STATUS_DIR.exists():
        fail("status/build-intelligence directory missing")
    records = sorted(STATUS_DIR.glob("*.yaml"))
    if not records:
        fail("status/build-intelligence contains no yaml records")
    for record in records:
        validate_record(record)
    print(json.dumps({"validated_build_intelligence_records": [str(p.relative_to(ROOT)) for p in records]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
