class BaseSession {
    constructor(sessionId, messageRouter) {
        this.sessionId = sessionId;
        this.messageRouter = messageRouter;
    }

    sendToBackend(action, payload = {}) {
        if (!this.messageRouter) return;

        const message = {
            session_id: this.sessionId,
            action: action,
            payload: payload
        };
        this.messageRouter.handle_frontend_message(JSON.stringify(message));
    }

    handleMessage(message) {
        console.log(`${this.sessionId} received:`, message);
    }
}


class SessionManager {
    constructor() {
        console.group('SessionManager: Initializing...');
        console.log('Creating new SessionManager instance');

        this.sessions = {};
        this.messageRouter = null;

        // Initialize after WebChannel is ready
        this.initializeWebChannel();
        this.initializeModalHandling();


        // Handle theme changes
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.addEventListener('change', (e) => {
                this.sessions.ui_state?.setTheme(e.target.value);
            });
        }

        console.dir({
            sessions: this.sessions,
            messageRouter: this.messageRouter
        }, { depth: null });
        console.groupEnd();
    }
addLogEntry(message, type = "info") {
    const logContainer = document.getElementById('log-container');
    if (!logContainer) return;

    const entry = document.createElement('div');
    entry.className = type === "error" ? 'text-error' : 'text-cyan';
    entry.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
    logContainer.insertBefore(entry, logContainer.firstChild);

    // Keep only last 50 entries
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

    setupEventListeners() {
        // Connect button shows the connection modal or disconnects
        this.elements.telemetry_connect.addEventListener('click', () => {
            if (this.isConnected) {
                this.disconnect();
            } else {
                this.showConnectionModal();
            }
        });

        // Modal cancel button
        this.elements.cancelBtn.addEventListener('click', () => {
            this.elements.connectionModal.style.display = 'none';
        });

        // Connection form submission
        this.elements.telemetryConnectForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleConnectionSubmit();
        });

        // Sync driver selects
        this.elements.driverSelect.addEventListener('change', () => {
            this.elements.modalDriverSelect.value = this.elements.driverSelect.value;
        });

        this.elements.modalDriverSelect.addEventListener('change', () => {
            this.elements.driverSelect.value = this.elements.modalDriverSelect.value;
        });

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target === this.elements.connectionModal) {
                this.elements.connectionModal.style.display = 'none';
            }
        });
    }

initializeZoomControls() {
    console.group('SessionManager: Initializing zoom controls');

    const zoomIn = document.getElementById('zoom-in');
    const zoomOut = document.getElementById('zoom-out');

    if (zoomIn && zoomOut) {
        if (this.messageRouter) {
            zoomIn.addEventListener('click', () => {
                this.messageRouter.handle_frontend_message(
                    JSON.stringify({
                        session_id: 'ui_state',  // Add session_id
                        action: 'zoom_in',
                        payload: {}  // Add empty payload
                    })
                );
            });

            zoomOut.addEventListener('click', () => {
                this.messageRouter.handle_frontend_message(
                    JSON.stringify({
                        session_id: 'ui_state',  // Add session_id
                        action: 'zoom_out',
                        payload: {}  // Add empty payload
                    })
                );
            });

            console.log('Zoom controls initialized');
        } else {
            console.warn('MessageRouter not yet available for zoom controls');
        }
    } else {
        console.warn('Zoom control elements not found');
    }

    console.groupEnd();
}

