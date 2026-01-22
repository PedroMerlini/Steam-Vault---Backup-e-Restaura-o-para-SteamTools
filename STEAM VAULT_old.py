import sys
import os
import shutil
import json
import subprocess
import argparse
import time

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

# Tenta importar PyQt6 para modo Gráfico (Com Auto-Install)
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                                 QProgressBar, QFrame, QMessageBox, QTextEdit)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
    from PyQt6.QtGui import QCursor, QIcon
    GUI_AVAILABLE = True
except ImportError:
    # Se falhar, tenta instalar e importa de novo
    if install_package("PyQt6"):
        try:
            from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                         QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                                         QProgressBar, QFrame, QMessageBox, QTextEdit)
            from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
            from PyQt6.QtGui import QCursor, QIcon
            GUI_AVAILABLE = True
        except ImportError:
            print("[ERRO] Instalação falhou ou biblioteca ainda inacessível.")
            GUI_AVAILABLE = False
    else:
        GUI_AVAILABLE = False

# --- CONFIGURAÇÕES DE TEMA (MIDNIGHT PRO) ---
THEME = {
    "bg_main": "#0b0f19",       # Azul Profundo
    "bg_panel": "#111827",      # Painel Escuro
    "accent": "#3b82f6",        # Azul Profissional
    "success": "#10b981",       # Verde Sucesso
    "error": "#ef4444",         # Vermelho Erro
    "text_main": "#f3f4f6",     # Branco
    "text_dim": "#9ca3af",      # Cinza
    "btn_bg": "#1f2937",        # Botões
    "btn_border": "#374151",
    "close_hover": "#ef4444"
}

# --- IDENTIDADE ---
APP_NAME = "STEAM VAULT"
CONFIG_FILE = "vault_config.json"
DEFAULT_CONFIG = {"steam_path": "", "backup_path": ""}

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
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)

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

    def run_backup(self, steam, backup_root):
        vault_folder = os.path.join(backup_root, "SteamVault_Backup")
        self.log(f"--- INICIANDO PROTOCOLO {APP_NAME} ---")
        self.safe_create_dir(vault_folder)
        
        self.copy_module(os.path.join(steam, "userdata"), os.path.join(vault_folder, "userdata"), "USERDATA")
        self.copy_module(os.path.join(steam, "config", "stplug-in"), os.path.join(vault_folder, "config", "stplug-in"), "STPLUG-IN")
        self.copy_module(os.path.join(steam, "config", "depotcache"), os.path.join(vault_folder, "config", "depotcache"), "DEPOTCACHE")
        self.copy_module(os.path.join(steam, "appcache", "stats"), os.path.join(vault_folder, "appcache", "stats"), "STATS")

        for dll in ["version.dll", "winmm.dll"]:
            src = os.path.join(steam, dll)
            if os.path.exists(src):
                if self.safe_copy(src, os.path.join(vault_folder, dll)):
                    self.log(f"[DLL] {dll} Protegida.")

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

        self.copy_module(os.path.join(origin, "userdata"), os.path.join(steam, "userdata"), "RESTORE USERDATA")
        self.copy_module(os.path.join(origin, "config", "stplug-in"), os.path.join(steam, "config", "stplug-in"), "RESTORE STPLUG-IN")
        self.copy_module(os.path.join(origin, "config", "depotcache"), os.path.join(steam, "config", "depotcache"), "RESTORE DEPOTCACHE")
        self.copy_module(os.path.join(origin, "appcache", "stats"), os.path.join(steam, "appcache", "stats"), "RESTORE STATS")

        for dll in ["version.dll", "winmm.dll"]:
            src = os.path.join(origin, dll)
            if os.path.exists(src):
                if self.safe_copy(src, os.path.join(steam, dll)):
                    self.log(f"[DLL] {dll} Restaurada.")

