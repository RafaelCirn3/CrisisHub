from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from backend.rag.processors.chunking import Chunk
from backend.rag.prompts.templates import RAGPromptBuilder, SYSTEM_PROMPT
from backend.rag.services.vector_store import VectorStore, VectorStoreHit


@dataclass(slots=True)
class RetrievedChunk:
    """Chunk returned by semantic retrieval."""

    chunk: Chunk
    score: float


@dataclass(slots=True)
class RAGAnswer:
    """Final answer returned by the RAG chain."""

    answer: str
    sources: list[dict[str, object]]
    retrieved_chunks: list[RetrievedChunk]
    context: str


class RAGChain:
    """Retrieve context and generate grounded answers."""

    MIN_RELEVANCE_SCORE = 0.26
    OVERFETCH_FACTOR = 4
    LEXICAL_BOOST = 0.18
    QA_STYLE_BONUS = 0.04
    _token_pattern = re.compile(r"[a-z0-9]+", re.IGNORECASE)

    def __init__(self, vector_store: VectorStore, embeddings_model, llm_client, prompt_builder: RAGPromptBuilder | None = None):
        self.vector_store = vector_store
        self.embeddings_model = embeddings_model
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder or RAGPromptBuilder()

    def answer(self, question: str, top_k: int = 4) -> RAGAnswer:
        query = question.strip()
        if not query:
            return RAGAnswer(answer="Pergunta vazia.", sources=[], retrieved_chunks=[], context="")

        hits = self._search_with_hybrid_rerank(query, top_k)

        retrieved_chunks = [RetrievedChunk(chunk=hit.chunk, score=hit.score) for hit in hits]
        context = self.prompt_builder.build_context(retrieved_chunks)

        if not hits or hits[0].score < self.MIN_RELEVANCE_SCORE:
            return RAGAnswer(
                answer="Não foram encontradas informações suficientes nos documentos fornecidos.",
                sources=[],
                retrieved_chunks=[],
                context=context,
            )

        user_prompt = self.prompt_builder.build_user_prompt(query, context)
        answer = self.llm_client.generate(user_prompt, system_prompt=SYSTEM_PROMPT).strip()

        if not answer:
            answer = "Não foram encontradas informações suficientes nos documentos fornecidos."

        sources = [
            {
                "chunk_id": hit.chunk.chunk_id,
                "source": hit.chunk.source,
                "score": round(hit.score, 4),
                "semantic_score": round(float(hit.chunk.metadata.get("semantic_score", hit.score)), 4),
                "lexical_overlap": round(float(hit.chunk.metadata.get("lexical_overlap", 0.0)), 4),
                "metadata": hit.chunk.metadata,
            }
            for hit in hits
        ]

        return RAGAnswer(answer=answer, sources=sources, retrieved_chunks=retrieved_chunks, context=context)

    def _search_with_hybrid_rerank(self, query: str, top_k: int) -> list[VectorStoreHit]:
        query_embedding = self.embeddings_model.embed_query(query)
        expanded_top_k = max(1, top_k * self.OVERFETCH_FACTOR)
        initial_hits: list[VectorStoreHit] = self.vector_store.search(query_embedding, top_k=expanded_top_k)
        if not initial_hits:
            return []

        query_tokens = self._tokenize(query)
        reranked: list[tuple[float, VectorStoreHit]] = []

        for hit in initial_hits:
            chunk_tokens = self._tokenize(hit.chunk.text)
            lexical_overlap = self._lexical_overlap(query_tokens, chunk_tokens)
            qa_bonus = self.QA_STYLE_BONUS if self._looks_like_qa_chunk(hit.chunk.text) else 0.0
            final_score = float(hit.score) + (self.LEXICAL_BOOST * lexical_overlap) + qa_bonus

            hit.chunk.metadata = {
                **hit.chunk.metadata,
                "semantic_score": float(hit.score),
                "lexical_overlap": lexical_overlap,
            }
            reranked.append((final_score, hit))

        reranked.sort(key=lambda item: item[0], reverse=True)

        selected: list[VectorStoreHit] = []
        for final_score, hit in reranked[:top_k]:
            selected.append(VectorStoreHit(chunk=hit.chunk, score=final_score))
        return selected

    @classmethod
    def _tokenize(cls, text: str) -> set[str]:
        normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
        return set(cls._token_pattern.findall(normalized))

    @staticmethod
    def _lexical_overlap(query_tokens: set[str], chunk_tokens: set[str]) -> float:
        if not query_tokens or not chunk_tokens:
            return 0.0
        return len(query_tokens & chunk_tokens) / max(len(query_tokens), 1)

    @staticmethod
    def _looks_like_qa_chunk(text: str) -> bool:
        lower_text = text.lower()
        return "pergunta:" in lower_text and "resposta:" in lower_text
