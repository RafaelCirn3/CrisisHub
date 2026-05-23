from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.rag.chains.rag_chain import RAGAnswer, RAGChain
from backend.rag.embeddings.sentence_transformer_embeddings import SentenceTransformerEmbeddings
from backend.rag.prompts.templates import RAGPromptBuilder
from backend.rag.services.document_index_service import DocumentIndexService
from backend.rag.services.llm_service import create_default_llm_client


@dataclass(slots=True)
class RAGPipeline:
    """High-level helper for building and querying the RAG flow."""

    source_path: Path
    index_directory: Path | None = None
    embeddings_model: SentenceTransformerEmbeddings | None = None
    index_service: DocumentIndexService | None = None
    llm_client: Any | None = None
    prompt_builder: RAGPromptBuilder | None = None
    _vector_store: Any | None = None

    def __post_init__(self) -> None:
        self.embeddings_model = self.embeddings_model or SentenceTransformerEmbeddings()
        self.index_service = self.index_service or DocumentIndexService(
            embeddings_model=self.embeddings_model,
            index_directory=self.index_directory,
        )
        self.llm_client = self.llm_client or create_default_llm_client()
        self.prompt_builder = self.prompt_builder or RAGPromptBuilder()
        self._vector_store = self._vector_store

    def build(self) -> None:
        self._vector_store = self.index_service.build(self.source_path, save=True)

    def load(self) -> None:
        self._vector_store = self.index_service.load_or_build(self.source_path)

    def ask(self, question: str, top_k: int = 4) -> RAGAnswer:
        if self._vector_store is None:
            self.load()

        chain = RAGChain(
            vector_store=self._vector_store,
            embeddings_model=self.embeddings_model,
            llm_client=self.llm_client,
            prompt_builder=self.prompt_builder,
        )
        return chain.answer(question=question, top_k=top_k)
