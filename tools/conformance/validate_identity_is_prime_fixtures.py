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
    # Minimal evaluator for fixtures shaped as: "a + b + c <= N".
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
        else:
            fail(path, "no validator registered for fixture family")

    validate_expected_files()
    print("OK: identity-is-prime conformance fixtures validated")


if __name__ == "__main__":
    main()