initializeWebChannel() {
    if (typeof QWebChannel !== 'undefined' && typeof qt !== 'undefined') {
        // We're running in Qt WebEngine
        console.log("QWebChannel exists, attempting to connect...");
        try {
            new QWebChannel(qt.webChannelTransport, (channel) => {
                console.log("WebChannel connected, available objects:", Object.keys(channel.objects));

                this.messageRouter = channel.objects.messageRouter;

                if (this.messageRouter) {
                    console.log("Message router found, connecting handlers");
                    this.messageRouter.message_to_frontend.connect(this.handleBackendMessage.bind(this));
                    this.addLogEntry("Backend communication established");

                    // IMPORTANT: Only set up event listeners AFTER WebChannel is established
                    this.setupEventListeners();

                    // Check for session manager with retry
                    this.checkSessionManager();
                } else {
                    console.error("Message router not available in channel objects");
                    this.addLogEntry("Error: Message router not available", "error");

                    // Still set up event listeners for simulation mode
                    this.setupEventListeners();
                }
            });
        } catch (error) {
            console.error("Error establishing WebChannel:", error);
            this.addLogEntry(`WebChannel connection failed: ${error.message}`, "error");

            // Fall back to simulation mode
            this.setupEventListeners();
        }
    } else {
        // We're running in a regular browser - use simulated mode
        console.log("QWebChannel not available, running in browser");
        this.addLogEntry("Running in browser simulation mode");

        // Set up event listeners for simulation mode
        this.setupEventListeners();
    }
}

    initializeSessions() {
        console.group('SessionManager: Initializing sessions');

        this.sessions = {
            terminal: new TerminalSession("terminal", this.messageRouter),
            telemetry: new TelemetrySession("telemetry", this.messageRouter),
            ui_state: new UISession("ui_state", this.messageRouter)
        };

        window.sessions = this.sessions;

        console.dir({
            message: 'Created sessions',
            sessions: this.sessions
        }, { depth: null });
        console.groupEnd();
    }

    handleBackendMessage(message) {
        console.group('SessionManager: Backend message received');
        try {
            const data = JSON.parse(message);
            console.log(`[${data.session_id}] Action:`, data.action);
            console.dir(data, { depth: null });

            const session = this.sessions[data.session_id];
            if (session) {
                session.handleMessage(data);
            } else {
                console.error("Unknown session:", data.session_id);
            }
        } catch (error) {
            console.error("Error handling backend message:", error);
            console.dir(error, { depth: null });
        }
        console.groupEnd();
    }

    initializeModalHandling() {
        console.group('SessionManager: Initializing modal handling');

        // Connect button handler
        const telemetryConnectBtn = document.getElementById('telemetry_connect');
        if (telemetryConnectBtn) {
            telemetryConnectBtn.addEventListener('click', () => {
                console.log('SessionManager: Telemetry connect button clicked');
                this.showConnectionModal();
            });
        }

        // Modal close handler
        const modal = document.getElementById('connection-modal');
        if (modal) {
            const cancelBtn = modal.querySelector('.cancel-btn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => {
                    console.log('SessionManager: Modal cancel clicked');
                    modal.style.display = 'none';
                });
            }

            // Close modal when clicking outside
            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    console.log('SessionManager: Modal outside click');
                    modal.style.display = 'none';
                }
            });
        }

        // Form submission handler
        const form = document.getElementById('ssh-connect-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                console.log('SessionManager: Connection form submitted');
                this.handleConnectionSubmit(e);
            });
        }

        console.dir({
            elements: {
                telemetry_connect: !!telemetryConnectBtn,
                modal: !!modal,
                form: !!form
            }
        }, { depth: null });
        console.groupEnd();
    }

    showConnectionModal() {
        console.group('SessionManager: Showing connection modal');

        const modal = document.getElementById('connection-modal');
        if (!modal) {
            console.error('Modal element not found');
            console.groupEnd();
            return;
        }

        modal.style.display = 'block';

        // Reset form
//        const form = document.getElementById('ssh-connect-form');
//        if (form) {
//            form.reset();
//
//            // Reset telemetry checkbox and type field
//            const telemetryCheckbox = document.getElementById('useTelemetry');
//            const typeField = document.getElementById('ssh-type');
//
//            if (telemetryCheckbox) telemetryCheckbox.checked = false;
//            if (typeField) {
//                typeField.value = 'terminal';
//                typeField.disabled = false;
//            }
//
//            console.dir({
//                message: 'Form reset complete:',
//                elements: {
//                    form,
//                    checkbox: telemetryCheckbox,
//                    typeField
//                }
//            }, { depth: null });
//        }

        console.groupEnd();
    }

