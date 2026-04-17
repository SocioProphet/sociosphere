from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .checkpoints import CheckpointStore
from .connectors.base import ConnectorContext
from .connectors.s3 import S3Executor
from .events import EventSink
from .mount_agent import MountAgent, MountRequest
from .retrieval_registry import RetrievalRegistry


def run_mount_and_s3_flow(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    checkpoints = CheckpointStore(root / "checkpoints")
    events = EventSink(root / "events.ndjson")
    registry = RetrievalRegistry()

    agent = MountAgent(registry, events)
    response = agent.register_mount(
        MountRequest(
            mount_name="demo-s3",
            backend_type="topolvm",
            resolved_path_or_handle="/workspaces/demo/mnt/data",
            node_ref="node-a",
            rw_mode="rw",
            capacity_bytes=2048,
            workspace_ref="ws/demo",
            dataset_ref="ds/demo-s3",
            pipeline_version="v1",
            policy_bundle_ref="policy/default",
            principal="tester",
        )
    )

    executor = S3Executor(
        ConnectorContext(
            connector_id="s3",
            dataset_ref="ds/demo-s3",
            policy_bundle_ref="policy/default",
            actor_ref="tester",
            workspace_ref="ws/demo",
        ),
        checkpoints,
        events,
    )
    executor.apply()

    checkpoint = checkpoints.load("s3", "ds/demo-s3")
    registration = registry.get("ws/demo", "ds/demo-s3")
    event_lines = (root / "events.ndjson").read_text(encoding="utf-8").strip().splitlines()

    return {
        "mount_registration": asdict(response),
        "registry_entry": asdict(registration) if registration else None,
        "checkpoint": asdict(checkpoint) if checkpoint else None,
        "event_count": len([line for line in event_lines if line]),
    }
