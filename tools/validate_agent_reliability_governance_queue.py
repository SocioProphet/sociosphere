#!/usr/bin/env python3
"""Validate SocioSphere Agent Reliability governance queue fixtures.

The validator is dependency-free by design. It validates the schema/example
contract shape plus the semantic invariants required for SourceOS Agent
Reliability review queues.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "standards" / "agent-reliability" / "governance-queue.schema.v0.1.json"
EXAMPLE = ROOT / "standards" / "agent-reliability" / "examples" / "governance-queue.example.v0.1.json"

VALID_ITEM_TYPES = {"break-glass-approval", "memory-learning-review", "stop-gate-waiver", "external-action-review"}
VALID_STATUSES = {"pending", "approved", "rejected", "superseded"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_SYSTEMS = {"policy-fabric", "memory-mesh", "agentplane", "guardrail-fabric"}
VALID_ARTIFACT_KINDS = {"BreakGlassOverride", "AgentLearningProposal", "StopGateArtifact", "GuardedInvocationArtifact", "PolicyDecisionArtifact", "ExternalActionDraft"}
VALID_ACTION_CLASSES = {"shell", "filesystem", "git", "network", "model", "browser", "infra", "database", "package", "runtime", "memory", "external", "unknown"}


def die(message: str) -> None:
    print(f"[agent-reliability-governance-queue] ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        die(f"missing file: {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(data, dict):
        die(f"expected JSON object in {path.relative_to(ROOT)}")
    return data


def require_keys(obj: dict[str, Any], keys: list[str], path: str) -> None:
    missing = [key for key in keys if key not in obj]
    if missing:
        die(f"{path} missing keys: {missing}")


def validate_schema_shape(schema: dict[str, Any]) -> None:
    require_keys(schema, ["$schema", "$id", "title", "type", "required", "properties"], "schema")
    for field in ["apiVersion", "kind", "queueId", "createdAt", "owner", "sourceLane", "items"]:
        if field not in schema.get("required", []):
            die(f"schema.required missing {field}")


def validate_item(item: dict[str, Any], seen_ids: set[str], index: int) -> None:
    path = f"items[{index}]"
    require_keys(
        item,
        ["itemId", "itemType", "status", "priority", "title", "summary", "sourceArtifact", "risk", "review", "evidenceRefs", "policyDecisionRefs"],
        path,
    )
    item_id = item["itemId"]
    if item_id in seen_ids:
        die(f"duplicate queue item id: {item_id}")
    seen_ids.add(item_id)
    if item["itemType"] not in VALID_ITEM_TYPES:
        die(f"{path}.itemType unsupported: {item['itemType']}")
    if item["status"] not in VALID_STATUSES:
        die(f"{path}.status unsupported: {item['status']}")
    if item["status"] != "pending":
        die(f"example queue item {item_id} must remain pending by default")
    if item["priority"] not in VALID_PRIORITIES:
        die(f"{path}.priority unsupported: {item['priority']}")

    source = item["sourceArtifact"]
    require_keys(source, ["system", "repo", "artifactKind", "artifactRef"], f"{path}.sourceArtifact")
    if source["system"] not in VALID_SYSTEMS:
        die(f"{path}.sourceArtifact.system unsupported: {source['system']}")
    if source["artifactKind"] not in VALID_ARTIFACT_KINDS:
        die(f"{path}.sourceArtifact.artifactKind unsupported: {source['artifactKind']}")

    risk = item["risk"]
    require_keys(risk, ["severity", "actionClass", "resource", "reason"], f"{path}.risk")
    if risk["severity"] not in VALID_PRIORITIES:
        die(f"{path}.risk.severity unsupported: {risk['severity']}")
    if risk["actionClass"] not in VALID_ACTION_CLASSES:
        die(f"{path}.risk.actionClass unsupported: {risk['actionClass']}")

    review = item["review"]
    require_keys(review, ["required", "reviewerRefs", "approvalRef", "decisionRef"], f"{path}.review")
    if review["required"] is not True:
        die(f"{path}.review.required must be true")
    if review["approvalRef"] is not None:
        die(f"{path}.review.approvalRef must be null for pending example items")
    if review["decisionRef"] is not None:
        die(f"{path}.review.decisionRef must be null for pending example items")
    if not review.get("reviewerRefs"):
        die(f"{path}.review.reviewerRefs must not be empty")

    if not item.get("evidenceRefs"):
        die(f"{path}.evidenceRefs must not be empty")
    if not item.get("policyDecisionRefs"):
        die(f"{path}.policyDecisionRefs must not be empty")

    if item["itemType"] == "break-glass-approval":
        if source["system"] != "policy-fabric" or source["artifactKind"] != "BreakGlassOverride":
            die("break-glass approval items must reference PolicyFabric BreakGlassOverride artifacts")
        if risk["severity"] not in {"high", "critical"}:
            die("break-glass approval items must be high or critical priority")
    if item["itemType"] == "memory-learning-review":
        if source["system"] != "memory-mesh" or source["artifactKind"] != "AgentLearningProposal":
            die("memory learning review items must reference MemoryMesh AgentLearningProposal artifacts")
        if risk["actionClass"] != "memory":
            die("memory learning review items must use actionClass=memory")


def validate_queue(queue: dict[str, Any]) -> None:
    require_keys(queue, ["apiVersion", "kind", "queueId", "createdAt", "owner", "sourceLane", "items"], "queue")
    if queue["apiVersion"] != "sociosphere.governance-queue/v1":
        die("queue apiVersion mismatch")
    if queue["kind"] != "AgentReliabilityGovernanceQueue":
        die("queue kind mismatch")
    if queue["sourceLane"] != "sourceos-agent-reliability-control-plane":
        die("queue sourceLane mismatch")
    items = queue["items"]
    if not isinstance(items, list) or not items:
        die("queue.items must be a non-empty list")
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            die(f"items[{index}] must be an object")
        validate_item(item, seen, index)
    types = {item["itemType"] for item in items}
    if "break-glass-approval" not in types:
        die("example queue must include at least one break-glass-approval item")
    if "memory-learning-review" not in types:
        die("example queue must include at least one memory-learning-review item")


def main() -> int:
    schema = load_json(SCHEMA)
    queue = load_json(EXAMPLE)
    validate_schema_shape(schema)
    validate_queue(queue)
    print("[agent-reliability-governance-queue] OK: queue schema and example validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
