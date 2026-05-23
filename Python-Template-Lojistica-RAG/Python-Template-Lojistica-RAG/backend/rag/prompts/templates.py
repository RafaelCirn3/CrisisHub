from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SYSTEM_PROMPT = """Voce e um assistente tecnico para gestao de crise em e-commerce apos incidente de vazamento de dados.
Use apenas o contexto recuperado dos documentos fornecidos.
Responda em portugues, com tom profissional, objetivo e seguro.
Se a informacao nao estiver no contexto, diga exatamente: "Nao foram encontradas informacoes suficientes nos documentos fornecidos."
Nao invente dados, numeros, prazos, procedimentos ou orientacoes.
Quando houver base documental, comece a resposta com: "Com base nos documentos analisados...".
Se citar fontes, seja consistente com os identificadores mostrados no contexto.
Priorize orientacoes relacionadas a LGPD, comunicacao oficial aos clientes, seguranca da informacao e obrigacoes regulatorias.
"""


@dataclass(slots=True)
class RAGPromptBuilder:
    """Create the final prompt sent to the LLM."""

    system_prompt: str = SYSTEM_PROMPT

    def build_context(self, chunks: list[Any]) -> str:
        if not chunks:
            return "Nenhum contexto recuperado."

        blocks: list[str] = []
        for index, item in enumerate(chunks, start=1):
            chunk = item.chunk
            source_label = chunk.source
            page_label = chunk.metadata.get("page")
            page_text = f" | pagina: {page_label}" if page_label is not None else ""
            blocks.append(f"[{index}] fonte: {source_label}{page_text} | score: {item.score:.3f}\n{chunk.text}")

        return "\n\n".join(blocks)

    def build_user_prompt(self, question: str, context: str) -> str:
        return f"""Contexto recuperado:\n{context}\n\nPergunta do usuario:\n{question}\n\nOrientacoes:\n- Responda somente com base no contexto recuperado.\n- Se nao houver informacao suficiente, use a frase padrao de insuficiencia.\n- Seja direto e tecnico.\n- Evite especulacao e respostas genericas.\n- Se possivel, mencione a fonte usando os identificadores do contexto.\n\nResposta:"""
