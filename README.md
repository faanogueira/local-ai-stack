# 🤖 Local AI Stack

> Stack completa para chat com **LLMs locais** via Ollama — sem cloud, sem custos de API, sem envio de dados externos.  
> Backend em **FastAPI** · Frontend em **Streamlit** · Modelo padrão: **Qwen3.5-fast** (otimizado para CPU)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local-black?style=flat)
![License](https://img.shields.io/badge/License-MIT-8B1A1A?style=flat)

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Execução](#execução)
  - [▶ Execução rápida (recomendado)](#-execução-rápida-recomendado)
  - [▶ Execução manual](#-execução-manual)
- [Endpoints da API](#endpoints-da-api)
- [Requisitos de Hardware](#requisitos-de-hardware)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Referências](#referências)

---

## Visão Geral

O **Local AI Stack** é uma aplicação de chat com modelos de linguagem que roda inteiramente na máquina local. Nenhum dado é enviado para servidores externos — ideal para uso profissional com informações sensíveis ou para desenvolvimento e estudo de LLMs sem custos de API.

| Camada | Tecnologia | Função |
|---|---|---|
| **LLM Runtime** | Ollama | Serve o modelo localmente com API REST |
| **Backend** | FastAPI + httpx | Gerencia sessões, histórico e roteamento |
| **Frontend** | Streamlit | Interface de chat com identidade visual customizada |
| **Modelo padrão** | qwen3.5-fast | Versão otimizada do Qwen3.5:4b para CPU sem GPU |

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                     Navegador                           │
│              http://localhost:8501                      │
│                                                         │
│              ┌─────────────────┐                        │
│              │  Streamlit UI   │                        │
│              │   (frontend)    │                        │
│              └────────┬────────┘                        │
└───────────────────────┼─────────────────────────────────┘
                        │ HTTP REST
                        ▼
┌─────────────────────────────────────────────────────────┐
│              http://localhost:8000                      │
│                                                         │
│              ┌─────────────────┐                        │
│              │   FastAPI API   │                        │
│              │   (backend)     │                        │
│              │                 │                        │
│              │  • /chat        │                        │
│              │  • /chat/stream │                        │
│              │  • /models      │                        │
│              │  • /health      │                        │
│              └────────┬────────┘                        │
└───────────────────────┼─────────────────────────────────┘
                        │ HTTP
                        ▼
┌─────────────────────────────────────────────────────────┐
│              http://localhost:11434                     │
│                                                         │
│              ┌─────────────────┐                        │
│              │     Ollama      │                        │
│              │  qwen3.5-fast   │                        │
│              └─────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

**Fluxo:** `Usuário digita` → `Streamlit` → `FastAPI (gerencia sessão)` → `Ollama (infere)` → `resposta retorna pela mesma cadeia`

---

## Pré-requisitos

- Python **3.10+**
- [Ollama](https://ollama.com/download) instalado
- Conexão com internet apenas para baixar o modelo (execução é 100% offline)

---

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/faanogueira/local-ai-stack.git
cd local-ai-stack
```

### 2. Instalar o Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:** baixe e instale o executável em [ollama.com/download](https://ollama.com/download)

### 3. Baixar o modelo base e criar o modelo otimizado

```bash
ollama pull qwen3.5:4b
ollama create qwen3.5-fast -f Modelfile
```

> O `Modelfile` está na raiz do repositório e aplica otimizações de velocidade para hardware sem GPU — redução de contexto, threads explícitos e thinking mode desativado.

### 4. Instalar dependências do backend

**Linux:**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 5. Instalar dependências do frontend

**Linux:**
```bash
cd ../frontend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
cd ..\frontend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

---

## Execução

### ▶ Execução rápida (recomendado)

Um único arquivo inicializa toda a stack automaticamente — Ollama, modelo, backend e frontend.

**Linux:**
```bash
chmod +x start_all.sh
bash start_all.sh
```

**Windows:**
```
start_all.bat
```

> No Windows, o Ollama precisa estar instalado manualmente antes de executar o script.  
> Download: [ollama.com/download](https://ollama.com/download)

O script realiza automaticamente:
1. Verifica (e instala, no Linux) o Ollama
2. Sobe o servidor Ollama em background
3. Baixa o `qwen3.5:4b` se necessário e cria o modelo `qwen3.5-fast` via Modelfile
4. Cria os ambientes virtuais, instala as dependências e sobe o backend
5. Instala as dependências do frontend e abre o navegador automaticamente

---

### ▶ Execução manual

Abra **três terminais** e execute em ordem:

**Linux:**
```bash
# Terminal 1 — Ollama
ollama serve

# Terminal 2 — Backend
cd backend && bash start.sh

# Terminal 3 — Frontend
cd frontend && bash start.sh
```

**Windows:**
```bash
# Terminal 1 — Ollama
ollama serve

# Terminal 2 — Backend
cd backend
.venv\Scripts\uvicorn api:app --host 0.0.0.0 --port 8000

# Terminal 3 — Frontend
cd frontend
.venv\Scripts\streamlit run app.py --server.port 8501
```

---

| Serviço | URL |
|---|---|
| Interface de chat | http://localhost:8501 |
| API REST | http://localhost:8000 |
| Documentação da API (Swagger) | http://localhost:8000/docs |

---

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Status da API e do Ollama |
| `GET` | `/models` | Modelos disponíveis no Ollama |
| `POST` | `/chat` | Chat com resposta completa |
| `POST` | `/chat/stream` | Chat com streaming (SSE) |
| `GET` | `/session/{id}` | Histórico de uma sessão |
| `DELETE` | `/session/{id}` | Limpa histórico da sessão |

Exemplo de requisição:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "O que é um Large Language Model?",
    "model": "qwen3.5-fast",
    "temperature": 0.7
  }'
```

---

## Requisitos de Hardware

| Componente | Mínimo | Testado |
|---|---|---|
| **RAM** | 8 GB | 16 GB |
| **CPU** | x86-64 dual-core | Intel i5 8ª geração |
| **GPU** | Não obrigatória | — |
| **Armazenamento** | 5 GB livres | SSD recomendado |
| **SO** | Ubuntu 20.04+ / Windows 10+ | Ubuntu 24.04 LTS |

> Sem GPU dedicada, o modelo roda via CPU. No hardware de referência (i5-8365U, 16 GB RAM), o `qwen3.5-fast` gera entre 5–12 tokens/segundo — otimizado via Modelfile com contexto reduzido e threads explícitos.

---

## Estrutura do Projeto

```
local-ai-stack/
├── Modelfile               # Configuração otimizada do modelo para CPU
├── start_all.sh            # Execução rápida — Linux
├── start_all.bat           # Execução rápida — Windows
├── .gitignore
├── backend/
│   ├── api.py              # API FastAPI — endpoints, sessões, streaming
│   ├── requirements.txt
│   ├── start.sh
│   ├── test_api.sh         # Testes dos endpoints via curl
│   └── README.md
├── frontend/
│   ├── app.py              # Interface Streamlit
│   ├── requirements.txt
│   ├── start.sh
│   ├── README.md
│   └── .streamlit/
│       └── config.toml     # Tema customizado
└── README.md
```

---

## Referências

- [Ollama — Documentação oficial](https://ollama.com)
- [Qwen3.5 — Hugging Face](https://huggingface.co/Qwen/Qwen3.5-4B)
- [FastAPI — Documentação](https://fastapi.tiangolo.com)
- [Streamlit — Documentação](https://docs.streamlit.io)

---

## 👤 Autor

<div>
  <p>Developed by <b>Fábio Nogueira</b></p>
</div>
<p>
<a href="https://www.linkedin.com/in/faanogueira/" target="_blank"><img style="padding-right: 10px;" src="https://img.icons8.com/?size=100&id=13930&format=png&color=000000" width="80"></a>
<a href="https://github.com/faanogueira" target="_blank"><img style="padding-right: 10px;" src="https://img.icons8.com/?size=100&id=AZOZNnY73haj&format=png&color=000000" width="80"></a>
<a href="https://api.whatsapp.com/send?phone=5571983937557" target="_blank"><img style="padding-right: 10px;" src="https://img.icons8.com/?size=100&id=16713&format=png&color=000000" width="80"></a>
<a href="mailto:faanogueira@gmail.com"><img style="padding-right: 10px;" src="https://img.icons8.com/?size=100&id=P7UIlhbpWzZm&format=png&color=000000" width="80"></a>
</p>

---
