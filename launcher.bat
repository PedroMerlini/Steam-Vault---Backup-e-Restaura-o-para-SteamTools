@echo off
cd /d "%~dp0"
title Steam Vault Launcher
cls

echo ==================================================
echo      STEAM VAULT - System Check ^& Launcher
echo ==================================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Python nao encontrado no sistema.
    echo.
    echo Tentando instalar Python 3.12 via Winget...
    echo Voce pode precisar aprovar a instalacao na janela que abrir.
    echo.
    
    winget install -e --id Python.Python.3.12
    
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar o Python automaticamente.
        echo Por favor, instale o Python manualmente em python.org e tente novamente.
        pause
        exit /b /1
    )
    
    echo.
    echo [SUCESSO] Python instalado. Reiniciando o launcher para carregar o PATH...
    timeout /t 3
    start "" "%~f0"
    exit /b
) else (
    echo [OK] Python detectado.
)

:: 2. Setup Virtual Environment (Optional but Recommended)
if not exist ".venv" (
    echo [INFO] Criando ambiente virtual isolado...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b
    )
)

:: 3. Install Dependencies
echo [INFO] Verificando dependencias...
call .venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Falha na verificacao silenciosa. Instalando com log detalhado...
    pip install -r requirements.txt
) else (
    echo [OK] Dependencias prontas.
)

:: 4. Launch Application
echo.
echo [INFO] Iniciando Steam Vault...
python -m src.main %*

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] O programa fechou com erro.
    pause
)
