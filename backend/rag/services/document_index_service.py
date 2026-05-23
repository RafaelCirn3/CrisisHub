from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.rag.embeddings.sentence_transformer_embeddings import SentenceTransformerEmbeddings
from backend.rag.loaders.base import LoadedDocument
from backend.rag.loaders.factory import load_documents_from_path
from backend.rag.processors.chunking import Chunk, ChunkingConfig, DocumentChunker
from backend.rag.processors.text_cleaner import TextCleaner
from backend.rag.services.vector_store import VectorStore


@dataclass(slots=True)
class DocumentIndexService:
    """Build and persist the complete document index."""

    embeddings_model: SentenceTransformerEmbeddings
    cleaner: TextCleaner | None = None
    chunker: DocumentChunker | None = None
    index_directory: Path | None = None

    def __post_init__(self) -> None:
        self.cleaner = self.cleaner or TextCleaner()
        self.chunker = self.chunker or DocumentChunker(ChunkingConfig())

    def build(self, source_path: str | Path, save: bool = True) -> VectorStore:
        documents = load_documents_from_path(source_path)
        cleaned_documents = self._clean_documents(documents)
        chunks: list[Chunk] = self.chunker.split(cleaned_documents)

        if not chunks:
            raise ValueError("No chunks were produced from the provided documents")

        embeddings = self.embeddings_model.embed_documents([chunk.text for chunk in chunks])
        vector_store = VectorStore(chunks=chunks, embeddings=embeddings)

        if save and self.index_directory is not None:
            vector_store.save(self.index_directory)

        return vector_store

    def load_or_build(self, source_path: str | Path) -> VectorStore:
        if self.index_directory is not None and (self.index_directory / "chunks.json").exists():
            return VectorStore.load(self.index_directory)
        return self.build(source_path, save=self.index_directory is not None)

    def _clean_documents(self, documents: list[LoadedDocument]) -> list[LoadedDocument]:
        cleaned_documents: list[LoadedDocument] = []
        for document in documents:
            cleaned_text = self.cleaner.clean(document.text)
            if not cleaned_text:
                continue
            cleaned_documents.append(
                LoadedDocument(
                    source=document.source,
                    text=cleaned_text,
                    metadata=document.metadata,
                )
            )
        return cleaned_documents
