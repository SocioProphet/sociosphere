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
from .result_preview import preview_from_card, previews_from_card_matrix
from .result_render import render_block_from_interface, render_blocks_from_interface_matrix
from .result_surface import outcome_from_flow_result
from .result_view import view_from_render_block, views_from_render_matrix
from .stale_mirror_flow_harness import run_stale_mirror_flow


class ResultPreviewSmokeTest(unittest.TestCase):
    def test_direct_result_preview_mapping(self) -> None:
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

            stale_preview = preview_from_card(
                card_from_view(
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
            )
            tombstone_preview = preview_from_card(
                card_from_view(
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
            )
            authority_preview = preview_from_card(
                card_from_view(
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
            )

            self.assertEqual(stale_preview.layout, "metadata_panel")
            self.assertEqual(stale_preview.visibility, "metadata_only")
            self.assertEqual(tombstone_preview.layout, "inline_alert")
            self.assertEqual(tombstone_preview.visibility, "hidden")
            self.assertEqual(authority_preview.visual_tone, "info")

    def test_matrix_result_preview_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            matrix = run_reconcile_matrix(Path(tmpdir))
            previews = previews_from_card_matrix(
                cards_from_view_matrix(
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
            )
            self.assertEqual(previews["stale_mirror"]["layout"], "metadata_panel")
            self.assertEqual(previews["tombstone"]["layout"], "inline_alert")
            self.assertEqual(previews["authority_transition"]["visual_tone"], "info")


if __name__ == "__main__":
    unittest.main()
