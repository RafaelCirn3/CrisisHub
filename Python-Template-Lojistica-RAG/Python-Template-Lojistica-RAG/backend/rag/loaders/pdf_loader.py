from __future__ import annotations

from pathlib import Path

from .base import BaseDocumentLoader, LoadedDocument


class PDFLoader(BaseDocumentLoader):
    """Load text from PDF files page by page."""

    def load(self, path: Path) -> list[LoadedDocument]:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError("pypdf is required to load PDF files") from exc

        reader = PdfReader(str(path))
        documents: list[LoadedDocument] = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            documents.append(
                LoadedDocument(
                    source=str(path),
                    text=text,
                    metadata={"file_type": "pdf", "page": page_number},
                )
            )

        return documents
