from __future__ import annotations

from pathlib import Path
from typing import Any

from .reconcile import (
    decide_authority_transition,
    decide_stale_mirror_action,
    decide_tombstone_action,
)
from .reconcile_flow_harness import run_authority_transition_flow, run_tombstone_propagation_flow
from .stale_mirror_flow_harness import run_stale_mirror_flow


def run_reconcile_matrix(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)

    tombstone = run_tombstone_propagation_flow(
        root / "tombstone",
        signed_tombstone=True,
        local_dirty=False,
        authority_mode="provider_first",
    )
    stale = run_stale_mirror_flow(
        root / "stale",
        stale_generation_gap=3,
        policy_allow_stale=True,
        authority_mode="local_first",
    )
    authority = run_authority_transition_flow(
        root / "authority",
        current_authority="local",
        requested_authority="remote",
        quorum_granted=True,
    )

    direct_decisions = {
        "tombstone": decide_tombstone_action(
            signed_tombstone=True,
            local_dirty=False,
            authority_mode="provider_first",
        ).__dict__,
        "stale_mirror": decide_stale_mirror_action(
            stale_generation_gap=3,
            policy_allow_stale=True,
            authority_mode="local_first",
        ).__dict__,
        "authority_transition": decide_authority_transition(
            current_authority="local",
            requested_authority="remote",
            quorum_granted=True,
        ).__dict__,
    }

    return {
        "tombstone": tombstone,
        "stale_mirror": stale,
        "authority_transition": authority,
        "direct_decisions": direct_decisions,
    }
