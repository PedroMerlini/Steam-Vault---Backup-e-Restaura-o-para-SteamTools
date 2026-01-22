import os
from .constants import APP_NAME
from .config_manager import ConfigManager
from .engine import VaultEngine

# --- MODO CLI ---
def run_cli(args):
    config = ConfigManager.load()
    steam = args.steam if args.steam else config.get('steam_path')
    backup = args.backup_path if args.backup_path else config.get('backup_path')

    print(f"\n{'-'*40}")
    print(f"   {APP_NAME} CLI")
    print(f"{'-'*40}")

    if not steam or not backup:
        print("[ERRO] Caminhos inválidos.")
        return

    engine = VaultEngine(print)

    if args.action == "backup":
        tgt = os.path.join(backup, "SteamVault_Backup")
        if os.path.exists(tgt) and os.listdir(tgt) and not args.force:
            if input("Sobrescrever Cofre? [S/N]: ").upper() != 'S': return
        engine.run_backup(steam, backup)
    elif args.action == "restore":
        engine.run_restore(steam, backup)
