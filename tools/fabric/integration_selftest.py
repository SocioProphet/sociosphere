from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .integration_harness import run_mount_and_drive_flow


class IntegrationHarnessSmokeTest(unittest.TestCase):
    def test_mount_and_drive_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_mount_and_drive_flow(Path(tmpdir))
            self.assertIsNotNone(result["mount_registration"])
            self.assertIsNotNone(result["registry_entry"])
            self.assertIsNotNone(result["checkpoint"])
            self.assertGreaterEqual(result["event_count"], 2)
            self.assertEqual(result["checkpoint"]["connector_id"], "drive")
            self.assertEqual(result["registry_entry"]["workspace_ref"], "ws/demo")


if __name__ == "__main__":
    unittest.main()
