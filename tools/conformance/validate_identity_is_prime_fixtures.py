#!/usr/bin/env python3
"""Validate Identity Is Prime / Regis / ACR conformance fixtures.

This validator is intentionally dependency-free. It is the first Sociosphere-side
conformance gate for the fixture skeleton under protocol/identity-is-prime/.
It does not try to reimplement the full Identity Is Prime reference analyzer;
it enforces fixture shape, deterministic result vocabulary, and the core
structural expectations needed before TRIT RPC wire fixtures are added.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "protocol" / "identity-is-prime" / "fixtures"
EXPECTED_DIR = ROOT / "protocol" / "identity-is-prime" / "expected"

RESULTS = {"VERIFIED", "REFUTED", "UNDECIDABLE", "STALE", "REQUIRES_REVIEW"}
REQUIRED_FIXTURES = {
    "polytope.valid.json",
    "polytope.invalid.json",
    "token.non_escape.violation.json",
    "acr.golden_record.proof.json",
    "meshrush.graph_exploration.simulation.json",
    "holmes.case.from_meshrush_trace.json",
    "sherlock.search.from_holmes_meshrush.json",
    "agent.manifest.valid.json",
    "agent.manifest.invalid_missing_policy_scope.json",
    "transition.admissible.json",
    "transition.no_admissible_path.json",
    "zeta.audit.window.json",
}


def fail(path: Path, message: str) -> None:
    raise SystemExit(f"{path}: {message}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(path, f"invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail(path, "top-level JSON value must be an object")
    return data


def require_str(obj: dict[str, Any], key: str, path: Path) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        fail(path, f"{key} must be a non-empty string")
    return value


def require_obj(obj: dict[str, Any], key: str, path: Path) -> dict[str, Any]:
    value = obj.get(key)
    if not isinstance(value, dict):
        fail(path, f"{key} must be an object")
    return value


def require_list(obj: dict[str, Any], key: str, path: Path) -> list[Any]:
    value = obj.get(key)
    if not isinstance(value, list):
        fail(path, f"{key} must be a list")
    return value


def validate_common(path: Path, fixture: dict[str, Any]) -> dict[str, Any]:
    require_str(fixture, "fixture_id", path)
    require_str(fixture, "fixture_version", path)
    require_str(fixture, "schema_version", path)
    require_str(fixture, "policy_version", path)
    require_str(fixture, "description", path)
    expected = require_obj(fixture, "expected", path)
    result = require_str(expected, "result", path)
    if result not in RESULTS:
        fail(path, f"expected.result must be one of {sorted(RESULTS)}")
    return expected


def eval_linear_expr(expr: str, values: dict[str, int]) -> bool:
    if "<=" not in expr:
        raise ValueError("only <= constraints are supported in fixture validator")
    left, right = expr.split("<=", 1)
    rhs = int(right.strip())
    total = 0
    for term in left.split("+"):
        name = term.strip()
        if not name:
            continue
        total += int(values.get(name, 0))
    return total <= rhs


def validate_polytope(path: Path, fixture: dict[str, Any]) -> None:
    expected = validate_common(path, fixture)
    basis = require_obj(fixture, "basis", path)
    primes = require_list(basis, "primes", path)
    scopes = require_list(basis, "scopes", path)
    mixture = require_obj(fixture, "mixture", path)
    prime_values = require_obj(mixture, "primes", path)
    scope_values = require_obj(mixture, "scopes", path)
    constraints = require_list(fixture, "constraints", path)

    values: dict[str, int] = {}
    for name in primes + scopes:
        if not isinstance(name, str):
            fail(path, "basis entries must be strings")
        values[name] = int(prime_values.get(name, scope_values.get(name, 0)))

    violations: list[str] = []
    for constraint in constraints:
        if not isinstance(constraint, dict):
            fail(path, "constraints entries must be objects")
        cid = require_str(constraint, "id", path)
        expr = require_str(constraint, "expr", path)
        try:
            ok = eval_linear_expr(expr, values)
        except Exception as exc:  # noqa: BLE001 - report fixture failure with context.
            fail(path, f"unsupported constraint expression {expr!r}: {exc}")
        if not ok:
            violations.append(cid)

    expected_result = expected["result"]
    if violations and expected_result != "REFUTED":
        fail(path, f"violations {violations} require expected.result REFUTED")
    if not violations and expected_result != "VERIFIED":
        fail(path, "no violations require expected.result VERIFIED")
    if sorted(expected.get("violations", [])) != sorted(violations):
        fail(path, f"expected.violations must be {violations}")


def validate_token_non_escape(path: Path, fixture: dict[str, Any]) -> None:
    expected = validate_common(path, fixture)
    lane = require_obj(fixture, "token_lane", path)
    allowed = set(require_list(lane, "allowed_scopes", path))
    forbidden = set(require_list(lane, "forbidden_scopes", path))
    observations = require_list(fixture, "observations", path)
    observed_forbidden = []
    for obs in observations:
        if not isinstance(obs, dict):
            fail(path, "observations entries must be objects")
        scope = require_str(obs, "scope", path)
        if scope in forbidden or (allowed and scope not in allowed):
            observed_forbidden.append(scope)
    if observed_forbidden and expected["result"] != "REFUTED":
        fail(path, "forbidden token observation requires expected.result REFUTED")
    reason_codes = set(expected.get("reason_codes", []))
    if observed_forbidden and "TOKEN_NON_ESCAPE_VIOLATION" not in reason_codes:
        fail(path, "expected.reason_codes must include TOKEN_NON_ESCAPE_VIOLATION")


def validate_acr(path: Path, fixture: dict[str, Any]) -> None:
    expected = validate_common(path, fixture)
    require_str(fixture, "template_version", path)
    require_str(fixture, "resolver_version", path)
    source_records = require_list(fixture, "source_records", path)
    crosswalk = require_list(fixture, "crosswalk", path)
    golden = require_obj(fixture, "golden_record", path)
    ledger = require_list(fixture, "ledger_pointers", path)
    if not source_records:
        fail(path, "source_records must not be empty")
    if not crosswalk:
        fail(path, "crosswalk must not be empty")
    if not ledger:
        fail(path, "ledger_pointers must not be empty")
    ceid = require_str(golden, "ceid", path)
    for link in crosswalk:
        if not isinstance(link, dict):
            fail(path, "crosswalk entries must be objects")
        if link.get("ceid") != ceid:
            fail(path, "all crosswalk entries must point to golden_record.ceid")
    if expected["result"] != "VERIFIED":
        fail(path, "current ACR golden proof fixture must expect VERIFIED")
    if not expected.get("requires_shared_ledger_pointer"):
        fail(path, "ACR proof fixture must require shared ledger pointer")


def validate_meshrush(path: Path, fixture: dict[str, Any]) -> None:
    expected = validate_common(path, fixture)
    require_str(fixture, "simulation_version", path)
    graph_view = require_obj(fixture, "graph_view", path)
    simulation = require_obj(fixture, "simulation", path)
    nodes = require_list(graph_view, "nodes", path)
    edges = require_list(graph_view, "edges", path)
    entry_nodes = set(require_list(simulation, "entry_nodes", path))
    stop_conditions = require_list(simulation, "stop_conditions", path)
    if not nodes:
        fail(path, "graph_view.nodes must not be empty")
    if not edges:
        fail(path, "graph_view.edges must not be empty")
    node_ids = {node.get("id") for node in nodes if isinstance(node, dict)}
    if not entry_nodes.issubset(node_ids):
        fail(path, "simulation.entry_nodes must all exist in graph_view.nodes")
    if not stop_conditions:
        fail(path, "simulation.stop_conditions must not be empty")
    blocked_edges = []
    for edge in edges:
        if not isinstance(edge, dict):
            fail(path, "graph_view.edges entries must be objects")
        edge_from = require_str(edge, "from", path)
        edge_to = require_str(edge, "to", path)
        if edge_from not in node_ids or edge_to not in node_ids:
            fail(path, "edge endpoints must exist in graph_view.nodes")
        if edge.get("admissible") is False:
            blocked_edges.append(f"{edge_from}->{edge_to}")
    if expected["result"] != "VERIFIED":
        fail(path, "current MeshRush simulation fixture must expect VERIFIED")
    if sorted(expected.get("blocked_edges", [])) != sorted(blocked_edges):
        fail(path, f"expected.blocked_edges must be {blocked_edges}")
    reason_codes = set(expected.get("reason_codes", []))
    if blocked_edges and "FORBIDDEN_EDGE_BLOCKED" not in reason_codes:
        fail(path, "MeshRush fixture with blocked edges must include FORBIDDEN_EDGE_BLOCKED")


def validate_transition(path: Path, fixture: dict[str, Any]) -> None:
    expected = validate_common(path, fixture)
    graph = require_obj(fixture, "transition_graph", path)
    claim = require_obj(fixture, "claim", path)
    nodes = require_list(graph, "nodes", path)
    edges = require_list(graph, "edges", path)
    if not nodes:
        fail(path, "transition_graph.nodes must not be empty")
    if not edges:
        fail(path, "transition_graph.edges must not be empty")
    node_ids = {node.get("id") for node in nodes if isinstance(node, dict)}
    claim_from = require_str(claim, "from", path)
    claim_to = require_str(claim, "to", path)
    if claim_from not in node_ids or claim_to not in node_ids:
        fail(path, "claim endpoints must exist in transition_graph.nodes")
    admissible_edges = []
    blocked_edges = []
    total_cost = 0.0
    for edge in edges:
        if not isinstance(edge, dict):
            fail(path, "transition_graph.edges entries must be objects")
        edge_from = require_str(edge, "from", path)
        edge_to = require_str(edge, "to", path)
        if edge_from not in node_ids or edge_to not in node_ids:
            fail(path, "transition edge endpoints must exist in transition_graph.nodes")
        if edge.get("admissible") is True:
            admissible_edges.append(f"{edge_from}->{edge_to}")
            total_cost += float(edge.get("cost", 0.0))
        elif edge.get("admissible") is False:
            blocked_edges.append(f"{edge_from}->{edge_to}")
    expected_result = expected["result"]
    if expected_result == "VERIFIED":
        expected_path = require_list(expected, "path", path)
        if expected_path != [claim_from, claim_to]:
            fail(path, "verified transition expected.path must match claim endpoints")
        if f"{claim_from}->{claim_to}" not in admissible_edges:
            fail(path, "verified transition requires an admissible claim edge")
        if float(expected.get("total_cost", -1.0)) != total_cost:
            fail(path, f"expected.total_cost must be {total_cost}")
    elif expected_result == "REFUTED":
        if f"{claim_from}->{claim_to}" not in blocked_edges:
            fail(path, "refuted transition requires a blocked claim edge")
        if sorted(expected.get("blocked_edges", [])) != sorted(blocked_edges):
            fail(path, f"expected.blocked_edges must be {blocked_edges}")
        reason_codes = set(expected.get("reason_codes", []))
        if "NO_ADMISSIBLE_PATH" not in reason_codes:
            fail(path, "refuted transition must include NO_ADMISSIBLE_PATH")
    else:
        fail(path, "transition fixture must expect VERIFIED or REFUTED")


def validate_zeta(path: Path, fixture: dict[str, Any]) -> None:
    expected = validate_common(path, fixture)
    require_str(fixture, "metric_version", path)
    audit_window = require_obj(fixture, "audit_window", path)
    require_str(audit_window, "audit_window_id", path)
    require_str(audit_window, "window_start", path)
    require_str(audit_window, "window_end", path)
    counts = require_list(audit_window, "counts", path)
    forbidden_states = set(require_list(audit_window, "forbidden_states", path))
    parameters = require_obj(audit_window, "parameters", path)
    if not counts:
        fail(path, "zeta audit counts must not be empty")
    threshold = int(parameters.get("forbidden_count_threshold", 0))
    near_threshold = int(parameters.get("near_forbidden_distance_threshold", 1))
    forbidden_observed = []
    near_forbidden_pressure = False
    for item in counts:
        if not isinstance(item, dict):
            fail(path, "zeta counts entries must be objects")
        state_id = require_str(item, "state_id", path)
        count = int(item.get("count", 0))
        distance = int(item.get("distance_to_forbidden", 999))
        if state_id in forbidden_states and count > threshold:
            forbidden_observed.append(state_id)
        if distance <= near_threshold and count > threshold:
            near_forbidden_pressure = True
    flags = set(expected.get("flags", []))
    if forbidden_observed:
        if expected["result"] != "REFUTED":
            fail(path, "forbidden zeta observations require expected.result REFUTED")
        if "FORBIDDEN_STATE_OBSERVED" not in flags:
            fail(path, "zeta expected.flags must include FORBIDDEN_STATE_OBSERVED")
    if near_forbidden_pressure and "NEAR_FORBIDDEN_PRESSURE" not in flags:
        fail(path, "zeta expected.flags must include NEAR_FORBIDDEN_PRESSURE")
    if sorted(expected.get("forbidden_observations", [])) != sorted(forbidden_observed):
        fail(path, f"zeta expected.forbidden_observations must be {forbidden_observed}")
    if not expected.get("requires_metric_version"):
        fail(path, "zeta expected.requires_metric_version must be true")


def validate_holmes(path: Path, fixture: dict[str, Any]) -> None:
    expected = validate_common(path, fixture)
    require_str(fixture, "case_model_version", path)
    input_trace = require_obj(fixture, "input_trace", path)
    case = require_obj(fixture, "case", path)
    require_str(input_trace, "trace_id", path)
    if input_trace.get("artifact_type") != "MeshRushSimulationTrace":
        fail(path, "Holmes fixture input_trace.artifact_type must be MeshRushSimulationTrace")
    findings = require_list(case, "findings", path)
    if not findings:
        fail(path, "Holmes case.findings must not be empty")
    for finding in findings:
        if not isinstance(finding, dict):
            fail(path, "Holmes findings entries must be objects")
        for key in ("regis_graph_pointers", "ledger_pointers", "certificate_pointers", "trace_pointers"):
            if not require_list(finding, key, path):
                fail(path, f"Holmes finding {key} must not be empty")
    if expected["result"] != "VERIFIED":
        fail(path, "current Holmes fixture must expect VERIFIED")
    for key in ("requires_trace_pointer", "requires_ledger_pointer", "requires_certificate_pointer"):
        if not expected.get(key):
            fail(path, f"Holmes expected.{key} must be true")


def validate_sherlock(path: Path, fixture: dict[str, Any]) -> None:
    expected = validate_common(path, fixture)
    require_str(fixture, "index_version", path)
    index_record = require_obj(fixture, "index_record", path)
    require_obj(fixture, "query", path)
    results = require_list(fixture, "results", path)
    indexed = require_list(index_record, "indexed_artifacts", path)
    if not indexed:
        fail(path, "Sherlock index_record.indexed_artifacts must not be empty")
    if index_record.get("claims_canonical_truth") is not False:
        fail(path, "Sherlock index_record must not claim canonical truth")
    if not results:
        fail(path, "Sherlock results must not be empty")
    for result in results:
        if not isinstance(result, dict):
            fail(path, "Sherlock result entries must be objects")
        if result.get("claims_canonical_truth") is not False:
            fail(path, "Sherlock results must not claim canonical truth")
        pointers = require_obj(result, "pointers", path)
        required_pointer_keys = {"holmes_case", "meshrush_trace", "regis_graph", "ledger", "certificate"}
        missing = sorted(required_pointer_keys - set(pointers))
        if missing:
            fail(path, f"Sherlock result pointers missing: {missing}")
    if expected["result"] != "VERIFIED":
        fail(path, "current Sherlock fixture must expect VERIFIED")
    if not expected.get("requires_pointer_backing"):
        fail(path, "Sherlock expected.requires_pointer_backing must be true")
    if not expected.get("forbids_direct_canonical_truth_claim"):
        fail(path, "Sherlock expected.forbids_direct_canonical_truth_claim must be true")


def validate_agent_manifest(path: Path, fixture: dict[str, Any]) -> None:
    expected = validate_common(path, fixture)
    agent = require_obj(fixture, "agent", path)
    require_str(agent, "agent_id", path)
    require_str(agent, "version", path)
    inputs = require_list(agent, "inputs", path)
    outputs = require_list(agent, "outputs", path)
    policy_scopes = require_list(agent, "policy_scopes", path)
    graph_permissions = require_list(agent, "graph_permissions", path)
    search_permissions = require_list(agent, "search_permissions", path)
    evidence_outputs = require_list(agent, "evidence_outputs", path)
    tritrpc_services = require_list(agent, "tritrpc_services", path)
    cannot_write = set(require_list(agent, "cannot_write", path))
    violations = []
    if not inputs:
        violations.append("MISSING_INPUTS")
    if not outputs:
        violations.append("MISSING_OUTPUTS")
    if not policy_scopes:
        violations.append("MISSING_POLICY_SCOPE")
    if not graph_permissions:
        violations.append("MISSING_GRAPH_PERMISSION")
    if not search_permissions:
        violations.append("MISSING_SEARCH_PERMISSION")
    if not evidence_outputs:
        violations.append("MISSING_EVIDENCE_OUTPUT")
    if not tritrpc_services:
        violations.append("MISSING_TRITRPC_SERVICE")
    forbidden_writes = {"canonical_entity_truth", "regis_graph_truth_without_policy_reducer"}
    if not forbidden_writes.intersection(cannot_write):
        violations.append("MISSING_CANONICAL_TRUTH_WRITE_GUARD")
    expected_violations = sorted(expected.get("violations", []))
    if violations:
        if expected["result"] != "REFUTED":
            fail(path, f"agent manifest violations {violations} require expected.result REFUTED")
        if sorted(violations) != expected_violations:
            fail(path, f"expected.violations must be {violations}")
    else:
        if expected["result"] != "VERIFIED":
            fail(path, "valid agent manifest must expect VERIFIED")
        for key in (
            "requires_policy_scope",
            "requires_graph_permission",
            "requires_search_permission",
            "forbids_direct_canonical_truth_write",
        ):
            if not expected.get(key):
                fail(path, f"agent expected.{key} must be true")


def validate_expected_files() -> None:
    path = EXPECTED_DIR / "polytope.valid.result.json"
    expected = load_json(path)
    if expected.get("result") != "VERIFIED":
        fail(path, "polytope valid expected result must be VERIFIED")
    for key in ("fixture_id", "policy_version", "schema_version"):
        require_str(expected, key, path)


def main() -> None:
    missing = sorted(name for name in REQUIRED_FIXTURES if not (FIXTURE_DIR / name).exists())
    if missing:
        raise SystemExit(f"missing required Identity Is Prime fixtures: {missing}")

    for name in sorted(REQUIRED_FIXTURES):
        path = FIXTURE_DIR / name
        fixture = load_json(path)
        if name.startswith("polytope."):
            validate_polytope(path, fixture)
        elif name.startswith("token."):
            validate_token_non_escape(path, fixture)
        elif name.startswith("acr."):
            validate_acr(path, fixture)
        elif name.startswith("meshrush."):
            validate_meshrush(path, fixture)
        elif name.startswith("transition."):
            validate_transition(path, fixture)
        elif name.startswith("zeta."):
            validate_zeta(path, fixture)
        elif name.startswith("holmes."):
            validate_holmes(path, fixture)
        elif name.startswith("sherlock."):
            validate_sherlock(path, fixture)
        elif name.startswith("agent."):
            validate_agent_manifest(path, fixture)
        else:
            fail(path, "no validator registered for fixture family")

    validate_expected_files()
    print("OK: identity-is-prime conformance fixtures validated")


if __name__ == "__main__":
    main()
