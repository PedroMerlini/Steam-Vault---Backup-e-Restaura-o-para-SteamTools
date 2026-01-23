@echo off
echo ========================================
echo    STEAM VAULT - Build Executable
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale o Python primeiro.
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias...
pip install -r requirements.txt

echo.
echo [2/3] Gerando executavel...
pyinstaller --onefile --windowed --icon=icone.ico --name "SteamVault" "STEAM VAULT.py"

echo.
echo [3/3] Limpando arquivos temporarios...
rmdir /s /q build 2>nul
del /q SteamVault.spec 2>nul

echo.
echo ========================================
echo    BUILD CONCLUIDO!
echo    Executavel: dist\SteamVault.exe
echo ========================================
echo.
pause
