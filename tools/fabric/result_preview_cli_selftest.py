from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .result_preview_cli import cmd_show_result_preview


class ResultPreviewCliSmokeTest(unittest.TestCase):
    def test_show_result_preview(self) -> None:
        cases = [
            argparse.Namespace(
                kind="stale_mirror",
                root=None,
                stale_generation_gap=3,
                policy_allow_stale=True,
                signed_tombstone=False,
                local_dirty=False,
                authority_mode="local_first",
                current_authority="local",
                requested_authority="remote",
                quorum_granted=False,
            ),
            argparse.Namespace(
                kind="tombstone",
                root=None,
                stale_generation_gap=3,
                policy_allow_stale=False,
                signed_tombstone=True,
                local_dirty=False,
                authority_mode="provider_first",
                current_authority="local",
                requested_authority="remote",
                quorum_granted=False,
            ),
            argparse.Namespace(
                kind="authority_transition",
                root=None,
                stale_generation_gap=3,
                policy_allow_stale=False,
                signed_tombstone=False,
                local_dirty=False,
                authority_mode="local_first",
                current_authority="local",
                requested_authority="remote",
                quorum_granted=True,
            ),
            argparse.Namespace(
                kind="reconcile_matrix",
                root=None,
                stale_generation_gap=3,
                policy_allow_stale=True,
                signed_tombstone=True,
                local_dirty=False,
                authority_mode="provider_first",
                current_authority="local",
                requested_authority="remote",
                quorum_granted=True,
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            for idx, ns in enumerate(cases):
                ns.root = str(Path(tmpdir) / f"case-{idx}")
                rc = cmd_show_result_preview(ns)
                self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
