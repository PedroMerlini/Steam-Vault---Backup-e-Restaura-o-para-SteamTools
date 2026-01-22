import os.path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import io
from googleapiclient.http import MediaIoBaseDownload

class DriveManager:
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'

    def __init__(self, log_callback=None):
        self.creds = None
        self.service = None
        self.log = log_callback if log_callback else print

    def authenticate(self):
        """Autentica o usuário via OAuth2."""
        if not os.path.exists(self.CREDENTIALS_FILE):
             self.log("[ERRO] Arquivo 'credentials.json' não encontrado. Obtenha no console do Google Cloud.")
             return False

        if os.path.exists(self.TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    self.log(f"[AUTH] Falha ao renovar token: {e}")
                    self.creds = None # Force re-login
            
            if not self.creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open(self.TOKEN_FILE, 'w') as token:
                        token.write(self.creds.to_json())
                except Exception as e:
                     self.log(f"[ERRO] Falha na autenticação: {e}")
                     return False

        try:
            self.service = build('drive', 'v3', credentials=self.creds)
            self.log("[SUCESSO] Conectado ao Google Drive.")
            return True
        except Exception as e:
            self.log(f"[ERRO] Falha ao conectar serviço: {e}")
            return False

    def upload_file(self, file_path):
        if not self.service: 
            if not self.authenticate(): return False

        if not os.path.exists(file_path):
            self.log(f"[ERRO] Arquivo não encontrado: {file_path}")
            return False

        file_name = os.path.basename(file_path)
        
        # Check if file exists to update it instead of creating duplicate
        query = f"name = '{file_name}' and trashed = false"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, mimetype='application/zip', resumable=True)

        try:
            if items:
                # Update existing
                file_id = items[0]['id']
                self.log(f">>> Atualizando backup existente (ID: {file_id})...")
                self.service.files().update(fileId=file_id, media_body=media).execute()
                self.log("[SUCESSO] Backup atualizado na nuvem.")
            else:
                # Create new
                self.log(f">>> Enviando novo backup para nuvem...")
                self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                self.log("[SUCESSO] Backup enviado para nuvem.")
            return True
        except Exception as e:
            self.log(f"[ERRO] Falha no upload: {e}")
            return False

    def download_latest_backup(self, dest_path):
        if not self.service: 
            if not self.authenticate(): return False

        try:
            # Find file
            query = "name = 'SteamVault_Backup.zip' and trashed = false"
            results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)', orderBy='modifiedTime desc').execute()
            items = results.get('files', [])

            if not items:
                self.log("[INFO] Nenhum backup encontrado no Drive.")
                return False

            file_id = items[0]['id']
            self.log(f">>> Baixando backup (ID: {file_id})...")

            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(dest_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                # self.log(f"Download {int(status.progress() * 100)}%")
            
            self.log("[SUCESSO] Download concluído.")
            return True

        except Exception as e:
            self.log(f"[ERRO] Falha no download: {e}")
            return False
