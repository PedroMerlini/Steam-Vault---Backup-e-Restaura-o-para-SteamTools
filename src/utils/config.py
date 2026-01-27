import json
import os
import sys

if sys.platform == 'win32':
    import winreg

def _config_path():
    if getattr(sys, "frozen", False):
        docs = os.path.join(os.path.expanduser("~"), "Documents", "SteamVault")
        return os.path.join(docs, "vault_config.json")
    return "vault_config.json"

CONFIG_FILE = _config_path()
DEFAULT_CONFIG = {"steam_path": "", "backup_path": ""}

class ConfigManager:
    @staticmethod
    def detect_steam_path():
        
        if sys.platform == 'win32':
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                path, _ = winreg.QueryValueEx(key, "SteamPath")
                path = os.path.normpath(path)
                if os.path.exists(path):
                    return path
            except Exception:
                pass
            
        common_paths = []
        
        if sys.platform == 'win32':
            common_paths = [
                r"C:\Program Files (x86)\Steam",
                r"C:\Program Files\Steam",
                r"D:\Steam",
                r"E:\Steam"
            ]
        else:
            home = os.path.expanduser("~")
            common_paths = [
                os.path.join(home, ".steam", "steam"),
                os.path.join(home, ".local", "share", "Steam"),
                os.path.join(home, ".var", "app", "com.valvesoftware.Steam", ".steam", "steam")
            ]

        for p in common_paths:
            if os.path.exists(p):
                return p
        
        return ""

    @staticmethod
    def load():
        config = DEFAULT_CONFIG.copy()
        
        detected_steam = ConfigManager.detect_steam_path()
        if detected_steam:
            config["steam_path"] = detected_steam

        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                try:
                    loaded = json.load(f)
                    saved_path = loaded.get("steam_path", "")
                    if saved_path:
                        config["steam_path"] = saved_path
                    
                    config["backup_path"] = loaded.get("backup_path", config["backup_path"])
                    
                    return config
                except json.JSONDecodeError:
                    return config
        
        return config

    @staticmethod
    def save(data):
        path = CONFIG_FILE
        folder = os.path.dirname(path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
