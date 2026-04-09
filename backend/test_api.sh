#!/usr/bin/env bash
# =============================================================================
# test_api.sh — testa os endpoints do backend manualmente
# Execute após o servidor estar rodando: bash start.sh
# =============================================================================

BASE="http://localhost:8000"
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

echo ""
echo -e "${CYAN}=== TESTE 1: Health Check ===${NC}"
curl -s "$BASE/health" | python3 -m json.tool

echo ""
echo -e "${CYAN}=== TESTE 2: Listar Modelos ===${NC}"
curl -s "$BASE/models" | python3 -m json.tool

echo ""
echo -e "${CYAN}=== TESTE 3: Chat (resposta completa) ===${NC}"
RESP=$(curl -s -X POST "$BASE/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "O que é um Large Language Model? Responda em 2 frases.",
    "model": "qwen3.5-fast",
    "temperature": 0.7
  }')
echo "$RESP" | python3 -m json.tool

SESSION_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

echo ""
echo -e "${CYAN}=== TESTE 4: Chat com histórico (mesmo session_id) ===${NC}"
curl -s -X POST "$BASE/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Dê um exemplo prático de aplicação no setor bancário.\",
    \"session_id\": \"$SESSION_ID\",
    \"model\": \"qwen3.5-fast\"
  }" | python3 -m json.tool

echo ""
echo -e "${CYAN}=== TESTE 5: Histórico da sessão ===${NC}"
curl -s "$BASE/session/$SESSION_ID" | python3 -m json.tool

echo ""
echo -e "${GREEN}Testes concluídos.${NC}"
echo ""
