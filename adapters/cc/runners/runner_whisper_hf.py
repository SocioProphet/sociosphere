from __future__ import annotations
from typing import Any, Dict, List
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import torch


class WhisperHFRunner:
    """HuggingFace Whisper ASR runner.

    Args:
        hf_id:    HuggingFace model identifier (e.g. 'openai/whisper-small').
        device:   Torch device string; auto-detects CUDA if None.
        language: Optional language hint (e.g. 'english').
        task:     Optional task hint ('transcribe' or 'translate').
    """

    def __init__(
        self,
        hf_id: str,
        device: str | None = None,
        language: str | None = None,
        task: str | None = None,
    ) -> None:
        self.hf_id = hf_id
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoProcessor.from_pretrained(hf_id)
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(hf_id).to(self.device)
        self.model.eval()
        self.generation_kwargs: Dict[str, Any] = {}
        if language:
            self.generation_kwargs["language"] = language
        if task:
            self.generation_kwargs["task"] = task

    @torch.inference_mode()
    def infer(self, batch: List[Dict[str, Any]]) -> List[str]:
        """Return a list of transcribed strings (one per audio item)."""
        waves = []
        target_sr = self.processor.feature_extractor.sampling_rate
        for b in batch:
            x = b.get("audio")
            if isinstance(x, str):
                import soundfile as sf
                wav, sr = sf.read(x)
            else:
                wav = x
                sr = target_sr
            if sr != target_sr:
                import librosa
                wav = librosa.resample(wav, orig_sr=sr, target_sr=target_sr)
            waves.append(wav)
        inputs = self.processor(waves, sampling_rate=target_sr, return_tensors="pt").to(self.device)
        gen = self.model.generate(**inputs, **self.generation_kwargs)
        return self.processor.batch_decode(gen, skip_special_tokens=True)
