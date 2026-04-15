from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional


class ReadinessState(str, Enum):
    WARMING = "WARMING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class IndexState(str, Enum):
    WARMING = "WARMING"
    READY = "READY"
    DEGRADED = "DEGRADED"


@dataclass(frozen=True)
class MountRef:
    mount_id: str
    backend_type: str
    resolved_path_or_handle: str
    node_ref: str
    rw_mode: str
    fingerprint: str
    capacity_bytes: int
    created_at: str


@dataclass(frozen=True)
class ManifestRef:
    manifest_id: str
    root_hash: str
    entry_count: int
    generation: int
    created_at: str


@dataclass(frozen=True)
class IndexRef:
    index_id: str
    manifest_id: str
    pipeline_version: str
    state: IndexState
    chunk_set_ref: Optional[str] = None
    embedding_set_ref: Optional[str] = None
    keyword_index_ref: Optional[str] = None


@dataclass(frozen=True)
class CapabilityGrant:
    grant_id: str
    principal: str
    mount_ref: str
    rights: list[str]
    network_profile: str
    expires_at: str
    secret_scope_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DistributionRef:
    ref_type: str
    ref_value: str


@dataclass(frozen=True)
class MountRegistrationResponse:
    mount_ref: MountRef
    manifest_ref: ManifestRef
    index_ref: IndexRef
    readiness_state: ReadinessState
    policy_bundle_ref: str
    capability_grants: list[CapabilityGrant]
    distribution_refs: list[DistributionRef] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ConnectorCheckpoint:
    checkpoint_id: str
    connector_id: str
    dataset_ref: str
    cursor_or_marker: str
    last_successful_scan_at: str
    last_applied_change_id: str
    integrity_digest: str
    executor_version: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class EvidenceEvent:
    event_id: str
    event_type: str
    occurred_at: str
    actor_ref: str
    workspace_ref: str
    policy_bundle_ref: str
    correlation_id: str
    dataset_ref: Optional[str] = None
    payload: dict[str, Any] = field(default_factory=dict)
    signature_ref: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
