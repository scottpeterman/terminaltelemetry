// interfacePanel.js

// Make the class available globally
window.InterfacePanel = class InterfacePanel {
    constructor(debugId) {
        this.debugId = debugId;
        this.panel = null;
    }

    update(interfaces) {
        console.group(`InterfacePanel ${this.debugId}: Updating interfaces`);

        try {
            // Early return if no valid interface data
            if (!interfaces?.length) {
                console.log('No new interface data to process');
                console.groupEnd();
                return;
            }

            // Get or create the interfaces panel
            this.panel = this.getOrCreatePanel();
            if (!this.panel) {
                throw new Error('Failed to get or create interfaces panel');
            }

            // Update only the grid content instead of the entire panel
            const interfaceGrid = this.panel.querySelector('.interface-grid');
            if (interfaceGrid) {
                this.updateGrid(interfaceGrid, interfaces);
            } else {
                console.warn('Interface grid not found, initializing full panel content');
                this.initializePanelContent(this.panel, interfaces);
            }

            console.log('Successfully updated interfaces:', interfaces);
        } catch (error) {
            console.error('Error updating interfaces:', error);
        }

        console.groupEnd();
    }

    getOrCreatePanel() {
        let panel = document.getElementById('interfaces-panel');

        if (!panel) {
            console.log('Creating new interfaces panel');
            panel = document.createElement('div');
            panel.id = 'interfaces-panel';
            panel.className = 'hud-panel';

            const container = document.querySelector('.controls-section .hud-container');
            if (!container) {
                console.error('Could not find container for interfaces panel');
                return null;
            }

            container.appendChild(panel);
            this.initializePanelStructure(panel);
        }

        return panel;
    }

    initializePanelStructure(panel) {
        panel.innerHTML = `
            <div class="hud-panel-background"></div>
            <div class="hud-panel-border"></div>
            ${this.getHUDCorners()}
            <div class="hud-panel-title">— Interfaces —</div>
            <div class="hud-panel-content">
                <div class="interface-grid"></div>
            </div>
        `;
    }

    getHUDCorners() {
        return `
            <div class="hud-corner top-left">
                <svg viewBox="0 0 100 100">
                    <path d="M 0 40 L 40 0 L 100 0 L 100 10 L 45 10 L 10 45 L 10 100 L 0 100 Z"
                          fill="none" stroke="currentColor" stroke-width="1"/>
                    <path d="M 0 45 L 35 10 M 45 10 L 95 10"
                          fill="none" stroke="currentColor" stroke-width="1" opacity="0.5"/>
                    <circle cx="40" cy="10" r="2" fill="currentColor"/>
                    <path d="M 55 10 L 65 0 M 75 10 L 85 0"
                          fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
                </svg>
            </div>
            <div class="hud-corner top-right">
                <svg viewBox="0 0 100 100">
                    <path d="M 0 0 L 60 0 L 100 40 L 100 100 L 90 100 L 90 45 L 55 10 L 0 10 Z"
                          fill="none" stroke="currentColor" stroke-width="1"/>
                </svg>
            </div>
            <div class="hud-corner bottom-right">
                <svg viewBox="0 0 100 100">
                    <path d="M 100 0 L 100 60 L 60 100 L 0 100 L 0 90 L 55 90 L 90 55 L 90 0 Z"
                          fill="none" stroke="currentColor" stroke-width="1"/>
                </svg>
            </div>
            <div class="hud-corner bottom-left">
                <svg viewBox="0 0 100 100">
                    <path d="M 40 100 L 0 60 L 0 0 L 10 0 L 10 55 L 45 90 L 100 90 L 100 100 Z"
                          fill="none" stroke="currentColor" stroke-width="1"/>
                </svg>
            </div>
        `;
    }

    updateGrid(grid, interfaces) {
        grid.innerHTML = interfaces.map(iface => this.createInterfaceRow(iface)).join('');
    }

    createInterfaceRow(iface) {
        return `
            <div class="interface-row">
                <span class="interface-name">${iface.name}</span>
                <span class="interface-status ${iface.status.toLowerCase()}">
                    ${iface.status}
                </span>
            </div>
        `;
    }

    initializePanelContent(panel, interfaces) {
        const content = panel.querySelector('.hud-panel-content');
        if (content) {
            content.innerHTML = `
                <div class="interface-grid">
                    ${interfaces.map(iface => this.createInterfaceRow(iface)).join('')}
                </div>
            `;
        }
    }
};