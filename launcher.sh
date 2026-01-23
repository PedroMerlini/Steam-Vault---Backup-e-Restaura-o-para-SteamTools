#!/bin/bash

echo "=================================================="
echo "      STEAM VAULT - System Check & Launcher"
echo "=================================================="
echo

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 nao encontrado."
    echo "Por favor, instale o python3 usando o gerenciador de pacotes da sua distro."
    echo "Ex: sudo apt install python3 python3-venv python3-pip"
    exit 1
else
    echo "[OK] Python 3 detectado."
fi

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[INFO] Criando ambiente virtual isolado..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao criar ambiente virtual."
        echo "Certifique-se que o modulo venv esta instalado (ex: sudo apt install python3-venv)"
        exit 1
    fi
fi

# 3. Install Dependencies
echo "[INFO] Verificando dependencias..."
source .venv/bin/activate
pip install -r requirements.txt &> /dev/null
if [ $? -ne 0 ]; then
    echo "[AVISO] Falha na verificacao silenciosa. Instalando com log detalhado..."
    pip install -r requirements.txt
else
    echo "[OK] Dependencias prontas."
fi

# 4. Launch Application
echo
echo "[INFO] Iniciando Steam Vault..."
python -m src.main "$@"
