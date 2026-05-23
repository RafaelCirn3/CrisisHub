# Grupo 3 - Ecommerce Crisis RAG

Projeto orientado a resposta de crise em e-commerce apos incidente de vazamento de dados, com interface RAG simples e organizada.

## Estrutura recomendada

- `app.py`: entrada principal da interface Streamlit.
- `api.py`: API principal (upload + indexacao automatica + consulta RAG).
- `api_ai.py`: servico auxiliar de IA (opcional).
- `frontend/`: camada de apresentacao (paginas, sidebar, estilos, estado).
- `backend/rag/`: pipeline modular de ingestao, embeddings, indexacao e resposta.
- `documentos/`: base documental local (conteudo ignorado no Git, exceto `.gitkeep`).
- `docs/`: documentacao e materiais de apoio.
- `scripts/`: scripts utilitarios.

## Compatibilidade legada

Os arquivos abaixo foram mantidos como ponte para comandos antigos:
- `app_pmli.py` -> importa `app.py`
- `api_pmli.py` -> importa `api.py`
- `api_ai_pmli.py` -> importa `api_ai.py`

## Abas da interface

- Visao Geral
- Base Documental
- Consulte Aqui

## Indexacao automatica

- Cada novo upload marca o indice como desatualizado.
- Na proxima consulta, o backend reindexa automaticamente antes de responder.
- Endpoint de status: `GET /rag/index-status`.

## Execucao

```bash
uvicorn api:app --reload --port 8000
streamlit run app.py
```

## Endpoints principais

- `POST /rag/upload`
- `POST /rag/ask`
- `GET /rag/sources`
- `GET /rag/index-status`
- `GET /health`