# --- MODO GUI (INTERFACE) ---
if GUI_AVAILABLE:
    class VaultWorkerGUI(QThread):
        log = pyqtSignal(str)
        finished = pyqtSignal()

        def __init__(self, mode, steam, backup):
            super().__init__()
            self.mode = mode
            self.steam = steam
            self.backup = backup
            self.engine = VaultEngine(self.emit_log)

        def emit_log(self, text):
            self.log.emit(text)

        def run(self):
            if self.mode == "backup":
                self.engine.run_backup(self.steam, self.backup)
            else:
                self.engine.run_restore(self.steam, self.backup)
            self.finished.emit()

    class SteamVaultGUI(QMainWindow):
        def __init__(self):
            super().__init__()
            self.config = ConfigManager.load()
            self.setFixedSize(900, 500)
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.old_pos = None
            self.init_ui()
            self.apply_styles()

        def init_ui(self):
            self.main_frame = QFrame()
            self.main_frame.setObjectName("MainFrame")
            self.setCentralWidget(self.main_frame)
            main_layout = QVBoxLayout(self.main_frame)
            main_layout.setContentsMargins(25, 15, 25, 25)
            main_layout.setSpacing(20)

            # --- TOPO ---
            top_bar = QHBoxLayout()
            title_box = QVBoxLayout(); title_box.setSpacing(0)
            
            lbl_title = QLabel(APP_NAME); lbl_title.setObjectName("Title")
            lbl_sub = QLabel("BACKUP E RESTAURAÇÃO"); lbl_sub.setObjectName("Subtitle")
            
            title_box.addWidget(lbl_title); title_box.addWidget(lbl_sub)
            top_bar.addLayout(title_box)
            top_bar.addStretch()
            
            self.btn_close = QPushButton("✕"); self.btn_close.setObjectName("BtnClose"); self.btn_close.setFixedSize(30, 30)
            self.btn_close.clicked.connect(self.close)
            top_bar.addWidget(self.btn_close)
            main_layout.addLayout(top_bar)

            # --- CONTEÚDO ---
            content = QHBoxLayout(); content.setSpacing(25)
            
            # Coluna Esquerda
            left = QVBoxLayout(); left.setSpacing(15)
            self.create_path(left, "DIRETÓRIO STEAM:", self.config['steam_path'], self.sel_steam, "lbl_steam")
            self.create_path(left, "LOCAL DO COFRE (BACKUP):", self.config['backup_path'], self.sel_backup, "lbl_backup")
            left.addStretch()
            
            actions = QHBoxLayout(); actions.setSpacing(10)
            btn_bkp = QPushButton("CRIAR BACKUP"); btn_bkp.setObjectName("BtnPrimary"); btn_bkp.clicked.connect(lambda: self.run_p("backup"))
            btn_res = QPushButton("RESTAURAR"); btn_res.setObjectName("BtnSecondary"); btn_res.clicked.connect(lambda: self.run_p("restore"))
            actions.addWidget(btn_bkp); actions.addWidget(btn_res)
            left.addLayout(actions)
            content.addLayout(left, stretch=4)

            # Coluna Direita (Log)
            right = QVBoxLayout(); right.setSpacing(5)
            right.addWidget(QLabel("REGISTRO DE OPERAÇÕES", styleSheet=f"color:{THEME['text_dim']}; font-weight:bold; font-size:10px;"))
            self.console = QTextEdit(); self.console.setReadOnly(True); self.console.setObjectName("Terminal")
            self.console.append(f"<span style='color:{THEME['text_dim']}'>Steam Vault Inicializado.</span>")
            right.addWidget(self.console)
            content.addLayout(right, stretch=6)
            
            main_layout.addLayout(content)

        def create_path(self, layout, title, val, cb, attr):
            layout.addWidget(QLabel(title, styleSheet=f"color:{THEME['accent']}; font-size:10px; font-weight:bold;"))
            row = QHBoxLayout()
            lbl = QLabel(val or "Não definido"); lbl.setStyleSheet(f"color:{THEME['text_main']}; font-family:'Consolas'; font-size:11px;")
            setattr(self, attr, lbl)
            btn = QPushButton("..."); btn.setFixedSize(30,25); btn.setObjectName("BtnSmall"); btn.clicked.connect(cb)
            row.addWidget(lbl); row.addWidget(btn)
            layout.addLayout(row)
            line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setStyleSheet(f"background:{THEME['btn_border']}; max-height:1px;")
            layout.addWidget(line)

        def update_term(self, text):
            col = THEME['text_main']
            if "[SUCESSO]" in text: col = THEME['success']
            elif "[ERRO]" in text: col = THEME['error']
            elif ">>>" in text: col = THEME['accent']
            self.console.append(f"<span style='color:{col}'>{text}</span>")
            self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

        def apply_styles(self):
            self.setStyleSheet(f"""
                QFrame#MainFrame {{ background: {THEME['bg_main']}; border: 1px solid {THEME['btn_border']}; border-radius: 8px; }}
                QLabel {{ color: {THEME['text_main']}; font-family: 'Segoe UI'; }}
                QLabel#Title {{ font-size: 22px; font-weight: 800; letter-spacing: 1px; }}
                QLabel#Subtitle {{ color: {THEME['text_dim']}; font-size: 10px; letter-spacing: 2px; }}
                QPushButton {{ background: {THEME['btn_bg']}; border: 1px solid {THEME['btn_border']}; color: {THEME['text_main']}; padding: 5px; border-radius: 4px; }}
                QPushButton:hover {{ border-color: {THEME['accent']}; }}
                QPushButton#BtnClose {{ background: transparent; border: none; font-weight: bold; }}
                QPushButton#BtnClose:hover {{ color: {THEME['close_hover']}; }}
                QPushButton#BtnPrimary {{ background: {THEME['accent']}; color: white; border: none; font-weight: bold; padding: 12px; }}
                QPushButton#BtnPrimary:hover {{ background: #2563eb; }}
                QPushButton#BtnSecondary {{ border: 1px solid {THEME['accent']}; color: {THEME['accent']}; font-weight: bold; padding: 12px; }}
                QTextEdit#Terminal {{ background: {THEME['bg_panel']}; border: 1px solid {THEME['btn_border']}; color: {THEME['text_main']}; font-family: 'Consolas'; font-size: 11px; padding: 10px; }}
                
                /* Estilo do Popup de Pergunta (QMessageBox) */
                QMessageBox {{ background-color: {THEME['bg_panel']}; color: {THEME['text_main']}; }}
                QMessageBox QLabel {{ color: {THEME['text_main']}; }}
            """)

        def sel_steam(self):
            p = QFileDialog.getExistingDirectory(self, "Pasta Steam"); 
            if p: self.config['steam_path'] = p; self.lbl_steam.setText(p); ConfigManager.save(self.config)
        def sel_backup(self):
            p = QFileDialog.getExistingDirectory(self, "Pasta para o Cofre"); 
            if p: self.config['backup_path'] = p; self.lbl_backup.setText(p); ConfigManager.save(self.config)

        def run_p(self, mode):
            if not self.config['steam_path'] or not self.config['backup_path']: self.update_term("[ERRO] Defina os diretórios."); return
            
            # Check Segurança (Overwrite) com Botoes Customizados
            if mode == "backup":
                tgt = os.path.join(self.config['backup_path'], "SteamVault_Backup")
                if os.path.exists(tgt) and os.listdir(tgt):
                    # Cria a caixa de mensagem customizada
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Cofre Ocupado")
                    msg.setText("Já existe um backup anterior.\nDeseja sobrescrever o cofre?")
                    msg.setIcon(QMessageBox.Icon.Question)
                    
                    # Botões em Português
                    btn_sim = msg.addButton("Sim", QMessageBox.ButtonRole.YesRole)
                    btn_nao = msg.addButton("Não", QMessageBox.ButtonRole.NoRole)
                    
                    # Aplica estilo manual para garantir
                    msg.setStyleSheet(f"background-color: {THEME['bg_panel']}; color: {THEME['text_main']};")
                    
                    msg.exec()
                    
                    if msg.clickedButton() != btn_sim:
                        self.update_term("Operação cancelada pelo usuário.")
                        return

            self.worker = VaultWorkerGUI(mode, self.config['steam_path'], self.config['backup_path'])
            self.worker.log.connect(self.update_term); self.worker.start()

        def mousePressEvent(self, e): self.old_pos = e.globalPosition().toPoint() if e.button() == Qt.MouseButton.LeftButton else None
        def mouseMoveEvent(self, e): 
            if self.old_pos: 
                d = e.globalPosition().toPoint() - self.old_pos; self.move(self.x()+d.x(), self.y()+d.y()); self.old_pos = e.globalPosition().toPoint()

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"{APP_NAME} Tool")
    parser.add_argument("action", nargs="?", choices=["backup", "restore"])
    parser.add_argument("--steam", help="Caminho Steam")
    parser.add_argument("--backup-path", help="Caminho Backup")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.action: run_cli(args)
    elif GUI_AVAILABLE:
        app = QApplication(sys.argv)
        w = SteamVaultGUI()
        w.show()
        sys.exit(app.exec())
    else: print("[ERRO] Instale PyQt6 ou use argumentos CLI.")