async handleConnectionSubmit(e) {
    console.group('SessionManager: Connection Submit');

    const typeField = document.getElementById('ssh-type');
    const telemetryCheckbox = document.getElementById('useTelemetry');

    console.dir({
        message: 'Connection state:',
        typeField: typeField?.value,
        telemetryEnabled: telemetryCheckbox?.checked,
        sessions: this.sessions
    }, { depth: null });

    const connectionInfo = {
        host: document.getElementById('ssh-host')?.value || '',
        username: document.getElementById('ssh-username')?.value || '',
        password: document.getElementById('ssh-password')?.value || ''
    };

    try {
        // Always establish terminal first, then add telemetry if needed
        console.log('SessionManager: Starting terminal connection');
        if (this.sessions.terminal) {
            await new Promise((resolve, reject) => {
                const checkConnection = (message) => {
                    try {
                        const data = JSON.parse(message);
                        if (data.session_id === 'terminal') {
                            if (data.action === 'connected') {
                                console.log('Terminal connection successful');
                                this.messageRouter.message_to_frontend.disconnect(checkConnection);
                                resolve();
                            } else if (data.action === 'error') {
                                console.error('Terminal connection failed:', data.payload);
                                this.messageRouter.message_to_frontend.disconnect(checkConnection);
                                reject(new Error(data.payload?.message));
                            }
                        }
                    } catch (e) {
                        console.error('Error parsing message:', e);
                    }
                };

                this.messageRouter.message_to_frontend.connect(checkConnection);
                this.sessions.terminal.connect(connectionInfo);

                // Safety timeout
                setTimeout(() => {
                    this.messageRouter.message_to_frontend.disconnect(checkConnection);
                    resolve();  // Resolve anyway to prevent hanging
                    console.log('Terminal connection timed out');
                }, 5000);
            });
        }

        // Only proceed with telemetry if checkbox is checked
        if (telemetryCheckbox?.checked) {
            console.log('SessionManager: Starting telemetry connection');
            if (this.sessions.telemetry) {
                await new Promise((resolve, reject) => {
                    const checkConnection = (message) => {
                        try {
                            const data = JSON.parse(message);
                            if (data.session_id === 'telemetry') {
                                if (data.action === 'connected') {
                                    console.log('Telemetry connection successful');
                                    this.messageRouter.message_to_frontend.disconnect(checkConnection);
                                    resolve();
                                } else if (data.action === 'error') {
                                    console.error('Telemetry connection failed:', data.payload);
                                    this.messageRouter.message_to_frontend.disconnect(checkConnection);
                                    reject(new Error(data.payload?.message));
                                }
                            }
                        } catch (e) {
                            console.error('Error parsing message:', e);
                        }
                    };

                    this.messageRouter.message_to_frontend.connect(checkConnection);
                    this.sessions.telemetry.connect(connectionInfo);

                    // Safety timeout
                    setTimeout(() => {
                        this.messageRouter.message_to_frontend.disconnect(checkConnection);
                        resolve();  // Resolve anyway to prevent hanging
                        console.log('Telemetry connection timed out');
                    }, 5000);
                });
            }
        }
    } catch (error) {
        console.error('Connection error:', error);
    } finally {
        const modal = document.getElementById('connection-modal');
        if (modal) modal.style.display = 'none';
    }

    console.groupEnd();
}

}

class TelemetrySession extends BaseSession {
constructor() {
    this.isConnected = false;
    this.currentDevice = null;
    this.simulationMode = false;
    this.telemetryData = {
        deviceInfo: null,
        interfaces: [],
        neighbors: [],
        routingTable: [],
        environment: null
    };
    this.telemetryInterval = null;
    this.messageRouter = null;

    // Initialize basic UI first
    this.initializeUI();

    // Connect WebChannel FIRST, then continue initialization AFTER connection
    this.initializeWebChannel();

    // Update device info display initially
    this.updateDeviceInfo(null);
    this.addLogEntry("Telemetry system initialized");
}
    initializeTelemetry() {
        console.group(`TelemetrySession ${this.debugId}: Initializing`);

        // Cache DOM elements
        this.elements = {
            telemetry_connect: document.getElementById('telemetry_connect'),
            deviceInfo: document.querySelectorAll('[data-device]'),
            routingTable: document.querySelector('#routing-panel tbody'),
            neighborsPanel: document.getElementById('neighbors-panel'),
            typeField: document.getElementById('ssh-type'),
            telemetryCheckbox: document.getElementById('useTelemetry'),
            driverSelect: document.getElementById('driver-select'),
            cpuStatus: document.getElementById('cpu-status'),
            memoryStatus: document.getElementById('memory-status'),
            temperatureStatus: document.getElementById('temperature-status'),
            powerStatus: document.getElementById('power-status'),
            fansStatus: document.getElementById('fans-status')        };

        console.dir({
            message: 'Initialization complete:',
            elements: this.elements,
            elementExists: {
                telemetry_connect: !!this.elements.telemetry_connect,
                deviceInfo: this.elements.deviceInfo.length,
                routingTable: !!this.elements.routingTable,
                neighborsPanel: !!this.elements.neighborsPanel,
                checkbox: !!this.elements.telemetryCheckbox,
                driverSelect: !!this.elements.driverSelect
            }
        }, { depth: null });

        console.groupEnd();
    }

