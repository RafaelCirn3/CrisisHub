# Terminal 1: API Principal (Logística)
uvicorn api_pmli:app --reload --port 8000

# Terminal 2: Serviço de IA (RAG)
uvicorn api_ai_pmli:app --reload --port 8001

# Terminal 3: Frontend Streamlit
streamlit run app_pmli_ianew.py