import re

import streamlit as st


def _adaptive_top_k(question: str) -> int:
    tokens = re.findall(r"\w+", question.lower())
    length = len(tokens)

    top_k = 4
    if length >= 18:
        top_k += 2
    elif length >= 10:
        top_k += 1

    multi_clause_markers = [" e ", " ou ", ",", ";", "quais", "como", "quando"]
    if any(marker in f" {question.lower()} " for marker in multi_clause_markers):
        top_k += 1

    return max(3, min(8, top_k))


def render(api_client, progress: dict) -> None:
    st.markdown('<div class="step-chip">Consulte Aqui</div>', unsafe_allow_html=True)
    st.header("Consulte Aqui")
    st.caption("Faça perguntas criticas e valide as fontes antes de compartilhar resposta ao cliente.")

    if not progress["has_sources"]:
        st.warning("Envie ao menos um documento na Base Documental para habilitar consultas.")
        return

    if progress.get("index_status") == "pending_reindex":
        st.info("Novos arquivos detectados. A atualizacao do indice sera executada automaticamente ao gerar a resposta.")

    question = st.text_area(
        "Pergunta",
        height=120,
        placeholder="Ex: A empresa deve comunicar clientes afetados e a ANPD?",
    )

    st.caption("Recuperacao de contexto automatica: o sistema ajusta a profundidade conforme a pergunta.")

    if st.button("Gerar resposta", use_container_width=True, type="primary"):
        if not question.strip():
            st.warning("Digite uma pergunta para continuar.")
        else:
            top_k = _adaptive_top_k(question)
            ok, data = api_client.post_json("/rag/ask", {"question": question, "top_k": top_k})
            if not ok:
                st.error(data.get("detail", "Erro na consulta."))
            else:
                st.session_state.last_answer = data.get("answer", "")
                st.session_state.last_sources = data.get("sources", [])
                st.session_state.last_top_k = top_k
                st.session_state.index_ready = True

    if st.session_state.last_answer:
        st.subheader("Resposta sugerida")
        st.write(st.session_state.last_answer)

        if "last_top_k" in st.session_state:
            st.caption(f"Top-K aplicado automaticamente nesta consulta: {st.session_state.last_top_k}")

        st.subheader("Fontes utilizadas")
        if st.session_state.last_sources:
            for i, source in enumerate(st.session_state.last_sources, start=1):
                st.write(f"{i}. {source.get('source', 'fonte_desconhecida')} (score: {source.get('score', '-')})")
        else:
            st.info("Nenhuma fonte retornada para esta consulta.")
