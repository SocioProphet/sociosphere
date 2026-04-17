from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReconcileDecision:
    action: str
    reason: str
    authoritative_side: str


def decide_reconcile_action(
    *,
    local_dirty: bool,
    remote_delete: bool,
    remote_newer: bool,
    authority_mode: str = "local_first",
    policy_allow_stale: bool = False,
) -> ReconcileDecision:
    if local_dirty and remote_delete:
        return ReconcileDecision(
            action="manual_reconcile",
            reason="local_dirty_remote_delete",
            authoritative_side="none",
        )

    if authority_mode == "local_first":
        if remote_newer and not policy_allow_stale:
            return ReconcileDecision(
                action="manual_reconcile",
                reason="remote_newer_but_local_authority",
                authoritative_side="local",
            )
        return ReconcileDecision(
            action="local_wins",
            reason="local_first_default",
            authoritative_side="local",
        )

    if authority_mode == "provider_first":
        if local_dirty and remote_newer:
            return ReconcileDecision(
                action="manual_reconcile",
                reason="provider_first_with_local_dirty_and_remote_newer",
                authoritative_side="remote",
            )
        return ReconcileDecision(
            action="remote_wins",
            reason="provider_first_default",
            authoritative_side="remote",
        )

    if authority_mode == "hybrid":
        if local_dirty or remote_delete or remote_newer:
            return ReconcileDecision(
                action="manual_reconcile",
                reason="hybrid_requires_explicit_resolution",
                authoritative_side="none",
            )
        return ReconcileDecision(
            action="no_op",
            reason="hybrid_no_change",
            authoritative_side="none",
        )

    return ReconcileDecision(
        action="manual_reconcile",
        reason="unknown_authority_mode",
        authoritative_side="none",
    )
