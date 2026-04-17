from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .checkpoints import CheckpointStore
from .connectors.base import ConnectorContext
from .connectors.hyper import HyperExecutor
from .events import EventSink
from .mount_agent import MountAgent, MountRequest
from .retrieval_registry import RetrievalRegistry


def run_mount_and_hyper_flow(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    checkpoints = CheckpointStore(root / "checkpoints")
    events = EventSink(root / "events.ndjson")
    registry = RetrievalRegistry()

    agent = MountAgent(registry, events)
    response = agent.register_mount(
        MountRequest(
            mount_name="demo-hyper",
            backend_type="topolvm",
            resolved_path_or_handle="/workspaces/demo/mnt/data",
            node_ref="node-a",
            rw_mode="rw",
            capacity_bytes=4096,
            workspace_ref="ws/demo",
            dataset_ref="ds/demo-hyper",
            pipeline_version="v1",
            policy_bundle_ref="policy/default",
            principal="tester",
        )
    )

    executor = HyperExecutor(
        ConnectorContext(
            connector_id="hyper",
            dataset_ref="ds/demo-hyper",
            policy_bundle_ref="policy/default",
            actor_ref="tester",
            workspace_ref="ws/demo",
        ),
        checkpoints,
        events,
    )
    executor.apply()

    checkpoint = checkpoints.load("hyper", "ds/demo-hyper")
    registration = registry.get("ws/demo", "ds/demo-hyper")
    event_lines = (root / "events.ndjson").read_text(encoding="utf-8").strip().splitlines()

    return {
        "mount_registration": asdict(response),
        "registry_entry": asdict(registration) if registration else None,
        "checkpoint": asdict(checkpoint) if checkpoint else None,
        "event_count": len([line for line in event_lines if line]),
    }
