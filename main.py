import sys
import argparse
from constants import APP_NAME
from setup_utils import install_package
from cli import run_cli

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
        # Check and install PyQt6 if needed
        try:
            from PyQt6.QtWidgets import QApplication
            GUI_AVAILABLE = True
        except ImportError:
            if install_package("PyQt6"):
                try:
                    from PyQt6.QtWidgets import QApplication
                    GUI_AVAILABLE = True
                except ImportError:
                    GUI_AVAILABLE = False
            else:
                GUI_AVAILABLE = False

        if GUI_AVAILABLE:
            from gui import SteamVaultGUI
            app = QApplication(sys.argv)
            w = SteamVaultGUI()
            w.show()
            sys.exit(app.exec())
        else:
            print("[ERRO] Instale PyQt6 ou use argumentos CLI.")

if __name__ == "__main__":
    main()
