from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple, Union
import numpy as np
import onnxruntime as ort
from PIL import Image


class VisionONNXRunner:
    """ONNX Runtime-backed image classification runner.

    Args:
        onnx_path:  Path to the .onnx model file.
        input_name: Name of the ONNX input node (default: 'pixel_values').
        image_size: Target square image size in pixels (default: 224).
        mean:       Per-channel normalisation mean (RGB).
        std:        Per-channel normalisation std (RGB).
    """

    def __init__(
        self,
        onnx_path: str,
        input_name: str = "pixel_values",
        image_size: int = 224,
        mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
        std: Tuple[float, float, float] = (0.229, 0.224, 0.225),
    ) -> None:
        self.sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        self.input_name = input_name
        self.image_size = image_size
        self.mean = np.array(mean, dtype=np.float32).reshape(3, 1, 1)
        self.std = np.array(std, dtype=np.float32).reshape(3, 1, 1)

    def _to_tensor(self, img: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """Convert an image (path, ndarray, or PIL Image) to a normalised CHW float32 array."""
        if isinstance(img, str):
            img = Image.open(img).convert("RGB")
        elif isinstance(img, np.ndarray):
            img = Image.fromarray(img)
        img = img.resize((self.image_size, self.image_size))
        arr = np.asarray(img).astype(np.float32) / 255.0  # HWC → [0, 1]
        arr = arr.transpose(2, 0, 1)  # CHW
        arr = (arr - self.mean) / self.std
        return arr

    def infer(self, batch: List[Dict[str, Any]]) -> List[int]:
        """Return a list of predicted class indices (one per input item)."""
        x = np.stack([self._to_tensor(b.get("image")) for b in batch], axis=0)  # NCHW
        outputs = self.sess.run(None, {self.input_name: x})
        logits = outputs[0]
        return np.argmax(logits, axis=-1).tolist()
