from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .cli import cmd_run_harness


class CliHarnessSmokeTest(unittest.TestCase):
    def test_run_harness_drive(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rc = cmd_run_harness(argparse.Namespace(connector="drive", root=tmpdir))
            self.assertEqual(rc, 0)
            self.assertTrue((Path(tmpdir) / "events.ndjson").exists())

    def test_run_harness_s3(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rc = cmd_run_harness(argparse.Namespace(connector="s3", root=tmpdir))
            self.assertEqual(rc, 0)
            self.assertTrue((Path(tmpdir) / "events.ndjson").exists())

    def test_run_harness_hyper(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            rc = cmd_run_harness(argparse.Namespace(connector="hyper", root=tmpdir))
            self.assertEqual(rc, 0)
            self.assertTrue((Path(tmpdir) / "events.ndjson").exists())


if __name__ == "__main__":
    unittest.main()
