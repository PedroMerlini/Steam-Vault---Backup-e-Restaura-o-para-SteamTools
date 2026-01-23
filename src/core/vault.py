import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

APP_NAME = "STEAM VAULT"
MAX_WORKERS = 8  # Número de threads paralelas

class VaultEngine:
    def __init__(self, logger_callback=print, progress_callback=None):
        self.log = logger_callback
        self.progress = progress_callback  # Callback para progresso (current, total)
        self.running = True

    def stop(self):
        self.running = False

    def _report_progress(self, current, total):
        """Reporta progresso se callback disponível."""
        if self.progress:
            self.progress(current, total)

    def safe_create_dir(self, path):
        if not os.path.exists(path):
            try: os.makedirs(path)
            except Exception as e: self.log(f"[ERRO] Criar pasta {path}: {e}")

    def safe_copy(self, src, dst):
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            self.log(f"[ERRO] Falha: {os.path.basename(src)} - {e}")
        return False

    def _copy_file_task(self, src, dst):
        """Task para cópia paralela de arquivo."""
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            return (True, src)
        except Exception as e:
            return (False, f"{src}: {e}")

    def _count_files_in_folder(self, folder):
        """Conta arquivos em uma pasta recursivamente."""
        if not os.path.exists(folder):
            return 0
        return sum([len(files) for r, d, files in os.walk(folder)])

    def _collect_files(self, src, dst):
        """Coleta pares de arquivos (origem, destino) para cópia."""
        if not os.path.exists(src):
            return []
        
        file_pairs = []
        for root, dirs, files in os.walk(src):
            if not self.running: break
            rel = os.path.relpath(root, src)
            target_dir = os.path.join(dst, rel)
            
            for file in files:
                if not self.running: break
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_dir, file)
                file_pairs.append((src_file, dst_file))
        
        return file_pairs

    def run_backup(self, steam, backup_root):
        vault_folder = os.path.join(backup_root, "SteamVault_Backup")
        self.log(f"--- INICIANDO PROTOCOLO {APP_NAME} ---")
        self.safe_create_dir(vault_folder)
        
        # Coletar todos os arquivos para progresso
        modules = [
            (os.path.join(steam, "userdata"), os.path.join(vault_folder, "userdata"), "USERDATA"),
            (os.path.join(steam, "config", "stplug-in"), os.path.join(vault_folder, "config", "stplug-in"), "STPLUG-IN"),
            (os.path.join(steam, "config", "depotcache"), os.path.join(vault_folder, "config", "depotcache"), "DEPOTCACHE"),
            (os.path.join(steam, "appcache", "stats"), os.path.join(vault_folder, "appcache", "stats"), "STATS"),
        ]
        
        # Coletar todos os arquivos
        all_files = []
        for src, dst, title in modules:
            all_files.extend(self._collect_files(src, dst))
        
        # DLLs (Windows only)
        dll_files = []
        if os.name == 'nt':
            for dll in ["version.dll", "winmm.dll"]:
                src = os.path.join(steam, dll)
                if os.path.exists(src):
                    dll_files.append((src, os.path.join(vault_folder, dll)))
        
        total_files = len(all_files) + len(dll_files)
        self.log(f"[INFO] Total de arquivos: {total_files}")
        
        if total_files == 0:
            self.log("[AVISO] Nenhum arquivo encontrado para backup.")
            return
        
        # Copiar em paralelo
        self.log(">>> COPIANDO ARQUIVOS...")
        errors = 0
        completed = 0
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(self._copy_file_task, src, dst): (src, dst) 
                      for src, dst in all_files + dll_files}
            
            for future in as_completed(futures):
                if not self.running:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                success, result = future.result()
                completed += 1
                self._report_progress(completed, total_files)
                if not success:
                    errors += 1
        
        # Log DLLs
        if os.name == 'nt':
            for src, dst in dll_files:
                if os.path.exists(dst):
                    self.log(f"[DLL] {os.path.basename(src)} Protegida.")
        
        if errors == 0:
            self.log(f"[SUCESSO] Backup concluído! ({completed} arquivos)")
        else:
            self.log(f"[AVISO] Backup concluído com {errors} erro(s).")

    def run_restore(self, steam, backup_root):
        vault_folder = os.path.join(backup_root, "SteamVault_Backup")
        origin = vault_folder
        
        # Retrocompatibilidade
        if not os.path.exists(origin):
            if os.path.exists(os.path.join(backup_root, "SteamBackup")):
                origin = os.path.join(backup_root, "SteamBackup")
                self.log("[AVISO] Detectado formato de backup antigo (SteamBackup).")

        if os.path.basename(backup_root) in ["SteamVault_Backup", "SteamBackup"]: 
            origin = backup_root

        self.log("--- INICIANDO RESTAURAÇÃO DO COFRE ---")
        
        if not os.path.exists(os.path.join(origin, "userdata")):
            self.log("[ERRO CRÍTICO] O Cofre está vazio ou inválido (userdata missing).")
            return

        # Coletar todos os arquivos
        modules = [
            (os.path.join(origin, "userdata"), os.path.join(steam, "userdata"), "USERDATA"),
            (os.path.join(origin, "config", "stplug-in"), os.path.join(steam, "config", "stplug-in"), "STPLUG-IN"),
            (os.path.join(origin, "config", "depotcache"), os.path.join(steam, "config", "depotcache"), "DEPOTCACHE"),
            (os.path.join(origin, "appcache", "stats"), os.path.join(steam, "appcache", "stats"), "STATS"),
        ]
        
        all_files = []
        for src, dst, title in modules:
            all_files.extend(self._collect_files(src, dst))
        
        # DLLs (Windows only)
        dll_files = []
        if os.name == 'nt':
            for dll in ["version.dll", "winmm.dll"]:
                src = os.path.join(origin, dll)
                if os.path.exists(src):
                    dll_files.append((src, os.path.join(steam, dll)))
        
        total_files = len(all_files) + len(dll_files)
        self.log(f"[INFO] Total de arquivos: {total_files}")
        
        if total_files == 0:
            self.log("[AVISO] Nenhum arquivo encontrado para restaurar.")
            return
        
        # Copiar em paralelo
        self.log(">>> RESTAURANDO ARQUIVOS...")
        errors = 0
        completed = 0
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(self._copy_file_task, src, dst): (src, dst) 
                      for src, dst in all_files + dll_files}
            
            for future in as_completed(futures):
                if not self.running:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                success, result = future.result()
                completed += 1
                self._report_progress(completed, total_files)
                if not success:
                    errors += 1
        
        # Log DLLs
        if os.name == 'nt':
            for src, dst in dll_files:
                if os.path.exists(dst):
                    self.log(f"[DLL] {os.path.basename(src)} Restaurada.")
        
        if errors == 0:
            self.log(f"[SUCESSO] Restauração concluída! ({completed} arquivos)")
        else:
            self.log(f"[AVISO] Restauração concluída com {errors} erro(s).")
