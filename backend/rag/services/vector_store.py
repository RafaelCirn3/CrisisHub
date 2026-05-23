from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from backend.rag.processors.chunking import Chunk

try:  # pragma: no cover - optional dependency guard
    import faiss
except ImportError:  # pragma: no cover
    faiss = None


@dataclass(slots=True)
class VectorStoreHit:
    chunk: Chunk
    score: float


class VectorStore:
    """Persisted vector store backed by FAISS when available."""

    def __init__(self, chunks: list[Chunk], embeddings: np.ndarray):
        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D matrix")

        self.chunks = chunks
        self.embeddings = embeddings.astype(np.float32)
        self._index = self._build_index(self.embeddings)

    def _build_index(self, embeddings: np.ndarray):
        if faiss is not None:
            vectors = embeddings.copy()
            faiss.normalize_L2(vectors)
            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)
            return index

        normalized = self._normalize_numpy(embeddings)
        return normalized

    @staticmethod
    def _normalize_numpy(embeddings: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return embeddings / norms

    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> list[VectorStoreHit]:
        if not self.chunks:
            return []

        query = np.asarray(query_embedding, dtype=np.float32).reshape(1, -1)
        top_k = max(1, min(top_k, len(self.chunks)))

        if faiss is not None:
            faiss.normalize_L2(query)
            scores, indices = self._index.search(query, top_k)
            return self._build_hits(scores[0], indices[0])

        normalized_query = self._normalize_numpy(query)[0]
        scores = self._index @ normalized_query
        indices = np.argsort(scores)[::-1][:top_k]
        return self._build_hits(scores[indices], indices)

    def _build_hits(self, scores: np.ndarray, indices: np.ndarray) -> list[VectorStoreHit]:
        hits: list[VectorStoreHit] = []
        for score, index in zip(scores, indices):
            if int(index) < 0 or int(index) >= len(self.chunks):
                continue
            hits.append(VectorStoreHit(chunk=self.chunks[int(index)], score=float(score)))
        return hits

    def save(self, directory: str | Path) -> None:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

        chunks_payload = [asdict(chunk) for chunk in self.chunks]
        (path / "chunks.json").write_text(json.dumps(chunks_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        np.save(path / "embeddings.npy", self.embeddings)

        if faiss is not None:
            faiss.write_index(self._index, str(path / "index.faiss"))

    @classmethod
    def load(cls, directory: str | Path) -> "VectorStore":
        path = Path(directory)
        chunks_data = json.loads((path / "chunks.json").read_text(encoding="utf-8"))
        chunks = [Chunk(**item) for item in chunks_data]
        embeddings = np.load(path / "embeddings.npy")
        return cls(chunks=chunks, embeddings=embeddings)
