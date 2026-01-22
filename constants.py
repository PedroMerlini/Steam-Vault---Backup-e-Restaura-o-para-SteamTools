import platform
import os

# --- DETECÇÃO DE OS ---
SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_LINUX = SYSTEM == "Linux"

# --- PATHS PADRÃO ---
def get_default_steam_path():
    if IS_WINDOWS:
        return r"C:\Program Files (x86)\Steam"
    elif IS_LINUX:
        # Tenta paths comuns linux
        paths = [
            os.path.expanduser("~/.steam/steam"),
            os.path.expanduser("~/.local/share/Steam"),
            os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.steam/steam") # Flatpak
        ]
        for p in paths:
            if os.path.exists(p): return p
    return ""

# --- CONFIGURAÇÕES DE TEMA (MIDNIGHT PRO) ---
THEME = {
    "bg_main": "#0b0f19",       # Azul Profundo
    "bg_panel": "#111827",      # Painel Escuro
    "accent": "#3b82f6",        # Azul Profissional
    "success": "#10b981",       # Verde Sucesso
    "error": "#ef4444",         # Vermelho Erro
    "text_main": "#f3f4f6",     # Branco
    "text_dim": "#9ca3af",      # Cinza
    "btn_bg": "#1f2937",        # Botões
    "btn_border": "#374151",
    "close_hover": "#ef4444"
}

# --- IDENTIDADE ---
APP_NAME = "STEAM VAULT"
CONFIG_FILE = "vault_config.json"
DEFAULT_CONFIG = {"steam_path": get_default_steam_path(), "backup_path": ""}
