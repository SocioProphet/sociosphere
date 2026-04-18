from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .cli import cmd_show_result_interface
from .planner_surface import planner_outcome_from_runtime_surface
from .reconcile_flow_harness import run_authority_transition_flow, run_tombstone_propagation_flow
from .result_interface import interface_from_serving_decision, interfaces_from_serving_matrix
from .result_plan import serving_decision_from_planner_outcome, serving_decisions_from_planner_matrix
from .result_surface import outcome_from_flow_result, outcomes_from_reconcile_matrix
from .reconcile_matrix_harness import run_reconcile_matrix
from .stale_mirror_flow_harness import run_stale_mirror_flow


class ResultInterfaceSmokeTest(unittest.TestCase):
    def test_direct_result_interface_mapping(self) -> None:
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

            stale_interface = interface_from_serving_decision(
                serving_decision_from_planner_outcome(
                    planner_outcome_from_runtime_surface(outcome_from_flow_result("stale_mirror", stale))
                )
            )
            tombstone_interface = interface_from_serving_decision(
                serving_decision_from_planner_outcome(
                    planner_outcome_from_runtime_surface(outcome_from_flow_result("tombstone", tombstone))
                )
            )
            authority_interface = interface_from_serving_decision(
                serving_decision_from_planner_outcome(
                    planner_outcome_from_runtime_surface(outcome_from_flow_result("authority_transition", authority))
                )
            )

            self.assertEqual(stale_interface.display_state, "metadata_only")
            self.assertFalse(stale_interface.content_visible)
            self.assertEqual(tombstone_interface.display_state, "hidden")
            self.assertFalse(tombstone_interface.metadata_visible)
            self.assertEqual(authority_interface.display_state, "pending_refresh")

    def test_matrix_interface_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            matrix = run_reconcile_matrix(Path(tmpdir))
            interfaces = interfaces_from_serving_matrix(
                serving_decisions_from_planner_matrix(
                    {
                        name: {
                            "flow_name": name,
                            "planner_mode": planner_outcome_from_runtime_surface(
                                outcome_from_flow_result(name, matrix[name]) if name != "authority_transition" else outcome_from_flow_result(name, matrix[name])
                            ).planner_mode,
                            "badge": planner_outcome_from_runtime_surface(
                                outcome_from_flow_result(name, matrix[name]) if name != "authority_transition" else outcome_from_flow_result(name, matrix[name])
                            ).badge,
                            "freshness_hint": planner_outcome_from_runtime_surface(
                                outcome_from_flow_result(name, matrix[name]) if name != "authority_transition" else outcome_from_flow_result(name, matrix[name])
                            ).freshness_hint,
                            "authority_hint": planner_outcome_from_runtime_surface(
                                outcome_from_flow_result(name, matrix[name]) if name != "authority_transition" else outcome_from_flow_result(name, matrix[name])
                            ).authority_hint,
                            "operator_action": planner_outcome_from_runtime_surface(
                                outcome_from_flow_result(name, matrix[name]) if name != "authority_transition" else outcome_from_flow_result(name, matrix[name])
                            ).operator_action,
                            "message": planner_outcome_from_runtime_surface(
                                outcome_from_flow_result(name, matrix[name]) if name != "authority_transition" else outcome_from_flow_result(name, matrix[name])
                            ).message,
                        }
                        for name in ["tombstone", "stale_mirror", "authority_transition"]
                    }
                )
            )
            self.assertEqual(interfaces["tombstone"]["display_state"], "hidden")
            self.assertEqual(interfaces["stale_mirror"]["display_state"], "metadata_only")
            self.assertEqual(interfaces["authority_transition"]["display_state"], "pending_refresh")

    def test_cli_show_result_interface(self) -> None:
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
                rc = cmd_show_result_interface(ns)
                self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
