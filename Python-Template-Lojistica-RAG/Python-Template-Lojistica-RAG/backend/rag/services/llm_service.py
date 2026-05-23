from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

import httpx

from backend.rag.prompts.templates import SYSTEM_PROMPT


@dataclass(slots=True)
class LLMClientConfig:
    """Configuration for the LLM backend."""

    provider: str = os.getenv("LLM_PROVIDER", "ollama")
    model: str = os.getenv("LLM_MODEL", "gemma3")
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "700"))


class LLMClient(Protocol):
    def generate(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        raise NotImplementedError


def _extract_fallback_answer(prompt: str) -> str:
    """Create a deterministic offline answer when the model backend is unavailable."""

    context_marker = "Contexto recuperado:\n"
    question_marker = "\n\nPergunta do usuario:\n"

    if context_marker not in prompt or question_marker not in prompt:
        return "Não foram encontradas informações suficientes nos documentos fornecidos."

    context_section = prompt.split(context_marker, 1)[1].split(question_marker, 1)[0].strip()
    if not context_section or context_section == "Nenhum contexto recuperado.":
        return "Não foram encontradas informações suficientes nos documentos fornecidos."

    lines = [line.strip() for line in context_section.splitlines() if line.strip()]
    excerpts = [line for line in lines if line.startswith("[")][:3]

    if not excerpts:
        excerpts = lines[:3]

    if not excerpts:
        return "Não foram encontradas informações suficientes nos documentos fornecidos."

    body = "\n".join(f"- {excerpt}" for excerpt in excerpts)
    return f"Com base nos documentos analisados, encontrei os seguintes trechos relevantes:\n{body}"


class OllamaLLMClient:
    """Talk to an Ollama server using the generate endpoint."""

    def __init__(self, config: LLMClientConfig):
        self.config = config

    def generate(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        payload = {
            "model": self.config.model,
            "prompt": f"{system_prompt}\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            },
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(f"{self.config.base_url.rstrip('/')}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
            answer = str(data.get("response", "")).strip()
            return answer or _extract_fallback_answer(prompt)
        except (httpx.HTTPError, OSError):
            return _extract_fallback_answer(prompt)


class OpenAICompatibleLLMClient:
    """Talk to OpenAI or any compatible chat-completions endpoint."""

    def __init__(self, config: LLMClientConfig):
        self.config = config

    def generate(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(f"{self.config.openai_base_url.rstrip('/')}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, OSError):
            return _extract_fallback_answer(prompt)

        choices = data.get("choices", [])
        if not choices:
            return _extract_fallback_answer(prompt)
        message = choices[0].get("message", {})
        answer = str(message.get("content", "")).strip()
        return answer or _extract_fallback_answer(prompt)


def create_default_llm_client(config: LLMClientConfig | None = None) -> LLMClient:
    """Choose the best available LLM backend from environment settings."""

    resolved = config or LLMClientConfig()
    provider = resolved.provider.lower().strip()

    if provider in {"openai", "openai-compatible", "chat-completions"}:
        return OpenAICompatibleLLMClient(resolved)

    if resolved.api_key:
        return OpenAICompatibleLLMClient(resolved)

    return OllamaLLMClient(resolved)
