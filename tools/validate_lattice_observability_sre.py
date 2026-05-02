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
REGISTRY = ROOT / "registry" / "lattice-observability-sre.yaml"
REQUIRED_SCOPE = {"control-plane-site", "release-store", "artifact-cache", "proof-store", "system-plane", "lifecycle-plane", "user-plane", "agent-plane", "shell-plane", "policy-fabric", "search-topic-membrane-path"}
REQUIRED_LOG_FIELDS = {"timestamp", "service", "environment", "tenant_or_workspace_ref", "actor_ref", "request_id", "release_set_ref", "policy_decision_ref", "severity"}
REQUIRED_METRICS = {"availability", "latency", "error_rate", "policy_decision_latency", "build_duration", "artifact_cache_hit_rate", "notebook_launch_latency", "agent_execution_duration", "release_deploy_duration", "rollback_duration"}
REQUIRED_SPANS = {"enrollment", "build-request", "release-set-build", "policy-decision", "artifact-fetch", "notebook-launch", "agent-execution", "replay-evidence-generation", "compliance-check", "rollback"}
REQUIRED_RECEIPTS = {"health-receipt", "policy-decision-receipt", "release-receipt", "deployment-receipt", "rollback-receipt", "incident-receipt", "compliance-receipt", "evidence-bundle-receipt"}
REQUIRED_HEALTH = {"control-plane-api-health", "release-store-health", "artifact-cache-health", "proof-store-health", "policy-fabric-health", "agentplane-health", "shell-command-surface-health", "notebook-launch-health", "topology-validator-health"}
REQUIRED_STATUSES = {"healthy", "degraded", "unhealthy", "unknown"}
REQUIRED_ALERTS = {"policy-fabric-unavailable", "agentplane-execution-failure-spike", "release-store-unavailable", "artifact-cache-integrity-failure", "proof-store-write-failure", "topology-validation-failure", "high-risk-execution-without-required-isolation", "secret-door-access-denied-spike", "rollback-receipt-missing"}
REQUIRED_RUNBOOKS = {"policy-fabric-degraded", "agentplane-execution-degraded", "release-build-failure", "artifact-cache-integrity-failure", "notebook-launch-failure", "rollback-failure", "security-incident", "topology-drift"}
REQUIRED_RUNBOOK_SECTIONS = {"symptoms", "impact", "immediate-containment", "diagnostic-commands", "evidence-to-capture", "rollback-or-repair", "post-incident-review"}
REQUIRED_LOOPS = {"release-health-loop", "execution-health-loop", "policy-health-loop", "topology-health-loop"}
REQUIRED_INCIDENT_SEQUENCE = ["detected", "triaged", "contained", "remediated", "reviewed", "closed"]
REQUIRED_INCIDENT_ARTIFACTS = {"incident-receipt", "timeline", "impacted-assets", "policy-impact-receipt", "runtime-impact-receipt", "tenant-impact-receipt", "post-incident-review"}


def fail(message: str) -> int:
    print(f"ERR: {message}", file=sys.stderr)
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def as_list(value: Any, field: str) -> list[Any]:
    require(isinstance(value, list) and value, f"{field} must be non-empty list")
    return value


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{field} must be mapping")
    return value


def require_set_contains(value: Any, required: set[str], field: str) -> None:
    actual = set(as_list(value, field))
    missing = sorted(required - actual)
    require(not missing, f"{field} missing {missing}")


