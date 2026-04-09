#!/usr/bin/env bash
# =============================================================================
# start.sh — inicializa o ambiente e sobe o servidor FastAPI
# =============================================================================

set -e

VENV_DIR=".venv"
PORT=8000

echo ""
echo "============================================"
echo "  Local LLM Chat — Backend"
echo "============================================"
echo ""

if [ ! -d "$VENV_DIR" ]; then
    echo "[1/3] Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
else
    echo "[1/3] Ambiente virtual já existe."
fi

source "$VENV_DIR/bin/activate"

echo "[2/3] Instalando dependências..."
pip install -q -r requirements.txt

echo "[3/3] Verificando Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "      Ollama OK."
else
    echo ""
    echo "  ⚠️  Ollama não está rodando."
    echo "      Inicie com: ollama serve"
    echo "      E em outro terminal: ollama pull qwen3.5:4b"
    echo ""
fi

echo ""
echo "  Servidor disponível em: http://localhost:$PORT"
echo "  Documentação (Swagger): http://localhost:$PORT/docs"
echo ""

uvicorn api:app --host 0.0.0.0 --port $PORT --reload
