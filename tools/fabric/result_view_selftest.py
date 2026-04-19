from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .cli import cmd_show_result_view
from .planner_surface import planner_outcome_from_runtime_surface, planner_outcomes_from_runtime_surface_matrix
from .reconcile_flow_harness import run_authority_transition_flow, run_tombstone_propagation_flow
from .reconcile_matrix_harness import run_reconcile_matrix
from .result_interface import interface_from_serving_decision, interfaces_from_serving_matrix
from .result_plan import serving_decision_from_planner_outcome, serving_decisions_from_planner_matrix
from .result_render import render_block_from_interface, render_blocks_from_interface_matrix
from .result_surface import outcome_from_flow_result, outcomes_from_reconcile_matrix
from .result_view import view_from_render_block, views_from_render_matrix
from .stale_mirror_flow_harness import run_stale_mirror_flow


class ResultViewSmokeTest(unittest.TestCase):
    def test_direct_result_view_mapping(self) -> None:
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

            stale_view = view_from_render_block(
                render_block_from_interface(
                    interface_from_serving_decision(
                        serving_decision_from_planner_outcome(
                            planner_outcome_from_runtime_surface(outcome_from_flow_result("stale_mirror", stale))
                        )
                    )
                )
            )
            tombstone_view = view_from_render_block(
                render_block_from_interface(
                    interface_from_serving_decision(
                        serving_decision_from_planner_outcome(
                            planner_outcome_from_runtime_surface(outcome_from_flow_result("tombstone", tombstone))
                        )
                    )
                )
            )
            authority_view = view_from_render_block(
                render_block_from_interface(
                    interface_from_serving_decision(
                        serving_decision_from_planner_outcome(
                            planner_outcome_from_runtime_surface(outcome_from_flow_result("authority_transition", authority))
                        )
                    )
                )
            )

            self.assertEqual(stale_view.container, "detail_card")
            self.assertFalse(stale_view.show_content)
            self.assertEqual(tombstone_view.container, "alert_strip")
            self.assertFalse(tombstone_view.show_metadata)
            self.assertEqual(authority_view.emphasis, "info")

    def test_matrix_result_view_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            matrix = run_reconcile_matrix(Path(tmpdir))
            views = views_from_render_matrix(
                render_blocks_from_interface_matrix(
                    interfaces_from_serving_matrix(
                        serving_decisions_from_planner_matrix(
                            planner_outcomes_from_runtime_surface_matrix(outcomes_from_reconcile_matrix(matrix))
                        )
                    )
                )
            )
            self.assertEqual(views["stale_mirror"]["container"], "detail_card")
            self.assertEqual(views["tombstone"]["container"], "alert_strip")
            self.assertEqual(views["authority_transition"]["emphasis"], "info")

    def test_cli_show_result_view(self) -> None:
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
                rc = cmd_show_result_view(ns)
                self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
