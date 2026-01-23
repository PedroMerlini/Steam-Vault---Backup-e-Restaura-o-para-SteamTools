# Steam Vault - Backup e Restauração para SteamTools

![Build Status](https://github.com/PedroMerlini/Steam-Vault---Backup-e-Restaura-o-para-SteamTools/actions/workflows/build.yml/badge.svg)

Um programa em Python desenvolvido para realizar backups e restaurá-los posteriormente para quem utiliza o SteamTools.

Atualmente, ele salva as pastas:
- `depotcache` (arquivos .manifest)
- `stplug-in` (arquivos .lua)
- `appcache\stats` (Basicamente conquistas)
- `userdata` (Tempo de jogo, Screenshots e possíveis saves)

Este programa foi feito por uma pessoa que ainda está aprendendo a programar, então podem existir bugs.

Estou planejando fazer uma versão integrada ao Millennium; aí o backup e a restauração seriam feitos diretamente de dentro da Steam.

---

## 🚀 Download

### Baixar executável pronto (Recomendado)
1. Vá na aba **[Releases](../../releases)** do GitHub
2. Baixe o arquivo `SteamVault.exe`
3. Execute diretamente - não precisa instalar nada!

---

## 🔧 Para Desenvolvedores

### Build Manual (Windows)
Dê duplo clique no arquivo `build_exe.bat` ou execute:
```cmd
pip install -r requirements.txt
pyinstaller --onefile --windowed --name "SteamVault" "STEAM VAULT.py"
```
O executável será gerado em `dist/SteamVault.exe`

### Build Automático via GitHub Actions
O projeto usa GitHub Actions para buildar automaticamente. Existem duas formas:

**1. Criar uma Release (via Tag):**
```bash
git tag v1.0.0
git push --tags
```
O executável será publicado automaticamente nos **Releases**.

**2. Build Manual:**
- Vá em **Actions** → **"Build Windows Executable"** → **"Run workflow"**
- Após o build, baixe o `.exe` nos **Artifacts**