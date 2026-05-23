import streamlit as st

from frontend.api_client import APIClient
from frontend.components.sidebar import render_sidebar
from frontend.pages import documents, overview, query
from frontend.state import evaluate_progress, init_state
from frontend.styles import apply_global_styles

st.set_page_config(page_title="CrisisHub - Crisis Console", page_icon="🛡️", layout="wide")

init_state()
apply_global_styles()

api_client = APIClient(base_url="http://127.0.0.1:8000")
progress = evaluate_progress(api_client)
current_step = render_sidebar(progress)

st.title("CrisisHub - Console de Crise para E-commerce")
st.caption("Assistente RAG para apoio operacional durante incidentes de vazamento de dados.")

if current_step == 1:
    overview.render(progress)
elif current_step == 2:
    documents.render(api_client, progress)
else:
    query.render(api_client, progress)
