import streamlit as st


def render(progress: dict) -> None:
    st.markdown('<div class="step-chip">Visao Geral</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero">
            <h2>Centro de Resposta a Incidente de Dados</h2>
            <p class="muted">
                Este painel foi desenhado para apoiar SAC, Juridico e Seguranca da Informacao durante crises no e-commerce.
                O objetivo e garantir respostas consistentes, rastreaveis e baseadas em documentos oficiais.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><b>Base documental</b><br><span class="muted">Envie politicas, FAQ, procedimentos e comunicados.</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><b>Consulte Aqui</b><br><span class="muted">Pergunte e receba resposta com fontes para auditoria.</span></div>', unsafe_allow_html=True)

    st.subheader("Checklist de prontidao")
    st.write("- API:", "Online" if progress["api_online"] else "Offline")
    st.write("- Documentos:", f"{len(progress['sources'])} arquivo(s) detectado(s)")

    status_map = {
        "ready": "Atualizado",
        "pending_reindex": "Pendente (sera atualizado automaticamente na proxima consulta)",
        "no_documents": "Aguardando documentos",
        "unknown": "Indisponivel",
    }
    st.write("- Indice:", status_map.get(progress.get("index_status", "unknown"), "Indisponivel"))
