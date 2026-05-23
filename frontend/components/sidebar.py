import streamlit as st


def render_sidebar(progress: dict) -> int:
    st.sidebar.title("CrisisHub")
    st.sidebar.caption("Assistente RAG para apoio operacional durante incidentes de vazamento de dados.")

    labels = [
        "Visao Geral",
        "Base Documental",
        "Consulte Aqui",
    ]

    selected_label = st.sidebar.radio(
        "Areas",
        labels,
        key="selected_area",
        label_visibility="collapsed",
    )

    selected_step = labels.index(selected_label) + 1
    st.session_state.current_step = selected_step

    st.sidebar.divider()
    st.sidebar.markdown("**Status rapido**")
    st.sidebar.write("API: online" if progress["api_online"] else "API: offline")
    st.sidebar.write("Documentos: carregados" if progress["has_sources"] else "Documentos: pendentes")

    status_map = {
        "ready": "Indice: atualizado",
        "pending_reindex": "Indice: atualizacao automatica pendente",
        "no_documents": "Indice: aguardando documentos",
        "unknown": "Indice: status indisponivel",
    }
    st.sidebar.write(status_map.get(progress.get("index_status", "unknown"), "Indice: status indisponivel"))

    st.sidebar.divider()
    st.sidebar.caption("Dica: busque sempre perguntar de forma direta.")

    return selected_step
