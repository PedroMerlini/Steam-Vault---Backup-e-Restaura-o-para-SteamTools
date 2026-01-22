import os
import shutil
import glob
from constants import APP_NAME, IS_WINDOWS, IS_LINUX

# --- MOTOR DO COFRE (Lógica Central) ---
class VaultEngine:
    def __init__(self, logger_callback):
        self.log = logger_callback
        self.running = True

    def stop(self):
        self.running = False

    def safe_create_dir(self, path):
        if not os.path.exists(path):
            try: os.makedirs(path)
            except: pass

    def safe_copy(self, src, dst):
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            self.log(f"[ERRO] Falha: {os.path.basename(src)} - {e}")
        return False

    def copy_module(self, src, dst, title):
        if not os.path.exists(src):
            self.log(f"[INFO] {title}: Não localizado (Ignorado).")
            return

        total = sum([len(files) for r, d, files in os.walk(src)])
        if total == 0: return

        self.log(f">>> PROCESSANDO: {title}...")
        self.safe_create_dir(dst)

        for root, dirs, files in os.walk(src):
            if not self.running: break
            rel = os.path.relpath(root, src)
            target_dir = os.path.join(dst, rel)
            self.safe_create_dir(target_dir)

            for file in files:
                if not self.running: break
                self.safe_copy(os.path.join(root, file), os.path.join(target_dir, file))
        
        self.log(f"[SUCESSO] {title} arquivado no cofre.")

    def backup_proton_saves(self, steam, backup_root):
        """Faz backup inteligente dos saves do Proton (Linux)."""
        compat_path = os.path.join(steam, "steamapps", "compatdata")
        if not os.path.exists(compat_path): return

        self.log(">>> PROCESSANDO: SAVE GAMES PROTON (LINUX)...")
        vault_proton = os.path.join(backup_root, "SteamVault_Backup", "proton_saves")
        self.safe_create_dir(vault_proton)

        # Itera sobre IDs de jogos ( pastas numéricas )
        for item in os.listdir(compat_path):
            if not self.running: break
            if not item.isdigit(): continue
            
            pfx_path = os.path.join(compat_path, item, "pfx", "drive_c", "users", "steamuser")
            if not os.path.exists(pfx_path): continue

            # Alvos comuns de save no windows (dentro do prefixo)
            targets = [
                "Documents",
                "Saved Games", 
                "AppData/Local", 
                "AppData/Roaming",
                "AppData/LocalLow" # Unity games use this a lot
            ]
            
            found_data = False
            for t in targets:
                src_target = os.path.join(pfx_path, t)
                if os.path.exists(src_target):
                    # Destination: proton_saves/<appid>/<target>
                    dst_target = os.path.join(vault_proton, item, t)
                    
                    # Evita copiar lixo do sistema (pastas vazias ou só com links)
                    if any(os.scandir(src_target)):
                        self.copy_module(src_target, dst_target, f"Proton AppID {item} - {t}")
                        found_data = True
            
            if found_data:
                self.log(f"[PROTON] AppID {item} verificado.")

    def restore_proton_saves(self, steam, backup_root):
        """Restaura saves do Proton."""
        vault_proton = os.path.join(backup_root, "SteamVault_Backup", "proton_saves")
        if not os.path.exists(vault_proton): return
        
        compat_path = os.path.join(steam, "steamapps", "compatdata")
        
        self.log(">>> RESTAURANDO: SAVE GAMES PROTON...")
        
        for appid in os.listdir(vault_proton):
            if not self.running: break
            
            # Se o jogo não estiver instalado/rodado (sem prefixo), avisa mas tenta criar? 
            # Proton cria o prefixo ao rodar. Melhor restaurar apenas se existir ou avisar.
            # Vamos tentar restaurar na estrutura correta.
            
            pfx_user_path = os.path.join(compat_path, appid, "pfx", "drive_c", "users", "steamuser")
            
            # Se a pasta compatdata/<appid> não existe, o usuário talvez não tenha rodado o jogo ainda.
            # Criar a estrutura manualmente pode bugar o Proton.
            # Política: Restaurar apenas se o prefixo existir.
            if not os.path.exists(pfx_user_path):
                self.log(f"[SKIP] AppID {appid} não possui prefixo Proton criado (Rode o jogo uma vez).")
                continue

            src_appid = os.path.join(vault_proton, appid)
            
            for root, dirs, files in os.walk(src_appid):
                rel = os.path.relpath(root, src_appid) # ex: Documents/My Games
                dst_in_pfx = os.path.join(pfx_user_path, rel)
                
                self.safe_create_dir(dst_in_pfx)
                
                for file in files:
                    self.safe_copy(os.path.join(root, file), os.path.join(dst_in_pfx, file))
            
            self.log(f"[SUCESSO] Proton Saves AppID {appid} restaurados.")

    def run_backup(self, steam, backup_root):
        vault_folder = os.path.join(backup_root, "SteamVault_Backup")
        self.log(f"--- INICIANDO PROTOCOLO {APP_NAME} ---")
        self.safe_create_dir(vault_folder)
        
        self.copy_module(os.path.join(steam, "userdata"), os.path.join(vault_folder, "userdata"), "USERDATA")
        self.copy_module(os.path.join(steam, "config", "stplug-in"), os.path.join(vault_folder, "config", "stplug-in"), "STPLUG-IN")
        self.copy_module(os.path.join(steam, "config", "depotcache"), os.path.join(vault_folder, "config", "depotcache"), "DEPOTCACHE")
        self.copy_module(os.path.join(steam, "appcache", "stats"), os.path.join(vault_folder, "appcache", "stats"), "STATS")

        if IS_WINDOWS:
            for dll in ["version.dll", "winmm.dll"]:
                src = os.path.join(steam, dll)
                if os.path.exists(src):
                    if self.safe_copy(src, os.path.join(vault_folder, dll)):
                        self.log(f"[DLL] {dll} Protegida.")
        
        if IS_LINUX:
            self.backup_proton_saves(steam, backup_root)

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
        
        if not os.path.exists(os.path.join(origin, "userdata")) and not os.path.exists(os.path.join(origin, "proton_saves")):
            self.log("[ERRO CRÍTICO] O Cofre está vazio ou inválido.")
            return

        self.copy_module(os.path.join(origin, "userdata"), os.path.join(steam, "userdata"), "RESTORE USERDATA")
        self.copy_module(os.path.join(origin, "config", "stplug-in"), os.path.join(steam, "config", "stplug-in"), "RESTORE STPLUG-IN")
        self.copy_module(os.path.join(origin, "config", "depotcache"), os.path.join(steam, "config", "depotcache"), "RESTORE DEPOTCACHE")
        self.copy_module(os.path.join(origin, "appcache", "stats"), os.path.join(steam, "appcache", "stats"), "RESTORE STATS")

        if IS_WINDOWS:
            for dll in ["version.dll", "winmm.dll"]:
                src = os.path.join(origin, dll)
                if os.path.exists(src):
                    if self.safe_copy(src, os.path.join(steam, dll)):
                        self.log(f"[DLL] {dll} Restaurada.")
        
        if IS_LINUX:
            self.restore_proton_saves(steam, backup_root)
