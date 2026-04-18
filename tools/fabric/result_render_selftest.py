from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .cli import cmd_show_result_render
from .planner_surface import planner_outcome_from_runtime_surface
from .reconcile_flow_harness import run_authority_transition_flow, run_tombstone_propagation_flow
from .result_interface import interface_from_serving_decision, interfaces_from_serving_matrix
from .result_plan import serving_decision_from_planner_outcome, serving_decisions_from_planner_matrix
from .result_render import render_block_from_interface, render_blocks_from_interface_matrix
from .result_surface import outcome_from_flow_result, outcomes_from_reconcile_matrix
from .reconcile_matrix_harness import run_reconcile_matrix
from .stale_mirror_flow_harness import run_stale_mirror_flow


class ResultRenderSmokeTest(unittest.TestCase):
    def test_direct_result_render_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            stale = run_stale_mirror_flow(
                Path(tmpdir) / "stale",
                stale_generation_gap=3,
                policy_allow_stale=True,
                authority_mode="local_first",
            )
            tombstone = run_tombstone_propagation_flow(
                Path(tmpdir) / "tombstone",
                signed_tombstone=True,
                local_dirty=False,
                authority_mode="provider_first",
            )
            authority = run_authority_transition_flow(
                Path(tmpdir) / "authority",
                current_authority="local",
                requested_authority="remote",
                quorum_granted=True,
            )

            stale_render = render_block_from_interface(
                interface_from_serving_decision(
                    serving_decision_from_planner_outcome(
                        planner_outcome_from_runtime_surface(outcome_from_flow_result("stale_mirror", stale))
                    )
                )
            )
            tombstone_render = render_block_from_interface(
                interface_from_serving_decision(
                    serving_decision_from_planner_outcome(
                        planner_outcome_from_runtime_surface(outcome_from_flow_result("tombstone", tombstone))
                    )
                )
            )
            authority_render = render_block_from_interface(
                interface_from_serving_decision(
                    serving_decision_from_planner_outcome(
                        planner_outcome_from_runtime_surface(outcome_from_flow_result("authority_transition", authority))
                    )
                )
            )

            self.assertEqual(stale_render.variant, "card")
            self.assertEqual(stale_render.status_tone, "warning")
            self.assertEqual(tombstone_render.variant, "banner")
            self.assertEqual(tombstone_render.status_tone, "critical")
            self.assertEqual(authority_render.status_tone, "info")

    def test_matrix_result_render_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            matrix = run_reconcile_matrix(Path(tmpdir))
            renders = render_blocks_from_interface_matrix(
                interfaces_from_serving_matrix(
                    serving_decisions_from_planner_matrix(
                        {
                            name: serving_decision_from_planner_outcome(
                                planner_outcome_from_runtime_surface(outcome_from_flow_result(name, matrix[name]))
                            ).to_dict()
                            for name in ["tombstone", "stale_mirror", "authority_transition"]
                        }
                    )
                )
            )
            self.assertEqual(renders["stale_mirror"]["status_tone"], "warning")
            self.assertEqual(renders["tombstone"]["status_tone"], "critical")
            self.assertEqual(renders["authority_transition"]["status_tone"], "info")

    def test_cli_show_result_render(self) -> None:
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
                rc = cmd_show_result_render(ns)
                self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
