from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .cli import cmd_run_stale_mirror_flow


class CliStaleMirrorFlowSmokeTest(unittest.TestCase):
    def test_run_stale_mirror_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rc = cmd_run_stale_mirror_flow(
                argparse.Namespace(
                    root=tmpdir,
                    stale_generation_gap=3,
                    policy_allow_stale=False,
                    authority_mode="local_first",
                )
            )
            self.assertEqual(rc, 0)
            self.assertTrue((Path(tmpdir) / "events.ndjson").exists())


if __name__ == "__main__":
    unittest.main()
