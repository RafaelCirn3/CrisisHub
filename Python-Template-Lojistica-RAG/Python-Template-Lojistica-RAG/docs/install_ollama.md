# Baixe os modelos necessários (CPU/GPU compatível)
ollama pull gemma3
ollama pull nomic-embed-text

# Verifique se o serviço está rodando na porta 11434
curl http://localhost:11434/api/tags