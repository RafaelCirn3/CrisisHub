from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.rag.pipeline import RAGPipeline

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DOCS_DIR = BASE_DIR / "documentos"
DEFAULT_INDEX_DIR = BASE_DIR / "ai_index"
INDEX_DIRTY_FLAG = BASE_DIR / ".rag_index_dirty"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

app = FastAPI(
    title="CrisisHub - Ecommerce Crisis RAG API",
    version="3.1.0",
    description="API de chatbot RAG para gestao de crise em e-commerce apos incidente de dados.",
)


class BuildIndexRequest(BaseModel):
    source_dir: str = Field(default="documentos", description="Diretorio com documentos de conhecimento")
    index_dir: str = Field(default="ai_index", description="Diretorio onde o indice vetorial sera salvo")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, description="Pergunta em linguagem natural")
    top_k: int = Field(default=4, ge=1, le=10)


class AskResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]]
    context: str


def _resolve_path(path_value: str) -> Path:
    raw = Path(path_value)
    return raw if raw.is_absolute() else BASE_DIR / raw


def _get_pipeline(source_dir: str, index_dir: str) -> RAGPipeline:
    return RAGPipeline(source_path=_resolve_path(source_dir), index_directory=_resolve_path(index_dir))


def _mark_index_dirty() -> None:
    INDEX_DIRTY_FLAG.write_text("dirty", encoding="utf-8")


def _mark_index_clean() -> None:
    if INDEX_DIRTY_FLAG.exists():
        INDEX_DIRTY_FLAG.unlink()


def _is_index_dirty() -> bool:
    return INDEX_DIRTY_FLAG.exists()


def _index_files_exist(index_dir: Path) -> bool:
    required = ["chunks.json", "embeddings.npy", "index.faiss"]
    return all((index_dir / name).exists() for name in required)


def _ensure_index_up_to_date(source_dir: str = "documentos", index_dir: str = "ai_index") -> dict[str, Any]:
    pipeline = _get_pipeline(source_dir, index_dir)

    if not pipeline.source_path.exists() or not pipeline.source_path.is_dir():
        raise HTTPException(status_code=400, detail="Diretorio de documentos nao encontrado.")

    docs_count = len([p for p in pipeline.source_path.rglob("*") if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS])
    if docs_count == 0:
        raise HTTPException(status_code=400, detail="Nenhum documento disponivel para indexacao.")

    needs_rebuild = _is_index_dirty() or not _index_files_exist(pipeline.index_directory)
    if not needs_rebuild:
        return {"rebuilt": False, "documents_count": docs_count}

    try:
        pipeline.build()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao construir indice: {exc}") from exc

    _mark_index_clean()
    return {"rebuilt": True, "documents_count": docs_count}


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "grupo3-ecommerce-rag"}


@app.get("/rag/index-status", tags=["RAG"])
def index_status() -> dict[str, Any]:
    sources = [
        p
        for p in DEFAULT_DOCS_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
    ]
    docs_count = len(sources)
    dirty = _is_index_dirty()
    has_index = _index_files_exist(DEFAULT_INDEX_DIR)

    if docs_count == 0:
        status = "no_documents"
    elif dirty or not has_index:
        status = "pending_reindex"
    else:
        status = "ready"

    return {
        "status": status,
        "documents_count": docs_count,
        "dirty": dirty,
        "has_index": has_index,
    }


@app.post("/rag/upload", tags=["RAG"])
async def upload_document(file: UploadFile = File(...), target_dir: str = Form("documentos")) -> dict[str, str]:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato invalido. Use PDF, TXT ou DOCX.")

    directory = _resolve_path(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target_path = directory / (file.filename or "documento")

    content = await file.read()
    target_path.write_bytes(content)
    _mark_index_dirty()

    return {
        "message": "Documento enviado com sucesso. A base sera reindexada automaticamente na proxima consulta.",
        "file": str(target_path.relative_to(BASE_DIR)),
    }


@app.post("/rag/index", tags=["RAG"])
def build_index(payload: BuildIndexRequest) -> dict[str, Any]:
    result = _ensure_index_up_to_date(payload.source_dir, payload.index_dir)
    return {
        "message": "Indice vetorial atualizado com sucesso." if result["rebuilt"] else "Indice ja estava atualizado.",
        "documents_dir": str(_resolve_path(payload.source_dir)),
        "index_dir": str(_resolve_path(payload.index_dir)),
        "documents_count": result["documents_count"],
        "rebuilt": result["rebuilt"],
    }


@app.post("/rag/ask", response_model=AskResponse, tags=["RAG"])
def ask(payload: AskRequest) -> AskResponse:
    _ensure_index_up_to_date("documentos", "ai_index")

    pipeline = _get_pipeline("documentos", "ai_index")
    try:
        result = pipeline.ask(payload.question, top_k=payload.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao consultar chatbot: {exc}") from exc

    return AskResponse(answer=result.answer, sources=result.sources, context=result.context)


@app.get("/rag/sources", tags=["RAG"])
def list_sources(source_dir: str = "documentos") -> dict[str, list[str]]:
    directory = _resolve_path(source_dir)
    if not directory.exists():
        return {"sources": []}

    files = [
        str(path.relative_to(BASE_DIR))
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS
    ]
    return {"sources": sorted(files)}


def ensure_default_dirs() -> None:
    DEFAULT_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_INDEX_DIR.mkdir(parents=True, exist_ok=True)


ensure_default_dirs()
