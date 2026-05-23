from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.rag.loaders.base import LoadedDocument


@dataclass(slots=True)
class Chunk:
    """Single chunk ready for indexing."""

    chunk_id: str
    source: str
    text: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class ChunkingConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 150
    separators: tuple[str, ...] = ("\n\n", "\n", ". ", "; ", ": ", " ", "")


class DocumentChunker:
    """Split cleaned documents into overlapping semantic chunks."""

    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()

    def _build_splitter(self):
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except ImportError:
            return None

        return RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=list(self.config.separators),
        )

    def split(self, documents: list[LoadedDocument]) -> list[Chunk]:
        splitter = self._build_splitter()
        chunks: list[Chunk] = []

        for document_index, document in enumerate(documents):
            if not document.text.strip():
                continue

            if splitter is not None:
                try:
                    from langchain_core.documents import Document

                    split_documents = splitter.split_documents(
                        [
                            Document(
                                page_content=document.text,
                                metadata={**document.metadata, "source": document.source},
                            )
                        ]
                    )
                    texts = [(piece.page_content, piece.metadata) for piece in split_documents]
                except ImportError:
                    texts = self._fallback_split(document.text)
            else:
                texts = self._fallback_split(document.text)

            for chunk_index, (chunk_text, metadata) in enumerate(texts):
                chunk_id = f"{self._make_safe_id(document.source)}_{document_index}_{chunk_index}"
                chunk_metadata = {**document.metadata, **metadata, "source": document.source, "chunk_index": chunk_index}
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        source=document.source,
                        text=chunk_text.strip(),
                        metadata=chunk_metadata,
                    )
                )

        return [chunk for chunk in chunks if chunk.text]

    def _fallback_split(self, text: str) -> list[tuple[str, dict[str, Any]]]:
        size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        if size <= 0:
            return [(text, {})]

        step = max(1, size - overlap)
        pieces: list[tuple[str, dict[str, Any]]] = []
        start = 0

        while start < len(text):
            end = min(len(text), start + size)
            pieces.append((text[start:end], {}))
            if end >= len(text):
                break
            start += step

        return pieces

    @staticmethod
    def _make_safe_id(source: str) -> str:
        return "".join(character if character.isalnum() else "_" for character in Path(source).name).strip("_") or "document"
