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

REM Guarda o diretório raiz
set ROOT_DIR=%CD%

REM =============================================================================
REM PASSO 1 — Verificar Ollama instalado
REM =============================================================================

echo [1/4] Verificando Ollama...

where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   Ollama nao encontrado.
    echo   Acesse https://ollama.com/download e instale antes de continuar.
    echo.
    pause
    exit /b 1
) else (
    echo   Ollama encontrado.
)

REM =============================================================================
REM PASSO 2 — Iniciar servidor Ollama em background
REM =============================================================================

echo [2/4] Iniciando servidor Ollama...

curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   Ollama ja esta rodando.
) else (
    start "Ollama Server" /min cmd /c "ollama serve"
    timeout /t 3 /nobreak >nul
    echo   Ollama iniciado em background.
)

REM Verifica modelo otimizado qwen3.5-fast
echo   Verificando modelo qwen3.5-fast...
ollama list | findstr "qwen3.5-fast" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    ollama list | findstr "qwen3.5:4b" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo   Baixando qwen3.5:4b (pode levar alguns minutos)...
        ollama pull qwen3.5:4b
    )
    echo   Criando modelo otimizado qwen3.5-fast...
    ollama create qwen3.5-fast -f "%ROOT_DIR%\Modelfile"
    echo   Modelo qwen3.5-fast criado com sucesso.
) else (
    echo   Modelo qwen3.5-fast ja disponivel.
)

REM =============================================================================
REM PASSO 3 — Iniciar Backend em background
REM =============================================================================

echo [3/4] Iniciando Backend (FastAPI)...

cd "%ROOT_DIR%\backend"

if not exist ".venv" (
    python -m venv .venv
)

.venv\Scripts\pip install -q -r requirements.txt

taskkill /f /im uvicorn.exe >nul 2>&1

start "Backend FastAPI" /min cmd /c ".venv\Scripts\uvicorn api:app --host 0.0.0.0 --port 8000"

cd "%ROOT_DIR%"

echo   Aguardando backend inicializar...
set TRIES=0
:WAIT_BACKEND
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% EQU 0 goto BACKEND_OK
set /a TRIES+=1
if %TRIES% GEQ 10 (
    echo   Backend nao respondeu. Verifique se ha erros no terminal do Backend.
    goto BACKEND_DONE
)
timeout /t 1 /nobreak >nul
goto WAIT_BACKEND

:BACKEND_OK
echo   Backend rodando em http://localhost:8000

:BACKEND_DONE

REM =============================================================================
REM PASSO 4 — Iniciar Frontend
REM =============================================================================

echo [4/4] Iniciando Frontend (Streamlit)...

cd "%ROOT_DIR%\frontend"

if not exist ".venv" (
    python -m venv .venv
)

.venv\Scripts\pip install -q -r requirements.txt

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

timeout /t 4 /nobreak >nul
start "" http://localhost:8501

.venv\Scripts\streamlit run app.py --server.port 8501
