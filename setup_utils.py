import sys
import subprocess

# --- AUTO-INSTALAÇÃO DE DEPENDÊNCIAS ---
def install_package(package):
    """Instala um pacote pip automaticamente."""
    print(f"[SETUP] A biblioteca '{package}' não foi encontrada.")
    print(f"[SETUP] Instalando {package} automaticamente, aguarde...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[SETUP] {package} instalado com sucesso!")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao instalar {package}: {e}")
        return False
