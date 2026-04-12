# =============================================================================
# Backend — API REST para chat com LLM local via Ollama
# Stack: FastAPI + httpx + SSE (Server-Sent Events para streaming)
#
# Endpoints:
#   POST /chat          — resposta completa (síncrono)
#   POST /chat/stream   — resposta em streaming (SSE)
#   GET  /models        — lista modelos disponíveis no Ollama
#   GET  /health        — status do servidor e do Ollama
#   DELETE /session/{id} — limpa histórico de uma sessão
# =============================================================================

import uuid
import json
import httpx
import asyncio
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL   = "qwen3.5-fast"   # modelo otimizado para CPU (ver Modelfile na raiz)
MAX_HISTORY     = 20    # máximo de turnos por sessão (evita context overflow)

# Calcula o número de threads ideal (metade dos núcleos lógicos, min 1, max 8)
CPU_THREADS = max(1, min(8, os.cpu_count() // 2)) if os.cpu_count() else 4

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Armazenamento em memória das sessões {session_id: [messages]}
sessions: dict[str, list[dict]] = {}


# =============================================================================
# LIFESPAN — verifica conexão com Ollama na inicialização
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando API — verificando conexão com Ollama...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            modelos = [m["name"] for m in resp.json().get("models", [])]
            logger.info(f"Ollama conectado. Modelos disponíveis: {modelos}")
    except Exception as e:
        logger.warning(f"Ollama não respondeu na inicialização: {e}")
    yield
    logger.info("API encerrada.")


# =============================================================================
# APLICAÇÃO
# =============================================================================

app = FastAPI(
    title="Local LLM Chat API",
    description="API para chat com modelos locais via Ollama",
    version="1.0.0",
    lifespan=lifespan,
)

# Permite requisições de qualquer origem (necessário para frontend separado)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# SCHEMAS
# =============================================================================

class ChatRequest(BaseModel):
    message: str                          = Field(..., min_length=1)
    session_id: Optional[str]            = Field(default=None)
    model: str                            = Field(default=DEFAULT_MODEL)
    system_prompt: Optional[str]         = Field(default=None)
    temperature: float                    = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int                       = Field(default=512, ge=64, le=8192)  # reduzido de 2048 para 512

class ChatResponse(BaseModel):
    session_id: str
    response: str
    model: str
    tokens_used: Optional[int]
    timestamp: str


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_or_create_session(session_id: Optional[str]) -> str:
    """Retorna o session_id existente ou cria um novo."""
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = []
        logger.info(f"Nova sessão criada: {session_id}")
    return session_id


def build_messages(
    session_id: str,
    user_message: str,
    system_prompt: Optional[str],
) -> list[dict]:
    """Monta a lista de mensagens com histórico + nova mensagem do usuário."""
    messages = []

    # System prompt no início, se fornecido
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # Histórico da sessão (limitado a MAX_HISTORY turnos)
    history = sessions[session_id][-MAX_HISTORY:]
    messages.extend(history)

    # Nova mensagem
    messages.append({"role": "user", "content": user_message})
    return messages


def update_history(session_id: str, user_message: str, assistant_reply: str):
    """Adiciona o par (user, assistant) ao histórico da sessão."""
    sessions[session_id].append({"role": "user",      "content": user_message})
    sessions[session_id].append({"role": "assistant", "content": assistant_reply})


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Verifica se a API e o Ollama estão operacionais."""
    ollama_ok = False
    modelos   = []

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp   = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            modelos = [m["name"] for m in resp.json().get("models", [])]
            ollama_ok = True
    except Exception as e:
        logger.warning(f"Health check — Ollama indisponível: {e}")

    return {
        "api":     "online",
        "ollama":  "online" if ollama_ok else "offline",
        "models":  modelos,
        "sessions_active": len(sessions),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/models")
async def list_models():
    """Lista todos os modelos disponíveis no Ollama local."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            modelos = resp.json().get("models", [])
            return {
                "models": [
                    {
                        "name":     m["name"],
                        "size_gb":  round(m.get("size", 0) / 1e9, 2),
                        "modified": m.get("modified_at", ""),
                    }
                    for m in modelos
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama indisponível: {e}")


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Envia uma mensagem e retorna a resposta completa do modelo.
    Mantém histórico por session_id.
    """
    session_id = get_or_create_session(req.session_id)
    messages   = build_messages(session_id, req.message, req.system_prompt)

    payload = {
        "model":    req.model,
        "messages": messages,
        "stream":   False,
        "options": {
            "temperature": req.temperature,
            "num_predict": req.max_tokens,
            "num_ctx":     2048,
            "num_thread":  CPU_THREADS,
        },
    }


    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout na resposta do modelo.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Erro do Ollama: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    assistant_reply = data["message"]["content"]
    tokens_used     = data.get("eval_count")

    update_history(session_id, req.message, assistant_reply)
    logger.info(f"[{session_id[:8]}] {req.model} — {tokens_used} tokens")

    return ChatResponse(
        session_id  = session_id,
        response    = assistant_reply,
        model       = req.model,
        tokens_used = tokens_used,
        timestamp   = datetime.now().isoformat(),
    )


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    Envia uma mensagem e retorna a resposta em streaming (Server-Sent Events).
    Ideal para interfaces que exibem tokens em tempo real.
    """
    session_id = get_or_create_session(req.session_id)
    messages   = build_messages(session_id, req.message, req.system_prompt)

    payload = {
        "model":    req.model,
        "messages": messages,
        "stream":   True,
        "options": {
            "temperature": req.temperature,
            "num_predict": req.max_tokens,
            "num_ctx":     2048,
            "num_thread":  CPU_THREADS,
        },
    }

    async def event_generator():
        full_reply = ""

        # Envia o session_id como primeiro evento
        yield f"data: {json.dumps({'session_id': session_id, 'type': 'start'})}\n\n"

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_BASE_URL}/api/chat",
                    json=payload,
                ) as response:
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            full_reply += token

                            yield f"data: {json.dumps({'token': token, 'type': 'token'})}\n\n"

                            # Último chunk — salva histórico e encerra
                            if chunk.get("done"):
                                update_history(session_id, req.message, full_reply)
                                yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
                                break

                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'detail': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # necessário para nginx/proxies
        },
    )


@app.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """Retorna o histórico de mensagens de uma sessão."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return {
        "session_id": session_id,
        "messages":   sessions[session_id],
        "total":      len(sessions[session_id]),
    }


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Limpa o histórico de uma sessão (inicia nova conversa)."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    sessions[session_id] = []
    logger.info(f"Histórico limpo: {session_id}")
    return {"message": "Histórico limpo com sucesso.", "session_id": session_id}


@app.delete("/sessions")
async def clear_all_sessions():
    """Limpa todas as sessões ativas (uso administrativo)."""
    total = len(sessions)
    sessions.clear()
    return {"message": f"{total} sessão(ões) removida(s)."}
