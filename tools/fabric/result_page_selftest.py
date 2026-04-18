from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from .planner_surface import planner_outcome_from_runtime_surface, planner_outcomes_from_runtime_surface_matrix
from .reconcile_flow_harness import run_authority_transition_flow, run_tombstone_propagation_flow
from .reconcile_matrix_harness import run_reconcile_matrix
from .result_card import card_from_view, cards_from_view_matrix
from .result_interface import interface_from_serving_decision, interfaces_from_serving_matrix
from .result_page import page_from_preview, page_from_preview_matrix
from .result_page_cli import cmd_show_result_page
from .result_plan import serving_decision_from_planner_outcome, serving_decisions_from_planner_matrix
from .result_preview import preview_from_card, previews_from_card_matrix
from .result_render import render_block_from_interface, render_blocks_from_interface_matrix
from .result_surface import outcome_from_flow_result, outcomes_from_reconcile_matrix
from .result_view import view_from_render_block, views_from_render_matrix
from .stale_mirror_flow_harness import run_stale_mirror_flow


class ResultPageSmokeTest(unittest.TestCase):
    def test_direct_result_page_mapping(self) -> None:
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

            def build_page(flow_name: str, flow: dict) -> str:
                preview = preview_from_card(
                    card_from_view(
                        view_from_render_block(
                            render_block_from_interface(
                                interface_from_serving_decision(
                                    serving_decision_from_planner_outcome(
                                        planner_outcome_from_runtime_surface(outcome_from_flow_result(flow_name, flow))
                                    )
                                )
                            )
                        )
                    )
                )
                return page_from_preview("Fabric Result Preview", preview)

            stale_page = build_page("stale_mirror", stale)
            tombstone_page = build_page("tombstone", tombstone)
            authority_page = build_page("authority_transition", authority)

            self.assertIn("<!doctype html>", stale_page)
            self.assertIn("metadata_panel", stale_page)
            self.assertIn("inline_alert", tombstone_page)
            self.assertIn("tone-info", authority_page)

    def test_matrix_result_page_mapping(self) -> None:
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
            page = page_from_preview_matrix("Fabric Result Preview", previews)
            self.assertIn("result-preview-grid", page)
            self.assertIn("metadata_panel", page)
            self.assertIn("inline_alert", page)

    def test_cli_show_result_page(self) -> None:
        cases = [
            argparse.Namespace(
                kind="stale_mirror",
                root=None,
                title="Fabric Result Preview",
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
                title="Fabric Result Preview",
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
                title="Fabric Result Preview",
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
                title="Fabric Result Preview",
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
                rc = cmd_show_result_page(ns)
                self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
