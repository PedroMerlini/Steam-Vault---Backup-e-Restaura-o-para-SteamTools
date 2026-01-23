# 🔒 Steam Vault

**Backup e Restauração de dados do SteamTools** - Proteja seus saves, configurações, estatísticas e DLLs.

---

## 📦 Instalação

Existem **duas formas** de usar o Steam Vault:

### Opção 1: Aplicativo Standalone (Recomendado)

Interface gráfica completa para gerenciar backups.

#### Windows
```bash
# Clone o repositório
git clone https://github.com/PedroMerlini/Steam-Vault---Backup-e-Restaura-o-para-SteamTools.git
cd Steam-Vault---Backup-e-Restaura-o-para-SteamTools

# Execute o launcher (instala Python automaticamente se necessário)
launcher.bat
```

#### Linux
```bash
# Clone o repositório
git clone https://github.com/PedroMerlini/Steam-Vault---Backup-e-Restaura-o-para-SteamTools.git
cd Steam-Vault---Backup-e-Restaura-o-para-SteamTools

# Dê permissão e execute
chmod +x launcher.sh
./launcher.sh
```

---

### Opção 2: Plugin Millennium

Integração direta com a Steam via [Millennium](https://steambrew.app).

#### Instalação
1. Baixe a pasta `steamvault/` ou a release `.zip`
2. Copie para a pasta de plugins:
   - **Windows:** `C:\Program Files (x86)\Steam\plugins\steamvault`
   - **Linux:** `~/.local/share/millennium/plugins/steamvault`
3. Reinicie a Steam

#### Uso
- Abra qualquer página web da Steam (Store, Community, etc)
- Pressione **Ctrl+Shift+V** para abrir o modal de backup/restore

---

## 🎯 O que é salvo no backup?

| Pasta/Arquivo | Descrição |
|---------------|-----------|
| `userdata/` | Saves, screenshots, configurações de jogos |
| `config/stplug-in/` | Configurações de plugins Steam |
| `config/depotcache/` | Cache de depots |
| `appcache/stats/` | Estatísticas de jogos |
| `version.dll` | DLL do SteamTools (Windows) |
| `winmm.dll` | DLL do SteamTools (Windows) |

---

## 📁 Estrutura do Projeto

```
Steam-Vault/
├── src/                    # Aplicativo Standalone
│   ├── core/vault.py       # Lógica de backup/restore
│   ├── gui/window.py       # Interface PyQt6
│   └── utils/config.py     # Gerenciamento de config
├── steamvault/             # Plugin Millennium
│   ├── backend/main.py     # Backend Python
│   ├── public/steamvault.js# Frontend JavaScript
│   └── plugin.json         # Configuração
├── launcher.bat            # Launcher Windows
├── launcher.sh             # Launcher Linux
└── requirements.txt        # Dependências Python
```

---

## ⚙️ Requisitos

### Standalone
- Python 3.10+
- PyQt6

### Plugin Millennium
- [Millennium](https://steambrew.app) v2.30+
- Steam instalada

---

## 🚀 Funcionalidades

- ✅ Backup paralelo multi-thread (8 threads)
- ✅ Barra de progresso em tempo real
- ✅ Detecção automática do caminho da Steam
- ✅ Suporte Windows e Linux
- ✅ Integração com Millennium

---

## 📄 Licença

MIT
