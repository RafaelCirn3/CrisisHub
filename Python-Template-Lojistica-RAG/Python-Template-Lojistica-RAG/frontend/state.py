import streamlit as st


TOTAL_STEPS = 3


def init_state() -> None:
    defaults = {
        "current_step": 1,
        "selected_area": "Visao Geral",
        "docs_uploaded": False,
        "index_ready": False,
        "last_answer": "",
        "last_sources": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def evaluate_progress(api_client) -> dict:
    ok_health, _ = api_client.get("/health")
    ok_sources, sources_resp = api_client.get("/rag/sources")
    ok_index, index_resp = api_client.get("/rag/index-status")

    sources = sources_resp.get("sources", []) if ok_sources else []
    has_sources = len(sources) > 0

    index_status = index_resp.get("status", "unknown") if ok_index else "unknown"
    st.session_state.docs_uploaded = has_sources
    st.session_state.index_ready = index_status == "ready"

    return {
        "api_online": ok_health,
        "has_sources": has_sources,
        "sources": sources,
        "index_status": index_status,
        "can_query": ok_health and has_sources,
    }


def set_step(step: int) -> None:
    st.session_state.current_step = max(1, min(TOTAL_STEPS, step))
