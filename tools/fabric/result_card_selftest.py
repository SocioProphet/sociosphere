from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .planner_surface import planner_outcome_from_runtime_surface
from .reconcile_flow_harness import run_authority_transition_flow, run_tombstone_propagation_flow
from .reconcile_matrix_harness import run_reconcile_matrix
from .result_card import card_from_view, cards_from_view_matrix
from .result_interface import interface_from_serving_decision, interfaces_from_serving_matrix
from .result_plan import serving_decision_from_planner_outcome, serving_decisions_from_planner_matrix
from .result_render import render_block_from_interface, render_blocks_from_interface_matrix
from .result_surface import outcome_from_flow_result
from .result_view import view_from_render_block, views_from_render_matrix
from .stale_mirror_flow_harness import run_stale_mirror_flow


class ResultCardSmokeTest(unittest.TestCase):
    def test_direct_result_card_mapping(self) -> None:
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

            stale_card = card_from_view(
                view_from_render_block(
                    render_block_from_interface(
                        interface_from_serving_decision(
                            serving_decision_from_planner_outcome(
                                planner_outcome_from_runtime_surface(outcome_from_flow_result("stale_mirror", stale))
                            )
                        )
                    )
                )
            )
            tombstone_card = card_from_view(
                view_from_render_block(
                    render_block_from_interface(
                        interface_from_serving_decision(
                            serving_decision_from_planner_outcome(
                                planner_outcome_from_runtime_surface(outcome_from_flow_result("tombstone", tombstone))
                            )
                        )
                    )
                )
            )
            authority_card = card_from_view(
                view_from_render_block(
                    render_block_from_interface(
                        interface_from_serving_decision(
                            serving_decision_from_planner_outcome(
                                planner_outcome_from_runtime_surface(outcome_from_flow_result("authority_transition", authority))
                            )
                        )
                    )
                )
            )

            self.assertEqual(stale_card.card_kind, "metadata_card")
            self.assertEqual(stale_card.content_mode, "metadata_only")
            self.assertEqual(tombstone_card.card_kind, "alert_card")
            self.assertEqual(tombstone_card.content_mode, "hidden")
            self.assertEqual(authority_card.tone, "info")

    def test_matrix_result_card_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            matrix = run_reconcile_matrix(Path(tmpdir))
            cards = cards_from_view_matrix(
                views_from_render_matrix(
                    render_blocks_from_interface_matrix(
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
                )
            )
            self.assertEqual(cards["stale_mirror"]["card_kind"], "metadata_card")
            self.assertEqual(cards["tombstone"]["card_kind"], "alert_card")
            self.assertEqual(cards["authority_transition"]["tone"], "info")


if __name__ == "__main__":
    unittest.main()
