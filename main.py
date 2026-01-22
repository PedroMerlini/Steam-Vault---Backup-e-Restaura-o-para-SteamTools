import sys
import argparse
from src.constants import APP_NAME
from src.cli import run_cli

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
        # Check if PyQt6 is available, effectively handled by launcher but good to keep safe
        try:
            from PyQt6.QtWidgets import QApplication
            from src.gui import SteamVaultGUI
            
            app = QApplication(sys.argv)
            w = SteamVaultGUI()
            w.show()
            sys.exit(app.exec())
        except ImportError:
            print("[ERRO] PyQt6 não encontrado. Execute através do launcher apropriado.")
            sys.exit(1)

if __name__ == "__main__":
    main()
