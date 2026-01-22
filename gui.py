from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QProgressBar, QFrame, QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QCursor, QIcon
import os
from constants import THEME, APP_NAME
from config_manager import ConfigManager
from engine import VaultEngine

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