def main() -> int:
    if yaml is None:
        return fail("PyYAML is required for observability SRE validation")
    if not REGISTRY.exists():
        return fail(f"missing {REGISTRY}")
    try:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        require(isinstance(data, dict), "registry must be mapping")
        require(data.get("kind") == "LatticeObservabilitySRERegistration", "kind mismatch")
        require(data.get("version") == "0.1.0", "version mismatch")
        umbrella = require_mapping(data.get("umbrella"), "umbrella")
        require(umbrella.get("repo") == "SocioProphet/prophet-platform", "umbrella repo mismatch")
        require(umbrella.get("issue") == 291, "umbrella issue mismatch")
        require(umbrella.get("work_order") == "work-order-0", "work order mismatch")
        require(umbrella.get("security_isolation_ref") == "registry/lattice-security-isolation-model.yaml", "security isolation ref mismatch")

        scope = require_mapping(data.get("observability_scope"), "observability_scope")
        require_set_contains(scope.get("applies_to"), REQUIRED_SCOPE, "observability_scope.applies_to")

        signals = require_mapping(data.get("signals"), "signals")
        logs = require_mapping(signals.get("logs"), "signals.logs")
        require(logs.get("required") is True, "logs.required must be true")
        require_set_contains(logs.get("minimum_fields"), REQUIRED_LOG_FIELDS, "logs.minimum_fields")
        metrics = require_mapping(signals.get("metrics"), "signals.metrics")
        require(metrics.get("required") is True, "metrics.required must be true")
        require_set_contains(metrics.get("minimum_metric_families"), REQUIRED_METRICS, "metrics.minimum_metric_families")
        traces = require_mapping(signals.get("traces"), "signals.traces")
        require(traces.get("required") is True, "traces.required must be true")
        require_set_contains(traces.get("required_spans"), REQUIRED_SPANS, "traces.required_spans")
        receipts = require_mapping(signals.get("receipts"), "signals.receipts")
        require(receipts.get("required") is True, "receipts.required must be true")
        require_set_contains(receipts.get("required_receipt_kinds"), REQUIRED_RECEIPTS, "receipts.required_receipt_kinds")

        health = require_mapping(data.get("health_checks"), "health_checks")
        require_set_contains(health.get("required_checks"), REQUIRED_HEALTH, "health_checks.required_checks")
        require(set(as_list(health.get("required_statuses"), "health_checks.required_statuses")) == REQUIRED_STATUSES, "health statuses mismatch")

        slos = require_mapping(data.get("slos"), "slos")
        for key in ["release_set_build", "notebook_launch", "policy_decision", "rollback"]:
            item = require_mapping(slos.get(key), f"slos.{key}")
            for required_field in ["objective", "signal", "burn_action"]:
                require(required_field in item, f"slos.{key} missing {required_field}")

        alerts = require_mapping(data.get("alerts"), "alerts")
        require_set_contains(alerts.get("required_alerts"), REQUIRED_ALERTS, "alerts.required_alerts")
        require_set_contains(alerts.get("notification_routes"), {"operator-console", "incident-queue", "audit-log"}, "alerts.notification_routes")

        runbooks = require_mapping(data.get("runbooks"), "runbooks")
        require_set_contains(runbooks.get("required_runbooks"), REQUIRED_RUNBOOKS, "runbooks.required_runbooks")
        require_set_contains(runbooks.get("required_sections"), REQUIRED_RUNBOOK_SECTIONS, "runbooks.required_sections")

        loops = as_list(data.get("control_loops"), "control_loops")
        loop_ids = {loop.get("id") for loop in loops if isinstance(loop, dict)}
        require(loop_ids == REQUIRED_LOOPS, f"control loop ids mismatch {loop_ids}")
        for loop in loops:
            require_mapping(loop, "control loop")
            as_list(loop.get("observes"), f"control_loop.{loop.get('id')}.observes")
            as_list(loop.get("decides"), f"control_loop.{loop.get('id')}.decides")
            as_list(loop.get("acts"), f"control_loop.{loop.get('id')}.acts")
        policy_loop = next(loop for loop in loops if loop.get("id") == "policy-health-loop")
        require("block-policy-bypass" in policy_loop.get("acts", []), "policy loop must block policy bypass")
        execution_loop = next(loop for loop in loops if loop.get("id") == "execution-health-loop")
        require("raise-isolation-profile" in execution_loop.get("acts", []), "execution loop must raise isolation profile")
        topology_loop = next(loop for loop in loops if loop.get("id") == "topology-health-loop")
        require("block-merge" in topology_loop.get("acts", []), "topology loop must block merge")

        incident = require_mapping(data.get("incident_model"), "incident_model")
        require(set(as_list(incident.get("severity_levels"), "incident.severity_levels")) == {"sev0", "sev1", "sev2", "sev3", "sev4"}, "incident severities mismatch")
        require(as_list(incident.get("required_state_sequence"), "incident.required_state_sequence") == REQUIRED_INCIDENT_SEQUENCE, "incident sequence mismatch")
        require_set_contains(incident.get("required_artifacts"), REQUIRED_INCIDENT_ARTIFACTS, "incident.required_artifacts")

        validation = require_mapping(data.get("validation_requirements"), "validation_requirements")
        for key in [
            "require_observability_scope",
            "require_logs_metrics_traces_receipts",
            "require_health_checks",
            "require_slos",
            "require_alerts",
            "require_runbooks",
            "require_control_loops",
            "require_incident_model",
            "require_policy_health_loop",
            "require_execution_health_loop",
            "require_topology_health_loop",
        ]:
            require(validation.get(key) is True, f"validation {key} must be true")
    except Exception as exc:
        return fail(str(exc))
    print("OK: validated Lattice observability SRE model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
