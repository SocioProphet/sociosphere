from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .cli import cmd_run_harness


class CliHarnessSmokeTest(unittest.TestCase):
    def test_run_harness_for_drive_s3_and_hyper(self) -> None:
        connectors = ["drive", "s3", "hyper"]
        with tempfile.TemporaryDirectory() as tmpdir:
            for idx, connector in enumerate(connectors):
                root = Path(tmpdir) / f"case-{idx}"
                rc = cmd_run_harness(argparse.Namespace(connector=connector, root=str(root)))
                self.assertEqual(rc, 0)
                self.assertTrue((root / "events.ndjson").exists())


if __name__ == "__main__":
    unittest.main()