    async requestEnvironmentData() {
        this.sendToBackend('get_environment');
    }

updateEnvironmentDisplay(data) {
//alert("updateEnvironmentDisplay called");
    if (!data) return;

    const formatBytes = (bytes) => {
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 B';
        const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return `${Math.round(bytes / Math.pow(1024, i))} ${sizes[i]}`;
    };

    // Update CPU
    if (data.cpu && this.elements.cpuStatus) {
        this.elements.cpuStatus.innerHTML = `
            <div class="env-item">Number of CPUs: ${data.cpu.num_cpus || 1} Usage: ${data.cpu.average_usage?.toFixed(1)}%</div>
        `;
    }

    // Update Memory
    if (data.memory && this.elements.memoryStatus) {
        const total = formatBytes(data.memory.total);
        const used = formatBytes(data.memory.used);
        this.elements.memoryStatus.innerHTML = `
            <div class="env-item">Total: ${total} Used: ${used} Usage: ${data.memory.usage_percent?.toFixed(1)}%</div>
        `;
    }

    // Update Temperature
    if (data.temperature && this.elements.temperatureStatus) {
        this.elements.temperatureStatus.innerHTML = data.temperature
            .map(temp => `
                <div class="env-item ${temp.critical ? 'critical' : temp.alert ? 'warning' : ''}">
                    ${temp.location !== 'invalid' ? temp.location : 'System'}: ${temp.temperature > 0 ? `${temp.temperature}°C` : 'N/A'}
                </div>
            `).join('');
    }

    // Update Power
    if (data.power && this.elements.powerStatus) {
        this.elements.powerStatus.innerHTML = data.power
            .map(psu => `
                <div class="env-item ${psu.status ? '' : 'warning'}">
                    ${psu.id !== 'invalid' ? `PSU ${psu.id}` : 'System Power'}: ${psu.status ? 'OK' : 'FAIL'}
                    ${psu.output > 0 ? ` ${psu.output}W / ${psu.capacity}W` : ''}
                </div>
            `).join('');
    }

    // Update Fans
    if (data.fans && this.elements.fansStatus) {
        this.elements.fansStatus.innerHTML = data.fans
            .map(fan => `
                <div class="env-item ${fan.status ? '' : 'warning'}">
                    ${fan.location !== 'invalid' ? fan.location : 'System Fan'}: ${fan.status ? 'OK' : 'FAIL'}
                </div>
            `).join('');
    }
}


    connect(connectionInfo) {
//            alert("discovering");
            this.updateDeviceInfo("discovering");
            this.deviceState = 'discovering';
        DeviceIcons.updateDeviceIcon('discovering');
        console.group(`TelemetrySession ${this.debugId}: Connection attempt`);

        const driverType = this.elements.driverSelect?.value || 'ios';
        const telemetryConnectionInfo = {
            host: connectionInfo.host,
            username: connectionInfo.username,
            password: connectionInfo.password,
            driver_type: driverType
        };

        console.log('Connection info:', telemetryConnectionInfo);
        this.sendToBackend('connect', telemetryConnectionInfo);
        console.groupEnd();
    }

    updateInterfaces(interfaces) {
    console.group(`TelemetrySession ${this.debugId}: Updating interfaces`);
    console.log('Received interfaces data:', interfaces);

    if (!interfaces || !Array.isArray(interfaces)) {
        console.warn('Invalid or missing interfaces data:', interfaces);
        console.groupEnd();
        return;
    }

    try {
        // Log interfacePanel state
        console.log('Current interfacePanel state:', this.interfacePanel);

        // Ensure interfacePanel exists
        if (!this.interfacePanel) {
            console.warn('InterfacePanel not initialized, creating new instance');
            this.interfacePanel = new this.InterfacePanel(this.debugId);
        }

        // Verify panel creation
        console.log('InterfacePanel after initialization:', this.interfacePanel);

        // Update the interface panel
        this.interfacePanel.update(interfaces);

        console.log('Successfully sent update to interface panel');
    } catch (error) {
        console.error('Error in updateInterfaces:', error);
        console.dir({
            error,
            interfaces,
            sessionState: this,
            interfacePanelState: this.interfacePanel
        }, { depth: null });
    }

    console.groupEnd();
}

