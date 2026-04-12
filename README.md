# 🤖 Local AI Stack

> Stack completa para chat com **LLMs locais** via Ollama — sem cloud, sem custos de API, sem envio de dados externos.  
> Backend em **FastAPI** · Frontend em **Streamlit** · Modelo padrão: **Qwen3.5:4b**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-v0.1.48-black?style=flat)
![License](https://img.shields.io/badge/License-MIT-8B1A1A?style=flat)

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Execução](#instalação-e-execução)
  - [▶ Execução rápida (recomendado)](#-execução-rápida-recomendado)
  - [▶ Execução manual](#-execução-manual)
- [Recursos de Performance](#recursos-de-performance)
- [Endpoints da API](#endpoints-da-api)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Referências](#referências)

---

## Visão Geral

O **Local AI Stack** é uma aplicação de chat com modelos de linguagem que roda inteiramente na máquina local. Esta versão foi otimizada para máxima velocidade em CPUs domésticas, utilizando uma versão estável do Ollama e suporte a streaming de tokens.

| Camada | Tecnologia | Função |
|---|---|---|
| **LLM Runtime** | Ollama (v0.1.48) | Serve o modelo localmente com alta performance em CPU |
| **Backend** | FastAPI + SSE | Gerencia sessões, histórico e streaming em tempo real |
| **Frontend** | Streamlit | Interface de chat com suporte a visualização progressiva |
| **Modelo padrão** | Qwen3.5:4b | Otimizado para hardware com 16 GB RAM sem GPU |

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                     Navegador                           │
│              http://localhost:8501                      │
│                                                         │
│              ┌─────────────────┐                        │
│              │  Streamlit UI   │                        │
│              │ (Streaming SSE) │                        │
│              └────────┬────────┘                        │
└───────────────────────┼─────────────────────────────────┘
                        │ HTTP Streaming
                        ▼
┌─────────────────────────────────────────────────────────┐
│              http://localhost:8000                      │
│                                                         │
│              ┌─────────────────┐                        │
│              │   FastAPI API   │                        │
│              │  (Gerenciador)  │                        │
│              │                 │                        │
│              │  • /chat        │                        │
│              │  • /chat/stream │◄─── Suporte a Tokens   │
│              │  • /models      │     em tempo real      │
│              │  • /health      │                        │
│              └────────┬────────┘                        │
└───────────────────────┼─────────────────────────────────┘
                        │ HTTP
                        ▼
┌─────────────────────────────────────────────────────────┐
│              http://localhost:11434                     │
│                                                         │
│              ┌─────────────────┐                        │
│              │ Ollama v0.1.48  │                        │
│              │  (Performance)  │                        │
│              └─────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

**Fluxo:** `Usuário digita` → `Streamlit` → `FastAPI (gerencia sessão)` → `Ollama (infere)` → `Streaming de tokens retorna em tempo real`

---

## Pré-requisitos

- Python **3.10+**
- Conexão com internet apenas na primeira execução para baixar o binário e o modelo.

---

## Instalação e Execução

### ▶ Execução rápida (recomendado)

Um único comando inicializa toda a stack automaticamente. O script prepara a versão estável do Ollama (0.1.48) localmente, garantindo que você não sofra com a lentidão das versões mais recentes (0.20+).

**Linux:**
```bash
bash linux_start_all.sh
```

**Windows:**
```batch
windows_start_all.bat
```

O script realiza automaticamente:
1. Download do binário estável do Ollama (v0.1.48).
2. Configuração do servidor Ollama em background.
3. Pull do modelo `qwen3.5:4b` e criação do `qwen3.5-fast`.
4. Instalação de dependências do Backend e Frontend em ambientes virtuais.
5. Abertura automática da interface no navegador.

![Agente em funcionamento](/backend/img/run_agent.png)

---

### ▶ Execução manual

Caso prefira configurar manualmente:

1. **Baixar Ollama 0.1.48:** [Releases Oficiais](https://github.com/ollama/ollama/releases/tag/v0.1.48)
2. **Iniciar Backend:**
   ```bash
   cd backend && python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn api:app --port 8000
   ```
3. **Iniciar Frontend:**
   ```bash
   cd frontend && python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   streamlit run app.py
   ```

---

## Recursos de Performance

- **Ollama Downgrade:** Versões acima da 0.20 apresentam degradação de performance em algumas CPUs. Este projeto utiliza a v0.1.48 que é até 2.5x mais rápida em inferência via CPU.
- **Streaming de Tokens:** O frontend utiliza Server-Sent Events (SSE) para exibir o texto conforme é gerado, reduzindo o tempo de espera percebido.
- **Contexto Otimizado:** O `Modelfile` reduz o contexto para 2048 tokens para economizar RAM e CPU.

---

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Status da API e do Ollama |
| `GET` | `/models` | Modelos disponíveis no Ollama |
| `POST` | `/chat` | Chat com resposta completa |
| `POST` | `/chat/stream` | Chat com streaming (SSE) |

---

## Estrutura do Projeto

```
local-ai-stack/
├── linux_start_all.sh      # Inicialização automática Linux
├── windows_start_all.bat   # Inicialização automática Windows
├── backend/
│   ├── ollama              # Binário estável (gerado no start)
│   ├── api.py              # API FastAPI com SSE
│   └── test_api.sh         # Testes de performance
├── frontend/
│   └── app.py              # Interface Streamlit com Streaming
└── README.md
```

---

## Referências

- [Ollama v0.1.48 Releases](https://github.com/ollama/ollama/releases/tag/v0.1.48)
- [Qwen3.5 4B Model](https://ollama.com/library/qwen2.5:4b)
- [Streamlit Streaming API](https://docs.streamlit.io/develop/api-reference/write-magic/st.write_stream)

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
