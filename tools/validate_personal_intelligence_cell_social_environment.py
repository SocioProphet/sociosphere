#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_SCHEMA = ROOT / "standards/personal-intelligence-cell/social-environment-snapshot.schema.json"
SNAPSHOT_EXAMPLE = ROOT / "standards/personal-intelligence-cell/social-environment-snapshot.example.json"
REPUTATION_SCHEMA = ROOT / "standards/personal-intelligence-cell/reputation-delta.schema.json"
REPUTATION_EXAMPLE = ROOT / "standards/personal-intelligence-cell/reputation-delta.example.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(f"Personal Intelligence Cell social environment validation failed: {message}")
    return 1


def require_fields(example: dict, schema: dict, label: str) -> int:
    missing = sorted(set(schema.get("required", [])) - set(example))
    if missing:
        return fail(f"{label} missing required fields: {', '.join(missing)}")
    return 0


def validate_snapshot() -> int:
    schema = load_json(SNAPSHOT_SCHEMA)
    example = load_json(SNAPSHOT_EXAMPLE)
    if schema.get("title") != "PersonalIntelligenceCellSocialEnvironmentSnapshot":
        return fail("snapshot schema title mismatch")
    status = require_fields(example, schema, "snapshot example")
    if status:
        return status
    if example["peer_count"] < len(example.get("stale_ties", [])):
        return fail("snapshot peer_count cannot be less than stale_ties length")
    if example["stale_tie_count"] != len(example.get("stale_ties", [])):
        return fail("snapshot stale_tie_count must match stale_ties length")
    if example["emerging_community_count"] != len(example.get("emerging_communities", [])):
        return fail("snapshot emerging_community_count must match emerging_communities length")
    if example["attention_sink_count"] != len(example.get("attention_sinks", [])):
        return fail("snapshot attention_sink_count must match attention_sinks length")
    if not example.get("relationship_hygiene"):
        return fail("snapshot relationship_hygiene recommendations required")
    return 0


def validate_reputation() -> int:
    schema = load_json(REPUTATION_SCHEMA)
    example = load_json(REPUTATION_EXAMPLE)
    if schema.get("title") != "PersonalIntelligenceCellReputationDelta":
        return fail("reputation schema title mismatch")
    status = require_fields(example, schema, "reputation example")
    if status:
        return status
    if not example.get("evidence_refs"):
        return fail("reputation evidence_refs required")
    if example["subject_kind"] not in ["human", "agent", "source", "model", "workflow", "community", "claim"]:
        return fail("invalid reputation subject_kind")
    if not -1 <= example["delta"] <= 1:
        return fail("reputation delta out of range")
    interval = example["confidence_interval"]
    if not interval["low"] <= example["delta"] <= interval["high"]:
        return fail("reputation confidence interval must contain delta")
    anti = example["anti_manipulation"]
    for key in ["sybil_score", "collusion_score", "provenance_weight", "anti_gaming_weight"]:
        if not 0 <= anti[key] <= 1:
            return fail(f"anti_manipulation.{key} out of range")
    components = example["score_components"]
    for key in ["trust", "authority", "popularity", "expertise"]:
        if not 0 <= components[key] <= 1:
            return fail(f"score_components.{key} out of range")
    if example["policy_effect"] == "review_required" and not anti.get("flags"):
        return fail("review_required reputation effect must cite anti-manipulation flags")
    return 0


def main() -> int:
    for path in [SNAPSHOT_SCHEMA, SNAPSHOT_EXAMPLE, REPUTATION_SCHEMA, REPUTATION_EXAMPLE]:
        if not path.exists():
            return fail(f"missing file: {path.relative_to(ROOT)}")
    status = validate_snapshot()
    if status:
        return status
    status = validate_reputation()
    if status:
        return status
    print("Personal Intelligence Cell social environment standards validate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