    handleMessage(message) {
        console.group(`TelemetrySession ${this.debugId}: Message received`);
        console.dir({
            message,
            currentState: {
                sessionId: this.sessionId,
                telemetryActive: this.telemetryActive,  // <-- Added comma
                widgetStates: this.widgetStates
            }
        }, { depth: null });

        if (!message || !message.action) {
            console.error('Invalid message format:', message);
            console.groupEnd();
            return;
        }

        try {

        switch (message.action) {
            case 'connected':
                 DeviceIcons.updateDeviceIcon("discovering");
                console.group('Processing connected message');
                this.handleConnectionStateChange(true);
                this.startPolling();
                console.log('Widget states after connection:', this.widgetStates);
                console.groupEnd();
                break;

            case 'disconnected':
                console.group('Processing disconnected message');
                this.handleConnectionStateChange(false);
                this.stopPolling();
                console.log('Widget states after disconnection:', this.widgetStates);
                console.groupEnd();
                break;

            case 'telemetry_update':
                console.log('Telemetry Updated');
                console.log(message.payload);
                console.group('Processing telemetry update');
                console.log('Current widget states:', this.widgetStates);

                    if (message.payload.device_info) {
                    console.log('Device info present in payload:', message.payload.device_info);
//                    alert("device info:" + message);
                    this.updateWidgetState('deviceInfo', message.payload.device_info);
                    console.log('Widget state after update:', this.widgetStates.deviceInfo);
                    }

                   if (message.payload.environment) {
//                   alert("envrionment in payload");
                    this.updateWidgetState('environment', message.payload.environment);
                    this.updateEnvironmentDisplay(message.payload.environment);
                }


                    if (this.widgetStates.deviceInfo.current) {
                        console.log('Updating device info with current state');
                        this.deviceState = 'connected';
                        this.updateDeviceInfo(this.widgetStates.deviceInfo.current);
                        DeviceIcons.updateDeviceIcon(this.widgetStates.deviceInfo.current);
                    } else {
                        console.warn('Widget state current is null after update');
                    }
                
 if (message.payload.neighbors) {
        console.log('Received neighbors payload:', message.payload.neighbors);
        this.updateWidgetState('neighbors', message.payload.neighbors);
        console.log('Widget state after update:', this.widgetStates.neighbors);
    this.addLogEntry(`Neighbors update received: ${JSON.stringify(message.payload.neighbors)}`);
        console.dir(message);
        if (this.widgetStates.neighbors.current &&
            this.widgetStates.neighbors.current.length > 0) {
            console.log('Updating neighbors display with:', this.widgetStates.neighbors.current);
            this.updateNeighbors(this.widgetStates.neighbors.current);
        } else {
            console.log('Empty or invalid neighbors data received:', {
                current: this.widgetStates.neighbors.current,
                hasLength: this.widgetStates.neighbors.current?.length,
                rawPayload: message.payload.neighbors
            });
        }
    }
                if (message.payload.routing_table) {
                    // Only update if we have actual routes
                    if (message.payload.routing_table.length > 0) {
                        this.updateWidgetState('routingTable', message.payload.routing_table);
                        if (this.widgetStates.routingTable.current &&
                            (!this.widgetStates.routingTable.previous ||
                             JSON.stringify(this.widgetStates.routingTable.current) !==
                             JSON.stringify(this.widgetStates.routingTable.previous))) {
                            this.updateRoutingTable(this.widgetStates.routingTable.current);
                        }
                    } else {
                        console.log('Received empty routing table update - preserving previous state');
                    }
                }
                if (message.payload.interfaces) {
                    this.updateWidgetState('interfaces', message.payload.interfaces);
                    if (this.widgetStates.interfaces.current &&
                        (!this.widgetStates.interfaces.previous ||
                         JSON.stringify(this.widgetStates.interfaces.current) !==
                         JSON.stringify(this.widgetStates.interfaces.previous))) {
                        this.updateInterfaces(this.widgetStates.interfaces.current);
                    }
                }

                console.log('Final widget states after telemetry update:', this.widgetStates);
                console.groupEnd();
                break;

            case 'error':
                console.group('Error message received');
                console.error('Error payload:', message.payload);
                console.groupEnd();
                break;

            default:
                console.warn('Unhandled message action:', message.action);
        }
        } catch (error) {
            console.error('Error processing message:', error);
            console.dir({
                error,
                message,
                sessionState: this
            }, { depth: null });
        }
        console.groupEnd();
    }

addLogEntry(message) {
    const logContainer = document.getElementById('log-container');
    if (logContainer) {
        const entry = document.createElement('div');
        entry.className = 'text-cyan';
        entry.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
        logContainer.insertBefore(entry, logContainer.firstChild);  // Add new entries at top

        // Keep only last 10 entries
        while (logContainer.children.length > 10) {
            logContainer.removeChild(logContainer.lastChild);
        }
    }
}

    handleConnectionStateChange(isConnected) {
        console.group(`TelemetrySession ${this.debugId}: Connection state change`);
        console.log('Changing connection state to:', isConnected);

        this.telemetryActive = isConnected;

        if (this.elements.telemetry_connect) {
            this.elements.telemetry_connect.textContent = isConnected ? 'Disconnect' : 'Connect';
            this.elements.telemetry_connect.classList.toggle('connected', isConnected);
        }

        console.groupEnd();
    }

