from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .reconcile_flow_harness import run_authority_transition_flow, run_tombstone_propagation_flow
from .reconcile_matrix_harness import run_reconcile_matrix
from .result_surface import outcome_from_flow_result, outcomes_from_reconcile_matrix
from .stale_mirror_flow_harness import run_stale_mirror_flow


class ResultSurfaceSmokeTest(unittest.TestCase):
    def test_stale_mirror_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            flow = run_stale_mirror_flow(
                Path(tmpdir),
                stale_generation_gap=3,
                policy_allow_stale=True,
                authority_mode="local_first",
            )
            surface = outcome_from_flow_result("stale_mirror", flow)
            self.assertEqual(surface.surface_state, "remote_metadata_only")
            self.assertEqual(surface.freshness_class, "bounded_stale")
            self.assertEqual(surface.reconcile_state, "degraded_read")

    def test_tombstone_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            flow = run_tombstone_propagation_flow(
                Path(tmpdir),
                signed_tombstone=True,
                local_dirty=False,
                authority_mode="provider_first",
            )
            surface = outcome_from_flow_result("tombstone", flow)
            self.assertEqual(surface.surface_state, "tombstoned")
            self.assertEqual(surface.authority_state, "remote_authoritative")
            self.assertEqual(surface.reconcile_state, "resolved")

    def test_authority_transition_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            flow = run_authority_transition_flow(
                Path(tmpdir),
                current_authority="local",
                requested_authority="remote",
                quorum_granted=True,
            )
            surface = outcome_from_flow_result("authority_transition", flow)
            self.assertEqual(surface.surface_state, "authority_transition_applied")
            self.assertEqual(surface.authority_state, "remote_authoritative")

    def test_reconcile_matrix_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            matrix = run_reconcile_matrix(Path(tmpdir))
            surfaces = outcomes_from_reconcile_matrix(matrix)
            self.assertEqual(surfaces["tombstone"]["surface_state"], "tombstoned")
            self.assertEqual(surfaces["stale_mirror"]["surface_state"], "remote_metadata_only")
            self.assertEqual(surfaces["authority_transition"]["surface_state"], "authority_transition_applied")


if __name__ == "__main__":
    unittest.main()
