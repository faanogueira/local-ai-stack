# Backend — Local AI Stack

API REST construída com **FastAPI** para servir como camada de comunicação entre qualquer frontend e modelos LLM locais via **Ollama**.

---

## Stack

| Componente | Tecnologia |
|---|---|
| Framework | FastAPI 0.115 |
| Servidor | Uvicorn (ASGI) |
| HTTP Client | httpx (assíncrono) |
| LLM Backend | Ollama (local) |
| Modelo padrão | qwen3.5-fast (otimizado para CPU) |

---

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Status da API e do Ollama |
| `GET` | `/models` | Modelos disponíveis no Ollama |
| `POST` | `/chat` | Chat com resposta completa |
| `POST` | `/chat/stream` | Chat com streaming (SSE) |
| `GET` | `/session/{id}` | Histórico de uma sessão |
| `DELETE` | `/session/{id}` | Limpa histórico da sessão |
| `DELETE` | `/sessions` | Limpa todas as sessões |

Documentação interativa: `http://localhost:8000/docs`

---

## Instalação e execução

### Pré-requisitos

```bash
# Ollama instalado e rodando
ollama serve

# Modelo base baixado
ollama pull qwen3.5:4b

# Modelo otimizado criado (na raiz do repositório)
ollama create qwen3.5-fast -f ../Modelfile
```

### Subir o servidor

```bash
cd backend
bash start.sh
```

### Testar os endpoints

```bash
bash test_api.sh
```

---

## Otimizações de performance (CPU)

O modelo `qwen3.5-fast` é criado a partir do `Modelfile` na raiz do repositório com os seguintes parâmetros otimizados para hardware sem GPU:

| Parâmetro | Valor | Motivo |
|---|---|---|
| `num_ctx` | 2048 | Reduz janela de contexto — principal ganho de velocidade |
| `num_thread` | 8 | Usa todos os threads do i5-8365U |
| `num_predict` | 512 | Limita tamanho da resposta para chat |
| `think` | False | Desativa reasoning mode desnecessário para chat |

---

## Exemplo de uso (Python)

```python
import httpx

resp = httpx.post("http://localhost:8000/chat", json={
    "message": "Explique o que é um modelo de linguagem.",
    "model": "qwen3.5-fast",
    "temperature": 0.7,
})
data = resp.json()
print(data["response"])

# Continuar a conversa com o mesmo session_id
session_id = data["session_id"]
resp2 = httpx.post("http://localhost:8000/chat", json={
    "message": "Dê um exemplo de aplicação bancária.",
    "session_id": session_id,
})
print(resp2.json()["response"])
```

---

## Estrutura

```
backend/
├── api.py            # Aplicação FastAPI principal
├── requirements.txt  # Dependências Python
├── start.sh          # Script de inicialização
└── test_api.sh       # Testes dos endpoints via curl
```

---

## Parâmetros do endpoint /chat

```json
{
  "message":       "sua pergunta aqui",
  "session_id":    "opcional — mantém histórico entre chamadas",
  "model":         "qwen3.5-fast",
  "system_prompt": "opcional — define personalidade/contexto do modelo",
  "temperature":   0.7,
  "max_tokens":    512
}
```
