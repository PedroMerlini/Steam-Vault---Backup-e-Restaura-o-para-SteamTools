from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QProgressBar, QFrame, QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QCursor, QIcon
import os
from .constants import THEME, APP_NAME
from .config_manager import ConfigManager
from .engine import VaultEngine

class VaultWorkerGUI(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, mode, steam, backup, drive_mgr=None):
        super().__init__()
        self.mode = mode
        self.steam = steam
        self.backup = backup
        self.drive_mgr = drive_mgr
        self.engine = VaultEngine(self.emit_log)

    def emit_log(self, text):
        self.log.emit(text)

    def run(self):
        if self.mode == "backup":
            self.engine.run_backup(self.steam, self.backup)
        elif self.mode == "restore":
            self.engine.run_restore(self.steam, self.backup)
        elif self.mode == "cloud_upload":
            zip_path = os.path.join(self.backup, "SteamVault_Backup.zip")
            if self.drive_mgr: self.drive_mgr.upload_file(zip_path)
        elif self.mode == "cloud_download":
            dest_path = os.path.join(self.backup, "SteamVault_Backup.zip")
            if self.drive_mgr: self.drive_mgr.download_latest_backup(dest_path)
        
        self.finished.emit()

class SteamVaultGUI(QMainWindow):
    sig_cloud_log = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = ConfigManager.load()
        self.setFixedSize(900, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)  # Essential for hover detection
        self.old_pos = None
        self.resize_margin = 10
        self.resize_mode = None
        self.is_maximized = False
        
        # Lazy Import to avoid potential startup crashes or circular deps
        from .cloud import DriveManager
        self.drive = DriveManager(self.update_term_cloud)
        
        self.init_ui()
        self.apply_styles()
        
        # Connect signal for thread-safe logging
        self.sig_cloud_log.connect(self.update_term)

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
        
        self.btn_min = QPushButton("─"); self.btn_min.setObjectName("BtnMin"); self.btn_min.setFixedSize(30, 30)
        self.btn_min.clicked.connect(self.showMinimized)
        top_bar.addWidget(self.btn_min)

        self.btn_max = QPushButton("☐"); self.btn_max.setObjectName("BtnMax"); self.btn_max.setFixedSize(30, 30)
        self.btn_max.clicked.connect(self.toggle_maximize)
        top_bar.addWidget(self.btn_max)

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
        
        # --- CLOUD SECTION ---
        left.addSpacing(10)
        left.addWidget(QLabel("NUVEM (GOOGLE DRIVE)", styleSheet=f"color:{THEME['accent']}; font-size:10px; font-weight:bold;"))
        
        cloud_row = QHBoxLayout(); cloud_row.setSpacing(10)
        btn_login = QPushButton("LOGIN"); btn_login.setFixedWidth(60); btn_login.setObjectName("BtnSmall")
        btn_login.clicked.connect(self.cloud_login)
        
        btn_up = QPushButton("☁ ENVIAR"); btn_up.setObjectName("BtnCloud"); btn_up.clicked.connect(lambda: self.run_p("cloud_upload"))
        btn_down = QPushButton("☁ BAIXAR"); btn_down.setObjectName("BtnCloud"); btn_down.clicked.connect(lambda: self.run_p("cloud_download"))
        
        cloud_row.addWidget(btn_login); cloud_row.addWidget(btn_up); cloud_row.addWidget(btn_down)
        left.addLayout(cloud_row)

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

    def update_term_cloud(self, text):
        # Thread-safe logging via Signal
        self.sig_cloud_log.emit(text)

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
            QPushButton#BtnMin {{ background: transparent; border: none; font-weight: bold; }}
            QPushButton#BtnMin:hover {{ color: {THEME['text_main']}; background-color: {THEME['btn_border']}; }}
            QPushButton#BtnMax {{ background: transparent; border: none; font-weight: bold; }}
            QPushButton#BtnMax:hover {{ color: {THEME['text_main']}; background-color: {THEME['btn_border']}; }}
            QPushButton#BtnPrimary {{ background: {THEME['accent']}; color: white; border: none; font-weight: bold; padding: 12px; }}
            QPushButton#BtnPrimary:hover {{ background: #2563eb; }}
            QPushButton#BtnSecondary {{ border: 1px solid {THEME['accent']}; color: {THEME['accent']}; font-weight: bold; padding: 12px; }}
            QPushButton#BtnCloud {{ background: {THEME['btn_bg']}; border: 1px solid {THEME['text_dim']}; color: {THEME['text_dim']}; padding: 8px; font-size: 10px; }}
            QPushButton#BtnCloud:hover {{ border-color: {THEME['text_main']}; color: {THEME['text_main']}; }}
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
            tgt_folder = os.path.join(self.config['backup_path'], "SteamVault_Backup")
            tgt_zip = os.path.join(self.config['backup_path'], "SteamVault_Backup.zip")
            
            exists_folder = os.path.exists(tgt_folder) and os.listdir(tgt_folder)
            exists_zip = os.path.exists(tgt_zip)

            if exists_folder or exists_zip:
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

        self.worker = VaultWorkerGUI(mode, self.config['steam_path'], self.config['backup_path'], self.drive)
        self.worker.log.connect(self.update_term); self.worker.start()

    def cloud_login(self):
        self.update_term(">>> Iniciando Login Google...")
        # Run in thread to not freeze UI
        import threading
        def _auth():
            if self.drive.authenticate(): pass # Log handled by callback
        
        t = threading.Thread(target=_auth)
        t.start()

    
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.is_maximized = False
            self.btn_max.setText("☐")
            self.main_frame.setStyleSheet(f"QFrame#MainFrame {{ background: {THEME['bg_main']}; border: 1px solid {THEME['btn_border']}; border-radius: 8px; }}")
        else:
            self.showMaximized()
            self.is_maximized = True
            self.btn_max.setText("❐")
            # Remove border/radius when maximized for cleaner look
            self.main_frame.setStyleSheet(f"QFrame#MainFrame {{ background: {THEME['bg_main']}; border: none; border-radius: 0px; }}")

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.old_pos = e.globalPosition().toPoint()
            
            # Identify resize mode if edges
            if not self.isMaximized():
                x = e.position().x()
                y = e.position().y()
                w = self.width()
                h = self.height()
                m = self.resize_margin

                on_left = x < m
                on_right = x > w - m
                on_top = y < m
                on_bottom = y > h - m

                if on_top and on_left: self.resize_mode = "top_left"
                elif on_top and on_right: self.resize_mode = "top_right"
                elif on_bottom and on_left: self.resize_mode = "bottom_left"
                elif on_bottom and on_right: self.resize_mode = "bottom_right"
                elif on_left: self.resize_mode = "left"
                elif on_right: self.resize_mode = "right"
                elif on_top: self.resize_mode = "top"
                elif on_bottom: self.resize_mode = "bottom"
                else: self.resize_mode = None
            else:
                self.resize_mode = None

    def mouseReleaseEvent(self, e):
        self.resize_mode = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseMoveEvent(self, e):
        # Update Cursor Icon
        if not self.isMaximized():
            x = e.position().x()
            y = e.position().y()
            w = self.width()
            h = self.height()
            m = self.resize_margin

            on_left = x < m
            on_right = x > w - m
            on_top = y < m
            on_bottom = y > h - m
            
            if not self.resize_mode: # Only update cursor if not currently dragging
                if (on_top and on_left) or (on_bottom and on_right): self.setCursor(Qt.CursorShape.FDiagPattern)
                elif (on_top and on_right) or (on_bottom and on_left): self.setCursor(Qt.CursorShape.BDiagPattern)
                elif on_left or on_right: self.setCursor(Qt.CursorShape.SizeHorCursor)
                elif on_top or on_bottom: self.setCursor(Qt.CursorShape.SizeVerCursor)
                else: self.setCursor(Qt.CursorShape.ArrowCursor)

        # Handle Dragging/Resizing
        if e.buttons() & Qt.MouseButton.LeftButton:
            if self.resize_mode:
                # Resizing logic
                g = self.geometry()
                gp = e.globalPosition().toPoint()
                
                # Use raw deltas might be better, but simpler to calculate new rect
                # Note: This simple logic might jitter if not careful with coordinate mapping, 
                # but standard for manual implementation.
                
                if "left" in self.resize_mode:
                    new_w = g.right() - gp.x()
                    if new_w > 100: # min width
                        g.setLeft(gp.x())
                if "right" in self.resize_mode:
                    new_w = gp.x() - g.left()
                    if new_w > 100:
                        g.setRight(gp.x())
                if "top" in self.resize_mode:
                    new_h = g.bottom() - gp.y()
                    if new_h > 100: # min height
                        g.setTop(gp.y())
                if "bottom" in self.resize_mode:
                    new_h = gp.y() - g.top()
                    if new_h > 100:
                        g.setBottom(gp.y())
                
                self.setGeometry(g)
                
            elif self.old_pos and not self.isMaximized():
                # Moving Window
                d = e.globalPosition().toPoint() - self.old_pos
                self.move(self.x() + d.x(), self.y() + d.y())
                self.old_pos = e.globalPosition().toPoint()
