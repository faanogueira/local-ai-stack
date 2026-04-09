#!/usr/bin/env bash
# =============================================================================
# start_all.sh — inicializa toda a stack: Ollama + Backend + Frontend
# Execute uma única vez a partir da raiz do repositório:
#   bash start_all.sh
# =============================================================================

set +e  # Não encerra o script se um comando falhar

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ROOT_DIR=$(pwd)

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}        Local AI Stack — Inicializando      ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# =============================================================================
# PASSO 1 — Verificar Ollama instalado
# =============================================================================

echo -e "${YELLOW}[1/4] Verificando Ollama...${NC}"

if ! command -v ollama &> /dev/null; then
    echo -e "${RED}  Ollama não encontrado. Instalando...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo -e "${GREEN}  Ollama já instalado.${NC}"
fi

# =============================================================================
# PASSO 2 — Iniciar servidor Ollama em background
# =============================================================================

echo -e "${YELLOW}[2/4] Iniciando servidor Ollama...${NC}"

if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}  Ollama já está rodando.${NC}"
else
    ollama serve > /tmp/ollama.log 2>&1 &
    disown $!
    sleep 3
    echo -e "${GREEN}  Ollama iniciado em background.${NC}"
fi

# Verifica se o modelo está baixado
echo -e "${YELLOW}      Verificando modelo qwen3.5:4b...${NC}"
if ollama list | grep -q "qwen3.5:4b"; then
    echo -e "${GREEN}  Modelo já disponível.${NC}"
else
    echo -e "${YELLOW}  Baixando qwen3.5:4b (pode levar alguns minutos)...${NC}"
    ollama pull qwen3.5:4b
fi

# =============================================================================
# PASSO 3 — Iniciar Backend em background
# =============================================================================

echo -e "${YELLOW}[3/4] Iniciando Backend (FastAPI)...${NC}"

cd "$ROOT_DIR/backend"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

.venv/bin/pip install -q -r requirements.txt

# Mata instância anterior se houver
pkill -f "uvicorn api:app" 2>/dev/null || true
sleep 1

# Sobe o backend desacoplado do script (nohup + disown)
nohup .venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
disown $!

cd "$ROOT_DIR"

# Aguarda até 10 segundos pelo backend responder
echo -e "${YELLOW}      Aguardando backend inicializar...${NC}"
TRIES=0
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    TRIES=$((TRIES + 1))
    if [ $TRIES -ge 10 ]; then
        echo -e "${RED}  Backend não respondeu. Verifique /tmp/backend.log${NC}"
        break
    fi
    sleep 1
done

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}  Backend rodando em http://localhost:8000${NC}"
fi

# =============================================================================
# PASSO 4 — Iniciar Frontend (abre no navegador)
# =============================================================================

echo -e "${YELLOW}[4/4] Iniciando Frontend (Streamlit)...${NC}"

cd "$ROOT_DIR/frontend"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Stack inicializada com sucesso!           ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Interface: ${CYAN}http://localhost:8501${NC}"
echo -e "  API:       ${CYAN}http://localhost:8000${NC}"
echo -e "  Docs API:  ${CYAN}http://localhost:8000/docs${NC}"
echo ""
echo -e "  Pressione ${RED}Ctrl+C${NC} para encerrar o frontend."
echo ""

# Abre o navegador automaticamente após 3 segundos (tempo para o Streamlit subir)
sleep 3 && xdg-open http://localhost:8501 &

streamlit run app.py --server.port 8501 --server.headless true
