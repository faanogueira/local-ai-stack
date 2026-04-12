@echo off
REM =============================================================================
REM start_all.bat — inicializa toda a stack: Ollama + Backend + Frontend
REM Execute uma única vez a partir da raiz do repositório:
REM   start_all.bat
REM =============================================================================

title Local AI Stack

echo.
echo ============================================
echo        Local AI Stack — Inicializando
echo ============================================
echo.

REM =============================================================================
REM PASSO 1 — Preparar Ollama estável (0.1.48)
REM =============================================================================

echo [1/4] Preparando Ollama estavel (0.1.48)...
set "OLLAMA_BIN=%ROOT_DIR%backend\ollama.exe"

if not exist "%OLLAMA_BIN%" (
    echo   Baixando Ollama 0.1.48 para Windows...
    curl -L https://github.com/ollama/ollama/releases/download/v0.1.48/ollama-windows-amd64.zip -o ollama.zip
    echo   Extraindo... (requer tar ou powershell)
    powershell -Command "Expand-Archive -Path ollama.zip -DestinationPath backend -Force"
    del ollama.zip
)
echo   Ollama 0.1.48 pronto.

REM =============================================================================
REM PASSO 2 — Iniciar servidor Ollama em background
REM =============================================================================

echo [2/4] Iniciando servidor Ollama...

REM Tenta encerrar instancias anteriores para evitar conflitos
taskkill /F /IM ollama.exe >nul 2>&1
timeout /t 2 /nobreak >nul

set OLLAMA_HOST=127.0.0.1:11434
start "Ollama Server" /min "%OLLAMA_BIN%" serve

echo   Aguardando Ollama inicializar...
:wait_ollama
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set /a count+=1
    if %count% GTR 15 (
        echo   Erro: Ollama nao respondeu. Verifique backend\ollama.log
        exit /b 1
    )
    goto wait_ollama
)
echo   Ollama iniciado em background.

echo   Verificando modelos Ollama...

REM 1. Garante o modelo base
"%OLLAMA_BIN%" list | findstr "qwen3.5:4b" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   Baixando qwen3.5:4b (pode levar alguns minutos)...
    "%OLLAMA_BIN%" pull qwen3.5:4b
) else (
    echo   Modelo base qwen3.5:4b disponivel.
)

REM 2. Cria o modelo otimizado se nao existir
"%OLLAMA_BIN%" list | findstr "qwen3.5-fast" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "Modelfile" (
        echo   Criando modelo otimizado qwen3.5-fast...
        "%OLLAMA_BIN%" create qwen3.5-fast -f Modelfile
    ) else (
        echo   Aviso: Modelfile nao encontrado. Pulando criacao do qwen3.5-fast.
    )
) else (
    echo   Modelo otimizado qwen3.5-fast disponivel.
)


REM =============================================================================
REM PASSO 3 — Iniciar Backend em background
REM =============================================================================

echo [3/4] Iniciando Backend (FastAPI)...

cd backend

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
start "Backend FastAPI" /min cmd /c "uvicorn api:app --host 0.0.0.0 --port 8000"
call .venv\Scripts\deactivate.bat

cd ..
timeout /t 3 /nobreak >nul

curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   Backend rodando em http://localhost:8000
) else (
    echo   Backend pode estar iniciando ainda. Aguarde alguns segundos.
)

REM =============================================================================
REM PASSO 4 — Iniciar Frontend
REM =============================================================================

echo [4/4] Iniciando Frontend (Streamlit)...

cd frontend

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo ============================================
echo   Stack inicializada com sucesso!
echo ============================================
echo.
echo   Interface: http://localhost:8501
echo   API:       http://localhost:8000
echo   Docs API:  http://localhost:8000/docs
echo.
echo   Feche esta janela para encerrar o frontend.
echo.

REM Aguarda o Streamlit subir e abre o navegador
timeout /t 4 /nobreak >nul
start "" http://localhost:8501

streamlit run app.py --server.port 8501
