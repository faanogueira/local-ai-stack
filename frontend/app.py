# =============================================================================
# Frontend — Local AI Stack
# Interface de chat Streamlit conectada ao backend FastAPI + Ollama
#
# Execução:
#   streamlit run app.py
# =============================================================================

import time
import httpx
import streamlit as st

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

BACKEND_URL  = "http://localhost:8000"
DEFAULT_MODEL = "qwen3.5:4b"

st.set_page_config(
    page_title="Local AI Stack",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CSS CUSTOMIZADO — identidade visual vermelho vinho / preto / branco
# =============================================================================

st.markdown("""
<style>
    /* Importa fonte */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Remove padding padrão do topo */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }

    /* Header da aplicação */
    .app-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.75rem 0 1.5rem 0;
        border-bottom: 1px solid #2a2a2a;
        margin-bottom: 1.5rem;
    }
    .app-header h1 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #F5F5F5;
        margin: 0;
    }
    .app-header span {
        font-size: 0.8rem;
        color: #8B1A1A;
        font-weight: 500;
        background: #1f0808;
        padding: 2px 10px;
        border-radius: 20px;
        border: 1px solid #8B1A1A44;
    }

    /* Balão do usuário */
    .msg-user {
        display: flex;
        justify-content: flex-end;
        margin: 0.5rem 0;
    }
    .msg-user .bubble {
        background: #8B1A1A;
        color: #ffffff;
        padding: 0.65rem 1rem;
        border-radius: 16px 16px 4px 16px;
        max-width: 75%;
        font-size: 0.92rem;
        line-height: 1.5;
        box-shadow: 0 2px 8px #8B1A1A33;
    }

    /* Balão do assistente */
    .msg-assistant {
        display: flex;
        justify-content: flex-start;
        margin: 0.5rem 0;
    }
    .msg-assistant .bubble {
        background: #1A1A1A;
        color: #F0F0F0;
        padding: 0.65rem 1rem;
        border-radius: 16px 16px 16px 4px;
        max-width: 75%;
        font-size: 0.92rem;
        line-height: 1.6;
        border: 1px solid #2a2a2a;
    }

    /* Avatar */
    .avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .avatar-ai {
        background: #8B1A1A;
        color: white;
        margin-right: 8px;
    }
    .avatar-user {
        background: #2a2a2a;
        color: #aaa;
        margin-left: 8px;
    }

    /* Área de mensagens */
    .chat-area {
        min-height: 420px;
        padding: 0.5rem 0;
    }

    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
    }
    .status-online {
        background: #0a1f0a;
        color: #4caf50;
        border: 1px solid #4caf5044;
    }
    .status-offline {
        background: #1f0808;
        color: #ef5350;
        border: 1px solid #ef535044;
    }

    /* Sidebar label */
    .sidebar-section {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #555;
        margin: 1.2rem 0 0.4rem 0;
        font-weight: 600;
    }

    /* Métricas */
    .metric-row {
        display: flex;
        gap: 8px;
        margin-top: 0.5rem;
    }
    .metric-box {
        flex: 1;
        background: #1A1A1A;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 8px 10px;
        text-align: center;
    }
    .metric-box .value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #8B1A1A;
    }
    .metric-box .label {
        font-size: 0.68rem;
        color: #666;
        margin-top: 2px;
    }

    /* Input de chat */
    .stChatInput textarea {
        border-color: #2a2a2a !important;
    }
    .stChatInput textarea:focus {
        border-color: #8B1A1A !important;
        box-shadow: 0 0 0 2px #8B1A1A22 !important;
    }

    /* Botões */
    .stButton > button {
        border-color: #2a2a2a;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        border-color: #8B1A1A;
        color: #8B1A1A;
    }

    /* Divider */
    hr {
        border-color: #2a2a2a !important;
        margin: 0.8rem 0;
    }

    /* Esconde elementos desnecessários */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# FUNÇÕES DE COMUNICAÇÃO COM O BACKEND
# =============================================================================

def check_backend_health() -> dict:
    try:
        resp = httpx.get(f"{BACKEND_URL}/health", timeout=4)
        return resp.json()
    except Exception:
        return {"api": "offline", "ollama": "offline", "models": []}


def get_available_models() -> list[str]:
    try:
        resp = httpx.get(f"{BACKEND_URL}/models", timeout=4)
        return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return [DEFAULT_MODEL]


def send_message(
    message: str,
    session_id: str | None,
    model: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    payload = {
        "message":       message,
        "session_id":    session_id,
        "model":         model,
        "system_prompt": system_prompt or None,
        "temperature":   temperature,
        "max_tokens":    max_tokens,
    }
    resp = httpx.post(
        f"{BACKEND_URL}/chat",
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def clear_session_backend(session_id: str):
    try:
        httpx.delete(f"{BACKEND_URL}/session/{session_id}", timeout=4)
    except Exception:
        pass


# =============================================================================
# ESTADO DA SESSÃO
# =============================================================================

if "messages"       not in st.session_state:
    st.session_state.messages       = []
if "session_id"     not in st.session_state:
    st.session_state.session_id     = None
if "total_tokens"   not in st.session_state:
    st.session_state.total_tokens   = 0
if "total_messages" not in st.session_state:
    st.session_state.total_messages = 0


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:

    st.markdown("## ⚙️ Configurações")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Status do backend
    st.markdown('<p class="sidebar-section">Status</p>', unsafe_allow_html=True)
    health = check_backend_health()

    ollama_ok = health.get("ollama") == "online"
    badge_class = "status-online" if ollama_ok else "status-offline"
    badge_icon  = "●" if ollama_ok else "●"
    badge_label = "Ollama online" if ollama_ok else "Ollama offline"

    st.markdown(
        f'<div class="status-badge {badge_class}">{badge_icon} {badge_label}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<p class="sidebar-section">Modelo</p>', unsafe_allow_html=True)

    # Lista de modelos disponíveis
    available_models = health.get("models", [DEFAULT_MODEL]) or [DEFAULT_MODEL]
    selected_model = st.selectbox(
        label="Modelo",
        options=available_models,
        index=0,
        label_visibility="collapsed",
    )

    st.markdown('<p class="sidebar-section">Parâmetros</p>', unsafe_allow_html=True)

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Valores altos = respostas mais criativas. Valores baixos = mais precisas.",
    )

    max_tokens = st.slider(
        "Max Tokens",
        min_value=256,
        max_value=4096,
        value=2048,
        step=256,
        help="Tamanho máximo da resposta gerada.",
    )

    st.markdown('<p class="sidebar-section">System Prompt</p>', unsafe_allow_html=True)

    system_prompt = st.text_area(
        label="System Prompt",
        value="Você é um assistente especializado em Ciência de Dados e análise financeira. Responda de forma clara e técnica.",
        height=120,
        label_visibility="collapsed",
        help="Define a personalidade e contexto do modelo.",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Métricas da sessão
    st.markdown('<p class="sidebar-section">Sessão atual</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box">
            <div class="value">{st.session_state.total_messages}</div>
            <div class="label">Mensagens</div>
        </div>
        <div class="metric-box">
            <div class="value">{st.session_state.total_tokens:,}</div>
            <div class="label">Tokens</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Botão limpar conversa
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        if st.session_state.session_id:
            clear_session_backend(st.session_state.session_id)
        st.session_state.messages       = []
        st.session_state.session_id     = None
        st.session_state.total_tokens   = 0
        st.session_state.total_messages = 0
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Session ID para debug
    if st.session_state.session_id:
        st.markdown(
            f'<p class="sidebar-section">Session ID</p>'
            f'<code style="font-size:0.68rem;color:#555">{st.session_state.session_id[:18]}…</code>',
            unsafe_allow_html=True,
        )


# =============================================================================
# ÁREA PRINCIPAL
# =============================================================================

# Header
st.markdown("""
<div class="app-header">
    <h1>🤖 Local AI Stack</h1>
    <span>100% local · sem cloud</span>
</div>
""", unsafe_allow_html=True)

# Aviso se backend offline
if health.get("api") == "offline":
    st.error(
        "Backend offline. Certifique-se de que o servidor está rodando: `bash start.sh`",
        icon="🔴",
    )

# Mensagem de boas-vindas
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0; color: #444;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💬</div>
        <p style="font-size: 1rem; color: #555;">Inicie uma conversa abaixo.</p>
        <p style="font-size: 0.8rem; color: #333;">Modelo: <span style="color:#8B1A1A">qwen3.5:4b</span> · rodando localmente</p>
    </div>
    """, unsafe_allow_html=True)

# Exibe histórico de mensagens
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div class="bubble">{msg["content"]}</div>
            <div class="avatar avatar-user">você</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-assistant">
            <div class="avatar avatar-ai">AI</div>
            <div class="bubble">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# INPUT DO USUÁRIO
# =============================================================================

user_input = st.chat_input(
    placeholder="Digite sua mensagem…",
    disabled=(health.get("api") == "offline"),
)

if user_input:
    # Adiciona mensagem do usuário ao histórico local
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.total_messages += 1

    # Exibe a mensagem imediatamente
    st.markdown(f"""
    <div class="msg-user">
        <div class="bubble">{user_input}</div>
        <div class="avatar avatar-user">você</div>
    </div>
    """, unsafe_allow_html=True)

    # Indicador de carregamento
    with st.spinner(""):
        try:
            data = send_message(
                message       = user_input,
                session_id    = st.session_state.session_id,
                model         = selected_model,
                system_prompt = system_prompt,
                temperature   = temperature,
                max_tokens    = max_tokens,
            )

            reply      = data["response"]
            session_id = data["session_id"]
            tokens     = data.get("tokens_used") or 0

            # Atualiza estado
            st.session_state.session_id    = session_id
            st.session_state.total_tokens += tokens
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Exibe resposta
            st.markdown(f"""
            <div class="msg-assistant">
                <div class="avatar avatar-ai">AI</div>
                <div class="bubble">{reply}</div>
            </div>
            """, unsafe_allow_html=True)

        except httpx.TimeoutException:
            st.error("Timeout: o modelo demorou demais para responder. Tente reduzir o Max Tokens.")
        except Exception as e:
            st.error(f"Erro ao comunicar com o backend: {e}")

    st.rerun()
