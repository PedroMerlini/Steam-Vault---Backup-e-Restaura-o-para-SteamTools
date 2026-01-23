import json
import os
import sys

# Importar winreg apenas no Windows
if sys.platform == 'win32':
    import winreg

CONFIG_FILE = "vault_config.json"
DEFAULT_CONFIG = {"steam_path": "", "backup_path": ""}

class ConfigManager:
    @staticmethod
    def detect_steam_path():
        """Tenta detectar o caminho da Steam via Registro (Win) ou caminhos padrao (Win/Linux)."""
        
        # 1. Tentar Registro do Windows (Apenas Windows)
        if sys.platform == 'win32':
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                path, _ = winreg.QueryValueEx(key, "SteamPath")
                path = os.path.normpath(path)
                if os.path.exists(path):
                    return path
            except Exception:
                pass
            
        # 2. Tentar caminhos padrao (Windows e Linux)
        common_paths = []
        
        if sys.platform == 'win32':
            common_paths = [
                r"C:\Program Files (x86)\Steam",
                r"C:\Program Files\Steam",
                r"D:\Steam",
                r"E:\Steam"
            ]
        else: # Linux / MacOS
            home = os.path.expanduser("~")
            common_paths = [
                os.path.join(home, ".steam", "steam"),
                os.path.join(home, ".local", "share", "Steam"),
                os.path.join(home, ".var", "app", "com.valvesoftware.Steam", ".steam", "steam") # Flatpak
            ]

        for p in common_paths:
            if os.path.exists(p):
                return p
        
        return ""

    @staticmethod
    def load():
        config = DEFAULT_CONFIG.copy()
        
        # Detectar path se nao tiver salvo
        detected_steam = ConfigManager.detect_steam_path()
        if detected_steam:
            config["steam_path"] = detected_steam

        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                try:
                    loaded = json.load(f)
                    # Merge: usa o salvo, senao usa o detectado (se o salvo estiver vazio)
                    saved_path = loaded.get("steam_path", "")
                    if saved_path:
                        config["steam_path"] = saved_path
                    
                    # Carregar outros campos
                    config["backup_path"] = loaded.get("backup_path", config["backup_path"])
                    
                    return config
                except json.JSONDecodeError:
                    return config
        
        return config

    @staticmethod
    def save(data):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
