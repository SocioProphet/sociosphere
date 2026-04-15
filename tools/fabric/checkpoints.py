from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from .types import ConnectorCheckpoint


class CheckpointStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, connector_id: str, dataset_ref: str) -> Path:
        safe_dataset = dataset_ref.replace('/', '__')
        return self.root / f"{connector_id}--{safe_dataset}.json"

    def save(self, checkpoint: ConnectorCheckpoint) -> Path:
        path = self.path_for(checkpoint.connector_id, checkpoint.dataset_ref)
        payload = json.dumps(asdict(checkpoint), sort_keys=True, separators=(",", ":"))
        with tempfile.NamedTemporaryFile("w", delete=False, dir=str(self.root), encoding="utf-8") as tmp:
            tmp.write(payload)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        tmp_path.replace(path)
        return path

    def load(self, connector_id: str, dataset_ref: str) -> ConnectorCheckpoint | None:
        path = self.path_for(connector_id, dataset_ref)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return ConnectorCheckpoint(**data)
