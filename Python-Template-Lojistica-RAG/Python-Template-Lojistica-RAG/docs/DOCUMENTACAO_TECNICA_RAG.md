# Documentacao Tecnica - RAG (CrisisHub Ecommerce)

## Objetivo

Este projeto implementa um pipeline RAG para responder perguntas sobre gestao de crise em e-commerce apos vazamento de dados.

## Arquitetura

1. Ingestao documental (`PDF`, `TXT`, `DOCX`).
2. Limpeza e chunking de texto.
3. Geracao de embeddings.
4. Indexacao vetorial em FAISS.
5. Recuperacao semantica dos trechos relevantes.
6. Geracao de resposta orientada por contexto.
7. Exibicao de resposta e fontes.

## Requisitos atendidos

- Upload de documentos.
- Processamento textual em chunks.
- Geracao de embeddings vetoriais.
- Banco vetorial persistente.
- Perguntas em linguagem natural.
- Recuperacao de contexto relevante.
- Resposta contextualizada por LLM.
- Exibicao de fontes no frontend.
- Interface minima para operacao.

## Estrutura modular

- `backend/rag/loaders`: carregadores por tipo de documento.
- `backend/rag/processors`: limpeza e chunking.
- `backend/rag/embeddings`: geracao de embeddings.
- `backend/rag/services`: indexacao, vector store e cliente LLM.
- `backend/rag/chains`: cadeia de recuperacao e resposta.
- `backend/rag/prompts`: prompt de sistema para dominio de e-commerce e LGPD.

## Operacao

- API: `uvicorn api_pmli:app --reload --port 8000`
- UI: `streamlit run app_pmli.py`
- Teste rapido: `python test_pipeline.py`
