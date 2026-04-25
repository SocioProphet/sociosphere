from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_DIR = ROOT / "registry" / "deployment-topology"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "recorded_at",
    "controller_repo",
    "subject_repo",
    "status",
    "source_prs",
    "deployment_surfaces",
    "required_invariants",
    "software_review",
}
REQUIRED_SOURCE_LOCK_KEYS = {"ref", "github_blob_sha", "sha256", "captured_at", "required_terms"}


def fail(message: str) -> None:
    raise SystemExit(f"ERR: {message}")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} did not parse to an object")
    return data


def require_non_empty_list(record: dict[str, Any], key: str, rel: str) -> list[Any]:
    value = record.get(key)
    if not isinstance(value, list) or not value:
        fail(f"{rel} requires non-empty list at {key}")
    return value


def validate_source_lock(surface: dict[str, Any], rel: str) -> None:
    source_lock = surface.get("source_lock")
    if not isinstance(source_lock, dict):
        fail(f"{rel} deployment surface {surface.get('id')} requires source_lock")
    missing = sorted(REQUIRED_SOURCE_LOCK_KEYS - set(source_lock))
    if missing:
        fail(f"{rel} source_lock missing required keys: {', '.join(missing)}")
    if source_lock["ref"] != "main":
        fail(f"{rel} source_lock.ref must be main")
    blob_sha = str(source_lock["github_blob_sha"])
    if len(blob_sha) != 40 or not all(ch in "0123456789abcdef" for ch in blob_sha.lower()):
        fail(f"{rel} source_lock.github_blob_sha must be a 40-character hex SHA")
    sha256 = str(source_lock["sha256"])
    if len(sha256) != 64 or not all(ch in "0123456789abcdef" for ch in sha256.lower()):
        fail(f"{rel} source_lock.sha256 must be a 64-character hex SHA-256")
    required_terms = source_lock["required_terms"]
    if not isinstance(required_terms, list) or not required_terms:
        fail(f"{rel} source_lock.required_terms must be a non-empty list")
    for term in ("kind: ApplicationSet", "search-orchestrator-academy-bridge", "infra/k8s/search-orchestrator/overlays/policy", "bundle: fogstack.knowledge"):
        if term not in required_terms:
            fail(f"{rel} source_lock.required_terms missing {term!r}")


def validate_application(app: dict[str, Any], rel: str) -> None:
    for key in ("name", "path", "role"):
        if key not in app:
            fail(f"{rel} application entry missing {key}")
    if app["name"] == "search-orchestrator-academy-bridge":
        if app.get("bundle") != "fogstack.knowledge":
            fail(f"{rel} academy bridge must bind bundle=fogstack.knowledge")
        if app.get("path") != "infra/k8s/search-orchestrator/overlays/policy":
            fail(f"{rel} academy bridge must target policy overlay")
        for key in ("required_validation", "release_artifacts", "bundle_artifacts"):
            if not isinstance(app.get(key), list) or not app[key]:
                fail(f"{rel} academy bridge requires non-empty {key}")


def validate_surface(surface: dict[str, Any], rel: str) -> None:
    for key in ("id", "kind", "repo", "path", "namespace", "destination_namespace", "target_revision", "applications"):
        if key not in surface:
            fail(f"{rel} deployment surface missing {key}")
    if surface["kind"] != "ArgoCDApplicationSet":
        fail(f"{rel} unsupported deployment surface kind={surface['kind']!r}")
    if surface["repo"] != "SocioProphet/prophet-platform":
        fail(f"{rel} currently supports prophet-platform surfaces only")
    validate_source_lock(surface, rel)
    apps = surface["applications"]
    if not isinstance(apps, list) or not apps:
        fail(f"{rel} deployment surface requires non-empty applications list")
    names = {app.get("name") for app in apps if isinstance(app, dict)}
    if "search-orchestrator-academy-bridge" not in names:
        fail(f"{rel} missing search-orchestrator-academy-bridge application")
    for app in apps:
        if not isinstance(app, dict):
            fail(f"{rel} application entries must be objects")
        validate_application(app, rel)


def validate_record(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    record = load_yaml(path)
    missing = sorted(REQUIRED_TOP_LEVEL - set(record))
    if missing:
        fail(f"{rel} missing required keys: {', '.join(missing)}")
    if record["schema_version"] != "sociosphere.deployment-topology/v0.1":
        fail(f"{rel} has unsupported schema_version={record['schema_version']!r}")
    if record["controller_repo"] != "SocioProphet/sociosphere":
        fail(f"{rel} must be controlled by SocioProphet/sociosphere")
    if record["subject_repo"] != "SocioProphet/prophet-platform":
        fail(f"{rel} subject_repo must be SocioProphet/prophet-platform")

    source_prs = require_non_empty_list(record, "source_prs", rel)
    if not any(item.get("repo") == "SocioProphet/prophet-platform" and item.get("pr") == 181 for item in source_prs if isinstance(item, dict)):
        fail(f"{rel} must reference prophet-platform PR 181")

    for surface in require_non_empty_list(record, "deployment_surfaces", rel):
        if not isinstance(surface, dict):
            fail(f"{rel} deployment_surfaces entries must be objects")
        validate_surface(surface, rel)

    invariants = require_non_empty_list(record, "required_invariants", rel)
    invariant_ids = {item.get("id") for item in invariants if isinstance(item, dict)}
    for required in {"appset-has-academy-bridge", "academy-bridge-bound-to-fogstack-knowledge", "deployment-topology-owned-by-sociosphere", "platform-appset-source-lock"}:
        if required not in invariant_ids:
            fail(f"{rel} missing required invariant {required}")

    review = record.get("software_review", {})
    if not isinstance(review, dict):
        fail(f"{rel} software_review must be an object")
    for key in ("correctness", "weaknesses", "next_hardening"):
        if not isinstance(review.get(key), list) or not review[key]:
            fail(f"{rel} software_review.{key} must be a non-empty list")


def main() -> int:
    if not TOPOLOGY_DIR.exists():
        fail("registry/deployment-topology directory missing")
    records = sorted(TOPOLOGY_DIR.glob("*.yaml"))
    if not records:
        fail("registry/deployment-topology contains no yaml records")
    for record in records:
        validate_record(record)
    print(json.dumps({"validated_deployment_topology_records": [str(p.relative_to(ROOT)) for p in records]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
