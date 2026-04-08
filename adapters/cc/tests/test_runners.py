"""Tests for the cc adapter.

Heavy ML dependencies (torch, transformers, onnxruntime, etc.) are optional:
tests that require them are skipped gracefully when they are not installed.
All other tests (deps_inventory, image preprocessing) run without heavy deps.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

CC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CC_DIR))

HAS_TORCH = importlib.util.find_spec("torch") is not None
HAS_NUMPY = importlib.util.find_spec("numpy") is not None
HAS_PIL = importlib.util.find_spec("PIL") is not None
HAS_ONNX = importlib.util.find_spec("onnxruntime") is not None


class TestDepsInventory(unittest.TestCase):
    """deps_inventory.py must always work without heavy deps."""

    def _run_inventory(self) -> dict:
        result = subprocess.run(
            [sys.executable, str(CC_DIR / "deps_inventory.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        return json.loads(result.stdout)

    def test_output_is_valid_json(self) -> None:
        data = self._run_inventory()
        self.assertIsInstance(data, dict)

    def test_has_required_keys(self) -> None:
        data = self._run_inventory()
        for key in ("python", "executable", "packages"):
            self.assertIn(key, data, msg=f"missing key '{key}'")

    def test_packages_have_name_and_version(self) -> None:
        data = self._run_inventory()
        packages = data["packages"]
        self.assertIsInstance(packages, list)
        # Spot-check the first few entries (pip should always report itself at least)
        for pkg in packages[:5]:
            self.assertIn("name", pkg, msg=f"package missing 'name': {pkg}")
            self.assertIn("version", pkg, msg=f"package missing 'version': {pkg}")


@unittest.skipUnless(HAS_NUMPY and HAS_PIL, "numpy/pillow not installed")
class TestVisionPreprocessing(unittest.TestCase):
    """Image pre-processing logic can be tested without an ONNX model file."""

    def _make_runner(self):
        import numpy as np
        from runners.runner_vision_onnx import VisionONNXRunner
        runner = VisionONNXRunner.__new__(VisionONNXRunner)
        runner.image_size = 224
        runner.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(3, 1, 1)
        runner.std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(3, 1, 1)
        return runner

    def test_to_tensor_output_shape(self) -> None:
        import numpy as np
        from PIL import Image
        runner = self._make_runner()
        img = Image.fromarray(
            np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        )
        tensor = runner._to_tensor(img)
        self.assertEqual(tensor.shape, (3, 224, 224))

    def test_to_tensor_normalised_range(self) -> None:
        """Pixel values after normalisation should be roughly centred around 0."""
        import numpy as np
        from PIL import Image
        runner = self._make_runner()
        # All-128 image → normalised values near (0.502 - 0.485) / 0.229 ≈ 0.07
        img = Image.fromarray(
            np.full((224, 224, 3), 128, dtype=np.uint8)
        )
        tensor = runner._to_tensor(img)
        self.assertLess(abs(float(tensor.mean())), 1.0)

    def test_to_tensor_accepts_ndarray(self) -> None:
        import numpy as np
        runner = self._make_runner()
        arr = np.random.randint(0, 255, (50, 60, 3), dtype=np.uint8)
        tensor = runner._to_tensor(arr)
        self.assertEqual(tensor.shape, (3, 224, 224))


@unittest.skipUnless(HAS_TORCH, "torch not installed")
class TestEmbeddingsRunnerInterface(unittest.TestCase):
    def test_class_has_infer_method(self) -> None:
        from runners.runner_embeddings_hf import EmbeddingsHFRunner
        self.assertTrue(callable(getattr(EmbeddingsHFRunner, "infer", None)))

    def test_default_pooling_is_mean(self) -> None:
        from runners.runner_embeddings_hf import EmbeddingsHFRunner
        from unittest.mock import MagicMock, patch
        with patch("runners.runner_embeddings_hf.AutoTokenizer") as mt, \
             patch("runners.runner_embeddings_hf.AutoModel") as mm:
            mt.from_pretrained.return_value = MagicMock()
            mm.from_pretrained.return_value = MagicMock()
            runner = EmbeddingsHFRunner("fake/model")
        self.assertEqual(runner.pooling, "mean")


@unittest.skipUnless(HAS_TORCH, "torch not installed")
class TestWhisperRunnerInterface(unittest.TestCase):
    def test_class_has_infer_method(self) -> None:
        from runners.runner_whisper_hf import WhisperHFRunner
        self.assertTrue(callable(getattr(WhisperHFRunner, "infer", None)))


if __name__ == "__main__":
    unittest.main()
