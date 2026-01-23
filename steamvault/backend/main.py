"""
Steam Vault - Backend para Millennium
Expõe funções de backup e restore para o frontend.
"""
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

import Millennium  # type: ignore

print("[SteamVault] Backend module loading...")

MAX_WORKERS = 8


def get_plugin_dir() -> str:
    """Retorna o diretório do plugin (pasta raiz, não backend)."""
    # __file__ = backend/main.py
    # Precisamos subir um nível para chegar na raiz do plugin
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.dirname(backend_dir)
    return plugin_dir


def public_path(filename: str) -> str:
    """Retorna o caminho para um arquivo na pasta public."""
    return os.path.join(get_plugin_dir(), "public", filename)


class Logger:
    @staticmethod
    def log(message: str) -> str:
        print(f"[SteamVault] {message}")
        return json.dumps({"success": True})

    @staticmethod
    def error(message: str) -> str:
        print(f"[SteamVault ERROR] {message}")
        return json.dumps({"success": True})


def _copy_file_task(src: str, dst: str) -> tuple:
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return (True, src)
    except Exception as e:
        return (False, f"{src}: {e}")


def _collect_files(src: str, dst: str) -> list:
    if not os.path.exists(src):
        return []
    
    file_pairs = []
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        target_dir = os.path.join(dst, rel)
        
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            file_pairs.append((src_file, dst_file))
    
    return file_pairs


def GetSteamPath() -> str:
    """Retorna o caminho da Steam."""
    return Millennium.steam_path()


def GetDefaultBackupPath() -> str:
    """Retorna caminho padrão para backup."""
    home = os.path.expanduser("~")
    return json.dumps({"success": True, "path": os.path.join(home, "Documents", "SteamVault")})


def RunBackup(backupPath: str) -> str:
    """Executa backup."""
    print(f"[SteamVault] RunBackup called with path: {backupPath}")
    steam = Millennium.steam_path()
    vault_folder = os.path.join(backupPath, "SteamVault_Backup")
    
    try:
        os.makedirs(vault_folder, exist_ok=True)
    except Exception as e:
        return json.dumps({"success": False, "error": f"Falha ao criar pasta: {e}"})
    
    modules = [
        (os.path.join(steam, "userdata"), os.path.join(vault_folder, "userdata")),
        (os.path.join(steam, "config", "stplug-in"), os.path.join(vault_folder, "config", "stplug-in")),
        (os.path.join(steam, "config", "depotcache"), os.path.join(vault_folder, "config", "depotcache")),
        (os.path.join(steam, "appcache", "stats"), os.path.join(vault_folder, "appcache", "stats")),
    ]
    
    all_files = []
    for src, dst in modules:
        all_files.extend(_collect_files(src, dst))
    
    # DLLs (Windows)
    if os.name == 'nt':
        for dll in ["version.dll", "winmm.dll"]:
            src = os.path.join(steam, dll)
            if os.path.exists(src):
                all_files.append((src, os.path.join(vault_folder, dll)))
    
    total = len(all_files)
    if total == 0:
        return json.dumps({"success": False, "error": "Nenhum arquivo encontrado."})
    
    print(f"[SteamVault] Backing up {total} files...")
    
    errors = 0
    completed = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_copy_file_task, src, dst): (src, dst) 
                  for src, dst in all_files}
        
        for future in as_completed(futures):
            success, result = future.result()
            completed += 1
            if not success:
                errors += 1
    
    print(f"[SteamVault] Backup completed: {completed} files, {errors} errors")
    
    return json.dumps({
        "success": errors == 0,
        "files_copied": completed,
        "errors": errors,
        "path": vault_folder
    })


def RunRestore(backupPath: str) -> str:
    """Executa restore."""
    print(f"[SteamVault] RunRestore called with path: {backupPath}")
    steam = Millennium.steam_path()
    vault_folder = os.path.join(backupPath, "SteamVault_Backup")
    
    if not os.path.exists(vault_folder):
        return json.dumps({"success": False, "error": "Pasta de backup não encontrada."})
    
    if not os.path.exists(os.path.join(vault_folder, "userdata")):
        return json.dumps({"success": False, "error": "Backup inválido (userdata missing)."})
    
    modules = [
        (os.path.join(vault_folder, "userdata"), os.path.join(steam, "userdata")),
        (os.path.join(vault_folder, "config", "stplug-in"), os.path.join(steam, "config", "stplug-in")),
        (os.path.join(vault_folder, "config", "depotcache"), os.path.join(steam, "config", "depotcache")),
        (os.path.join(vault_folder, "appcache", "stats"), os.path.join(steam, "appcache", "stats")),
    ]
    
    all_files = []
    for src, dst in modules:
        all_files.extend(_collect_files(src, dst))
    
    if os.name == 'nt':
        for dll in ["version.dll", "winmm.dll"]:
            src = os.path.join(vault_folder, dll)
            if os.path.exists(src):
                all_files.append((src, os.path.join(steam, dll)))
    
    total = len(all_files)
    print(f"[SteamVault] Restoring {total} files...")
    
    errors = 0
    completed = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_copy_file_task, src, dst): (src, dst) 
                  for src, dst in all_files}
        
        for future in as_completed(futures):
            success, result = future.result()
            completed += 1
            if not success:
                errors += 1
    
    print(f"[SteamVault] Restore completed: {completed} files, {errors} errors")
    
    return json.dumps({
        "success": errors == 0,
        "files_restored": completed,
        "errors": errors
    })


class Plugin:
    def _load(self):
        """Chamado quando o plugin carrega."""
        print(f"[SteamVault] Plugin loading, millennium version: {Millennium.version()}")
        
        # Injetar o JS no frontend (OBRIGATÓRIO para UI funcionar!)
        try:
            steam_path = Millennium.steam_path()
            # Caminho direto baseado no steam_path
            js_path = os.path.join(steam_path, "plugins", "steamvault", "public", "steamvault.js")
            print(f"[SteamVault] Looking for JS at: {js_path}")
            
            if os.path.exists(js_path):
                # Copiar para steamui para ser acessível
                steamui_dir = os.path.join(steam_path, "steamui", "steamvault")
                os.makedirs(steamui_dir, exist_ok=True)
                
                dst_js = os.path.join(steamui_dir, "steamvault.js")
                shutil.copy(js_path, dst_js)
                print(f"[SteamVault] Copied JS to {dst_js}")
                
                # Injetar no browser
                Millennium.add_browser_js("steamvault/steamvault.js")
                print("[SteamVault] JS injected via add_browser_js")
            else:
                print(f"[SteamVault ERROR] JS file not found at {js_path}")
        except Exception as e:
            print(f"[SteamVault ERROR] Failed to inject JS: {e}")
        
        Millennium.ready()
        print("[SteamVault] Plugin ready!")

    def _unload(self):
        """Chamado quando o plugin descarrega."""
        print("[SteamVault] Plugin unloading...")

    def _front_end_loaded(self):
        """Chamado quando o frontend carrega."""
        print("[SteamVault] Frontend loaded!")


# Instância do plugin (OBRIGATÓRIO!)
plugin = Plugin()

print("[SteamVault] Backend module loaded!")
