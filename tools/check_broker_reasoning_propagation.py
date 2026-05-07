#!/usr/bin/env python3
"""Validate broker reasoning propagation rule structure.

This checker intentionally uses only the Python standard library and a small
structure-oriented parser for the committed YAML subset. It verifies that the
broker propagation file names the required rules and required affected repos.
"""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "registry" / "broker-reasoning-propagation-rules.yaml"

REQUIRED_RULE_IDS = {
    "broker-standard-change",
    "provider-binding-contract-change",
    "provider-binding-evidence-profile-change",
    "broker-reasoning-output-change",
}

REQUIRED_AFFECTED_REPOS = {
    "prophet-platform",
    "policy-fabric",
    "agentplane",
    "global-devsecops-intelligence",
    "alexandrian-academy",
    "sociosphere",
}


def main() -> int:
    if not RULES.exists():
        print(f"Missing broker propagation rules: {RULES}")
        return 1

    text = RULES.read_text(encoding="utf-8")
    rule_ids = set(re.findall(r"^\s*-\s+id:\s*([a-z0-9._-]+)\s*$", text, flags=re.MULTILINE))
    repos = set(re.findall(r"^\s*-\s+repo:\s*([a-z0-9._-]+)\s*$", text, flags=re.MULTILINE))

    missing_rules = sorted(REQUIRED_RULE_IDS - rule_ids)
    missing_repos = sorted(REQUIRED_AFFECTED_REPOS - repos)

    if missing_rules:
        print("Missing broker propagation rule ids:")
        for item in missing_rules:
            print(f" - {item}")
    if missing_repos:
        print("Missing affected repositories:")
        for item in missing_repos:
            print(f" - {item}")

    if missing_rules or missing_repos:
        return 1

    print("Broker propagation rules include required rule ids and affected repos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
