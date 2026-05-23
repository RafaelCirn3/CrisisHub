from __future__ import annotations

from pathlib import Path

from .base import BaseDocumentLoader, LoadedDocument


class DOCXLoader(BaseDocumentLoader):
    """Load text from DOCX files."""

    def load(self, path: Path) -> list[LoadedDocument]:
        try:
            from docx import Document
            from docx.table import Table
            from docx.text.paragraph import Paragraph
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError("python-docx is required to load DOCX files") from exc

        document = Document(str(path))
        blocks: list[str] = []

        for block in self._iter_blocks(document, Paragraph, Table):
            if isinstance(block, Paragraph):
                text = block.text.strip()
            else:
                text = self._table_to_text(block)

            if text:
                blocks.append(text)

        text = "\n".join(blocks).strip()

        if not text:
            return []

        return [
            LoadedDocument(
                source=str(path),
                text=text,
                metadata={"file_type": "docx"},
            )
        ]

    @staticmethod
    def _iter_blocks(document, paragraph_type, table_type):
        from docx.oxml.ns import qn

        body = document.element.body
        for child in body.iterchildren():
            if child.tag == qn("w:p"):
                yield paragraph_type(child, document)
            elif child.tag == qn("w:tbl"):
                yield table_type(child, document)

    @staticmethod
    def _table_to_text(table) -> str:
        rows: list[str] = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                rows.append(" | ".join(cells))
        return "\n".join(rows)
