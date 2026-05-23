from __future__ import annotations

from pathlib import Path

from .base import BaseDocumentLoader, LoadedDocument


class TXTLoader(BaseDocumentLoader):
    """Load text from TXT files using tolerant decoding."""

    def load(self, path: Path) -> list[LoadedDocument]:
        text = path.read_text(encoding="utf-8", errors="ignore").strip()

        if not text:
            return []

        return [
            LoadedDocument(
                source=str(path),
                text=text,
                metadata={"file_type": "txt"},
            )
        ]