    updateWidgetState(widgetName, newData) {
        if (!this.widgetStates[widgetName]) return;

        // Store previous state before updating
        this.widgetStates[widgetName].previous = this.widgetStates[widgetName].current;
        this.widgetStates[widgetName].current = newData;

        console.log(`Widget ${widgetName} state update:`, {
            previous: this.widgetStates[widgetName].previous,
            current: this.widgetStates[widgetName].current,
            hasChanged: JSON.stringify(this.widgetStates[widgetName].previous) !==
                       JSON.stringify(this.widgetStates[widgetName].current)
        });
    }
updateDeviceInfo(info) {
        console.group(`TelemetrySession ${this.debugId}: Updating device info`);

        try {
            if (!this.elements.deviceInfo) {
                console.warn('No device info elements found');
                return;
            }

            if (info === "discovering") {
                // Set discovering state
                this.elements.deviceInfo.forEach(element => {
                    const labelText = element.textContent.split(':')[0];
                    element.innerHTML = `${labelText}: Discovering...`;
                });
            } else if (info === null) {
                // Set unknown state
                this.elements.deviceInfo.forEach(element => {
                    const labelText = element.textContent.split(':')[0];
                    element.innerHTML = `${labelText}: Unknown`;
                });
            } else if (info && typeof info === 'object') {
                // Update with actual device info
                this.elements.deviceInfo.forEach(element => {
                    const key = element.dataset.device;
                    if (key && info.hasOwnProperty(key)) {
                        const labelText = element.textContent.split(':')[0];
                        element.innerHTML = `${labelText}: ${info[key]}`;
                        console.log(`Updated ${key} to ${info[key]}`);
                    }
                });
            }
        } catch (error) {
            console.error('Error updating device info:', error);
        }

        console.groupEnd();
    }
updateNeighbors(neighbors) {
    console.log('Updating neighbors display:', neighbors);

    const panel = this.elements.neighborsPanel?.querySelector('.hud-panel-content');
    if (!panel) {
        console.error('Neighbors panel element not found');
        return;
    }

    try {
        // Create base structure with tabs and scrollable table
        panel.innerHTML = `
            <div class="tabs">
                <div class="tab active">LLDP</div>
            </div>
            <div class="neighbors-table-container" style="
                margin-top: 1rem;
                max-height: 300px;
                overflow-y: auto;
            ">
                <table class="neighbors-table" style="
                    width: 100%;
                    border-collapse: collapse;
                ">
                    <thead>
                        <tr>
                            <th class="text-cyan" style="text-align: left; padding: 0.5rem 0;">LOCAL PORT</th>
                            <th class="text-cyan" style="text-align: left; padding: 0.5rem 0;">NEIGHBOR</th>
                            <th class="text-cyan" style="text-align: left; padding: 0.5rem 0;">REMOTE PORT</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${neighbors.map(neighbor => `
                            <tr>
                                <td style="padding: 0.25rem 0;">${neighbor.local_port}</td>
                                <td style="padding: 0.25rem 0;">${neighbor.neighbor}</td>
                                <td style="padding: 0.25rem 0;">${neighbor.remote_port}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        // Add custom scrollbar styles
        const style = document.createElement('style');
        style.textContent = `
            .neighbors-table-container::-webkit-scrollbar {
                width: 6px;
            }
            .neighbors-table-container::-webkit-scrollbar-track {
                background: rgba(0, 255, 255, 0.1);
                border-radius: 3px;
            }
            .neighbors-table-container::-webkit-scrollbar-thumb {
                background: rgba(0, 255, 255, 0.3);
                border-radius: 3px;
            }
            .neighbors-table-container::-webkit-scrollbar-thumb:hover {
                background: rgba(0, 255, 255, 0.5);
            }
            .neighbors-table tr:hover {
                background: rgba(0, 255, 255, 0.1);
            }
        `;
        panel.appendChild(style);

    } catch (error) {
        console.error('Error updating neighbors display:', error);
    }
}

    updateRoutingTable(routes) {
        console.group(`TelemetrySession ${this.debugId}: Updating routing table`);
        if (!this.elements.routingTable || !routes) {
            console.warn('Routing table not found or no route data');
            console.groupEnd();
            return;
        }

        this.elements.routingTable.innerHTML = routes.map(route => `
            <tr>
                <td>${route.network}</td>
                <td>${route.mask}</td>
                <td>${route.next_hop}</td>
            </tr>
        `).join('');

        console.log('Updated routes:', routes);
        console.groupEnd();
    }



    startPolling() {
        console.log(`TelemetrySession ${this.debugId}: Starting polling`);
        this.stopPolling();

        // Initial data request
        this.requestAllTelemetryData();

        // Set up polling interval
        this.pollingInterval = setInterval(() => {
            if (this.telemetryActive) {
                this.requestAllTelemetryData();
            }
        }, 30000);
    }

