#!/usr/bin/env python
"""Execucao de teste rapido do pipeline RAG."""

from pathlib import Path

from backend.rag.pipeline import RAGPipeline


def main() -> None:
    docs_path = Path("documentos")
    index_path = Path("ai_index")

    print("Inicializando pipeline...")
    pipeline = RAGPipeline(source_path=docs_path, index_directory=index_path)

    print(f"Construindo indice a partir de {docs_path}...")
    try:
        pipeline.build()
        print("Indice construido com sucesso.")
    except Exception as exc:
        print(f"Erro ao construir indice: {exc}")
        return

    question = "A empresa deve comunicar os clientes afetados e a ANPD?"
    result = pipeline.ask(question, top_k=4)
    print("\nPergunta:", question)
    print("Resposta:\n", result.answer)


if __name__ == "__main__":
    main()
