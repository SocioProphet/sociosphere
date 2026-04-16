from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .events import EventSink
from .mount_agent import MountAgent, MountRequest
from .retrieval_registry import RetrievalRegistry
from .schema_refs import MANIFEST_V1
from .validator import load_schema, validate_instance


class FabricSmokeTest(unittest.TestCase):
    def test_mount_registration_and_event_emission(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            events_path = Path(tmpdir) / "events.ndjson"
            registry = RetrievalRegistry()
            sink = EventSink(events_path)
            agent = MountAgent(registry, sink)
            response = agent.register_mount(
                MountRequest(
                    mount_name="demo",
                    backend_type="topolvm",
                    resolved_path_or_handle="/workspaces/demo/mnt/data",
                    node_ref="node-a",
                    rw_mode="rw",
                    capacity_bytes=1024,
                    workspace_ref="ws/demo",
                    dataset_ref="ds/demo",
                    pipeline_version="v1",
                    policy_bundle_ref="policy/default",
                    principal="tester",
                )
            )
            self.assertEqual(response.mount_ref.backend_type, "topolvm")
            self.assertTrue(events_path.exists())
            lines = events_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            payload = json.loads(lines[0])
            self.assertEqual(payload["event_type"], "mount.ready")

    def test_manifest_schema_validator_basics(self) -> None:
        schema = load_schema(MANIFEST_V1)
        instance = {
            "schema_version": "manifest.v1",
            "manifest_id": "m1",
            "created_at": "2026-04-16T00:00:00Z",
            "dataset_ref": "ds/demo",
            "mount_ref": "mnt/demo",
            "policy_bundle_ref": "policy/default",
            "entries": [],
            "root_hash": "abc"
        }
        errors = validate_instance(instance, schema)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
