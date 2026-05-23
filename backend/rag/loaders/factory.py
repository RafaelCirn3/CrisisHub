from __future__ import annotations

from pathlib import Path

from .base import BaseDocumentLoader, LoadedDocument
from .docx_loader import DOCXLoader
from .pdf_loader import PDFLoader
from .txt_loader import TXTLoader


class DocumentLoaderFactory:
    """Resolve document loaders by file extension."""

    _loaders: dict[str, BaseDocumentLoader] = {
        ".pdf": PDFLoader(),
        ".docx": DOCXLoader(),
        ".txt": TXTLoader(),
    }

    @classmethod
    def get_loader(cls, path: Path) -> BaseDocumentLoader:
        extension = path.suffix.lower()
        if extension not in cls._loaders:
            raise ValueError(f"Unsupported document type: {path.suffix}")
        return cls._loaders[extension]


def load_documents_from_path(path: str | Path, recursive: bool = True) -> list[LoadedDocument]:
    """Load all supported documents from a file or directory."""

    root = Path(path)
    if root.is_file():
        return DocumentLoaderFactory.get_loader(root).load(root)

    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    pattern = "**/*" if recursive else "*"
    documents: list[LoadedDocument] = []

    for file_path in sorted(root.glob(pattern)):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in DocumentLoaderFactory._loaders:
            continue
        documents.extend(DocumentLoaderFactory.get_loader(file_path).load(file_path))

    return documents
