# Steam Vault - Millennium Plugin

Backup e Restauração de dados do SteamTools (userdata, configs, stats, DLLs).

## Instalação

1. Baixe a última release (`.zip`)
2. Extraia na pasta de plugins do Millennium:
   - **Windows:** `C:\Program Files (x86)\Steam\plugins\steamvault`
   - **Linux:** `~/.local/share/millennium/plugins/steamvault`
3. Reinicie a Steam

## Uso

- Abra qualquer página web da Steam (Store, Community, etc)
- Pressione **Ctrl+Shift+V** para abrir o modal de backup/restore

## Estrutura

```
steamvault/
├── backend/
│   └── main.py         # Lógica de backup/restore (Python)
├── public/
│   └── steamvault.js   # Interface do usuário (JavaScript)
├── plugin.json         # Configuração do plugin
└── package.json        # Metadados
```

## O que é salvo no backup?

- `userdata/` - Saves, screenshots, configurações de jogos
- `config/stplug-in/` - Configurações de plugins
- `config/depotcache/` - Cache de depots
- `appcache/stats/` - Estatísticas
- `version.dll` e `winmm.dll` - DLLs do SteamTools (Windows)

## Requisitos

- [Millennium](https://steambrew.app) v2.30+
- Steam instalada

## Licença

MIT
