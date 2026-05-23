from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.rag.pipeline import RAGPipeline

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "documentos"
INDEX_DIR = BASE_DIR / "ai_index"

app = FastAPI(title="CrisisHub - AI Service", version="3.0.0")


class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=4, ge=1, le=10)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    status: str = "success"
    processing_time: float = 0.0


@app.post("/ai/sync")
def sync_index() -> dict[str, object]:
    pipeline = RAGPipeline(source_path=DOCS_DIR, index_directory=INDEX_DIR)
    try:
        pipeline.build()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao atualizar indice: {exc}") from exc
    return {"status": "success", "message": "Indice RAG atualizado", "indexed_docs": len(list(DOCS_DIR.glob("*")))}


@app.post("/ai/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    start = time.time()
    pipeline = RAGPipeline(source_path=DOCS_DIR, index_directory=INDEX_DIR)
    try:
        result = pipeline.ask(req.query, top_k=req.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha na consulta: {exc}") from exc

    return ChatResponse(
        answer=result.answer,
        sources=[src.get("source", "") for src in result.sources],
        processing_time=time.time() - start,
    )


@app.get("/ai/health")
def health() -> dict[str, object]:
    return {
        "status": "healthy",
        "service": "grupo3-ecommerce-ai",
        "indexed_docs": len(list(DOCS_DIR.glob("*"))) if DOCS_DIR.exists() else 0,
    }
