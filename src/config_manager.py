import os
import json
from .constants import CONFIG_FILE, DEFAULT_CONFIG

# --- GERENCIADOR DE CONFIG ---
class ConfigManager:
    @staticmethod
    def load():
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        return DEFAULT_CONFIG

    @staticmethod
    def save(data):
        # Ensure directory exists if it's a full path
        directory = os.path.dirname(CONFIG_FILE)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
