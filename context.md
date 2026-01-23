# Projeto: Steam Vault - Backup e Restauração

Ferramenta em Python para backup e restauração de arquivos críticos do SteamTools (userdata, configs, stats, DLLs).

## Tecnologia
- **Linguagem:** Python 3
- **GUI:** PyQt6 (Auto-instalável)
- **Bibliotecas:** `shutil`, `json`, `subprocess`, `argparse`

## Estrutura
- `STEAM VAULT.py`: Script único contendo toda a lógica (GUI, CLI, Backup Engine).
- `vault_config.json`: Arquivo de configuração (caminhos Steam e Backup).
- `README.md`: Documentação básica.

## Funcionalidades
- **Backup:** Copia pastas específicas (`userdata`, `stplug-in`, `depotcache`, `stats`) e DLLs.
- **Restore:** Restaura os arquivos do backup para o diretório Steam.
- **Modos:**
    - **GUI:** Interface gráfica moderna com tema escuro ("Midnight Pro").
    - **CLI:** Interface de linha de comando para automação.
- **Auto-setup:** Instala `PyQt6` se não estiver presente.

## Pontos de Atenção (Audit Preliminar)
- Script monolítico (mistura lógica de negócio/GUI/Config).
- Manipulação de arquivos direta.
- Execução de subprocessos para instalação de pip.