        async requestAllTelemetryData() {
            try {
                await this.getTelemetryData('get_device_info', 'device_info')
                    .then(deviceInfo => {
                        if (!deviceInfo || !deviceInfo.hostname || deviceInfo.hostname === 'Unknown') {
                            throw new Error('Invalid device info');
                        }
                        return this.getTelemetryData('get_interfaces', 'interfaces');
                    })
                    .then(() => this.getTelemetryData('get_neighbors', 'neighbors'))
                    .then(() => this.getTelemetryData('get_routes', 'routing_table'))
                    .then(() => this.getTelemetryData('get_environment', 'environment'));
            } catch (error) {
                console.error('Telemetry chain failed:', error);
                this.stopPolling();
            }
        }
async getTelemetryData(action, payloadKey, timeout = 10000) {
    return new Promise((resolve, reject) => {
        const checkResponse = (message) => {
            try {
                const data = JSON.parse(message);
                if (data.session_id === 'telemetry' &&
                    data.action === 'telemetry_update' &&
                    data.payload[payloadKey] !== undefined) {
                    this.messageRouter.message_to_frontend.disconnect(checkResponse);
                    resolve(data.payload[payloadKey]);
                }
            } catch (e) {
                console.error(`Error in ${action}:`, e);
            }
        };

        this.messageRouter.message_to_frontend.connect(checkResponse);
        this.sendToBackend(action);

        setTimeout(() => {
            this.messageRouter.message_to_frontend.disconnect(checkResponse);
            reject(new Error(`${action} timeout`));
        }, timeout);
    });
}
    stopPolling() {
        if (this.pollingInterval) {
            console.log(`TelemetrySession ${this.debugId}: Stopping polling`);
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    InterfacePanel = class InterfacePanel {
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

}


class TerminalSession extends BaseSession {
    constructor(sessionId, messageRouter) {
        super(sessionId, messageRouter);
        this.term = null;
        this.fitAddon = null;
        this.initializeTerminal();
        this.setupResizeHandling();

    }


initializeTerminal() {
    const terminalConfig = {
        scrollback: 1000,
        cursorBlink: true,
        fontSize: 14,
        fontFamily: 'Courier New',
//        theme: window.TERMINAL_THEMES && window.TERMINAL_THEMES.cyber
    };
    this.term = new Terminal(terminalConfig);
    this.fitAddon = new FitAddon.FitAddon();
    this.term.loadAddon(this.fitAddon);
    const terminalElement = document.getElementById('terminal');
    if (!terminalElement) {
        console.error('Terminal element not found');
        return;
    }
    this.term.open(terminalElement);
    this.fitAddon.fit();

    // Clean up existing listener if any
    if (this.boundOnData) {
        this.boundOnData.dispose();
    }

    // Set up new listener
    this.boundOnData = this.term.onData(data => {
        this.sendToBackend('data', { text: data });
    });
}

// Add cleanup method
cleanup() {
    if (this.boundOnData) {
        this.boundOnData.dispose();
        this.boundOnData = null;
    }
}

    setupResizeHandling() {
        // Debounced resize handler
        this.debouncedResize = this.debounce(() => this.handleResize(), 100);

        // Add resize listener
        window.addEventListener('resize', this.debouncedResize);

        // Initial fit after a short delay
        setTimeout(() => this.handleResize(), 50);
    }

    handleResize() {
        if (!this.fitAddon) return;

        requestAnimationFrame(() => {
            this.fitAddon.fit();
            this.updatePtySize();
        });
    }

    updatePtySize() {
        if (!this.term?.cols || !this.term?.rows) return;

        this.sendToBackend('resize', {
            cols: this.term.cols,
            rows: this.term.rows
        });
    }

    debounce(func, wait) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    connect(connectionInfo) {
        if (!this.term) return;

        this.term.clear();
        this.term.write('Connecting...\r\n');
        this.sendToBackend('connect', connectionInfo);
    }

handleMessage(message) {
    if (!this.term) return;
    console.log('terminal session message!');
    console.log(message)
    switch (message.action) {

        case 'data':
            this.term.write(message.payload.text);
//            window.sessions.terminal.term.fitAddon.fit();
//              console.dir(window.sessions.terminal)
            break;
        case 'connected':
            console.log('\r\nConnection established.\r\n');

            const resizeAttempts = [0, 1000, 2000];
                resizeAttempts.forEach(delay => {
                    setTimeout(() => {
                        this.fitAddon.fit();
                        this.term.refresh(0, this.term.rows - 1);
                        this.updatePtySize();
                        console.log(`[terminal] Resize attempt at ${delay}ms:`, {
                            cols: this.term.cols,
                            rows: this.term.rows
                        });
                    }, delay);
                });
                break;
            setTimeout(() => {
                this.handleResize();
                console.log('[terminal] Sending initial size:', {
                    cols: this.term.cols,
                    rows: this.term.rows
                });
            }, 1000);
            break;
        case 'disconnected':
            this.term.write('\r\nConnection closed.\r\n');
            break;
        case 'error':
            this.term.write(`\r\nError: ${message.payload.message}\r\n`);
            break;
    }
}
    cleanup() {
        window.removeEventListener('resize', this.debouncedResize);
        if (this.term) {
            this.term.dispose();
        }
    }
}


class UISession extends BaseSession {
    constructor(sessionId, messageRouter) {
        super(sessionId, messageRouter);
        this.styleElement = document.createElement('style');
        document.head.appendChild(this.styleElement);

        // Initialize theme from localStorage but also request from backend
        this.currentTheme = localStorage.getItem('preferredTheme') || 'cyber';
        this.initializeThemeHandling();

        // Request theme from backend to ensure sync
        this.requestCurrentTheme();
    }

    initializeThemeHandling() {
        // Set up theme selector
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.addEventListener('change', (e) => this.setTheme(e.target.value));
            themeSelect.value = this.currentTheme;
        }

        // Apply initial theme
        this.applyTheme(this.currentTheme);

        // Set up tab handling
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => this.handleTabClick(tab));
        });
    }

    handleTabClick(tab) {
        if (!tab?.parentElement) return;

        const currentActive = tab.parentElement.querySelector('.tab.active');
        if (currentActive) {
            currentActive.classList.remove('active');
        }
        tab.classList.add('active');
    }

    requestCurrentTheme() {
        console.log('UISession: Requesting theme from backend');
        this.sendToBackend('get_theme');
    }

    setTheme(themeName) {
        if (!themeName) return;
        console.log('UISession: Setting theme:', themeName);

        // Send to backend first
        this.sendToBackend('set_theme', { theme: themeName });

        // Apply theme locally
        this.applyTheme(themeName);
    }

    applyTheme(themeName) {
        if (!themeName) return;
        console.log('UISession: Applying theme:', themeName);

        // Store theme
        this.currentTheme = themeName;
        localStorage.setItem('preferredTheme', themeName);

        // Apply CSS styles
        if (window.THEME_STYLES && window.THEME_STYLES[themeName]) {
            this.styleElement.textContent = window.THEME_STYLES[themeName];
        }

        // Apply terminal theme
        if (window.sessionManager?.sessions?.terminal?.term &&
            window.TERMINAL_THEMES &&
            window.TERMINAL_THEMES[themeName]) {
            window.sessionManager.sessions.terminal.term.setOption('theme',
                window.TERMINAL_THEMES[themeName]);
        }

        // Apply theme colors
        const themeColors = window.THEME_COLORS && window.THEME_COLORS[themeName];
        if (themeColors) {
            Object.entries(themeColors).forEach(([key, value]) => {
                document.documentElement.style.setProperty(key, value);
            });
        }

        // Update scrollbar styles
        this.updateScrollbarStyles(themeName);

        // Update select element to match
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect && themeSelect.value !== themeName) {
            themeSelect.value = themeName;
        }

        // Update dynamic UI elements
        this.updateDynamicElements();

        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: themeName }
        }));
    }

    updateDynamicElements() {
        // Update HUD panel titles
        document.querySelectorAll('.hud-panel-title').forEach((el) => {
            el.style.color = 'var(--text-secondary)';
            el.style.background = 'var(--bg-primary)';
        });

        // Update HUD panels
        document.querySelectorAll('.hud-panel::before').forEach((el) => {
            el.style.background = 'var(--bg-secondary)';
            el.style.border = '1px solid var(--border-color)';
        });

        // Update tabs
        document.querySelectorAll('.tab').forEach((el) => {
            el.style.color = 'var(--text-primary)';
        });

        document.querySelectorAll('.tab.active').forEach((el) => {
            el.style.color = 'var(--accent-color)';
            el.style.borderBottom = '2px solid var(--accent-color)';
        });
    }

    updateScrollbarStyles(themeName) {
        if (!themeName || !window.THEME_COLORS || !window.THEME_COLORS[themeName]) return;

        const style = document.getElementById('scrollbar-style') || document.createElement('style');
        style.id = 'scrollbar-style';
        style.textContent = `
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: var(--scrollbar-track);
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb {
                background: var(--scrollbar-thumb);
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: var(--scrollbar-thumb-hover);
                transition: background-color 0.2s ease;
            }
        `;
        if (!style.parentNode) {
            document.head.appendChild(style);
        }
    }

    handleMessage(message) {
        console.log('UI State session message:', message);
        if (message.action === 'theme_changed' && message.payload?.theme) {
            this.applyTheme(message.payload.theme);
        }
    }
}
function initNetworkGraph() {
 // save
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sessionManager = new SessionManager();
//        initNetworkGraph();


});

// interfacePanel.js

// Make the class available globally
