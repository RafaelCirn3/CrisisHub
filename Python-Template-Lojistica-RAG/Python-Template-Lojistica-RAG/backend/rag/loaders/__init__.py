"""Document loaders for PDF, DOCX and TXT files."""

from .base import BaseDocumentLoader, LoadedDocument
from .docx_loader import DOCXLoader
from .factory import DocumentLoaderFactory, load_documents_from_path
from .pdf_loader import PDFLoader
from .txt_loader import TXTLoader
