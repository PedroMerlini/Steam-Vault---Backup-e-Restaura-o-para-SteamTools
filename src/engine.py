import os
import shutil
import glob
import zipfile
import subprocess
from .constants import APP_NAME, IS_WINDOWS, IS_LINUX, CONFIG_FILE

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

    def sudo_copy(self, src, dst):
        """Tenta copiar com privilégios elevados se necessário."""
        try:
            shutil.copy2(src, dst)
            return True
        except PermissionError:
            self.log(f"[PERMISSÃO] Tentando elevar privilégios para copiar: {os.path.basename(src)}")
            # Tenta usar pkexec para GUI ou sudo para CLI (mas aqui assumimos GUI flow principal)
            try:
                subprocess.check_call(['pkexec', 'cp', src, dst])
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to older gksudo or just fail gracefully
                self.log(f"[ERRO] Falha de permissão e falha ao elevar privilégios para: {src}")
                return False
        except Exception as e:
            self.log(f"[ERRO] Falha ao copiar {src}: {e}")
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


    def compress_backup(self, src_dir, zip_path):
        """Compacta o diretório de backup em um arquivo ZIP com alta compressão."""
        self.log(">>> COMPACTANDO BACKUP (Isso pode demorar)...")
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                for root, dirs, files in os.walk(src_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, src_dir)
                        zipf.write(file_path, arcname)
            self.log("[SUCESSO] Backup compactado criado com sucesso.")
            return True
        except Exception as e:
            self.log(f"[ERRO] Falha na compactação: {e}")
            return False

    def extract_backup(self, zip_path, extract_to):
        """Extrai o backup compactado."""
        self.log(">>> EXTRAINDO BACKUP...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_to)
            self.log("[SUCESSO] Backup extraído.")
            return True
        except Exception as e:
            self.log(f"[ERRO] Falha na extração: {e}")
            return False

    def run_backup(self, steam, backup_root):
        # Stage area for backup before compression
        stage_dir = os.path.join(backup_root, "stage_temp")
        vault_folder = os.path.join(stage_dir, "SteamVault_Backup")
        final_zip = os.path.join(backup_root, "SteamVault_Backup.zip")

        self.log(f"--- INICIANDO PROTOCOLO {APP_NAME} ---")
        
        # Cleanup potential leftovers
        if os.path.exists(stage_dir): shutil.rmtree(stage_dir)
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
            self.backup_proton_saves(steam, stage_dir)
            
            # --- SLS STEAM CONFIG BACKUP ---
            sls_config = os.path.expanduser("~/.config/SLSsteam/config.yaml")
            if os.path.exists(sls_config):
                self.log(">>> PROCESSANDO: CONFIGURAÇÃO SLS STEAM...")
                sls_dest_dir = os.path.join(stage_dir, "SLS_Config")
                self.safe_create_dir(sls_dest_dir)
                
                if self.sudo_copy(sls_config, os.path.join(sls_dest_dir, "config.yaml")):
                    self.log("[SUCESSO] Configuração SLS arquivada.")
                else:
                    self.log("[FALHA] Não foi possível fazer backup do SLS Config.")

        # Backup Config File
        if os.path.exists(CONFIG_FILE):
             self.safe_copy(CONFIG_FILE, os.path.join(vault_folder, "vault_config.json"))
             self.log(f"[CONFIG] {CONFIG_FILE} arquivado.")

        # Compress and Cleanup
        if self.compress_backup(stage_dir, final_zip):
            shutil.rmtree(stage_dir)
        else:
             self.log("[AVISO] Falha ao compactar. Os arquivos temporários foram mantidos.")

    def run_restore(self, steam, backup_root):
        zip_path = os.path.join(backup_root, "SteamVault_Backup.zip")
        # Temp dir for extraction
        temp_extract = os.path.join(backup_root, "restore_temp")
        
        origin = None
        is_zip = False

        self.log("--- INICIANDO RESTAURAÇÃO DO COFRE ---")

        if os.path.exists(zip_path):
            self.log("[DETECTADO] Backup Compactado.")
            if self.extract_backup(zip_path, temp_extract):
                origin = os.path.join(temp_extract, "SteamVault_Backup")
                is_zip = True
            else:
                return
        else:
            # Fallback to legacy folders
            legacy_1 = os.path.join(backup_root, "SteamVault_Backup")
            legacy_2 = os.path.join(backup_root, "SteamBackup")
            
            if os.path.exists(legacy_1): origin = legacy_1
            elif os.path.exists(legacy_2): 
                origin = legacy_2
                self.log("[AVISO] Backup legado detectado.")

        if not origin or (not os.path.exists(origin)):
            self.log("[ERRO CRÍTICO] Nenhum backup válido encontrado.")
            if is_zip: shutil.rmtree(temp_extract)
            return

        if not os.path.exists(os.path.join(origin, "userdata")) and not os.path.exists(os.path.join(origin, "proton_saves")):
            self.log("[ERRO CRÍTICO] O Cofre está vazio ou inválido.")
            if is_zip: shutil.rmtree(temp_extract)
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
            self.restore_proton_saves(steam, os.path.dirname(origin)) # proton logic expects root of backup structure
            
            # --- SLS STEAM CONFIG RESTORE ---
            sls_bkp_file = os.path.join(os.path.dirname(origin), "SLS_Config", "config.yaml")
            if os.path.exists(sls_bkp_file):
                self.log(">>> RESTAURANDO: CONFIGURAÇÃO SLS STEAM...")
                sls_target_dir = os.path.expanduser("~/.config/SLSsteam")
                sls_target_file = os.path.join(sls_target_dir, "config.yaml")
                
                self.safe_create_dir(sls_target_dir)
                
                if self.sudo_copy(sls_bkp_file, sls_target_file):
                    self.log("[SUCESSO] Configuração SLS restaurada.")
                else:
                    self.log("[FALHA] Não foi possível restaurar SLS Config (Permissão?).")

        # Restore Config File
        src_config = os.path.join(origin, "vault_config.json")
        if os.path.exists(src_config):
            if self.safe_copy(src_config, CONFIG_FILE):
                self.log(f"[CONFIG] {CONFIG_FILE} Restaurada.")
        
        # Cleanup
        if is_zip and os.path.exists(temp_extract):
            shutil.rmtree(temp_extract)
            self.log("[LIMPEZA] Arquivos temporários removidos.")
