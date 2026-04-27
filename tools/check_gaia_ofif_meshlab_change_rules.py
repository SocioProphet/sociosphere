#!/usr/bin/env python3
"""Validate GAIA / OFIF / MeshLab change propagation rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "registry/gaia-ofif-meshlab-change-propagation-rules.v1.json"
REQUIRED_TOP = ["rules_version", "program", "updated_at", "purpose", "rules"]
REQUIRED_RULE = ["id", "when", "notify", "required_actions"]
REQUIRED_RULE_IDS = {
    "gaia-schema-change",
    "gaia-fixture-change",
    "ofif-event-fixture-change",
    "sherlock-result-schema-change",
    "meshrush-crystallization-change",
    "agentplane-meshrush-candidate-change",
    "lattice-runtime-admission-change",
    "progress-ledger-change",
    "smart-spaces-boundary-change",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError:
        fail(f"missing rules file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail("rules file must be a JSON object")
    return value


def require_fields(doc: Dict[str, Any], fields: Iterable[str], scope: str) -> None:
    missing = [field for field in fields if field not in doc]
    if missing:
        fail(f"{scope} missing fields: {', '.join(missing)}")


def main() -> int:
    doc = load_json(RULES)
    require_fields(doc, REQUIRED_TOP, "change rules")
    if doc.get("rules_version") != "v1":
        fail("rules_version must be v1")
    if doc.get("program") != "gaia-ofif-meshlab-control-tower":
        fail("unexpected program")
    rules = doc.get("rules")
    if not isinstance(rules, list) or not rules:
        fail("rules must be a non-empty array")
    seen = set()
    for rule in rules:
        if not isinstance(rule, dict):
            fail("each rule must be an object")
        require_fields(rule, REQUIRED_RULE, "rule")
        rule_id = rule.get("id")
        if rule_id in seen:
            fail(f"duplicate rule id: {rule_id}")
        seen.add(rule_id)
        when = rule.get("when")
        if not isinstance(when, dict) or "repo" not in when or "paths" not in when:
            fail(f"rule {rule_id} requires when.repo and when.paths")
        if not isinstance(when.get("paths"), list) or not when["paths"]:
            fail(f"rule {rule_id} when.paths must be non-empty array")
        for field in ["notify", "required_actions"]:
            if not isinstance(rule.get(field), list) or not rule[field]:
                fail(f"rule {rule_id} {field} must be non-empty array")
    missing = REQUIRED_RULE_IDS - seen
    if missing:
        fail(f"missing required rule ids: {', '.join(sorted(missing))}")
    print("GAIA / OFIF / MeshLab change rules passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
