// Steam Vault - Plugin para Millennium
// Injeta botão de backup/restore no menu da Steam
(function () {
    'use strict';

    // Log para debug via backend
    function backendLog(message) {
        try {
            if (typeof Millennium !== 'undefined' && typeof Millennium.callServerMethod === 'function') {
                Millennium.callServerMethod('steamvault', 'Logger.log', { message: String(message) });
            }
        } catch (err) {
            console.warn('[SteamVault] backendLog failed', err);
        }
    }

    backendLog('Steam Vault script loaded');

    // Estado
    let isOperationRunning = false;
    let currentBackupPath = '';

    // Injetar estilos
    function ensureStyles() {
        if (document.getElementById('steamvault-styles')) return;
        try {
            const style = document.createElement('style');
            style.id = 'steamvault-styles';
            style.textContent = `
                .steamvault-btn {
                    padding: 10px 20px;
                    background: rgba(59, 130, 246, 0.15);
                    border: 2px solid rgba(59, 130, 246, 0.4);
                    border-radius: 8px;
                    color: #3b82f6;
                    font-size: 14px;
                    font-weight: 600;
                    text-decoration: none;
                    transition: all 0.3s ease;
                    cursor: pointer;
                    margin: 4px 0;
                    display: block;
                    text-align: center;
                }
                .steamvault-btn:hover:not([disabled]) {
                    background: rgba(59, 130, 246, 0.25);
                    transform: translateY(-1px);
                    border-color: #3b82f6;
                }
                .steamvault-btn.primary {
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    border-color: #3b82f6;
                    color: #fff;
                }
                .steamvault-btn.primary:hover:not([disabled]) {
                    background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
                }
                .steamvault-btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                .steamvault-overlay {
                    position: fixed;
                    inset: 0;
                    background: rgba(0,0,0,0.75);
                    backdrop-filter: blur(8px);
                    z-index: 99999;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .steamvault-modal {
                    background: linear-gradient(135deg, #1b2838 0%, #2a475e 100%);
                    color: #fff;
                    border: 2px solid #3b82f6;
                    border-radius: 12px;
                    min-width: 400px;
                    max-width: 500px;
                    padding: 24px;
                    box-shadow: 0 20px 60px rgba(0,0,0,.8);
                }
                .steamvault-title {
                    font-size: 20px;
                    font-weight: 700;
                    color: #3b82f6;
                    margin-bottom: 16px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                .steamvault-input {
                    width: 100%;
                    padding: 10px;
                    border-radius: 6px;
                    border: 1px solid #374151;
                    background: #111827;
                    color: #fff;
                    font-size: 13px;
                    margin-bottom: 12px;
                    box-sizing: border-box;
                }
                .steamvault-result {
                    padding: 10px;
                    border-radius: 6px;
                    background: #111827;
                    border: 1px solid #374151;
                    margin-top: 12px;
                    font-size: 13px;
                }
            `;
            document.head.appendChild(style);
        } catch (err) {
            backendLog('Styles injection failed: ' + err);
        }
    }

    // Obter caminho padrão do backup
    async function getDefaultPath() {
        try {
            if (typeof Millennium !== 'undefined' && typeof Millennium.callServerMethod === 'function') {
                const res = await Millennium.callServerMethod('steamvault', 'GetDefaultBackupPath', {});
                const data = typeof res === 'string' ? JSON.parse(res) : res;
                if (data && data.success && data.path) {
                    return data.path;
                }
            }
        } catch (err) {
            backendLog('GetDefaultBackupPath failed: ' + err);
        }
        return '';
    }

    // Executar backup
    async function runBackup(path) {
        try {
            if (typeof Millennium !== 'undefined' && typeof Millennium.callServerMethod === 'function') {
                const res = await Millennium.callServerMethod('steamvault', 'RunBackup', { backupPath: path });
                return typeof res === 'string' ? JSON.parse(res) : res;
            }
        } catch (err) {
            backendLog('RunBackup failed: ' + err);
            return { success: false, error: String(err) };
        }
        return { success: false, error: 'Millennium not available' };
    }

    // Executar restore
    async function runRestore(path) {
        try {
            if (typeof Millennium !== 'undefined' && typeof Millennium.callServerMethod === 'function') {
                const res = await Millennium.callServerMethod('steamvault', 'RunRestore', { backupPath: path });
                return typeof res === 'string' ? JSON.parse(res) : res;
            }
        } catch (err) {
            backendLog('RunRestore failed: ' + err);
            return { success: false, error: String(err) };
        }
        return { success: false, error: 'Millennium not available' };
    }

    // Mostrar modal principal
    async function showVaultModal() {
        if (document.querySelector('.steamvault-overlay')) return;

        ensureStyles();

        // Obter caminho padrão se não tiver
        if (!currentBackupPath) {
            currentBackupPath = await getDefaultPath();
        }

        const overlay = document.createElement('div');
        overlay.className = 'steamvault-overlay';

        const modal = document.createElement('div');
        modal.className = 'steamvault-modal';

        modal.innerHTML = `
            <div class="steamvault-title">🔒 Steam Vault</div>
            <p style="color: #9ca3af; margin-bottom: 16px; font-size: 13px;">
                Backup e Restauração de dados do SteamTools
            </p>
            
            <label style="display: block; margin-bottom: 4px; color: #3b82f6; font-size: 11px; font-weight: 600;">
                CAMINHO DO BACKUP:
            </label>
            <input type="text" class="steamvault-input" id="sv-backup-path" value="${currentBackupPath}" />
            
            <div style="display: flex; gap: 10px;">
                <button class="steamvault-btn primary" id="sv-btn-backup" style="flex: 1;">
                    CRIAR BACKUP
                </button>
                <button class="steamvault-btn" id="sv-btn-restore" style="flex: 1;">
                    RESTAURAR
                </button>
            </div>
            
            <div class="steamvault-result" id="sv-result" style="display: none;"></div>
            
            <div style="margin-top: 16px; text-align: right;">
                <button class="steamvault-btn" id="sv-btn-close">Fechar</button>
            </div>
        `;

        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // Event listeners
        const pathInput = modal.querySelector('#sv-backup-path');
        const btnBackup = modal.querySelector('#sv-btn-backup');
        const btnRestore = modal.querySelector('#sv-btn-restore');
        const btnClose = modal.querySelector('#sv-btn-close');
        const resultDiv = modal.querySelector('#sv-result');

        pathInput.addEventListener('change', (e) => {
            currentBackupPath = e.target.value;
        });

        btnClose.addEventListener('click', () => {
            overlay.remove();
        });

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });

        btnBackup.addEventListener('click', async () => {
            if (isOperationRunning) return;

            const path = pathInput.value.trim();
            if (!path) {
                resultDiv.textContent = '❌ Defina o caminho do backup!';
                resultDiv.style.display = 'block';
                return;
            }

            isOperationRunning = true;
            btnBackup.disabled = true;
            btnRestore.disabled = true;
            resultDiv.textContent = '⏳ Fazendo backup...';
            resultDiv.style.display = 'block';

            const result = await runBackup(path);

            if (result.success) {
                resultDiv.textContent = `✅ Backup concluído! ${result.files_copied || 0} arquivos copiados.`;
            } else {
                resultDiv.textContent = `❌ Erro: ${result.error || 'Falha desconhecida'}`;
            }

            isOperationRunning = false;
            btnBackup.disabled = false;
            btnRestore.disabled = false;
        });

        btnRestore.addEventListener('click', async () => {
            if (isOperationRunning) return;

            const path = pathInput.value.trim();
            if (!path) {
                resultDiv.textContent = '❌ Defina o caminho do backup!';
                resultDiv.style.display = 'block';
                return;
            }

            isOperationRunning = true;
            btnBackup.disabled = true;
            btnRestore.disabled = true;
            resultDiv.textContent = '⏳ Restaurando...';
            resultDiv.style.display = 'block';

            const result = await runRestore(path);

            if (result.success) {
                resultDiv.textContent = `✅ Restauração concluída! ${result.files_restored || 0} arquivos restaurados.`;
            } else {
                resultDiv.textContent = `❌ Erro: ${result.error || 'Falha desconhecida'}`;
            }

            isOperationRunning = false;
            btnBackup.disabled = false;
            btnRestore.disabled = false;
        });
    }

    // Injetar botão no menu da biblioteca
    function injectLibraryButton() {
        // Procurar pelo menu dropdown da biblioteca
        const menuContainers = document.querySelectorAll('[class*="contextmenu"], [class*="ContextMenu"], [class*="popup"], .popup_body');

        menuContainers.forEach(container => {
            // Evitar duplicação
            if (container.querySelector('.steamvault-menu-item')) return;

            // Verificar se parece um menu de contexto
            const menuItems = container.querySelectorAll('[class*="MenuItem"], [class*="menuitem"], .popup_menu_item');

            if (menuItems.length > 0) {
                ensureStyles();

                const separator = document.createElement('div');
                separator.style.cssText = 'height: 1px; background: #374151; margin: 8px 0;';

                const vaultItem = document.createElement('div');
                vaultItem.className = 'steamvault-menu-item popup_menu_item';
                vaultItem.style.cssText = 'padding: 8px 16px; color: #3b82f6; cursor: pointer; display: flex; align-items: center; gap: 8px;';
                vaultItem.innerHTML = '🔒 Steam Vault';

                vaultItem.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    showVaultModal();
                });

                vaultItem.addEventListener('mouseenter', () => {
                    vaultItem.style.background = 'rgba(59, 130, 246, 0.15)';
                });

                vaultItem.addEventListener('mouseleave', () => {
                    vaultItem.style.background = 'none';
                });

                container.appendChild(separator);
                container.appendChild(vaultItem);

                backendLog('Steam Vault menu item injected');
            }
        });
    }

    // Observar mudanças no DOM para injetar em menus que aparecem dinamicamente
    function startObserving() {
        const observer = new MutationObserver((mutations) => {
            let shouldCheck = false;

            mutations.forEach(mutation => {
                if (mutation.addedNodes.length > 0) {
                    shouldCheck = true;
                }
            });

            if (shouldCheck) {
                setTimeout(injectLibraryButton, 100);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        backendLog('MutationObserver started');
    }

    // Também adicionar um atalho de teclado (Ctrl+Shift+V)
    function setupKeyboardShortcut() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'V') {
                e.preventDefault();
                showVaultModal();
            }
        });

        backendLog('Keyboard shortcut registered (Ctrl+Shift+V)');
    }

    // Inicializar
    function init() {
        ensureStyles();
        injectLibraryButton();
        startObserving();
        setupKeyboardShortcut();
        backendLog('Steam Vault initialized');
    }

    // Aguardar DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
