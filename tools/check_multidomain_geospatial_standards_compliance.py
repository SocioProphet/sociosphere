#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_AUTHORITIES = {
    "SocioProphet/prophet-platform-standards",
    "SocioProphet/socioprophet-standards-storage",
    "SocioProphet/socioprophet-standards-knowledge",
    "SocioProphet/socioprophet-agent-standards",
}
REQUIRED_IMPLEMENTATIONS = {
    "SocioProphet/prophet-platform",
    "SocioProphet/gaia-world-model",
    "SocioProphet/sociosphere",
    "SocioProphet/sherlock-search",
    "SocioProphet/agentplane",
    "SocioProphet/lattice-forge",
}
REQUIRED_TOP = ["registry_id", "version", "status", "standards_authorities", "required_implementation_docs", "minimum_checks"]
REQUIRED_DOC = ["repo", "path", "status"]
ALLOWED_STATUS = {"committed", "open_pr", "blocked"}


def fail(msg: str) -> None:
    print(f"ERR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path}: invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path}: expected object")
    return data


def require_keys(obj: dict, keys: list[str], where: str) -> None:
    missing = [key for key in keys if key not in obj]
    if missing:
        fail(f"{where}: missing required keys: {', '.join(missing)}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "registry/multidomain_geospatial_standards_compliance.v1.json"
    if not path.exists():
        fail("missing registry/multidomain_geospatial_standards_compliance.v1.json")
    data = load_json(path)
    require_keys(data, REQUIRED_TOP, "registry")

    authorities = set(data["standards_authorities"])
    missing_authorities = sorted(REQUIRED_AUTHORITIES - authorities)
    if missing_authorities:
        fail(f"missing standards authorities: {', '.join(missing_authorities)}")

    docs = data["required_implementation_docs"]
    if not isinstance(docs, list) or not docs:
        fail("required_implementation_docs must be non-empty array")
    seen_repos = set()
    for idx, doc in enumerate(docs):
        if not isinstance(doc, dict):
            fail(f"required_implementation_docs[{idx}] must be object")
        require_keys(doc, REQUIRED_DOC, f"required_implementation_docs[{idx}]")
        if doc["status"] not in ALLOWED_STATUS:
            fail(f"{doc['repo']}: invalid status {doc['status']!r}")
        if not doc["path"].endswith("COMPLIES_WITH_MULTIDOMAIN_GEOSPATIAL_STANDARDS.md"):
            fail(f"{doc['repo']}: unexpected compliance doc path {doc['path']!r}")
        if doc["status"] == "open_pr" and "pr" not in doc:
            fail(f"{doc['repo']}: open_pr status requires pr number")
        seen_repos.add(doc["repo"])
    missing_repos = sorted(REQUIRED_IMPLEMENTATIONS - seen_repos)
    if missing_repos:
        fail(f"missing implementation repos: {', '.join(missing_repos)}")

    checks = data["minimum_checks"]
    if not isinstance(checks, dict):
        fail("minimum_checks must be object")
    for key, value in checks.items():
        if not isinstance(value, bool):
            fail(f"minimum_checks.{key} must be boolean")
    print("OK: multidomain geospatial standards compliance registry is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
