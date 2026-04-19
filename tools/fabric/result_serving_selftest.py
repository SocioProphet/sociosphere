from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .result_serving_harness import run_result_serving_pipeline


class ResultServingPipelineSmokeTest(unittest.TestCase):
    def test_end_to_end_serving_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_result_serving_pipeline(Path(tmpdir))
            self.assertEqual(result["stale_mirror"]["serve_mode"], "metadata_only")
            self.assertFalse(result["stale_mirror"]["include_content"])
            self.assertEqual(result["tombstone"]["serve_mode"], "omit")
            self.assertFalse(result["tombstone"]["include_metadata"])
            self.assertEqual(result["authority_transition"]["serve_mode"], "defer_until_refresh")
            self.assertEqual(result["reconcile_matrix"]["stale_mirror"]["serve_mode"], "metadata_only")
            self.assertEqual(result["reconcile_matrix"]["tombstone"]["serve_mode"], "omit")
            self.assertEqual(result["reconcile_matrix"]["authority_transition"]["serve_mode"], "defer_until_refresh")


if __name__ == "__main__":
    unittest.main()
