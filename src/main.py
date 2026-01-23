import sys
import argparse
from PyQt6.QtWidgets import QApplication

from src.utils.config import ConfigManager
from src.core.vault import VaultEngine, APP_NAME
from src.gui.window import SteamVaultGUI

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
        # Note: CLI force logic handled here lightly, but ideally should be in engine or interactive
        # For now, mirroring original behavior
        engine.run_backup(steam, backup)
    elif args.action == "restore":
        engine.run_restore(steam, backup)

def main():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} Tool")
    parser.add_argument("action", nargs="?", choices=["backup", "restore"])
    parser.add_argument("--steam", help="Caminho Steam")
    parser.add_argument("--backup-path", help="Caminho Backup")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.action:
        run_cli(args)
    else:
        app = QApplication(sys.argv)
        w = SteamVaultGUI()
        w.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
