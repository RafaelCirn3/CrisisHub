from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class LoadedDocument:
    """Text extracted from a source document before chunking."""

    source: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseDocumentLoader(ABC):
    """Base interface for document loaders."""

    @abstractmethod
    def load(self, path: Path) -> list[LoadedDocument]:
        raise NotImplementedError
