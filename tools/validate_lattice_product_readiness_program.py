#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "lattice-product-readiness-program.yaml"
REQUIRED_WORK_ORDERS = {
    "work-order-0",
    "work-order-a",
    "work-order-b",
    "work-order-c",
    "work-order-d",
    "work-order-e",
}
REQUIRED_NEXT_SCOPE = {"work-order-0", "work-order-a"}
REQUIRED_PARENT_REGISTRIES = {
    "registry/lattice-data-governai-lanes.yaml",
    "registry/lattice-demo-readiness.yaml",
    "registry/lattice-runtime-release-readiness.yaml",
}


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def as_list(value: Any, field: str) -> list[Any]:
    require(isinstance(value, list) and value, f"{field} must be non-empty list")
    return value


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for product readiness validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeProductReadinessProgramRegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = data.get("umbrella")
        require(isinstance(umbrella, dict), "umbrella must be mapping")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella.repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella.issue mismatch")
        parents = set(as_list(umbrella.get("parent_registries"), "umbrella.parent_registries"))
        require(REQUIRED_PARENT_REGISTRIES <= parents, "parent registries incomplete")

        budget = data.get("turn_budget")
        require(isinstance(budget, dict), "turn_budget must be mapping")
        require(budget.get("estimate_total_turns") == "45-65", "total turn estimate mismatch")
        require(budget.get("phase_0_and_a_turns") == "10-14", "phase turn estimate mismatch")
        as_list(budget.get("assumptions"), "turn_budget.assumptions")

        work_orders = as_list(data.get("work_orders"), "work_orders")
        ids = {item.get("id") for item in work_orders if isinstance(item, dict)}
        require(ids == REQUIRED_WORK_ORDERS, f"work order ids mismatch: {ids}")
        for item in work_orders:
            require(isinstance(item, dict), "work order must be mapping")
            require(isinstance(item.get("priority"), int), f"{item.get('id')}: priority must be int")
            require(item.get("status") in {"approved-for-execution", "planned"}, f"{item.get('id')}: invalid status")
            as_list(item.get("owner_repos"), f"{item.get('id')}.owner_repos")
            as_list(item.get("required_lanes"), f"{item.get('id')}.required_lanes")
            as_list(item.get("acceptance_gates"), f"{item.get('id')}.acceptance_gates")

        approved = {item["id"] for item in work_orders if item.get("status") == "approved-for-execution"}
        require(approved == REQUIRED_NEXT_SCOPE, f"approved scope mismatch: {approved}")

        rules = data.get("execution_rules")
        require(isinstance(rules, dict), "execution_rules must be mapping")
        require(set(as_list(rules.get("next_approved_scope"), "execution_rules.next_approved_scope")) == REQUIRED_NEXT_SCOPE, "next approved scope mismatch")
        for key in [
            "topology_registration_required_after_each_lane",
            "ci_required_before_merge",
            "fixture_before_live_infrastructure",
            "no_parallel_metadata_spines",
            "policy_fabric_required_for_authoritative_actions",
            "agentplane_required_for_execution",
            "slash_topics_public_surface",
            "new_hope_semantic_membrane",
        ]:
            require(rules.get(key) is True, f"execution_rules.{key} must be true")

        validation = data.get("validation_requirements")
        require(isinstance(validation, dict), "validation_requirements must be mapping")
        require(set(as_list(validation.get("required_work_orders"), "validation.required_work_orders")) == REQUIRED_WORK_ORDERS, "required work orders mismatch")
        require(set(as_list(validation.get("required_next_scope"), "validation.required_next_scope")) == REQUIRED_NEXT_SCOPE, "required next scope mismatch")
        for key in [
            "require_turn_budget",
            "require_acceptance_gates",
            "require_owner_repos",
            "require_topology_registration",
            "require_ci_before_merge",
            "forbid_live_execution_without_policy_and_agentplane",
        ]:
            require(validation.get(key) is True, f"validation.{key} must be true")
    except Exception as exc:  # noqa: BLE001
        return fail(str(exc))
    print("OK: validated Lattice product readiness program")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
