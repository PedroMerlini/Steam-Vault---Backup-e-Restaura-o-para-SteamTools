#!/bin/bash

# Define environment directory
VENV_DIR="venv"

# Check Python3
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python 3 could not be found."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "[LAUNCHER] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

echo "[LAUNCHER] Checking dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies."
    deactivate
    exit 1
fi

echo "[LAUNCHER] Starting Steam Vault..."
python main.py "$@"
deactivate
