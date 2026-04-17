from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .cli import cmd_run_authority_flow, cmd_run_tombstone_flow


class CliReconcileFlowSmokeTest(unittest.TestCase):
    def test_run_tombstone_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rc = cmd_run_tombstone_flow(
                argparse.Namespace(
                    root=tmpdir,
                    signed_tombstone=True,
                    local_dirty=False,
                    authority_mode="provider_first",
                )
            )
            self.assertEqual(rc, 0)
            self.assertTrue((Path(tmpdir) / "events.ndjson").exists())

    def test_run_authority_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rc = cmd_run_authority_flow(
                argparse.Namespace(
                    root=tmpdir,
                    current_authority="local",
                    requested_authority="remote",
                    quorum_granted=True,
                )
            )
            self.assertEqual(rc, 0)
            self.assertTrue((Path(tmpdir) / "events.ndjson").exists())


if __name__ == "__main__":
    unittest.main()
