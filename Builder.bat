@echo off
cd /d "%~dp0"
title Steam Vault - Build EXE
cls

echo ==================================================
echo      STEAM VAULT - Compilador para .exe
echo ==================================================
echo.

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
        exit /b 1
    )
    echo.
    echo [SUCESSO] Python instalado. Reiniciando o build para carregar o PATH...
    timeout /t 3
    start "" "%~f0"
    exit /b 0
) else (
    echo [OK] Python detectado.
)

if not exist ".venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo [INFO] Instalando dependencias de build...
pip install -r requirements.txt -q
pip install pyinstaller -q

echo.
echo [INFO] Compilando com PyInstaller (modo pasta)...
pyinstaller --noconfirm --clean SteamVault.spec

if %errorlevel% neq 0 (
    echo [ERRO] Falha na compilacao.
    pause
    exit /b 1
)

echo.
echo [OK] Build concluido.
echo     Saida: dist\SteamVault\
echo     Execute: dist\SteamVault\SteamVault.exe
echo.
echo Para gerar UM unico .exe (mais lento ao abrir), use:
echo     pyinstaller --noconfirm --clean --onefile --name SteamVault --paths=. --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWidgets --console src\main.py
echo.
pause
