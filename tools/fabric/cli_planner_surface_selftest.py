from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .cli import cmd_show_planner_surface


class CliPlannerSurfaceSmokeTest(unittest.TestCase):
    def test_show_planner_surface_matrix(self) -> None:
        cases = [
            (
                "stale_mirror",
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
            ),
            (
                "tombstone",
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
            ),
            (
                "authority_transition",
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
            ),
            (
                "reconcile_matrix",
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
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            for idx, (_, ns) in enumerate(cases):
                root = Path(tmpdir) / f"case-{idx}"
                ns.root = str(root)
                rc = cmd_show_planner_surface(ns)
                self.assertEqual(rc, 0)
                self.assertTrue(root.exists())


if __name__ == "__main__":
    unittest.main()
