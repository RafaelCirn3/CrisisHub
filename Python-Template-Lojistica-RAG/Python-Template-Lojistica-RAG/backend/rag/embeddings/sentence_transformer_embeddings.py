from __future__ import annotations

import os

import numpy as np


class SentenceTransformerEmbeddings:
    """Generate normalized embeddings with SentenceTransformers."""

    def __init__(self, model_name: str | None = None, device: str | None = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.device = device or os.getenv("EMBEDDING_DEVICE") or None

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError("sentence-transformers is required for embeddings") from exc

        self._model = SentenceTransformer(self.model_name, device=self.device)
        self._dimension: int | None = None

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.astype(np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        embedding = self._model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embedding[0].astype(np.float32)

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            probe = self._model.encode(["probe"], convert_to_numpy=True, show_progress_bar=False)
            self._dimension = int(probe.shape[1])
        return self._dimension
