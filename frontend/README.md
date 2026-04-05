# 🖥️ Frontend — Local AI Stack

> Interface de chat construída com **Streamlit**, conectada ao backend FastAPI via HTTP.  
> Identidade visual em vermelho vinho, preto e branco — 100% customizada via CSS e tema nativo.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Interface](#interface)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Execução](#execução)
- [Configuração Avançada](#configuração-avançada)
- [Estrutura](#estrutura)

---

## Visão Geral

O frontend consome a API REST do backend e oferece uma experiência de chat completa, com controle de parâmetros do modelo, histórico de sessão e métricas em tempo real — tudo rodando localmente no browser.

| Recurso | Detalhe |
|---|---|
| Framework | Streamlit 1.41 |
| HTTP Client | httpx (assíncrono) |
| Tema | Dark · vermelho vinho `#8B1A1A` · preto `#0D0D0D` |
| Fonte | Inter (Google Fonts) |
| Backend | FastAPI em `http://localhost:8000` |

---

## Interface

**Sidebar**

| Componente | Função |
|---|---|
| Status badge | Indica se o Ollama está online/offline |
| Seletor de modelo | Lista os modelos instalados no Ollama |
| Temperature | Controla criatividade das respostas (0.0 – 2.0) |
| Max Tokens | Limite de tamanho da resposta (256 – 4096) |
| System Prompt | Define personalidade e contexto do modelo |
| Métricas | Contador de mensagens e tokens da sessão |
| Limpar conversa | Reseta histórico local e no backend |

**Área de chat**

- Balões diferenciados por papel (usuário / assistente)
- Mensagem de boas-vindas quando o histórico está vazio
- Indicador de carregamento durante geração da resposta
- Alerta visual quando o backend está offline

---

## Pré-requisitos

- Python **3.10+**
- Backend rodando em `http://localhost:8000` → veja `../backend/README.md`

---

## Instalação

```bash
cd frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Execução

```bash
bash start.sh
```

Acesse em: `http://localhost:8501`

Ou diretamente:

```bash
streamlit run app.py --server.port 8501
```

---

## Configuração Avançada

### Alterar URL do backend

Em `app.py`, localize e edite:

```python
BACKEND_URL = "http://localhost:8000"
```

### Alterar paleta de cores

Em `.streamlit/config.toml`:

```toml
[theme]
primaryColor             = "#8B1A1A"   # vermelho vinho
backgroundColor          = "#0D0D0D"   # preto
secondaryBackgroundColor = "#1A1A1A"   # cinza escuro
textColor                = "#F5F5F5"   # branco
```

### Alterar system prompt padrão

Em `app.py`, localize o argumento `value` do `st.text_area` do system prompt e edite conforme seu caso de uso.

---

## Estrutura

```
frontend/
├── app.py              # Aplicação Streamlit principal
├── requirements.txt    # Dependências Python
├── start.sh            # Script de inicialização
└── .streamlit/
    └── config.toml     # Tema e configurações do Streamlit
```

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
