from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOCK_DIR = ROOT / "registry" / "contract-locks"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "recorded_at",
    "controller_repo",
    "upstream_repo",
    "consumer_repo",
    "status",
    "contract",
    "source_prs",
    "validation",
    "software_review",
}
REQUIRED_CONTRACT_KEYS = {
    "name",
    "version",
    "upstream_path",
    "consumer_path",
    "local_snapshot",
    "github_blob_sha",
    "sha256",
    "required_terms",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERR: {message}")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} did not parse to an object")
    return data


def validate_hex(value: str, expected_len: int, label: str, rel: str) -> None:
    if len(value) != expected_len or not all(ch in "0123456789abcdef" for ch in value.lower()):
        fail(f"{rel} {label} must be {expected_len} hex characters")


def validate_record(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    record = load_yaml(path)
    missing = sorted(REQUIRED_TOP_LEVEL - set(record))
    if missing:
        fail(f"{rel} missing required keys: {', '.join(missing)}")
    if record["schema_version"] != "sociosphere.contract-lock/v0.1":
        fail(f"{rel} has unsupported schema_version={record['schema_version']!r}")
    if record["controller_repo"] != "SocioProphet/sociosphere":
        fail(f"{rel} must be controlled by SocioProphet/sociosphere")
    if record["upstream_repo"] != "SocioProphet/policy-fabric":
        fail(f"{rel} upstream_repo must be SocioProphet/policy-fabric")
    if record["consumer_repo"] != "SocioProphet/prophet-platform":
        fail(f"{rel} consumer_repo must be SocioProphet/prophet-platform")

    contract = record["contract"]
    if not isinstance(contract, dict):
        fail(f"{rel} contract must be an object")
    missing_contract = sorted(REQUIRED_CONTRACT_KEYS - set(contract))
    if missing_contract:
        fail(f"{rel} contract missing required keys: {', '.join(missing_contract)}")
    if contract["name"] != "ProphetOperationsActionDecision":
        fail(f"{rel} unexpected contract.name={contract['name']!r}")
    if contract["version"] != "v1":
        fail(f"{rel} unexpected contract.version={contract['version']!r}")

    validate_hex(str(contract["github_blob_sha"]), 40, "contract.github_blob_sha", rel)
    expected_sha256 = str(contract["sha256"])
    validate_hex(expected_sha256, 64, "contract.sha256", rel)

    snapshot_rel = str(contract["local_snapshot"])
    snapshot_path = ROOT / snapshot_rel
    if not snapshot_path.exists():
        fail(f"{rel} contract.local_snapshot missing file: {snapshot_rel}")
    actual_sha256 = sha256_file(snapshot_path)
    if actual_sha256 != expected_sha256:
        fail(f"{rel} local snapshot sha256 mismatch: expected {expected_sha256}, got {actual_sha256}")
    snapshot_text = snapshot_path.read_text(encoding="utf-8")

    required_terms = contract["required_terms"]
    if not isinstance(required_terms, list) or not required_terms:
        fail(f"{rel} contract.required_terms must be a non-empty list")
    for term in required_terms:
        if term not in snapshot_text:
            fail(f"{rel} local snapshot missing required term {term!r}")

    source_prs = record["source_prs"]
    if not isinstance(source_prs, list) or not source_prs:
        fail(f"{rel} source_prs must be a non-empty list")
    if not any(isinstance(item, dict) and item.get("repo") == "SocioProphet/prophet-platform" and item.get("pr") == 182 for item in source_prs):
        fail(f"{rel} must reference prophet-platform PR 182")

    review = record.get("software_review", {})
    if not isinstance(review, dict):
        fail(f"{rel} software_review must be an object")
    for key in ("correctness", "weaknesses", "next_hardening"):
        if not isinstance(review.get(key), list) or not review[key]:
            fail(f"{rel} software_review.{key} must be a non-empty list")


def main() -> int:
    if not LOCK_DIR.exists():
        fail("registry/contract-locks directory missing")
    records = sorted(LOCK_DIR.glob("**/*.lock.yaml"))
    if not records:
        fail("registry/contract-locks contains no lock records")
    for record in records:
        validate_record(record)
    print(json.dumps({"validated_contract_locks": [str(p.relative_to(ROOT)) for p in records]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
