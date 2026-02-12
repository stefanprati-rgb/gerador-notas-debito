@echo off
:: 1. Garante que o script rode na pasta correta (Correção do erro de fechar rápido)
cd /d "%~dp0"

title Hube Energy - Sistema de Notas
color 0F
cls

echo ========================================================
echo        HUBE ENERGY - GERADOR DE NOTAS AUTOMATICO
echo ========================================================
echo.
echo [1/3] Verificando ambiente...

:: 2. Verifica Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO CRITICO] Python nao encontrado.
    echo Por favor, instale o Python marcando a opcao "Add to PATH".
    pause
    exit
)

:: 3. Cria/Ativa ambiente virtual (Isolamento para nao dar conflito)
if not exist "venv" (
    echo [2/3] Configurando sistema pela primeira vez...
    python -m venv venv
)
call venv\Scripts\activate

:: 4. Instala dependencias silenciosamente (se necessario)
if not exist "venv\installed.flag" (
    echo [2/3] Atualizando bibliotecas...
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install -r requirements.txt >nul 2>&1
    echo OK > venv\installed.flag
)

:: 5. Inicia o Sistema
echo [3/3] Iniciando o aplicativo...
echo.
echo ========================================================
echo    O NAVEGADOR ABRIRA AUTOMATICAMENTE EM INSTANTES
echo    Mantenha esta janela aberta enquanto usa o sistema.
echo ========================================================
echo.

:: O comando que funcionou no seu teste:
python -m streamlit run app.py --server.headless true

:: Se o sistema fechar por erro, segura a tela para voce ler
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] O sistema fechou inesperadamente.
    pause
)