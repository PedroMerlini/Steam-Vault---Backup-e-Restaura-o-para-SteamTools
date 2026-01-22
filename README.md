# Steam Vault

O **Steam Vault** é uma ferramenta gráfica avançada para backup e restauração de dados críticos da Steam e do SteamTools. Desenvolvido para ser robusto, multiplataforma (Windows/Linux) e fácil de usar.

## 🚀 Funcionalidades

### 🛡️ Backup e Restauração
Salva e restaura dados essenciais que a Steam Cloud muitas vezes ignora:
-   **Configurações do SteamTools**: `config/stplug-in`, `config/depotcache`.
-   **Estatísticas e Conquistas**: `appcache/stats`.
-   **Userdata**: Screenshots, configurações locais e saves.
-   **Proteção de DLLs (Windows)**: Faz backup automático de `version.dll` e `winmm.dll`.
-   **Saves do Proton (Linux)**: Detecta e salva automaticamente os jogos rodando via Proton em `compatdata`.
-   **SLS Steam Config (Linux)**: Detecta e salva automaticamente a configuração do SLS (`~/.config/SLSsteam`).

### ☁️ Nuvem (Google Drive)
Integração nativa com Google Drive:
-   **Login Seguro**: Autenticação via OAuth2.
-   **Upload**: Envie seus backups compactados diretamente para a nuvem.
-   **Download**: Baixe e restaure a versão mais recente de qualquer lugar.

### ⚡ Alta Compressão
Todos os backups são automaticamente compactados em formato `.zip` com nível máximo de compressão, economizando espaço em disco e na nuvem.

### 🎨 Interface Moderna
-   UI personalizada "Midnight Pro Design".
-   Janela frameless (sem bordas) com suporte a arrastar, minimizar e fechar.
-   Logs detalhados em tempo real de todas as operações.

---

## 🛠️ Instalação e Uso

### Linux
1.  Garanta que tem o Python 3 instalado.
2.  Execute o script de inicialização:
    ```bash
    ./start.sh
    ```
    *O script criará automaticamente o ambiente virtual (venv) e instalará as dependências.*

### Windows
1.  Garanta que tem o Python 3 instalado (marque "Add to PATH" na instalação).
2.  Execute o launcher do PowerShell:
    ```powershell
    ./launcher.ps1
    ```
    *Se houver erro de permissão, abra o PowerShell como Admin e rode `Set-ExecutionPolicy RemoteSigned`.*

---

## 🔑 Configuração da Nuvem (Opcional)

Para usar os recursos de nuvem, você precisa de um arquivo `credentials.json` do Google Cloud:

1.  Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2.  Crie um projeto e ative a **Google Drive API**.
3.  Vá em **Credenciais** -> **Criar Credenciais** -> **ID do cliente OAuth**.
4.  Escolha "App para computador" (Desktop App).
5.  Baixe o arquivo JSON, renomeie para `credentials.json` e coloque na **pasta raiz** do Steam Vault.

---

## ⚠️ Notas Importantes
-   **Permissões (Linux)**: O programa pode solicitar sua senha (via interface gráfica `pkexec`) para restaurar/copiar arquivos em locais protegidos (como configurações do SLS).
-   **Segurança**: O programa verifica se já existe um backup antes de sobrescrever.
-   **Desenvolvimento**: Projeto em evolução contínua.

---
*Desenvolvido com Python e PyQt6.*