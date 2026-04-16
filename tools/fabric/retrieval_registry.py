from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .types import IndexRef


@dataclass(frozen=True)
class RegisteredIndex:
    workspace_ref: str
    dataset_ref: str
    visibility: str
    index_ref: IndexRef


class RetrievalRegistry:
    def __init__(self) -> None:
        self._entries: Dict[Tuple[str, str], RegisteredIndex] = {}

    def register(self, workspace_ref: str, dataset_ref: str, visibility: str, index_ref: IndexRef) -> None:
        self._entries[(workspace_ref, dataset_ref)] = RegisteredIndex(
            workspace_ref=workspace_ref,
            dataset_ref=dataset_ref,
            visibility=visibility,
            index_ref=index_ref,
        )

    def get(self, workspace_ref: str, dataset_ref: str) -> RegisteredIndex | None:
        return self._entries.get((workspace_ref, dataset_ref))
