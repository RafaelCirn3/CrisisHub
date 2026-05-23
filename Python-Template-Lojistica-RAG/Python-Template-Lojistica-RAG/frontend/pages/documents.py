import streamlit as st


def render(api_client, progress: dict) -> None:
    st.markdown('<div class="step-chip">Base Documental</div>', unsafe_allow_html=True)
    st.header("Base Documental")
    st.caption("Alimente o assistente com documentos oficiais para respostas juridicamente seguras.")

    upload = st.file_uploader(
        "Envie documentos (PDF, TXT, DOCX)",
        type=["pdf", "txt", "docx"],
        help="Sugestao: LGPD, politica interna, playbook de crise, FAQ e modelos de comunicacao.",
    )

    if st.button("Enviar para a base", use_container_width=True, type="primary"):
        if not upload:
            st.warning("Selecione um documento antes de enviar.")
        else:
            ok, data = api_client.post_file("/rag/upload", upload, "documentos")
            if ok:
                st.success(data.get("message", "Documento enviado."))
                st.rerun()
            else:
                st.error(data.get("detail", "Falha no upload."))

    st.subheader("Documentos atuais")
    if progress["sources"]:
        for idx, source in enumerate(progress["sources"], start=1):
            st.write(f"{idx}. {source}")
    else:
        st.info("Nenhum documento foi carregado ainda.")

    st.markdown('<div class="card"><b>Indexacao automatica:</b> ao enviar novo arquivo, o sistema marca o indice para atualizacao e reindexa automaticamente na proxima consulta.</div>', unsafe_allow_html=True)
