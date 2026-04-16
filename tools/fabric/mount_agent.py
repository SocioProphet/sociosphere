from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from .events import EventSink
from .retrieval_registry import RetrievalRegistry
from .types import (
    CapabilityGrant,
    EvidenceEvent,
    IndexRef,
    IndexState,
    ManifestRef,
    MountRef,
    MountRegistrationResponse,
    ReadinessState,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class MountRequest:
    mount_name: str
    backend_type: str
    resolved_path_or_handle: str
    node_ref: str
    rw_mode: str
    capacity_bytes: int
    workspace_ref: str
    dataset_ref: str
    pipeline_version: str
    policy_bundle_ref: str
    principal: str


class MountAgent:
    def __init__(self, registry: RetrievalRegistry, events: EventSink) -> None:
        self.registry = registry
        self.events = events

    def register_mount(self, request: MountRequest) -> MountRegistrationResponse:
        now = _now()
        fingerprint = _digest(f"{request.backend_type}:{request.resolved_path_or_handle}")
        mount_ref = MountRef(
            mount_id=f"mnt_{_digest(request.mount_name)[:12]}",
            backend_type=request.backend_type,
            resolved_path_or_handle=request.resolved_path_or_handle,
            node_ref=request.node_ref,
            rw_mode=request.rw_mode,
            fingerprint=fingerprint,
            capacity_bytes=request.capacity_bytes,
            created_at=now,
        )
        manifest_ref = ManifestRef(
            manifest_id=f"manifest_{_digest(request.resolved_path_or_handle + now)}",
            root_hash=_digest(request.resolved_path_or_handle),
            entry_count=0,
            generation=1,
            created_at=now,
        )
        index_ref = IndexRef(
            index_id=f"idx_{_digest(request.dataset_ref + request.pipeline_version)[:12]}",
            manifest_id=manifest_ref.manifest_id,
            pipeline_version=request.pipeline_version,
            state=IndexState.WARMING,
        )
        grant = CapabilityGrant(
            grant_id=f"grant_{_digest(request.principal + request.mount_name)[:12]}",
            principal=request.principal,
            mount_ref=mount_ref.mount_id,
            rights=["l", "r"],
            network_profile="network.none",
            expires_at=now,
        )
        self.registry.register(
            workspace_ref=request.workspace_ref,
            dataset_ref=request.dataset_ref,
            visibility="partial",
            index_ref=index_ref,
        )
        self.events.emit(
            EvidenceEvent(
                event_id=f"evt_{_digest(mount_ref.mount_id + now)[:16]}",
                event_type="mount.ready",
                occurred_at=now,
                actor_ref=request.principal,
                workspace_ref=request.workspace_ref,
                dataset_ref=request.dataset_ref,
                policy_bundle_ref=request.policy_bundle_ref,
                correlation_id=mount_ref.mount_id,
                payload={
                    "mount_id": mount_ref.mount_id,
                    "manifest_id": manifest_ref.manifest_id,
                    "index_id": index_ref.index_id,
                },
            )
        )
        return MountRegistrationResponse(
            mount_ref=mount_ref,
            manifest_ref=manifest_ref,
            index_ref=index_ref,
            readiness_state=ReadinessState.WARMING,
            policy_bundle_ref=request.policy_bundle_ref,
            capability_grants=[grant],
        )
