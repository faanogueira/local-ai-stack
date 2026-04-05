#!/usr/bin/env bash
# =============================================================================
# start.sh — inicializa o ambiente e sobe o frontend Streamlit
# Execute após o backend já estar rodando (backend/start.sh)
# =============================================================================

set -e

VENV_DIR=".venv"
PORT=8501

echo ""
echo "============================================"
echo "  Local AI Stack — Frontend"
echo "============================================"
echo ""

if [ ! -d "$VENV_DIR" ]; then
    echo "[1/2] Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
else
    echo "[1/2] Ambiente virtual já existe."
fi

source "$VENV_DIR/bin/activate"

echo "[2/2] Instalando dependências..."
pip install -q -r requirements.txt

echo ""
echo "  Interface disponível em: http://localhost:$PORT"
echo "  Certifique-se de que o backend está rodando em: http://localhost:8000"
echo ""

streamlit run app.py --server.port $PORT --server.headless true
