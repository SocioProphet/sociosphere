#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_NON_CLAIMS = {
    "no_runtime_receipt_lookup",
    "no_runtime_non_claim_verification",
    "no_runtime_monitor_attestation",
    "no_timestamp_authenticity",
    "opaque_hashes_not_resolved",
    "no_runtime_authority_resolution",
    "no_runtime_cancellation_propagation",
    "no_estate_topology_verification",
    "no_authority_chain_traversal",
    "no_cross_plane_runtime_attestation",
}

FORBIDDEN_RUNTIME_OR_FULL_COMPOSITION_FIELDS = {
    "receipt_integration",
    "authority_scope_analysis",
    "non_claim_analysis",
    "monitor_independence_analysis",
    "evidence_freshness_analysis",
    "evidence_receipt_refs",
    "constituent_authority_chain_refs",
    "composition_authority_chain_ref",
    "composition_rule",
    "composed_authority_scope",
    "execution_status",
    "ledger_entry",
    "runtime_receipt_lookup",
    "resolved_at",
    "monitor_attestation_token",
    "timestamp_authenticity_proof",
    "runtime_authority_resolution",
    "runtime_cancellation_propagation",
    "estate_topology_verification",
    "authority_chain_traversal",
    "cross_plane_runtime_attestation",
    "resolved_authority_edges",
    "propagated_cancellation_effects",
    "verified_plane_owners",
    "traversed_authority_chains",
}

MULTI_REF_FIELDS = (
    "authority_dependency_refs",
    "control_effect_refs",
    "cancellation_binding_refs",
    "plane_owner_refs",
)


def _check_hash_ref(ref: dict, label: str) -> tuple[bool, str]:
    opaque_hash = ref.get("opaque_hash", "")
    if not opaque_hash.startswith("sha256:"):
        return False, f"{label}.opaque_hash must use sha256: prefix"
    return True, ""


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_sociosphere_authority_dependency_tier2_binding.py <fixture.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))

    non_claims = set(data.get("non_claims", []))
    if non_claims != REQUIRED_NON_CLAIMS:
        missing = sorted(REQUIRED_NON_CLAIMS - non_claims)
        extra = sorted(non_claims - REQUIRED_NON_CLAIMS)
        print(
            f"non_claims must exactly match required SocioSphere doctrine boundary; missing={missing} extra={extra}",
            file=sys.stderr,
        )
        return 1

    forbidden_present = sorted(FORBIDDEN_RUNTIME_OR_FULL_COMPOSITION_FIELDS & set(data))
    if forbidden_present:
        print(
            "SocioSphere authority-dependency Tier 2 binding must remain doctrine-only; forbidden fields present: "
            + ", ".join(forbidden_present),
            file=sys.stderr,
        )
        return 1

    for field in MULTI_REF_FIELDS:
        for idx, ref in enumerate(data.get(field, [])):
            ok, message = _check_hash_ref(ref, f"{field}[{idx}]")
            if not ok:
                print(message, file=sys.stderr)
                return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
