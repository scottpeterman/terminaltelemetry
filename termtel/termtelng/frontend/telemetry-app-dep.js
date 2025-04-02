// Global function to initialize QWebChannel when qt.webChannelTransport becomes available
function waitForWebChannel() {
    console.log("Checking for qt.webChannelTransport...");

    // Check if qt and webChannelTransport are available
    if (typeof qt !== 'undefined' && typeof qt.webChannelTransport !== 'undefined') {
        console.log("qt.webChannelTransport found, initializing QWebChannel");
        initializeQWebChannel();
    } else {
        console.log("qt.webChannelTransport not available yet, waiting...");
        setTimeout(waitForWebChannel, 100); // Check again in 100ms
    }
}

// Initialize QWebChannel once qt.webChannelTransport is available
function initializeQWebChannel() {
    console.log("Initializing QWebChannel");
    try {
        new QWebChannel(qt.webChannelTransport, function(channel) {
            console.log("QWebChannel initialized, available objects:", Object.keys(channel.objects));

            if (channel.objects.messageRouter) {
                window.messageRouter = channel.objects.messageRouter;
                console.log("messageRouter found and assigned to window.messageRouter");

                // Dispatch event to notify app
                document.dispatchEvent(new CustomEvent('messageRouterReady', {
                    detail: { messageRouter: window.messageRouter }
                }));
            } else {
                console.error("messageRouter not found in channel objects");
            }
        });
    } catch (error) {
        console.error("Error initializing QWebChannel:", error);
    }
}

// Start waiting for WebChannel
waitForWebChannel();


// Main Telemetry Application Class
class TelemetryApp {
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
        this.messageRouter = window.messageRouter; // Use global if already available

        this.initializeUI();
        this.setupEventListeners();
           if (!this.messageRouter) {
            document.addEventListener('messageRouterReady', (event) => {
                console.log("Message router ready event received");
                this.messageRouter = event.detail.messageRouter;
                this.addLogEntry("Backend communication established");
            });
        } else {
            this.addLogEntry("Backend communication established immediately");
        }
        // Initialize with empty state
        this.updateDeviceInfo(null);
        this.addLogEntry("Telemetry system initialized");
    }

    // Initialize WebChannel connection to backend
initializeWebChannel() {
    if (typeof QWebChannel !== 'undefined' && typeof qt !== 'undefined') {
        // We're running in Qt WebEngine
        new QWebChannel(qt.webChannelTransport, (channel) => {
            this.messageRouter = channel.objects.messageRouter;
            if (this.messageRouter) {
                this.messageRouter.message_to_frontend.connect(this.handleBackendMessage.bind(this));
                this.addLogEntry("Backend communication established");

                // Check for session manager with retry
                this.checkSessionManager();
            } else {
                this.addLogEntry("Error: Message router not available", "error");
            }
        });
    } else {
        // We're running in a regular browser - use simulated mode
        this.addLogEntry("Running in browser simulation mode");
    }
}

checkSessionManager(attempts = 0) {
    if (attempts > 10) {
        this.addLogEntry("Failed to find SessionManager after multiple attempts", "error");
        return;
    }

    if (window.sessionManager && window.sessionManager.sessions) {
        this.addLogEntry("SessionManager found, real mode initialized");
    } else {
        // Retry after a short delay
        this.addLogEntry(`SessionManager not ready, retrying... (${attempts+1}/10)`);
        setTimeout(() => this.checkSessionManager(attempts + 1), 500);
    }
}
    initializeUI() {
        // Initialize all UI components
//            this.elements.simulationCheckbox = document.getElementById('simulation-mode');

        this.elements = {
            connectBtn: document.getElementById('telemetry-connect'),
            deviceInfo: document.querySelectorAll('[data-device]'),
            routingTable: document.querySelector('#routing-panel tbody'),
            neighborsPanel: document.getElementById('neighbors-panel'),
            driverSelect: document.getElementById('driver-select'),
            modalDriverSelect: document.getElementById('modal-driver-select'),
            cpuStatus: document.getElementById('cpu-status'),
            memoryStatus: document.getElementById('memory-status'),
            temperatureStatus: document.getElementById('temperature-status'),
            powerStatus: document.getElementById('power-status'),
            fansStatus: document.getElementById('fans-status'),
            connectionModal: document.getElementById('connection-modal'),
            telemetryConnectForm: document.getElementById('telemetry-connect-form'),
            cancelBtn: document.querySelector('.cancel-btn'),
            interfacesPanel: document.querySelector('#interfaces-panel .interface-grid'),
            logContainer: document.getElementById('log-container'),
            simulationCheckbox: document.getElementById('simulation-mode') // Add this line here instead


        };
    }

    setupEventListeners() {
        // Connect button shows the connection modal or disconnects
        this.elements.connectBtn.addEventListener('click', () => {
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

if (this.elements.simulationCheckbox) {
        this.elements.simulationCheckbox.addEventListener('change', (e) => {
            this.simulationMode = e.target.checked;
            localStorage.setItem('simulationMode', this.simulationMode);
            this.addLogEntry(`Simulation mode ${this.simulationMode ? 'enabled' : 'disabled'}`);
        });
    }
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

    showConnectionModal() {
        this.elements.connectionModal.style.display = 'block';
    }


    handleConnectionSubmit() {
        const connectionInfo = {
            host: document.getElementById('host').value,
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            driver_type: this.elements.modalDriverSelect.value
        };

        this.addLogEntry(`Connecting to ${connectionInfo.host} (${connectionInfo.driver_type})...`);
        this.elements.connectionModal.style.display = 'none';

        // Update UI to discovering state
        this.updateDeviceInfo("discovering");
        DeviceIcons.updateDeviceIcon("discovering");

        // Add detailed debugging to check what's causing simulation mode
        console.log("Simulation checkbox state:", this.simulationMode);
        console.log("Message router state:", this.messageRouter);
        console.log("Combined condition:", this.simulationMode || !this.messageRouter);

        if (this.simulationMode || !this.messageRouter) {
            // Either user selected simulation mode OR we don't have a message router
            this.addLogEntry("Using simulation mode for this connection");
            console.log("running in sim mode!");
            this.simulateConnection(connectionInfo);
        } else {
            // Real mode with backend connection
            this.addLogEntry("Using real backend connection");
            console.log("running in real mode");
            this.connect(connectionInfo);
        }
    }
    // Connect to the device using the backend
    connect(connectionInfo) {
        this.sendToBackend('connect', connectionInfo);
    }

    // Disconnect from the device
    disconnect() {
        if (this.isConnected) {
            if (this.messageRouter) {
                this.sendToBackend('disconnect', {});
            } else {
                // Simulation mode
                clearInterval(this.telemetryInterval);
                this.isConnected = false;
                this.elements.connectBtn.textContent = 'Connect';
                this.elements.connectBtn.classList.remove('connected');
                this.updateDeviceInfo(null);
                DeviceIcons.updateDeviceIcon(null);
                this.addLogEntry("Disconnected from device");
            }
        }
    }

    // Send message to the backend
    sendToBackend(action, payload = {}) {
        if (!this.messageRouter) return;

        const message = {
            session_id: 'telemetry',
            action: action,
            payload: payload
        };

        try {
            this.messageRouter.handle_frontend_message(JSON.stringify(message));
        } catch (error) {
            this.addLogEntry(`Error sending message to backend: ${error.message}`, "error");
        }
    }

    // Handle messages from the backend
    handleBackendMessage(message) {
        try {
            const data = JSON.parse(message);

            if (data.session_id !== 'telemetry') return;

            switch (data.action) {
                case 'connected':
                    this.handleConnectionStateChange(true);
                    this.addLogEntry("Connected to device successfully");
                    break;

                case 'disconnected':
                    this.handleConnectionStateChange(false);
                    this.addLogEntry("Disconnected from device");
                    break;

                case 'telemetry_update':
                    this.processUpdateData(data.payload);
                    break;

                case 'error':
                    this.addLogEntry(`Error: ${data.payload.message}`, "error");
                    break;

                default:
                    this.addLogEntry(`Received unknown action: ${data.action}`);
            }
        } catch (error) {
            this.addLogEntry(`Error handling message: ${error.message}`, "error");
        }
    }

    // Process telemetry update data
    processUpdateData(payload) {
        // Process device info
        if (payload.device_info) {
            this.telemetryData.deviceInfo = payload.device_info;
            this.updateDeviceInfo(payload.device_info);
            DeviceIcons.updateDeviceIcon(payload.device_info);
        }

        // Process interfaces
        if (payload.interfaces) {
            this.telemetryData.interfaces = payload.interfaces;
            this.updateInterfaces(payload.interfaces);
        }

        // Process neighbors
        if (payload.neighbors) {
            this.telemetryData.neighbors = payload.neighbors;
            this.updateNeighbors(payload.neighbors);
        }

        // Process routing table
        if (payload.routing_table) {
            this.telemetryData.routingTable = payload.routing_table;
            this.updateRoutingTable(payload.routing_table);
        }

        // Process environment data
        if (payload.environment) {
            this.telemetryData.environment = payload.environment;
            this.updateEnvironmentDisplay(payload.environment);
        }
    }

    // Update connection state in UI
    handleConnectionStateChange(isConnected) {
        this.isConnected = isConnected;

        if (this.elements.connectBtn) {
            this.elements.connectBtn.textContent = isConnected ? 'Disconnect' : 'Connect';
            this.elements.connectBtn.classList.toggle('connected', isConnected);
        }
    }

    // Update device info display
    updateDeviceInfo(info) {
        try {
            if (!this.elements.deviceInfo) return;

            if (info === "discovering") {
                // Set discovering state
                this.elements.deviceInfo.forEach(element => {
                    const labelText = element.textContent.split(':')[0];
                    element.innerHTML = `${labelText}: <span>Discovering...</span>`;
                });
            } else if (info === null) {
                // Set unknown state
                this.elements.deviceInfo.forEach(element => {
                    const labelText = element.textContent.split(':')[0];
                    element.innerHTML = `${labelText}: <span>Unknown</span>`;
                });
            } else if (info && typeof info === 'object') {
                // Update with actual device info
                this.elements.deviceInfo.forEach(element => {
                    const key = element.dataset.device;
                    if (key && info.hasOwnProperty(key)) {
                        const labelText = element.textContent.split(':')[0];
                        element.innerHTML = `${labelText}: <span>${info[key]}</span>`;
                    }
                });
            }
        } catch (error) {
            this.addLogEntry(`Error updating device info: ${error.message}`, "error");
        }
    }

    // Update interfaces display
    updateInterfaces(interfaces) {
        if (!this.elements.interfacesPanel || !interfaces) return;

        try {
            this.elements.interfacesPanel.innerHTML = interfaces.map(iface => `
                <div class="interface-row">
                    <span class="interface-name">${iface.name}</span>
                    <span class="interface-status ${iface.status.toLowerCase()}">
                        ${iface.status}
                    </span>
                </div>
            `).join('');

            this.addLogEntry(`Updated ${interfaces.length} interfaces`);
        } catch (error) {
            this.addLogEntry(`Error updating interfaces: ${error.message}`, "error");
        }
    }

    // Update neighbors display
    updateNeighbors(neighbors) {
        const panel = this.elements.neighborsPanel;
        if (!panel) return;

        try {
            if (!neighbors.length) {
                panel.innerHTML = `
                    <div class="tabs">
                        <div class="tab active">LLDP</div>
                    </div>
                    <div style="padding: 10px; color: #00b0f0;">
                        No neighbors found
                    </div>
                `;
                return;
            }

            panel.innerHTML = `
                <div class="tabs">
                    <div class="tab active">LLDP</div>
                </div>
                <div class="neighbors-table-container">
                    <table class="neighbors-table">
                        <thead>
                            <tr>
                                <th class="text-cyan">LOCAL PORT</th>
                                <th class="text-cyan">NEIGHBOR</th>
                                <th class="text-cyan">REMOTE PORT</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${neighbors.map(neighbor => `
                                <tr>
                                    <td>${neighbor.local_port}</td>
                                    <td>${neighbor.neighbor}</td>
                                    <td>${neighbor.remote_port}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;

            this.addLogEntry(`Updated ${neighbors.length} neighbors`);
        } catch (error) {
            this.addLogEntry(`Error updating neighbors: ${error.message}`, "error");
        }
    }

    // Update routing table display
    updateRoutingTable(routes) {
        if (!this.elements.routingTable || !routes) return;

        try {
            this.elements.routingTable.innerHTML = routes.map(route => `
                <tr>
                    <td>${route.network}</td>
                    <td>${route.mask}</td>
                    <td>${route.next_hop}</td>
                </tr>
            `).join('');

            this.addLogEntry(`Updated ${routes.length} routes`);
        } catch (error) {
            this.addLogEntry(`Error updating routing table: ${error.message}`, "error");
        }
    }

    // Update environment display
    updateEnvironmentDisplay(data) {
        if (!data) return;

        const formatBytes = (bytes) => {
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            if (bytes === 0) return '0 B';
            const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
            return `${Math.round(bytes / Math.pow(1024, i))} ${sizes[i]}`;
        };

        try {
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

            this.addLogEntry("Updated environment data");
        } catch (error) {
            this.addLogEntry(`Error updating environment display: ${error.message}`, "error");
        }
    }

    // Add an entry to the debug log
    addLogEntry(message, type = "info") {
        const logContainer = this.elements.logContainer;
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

    // For demo purposes - simulates a connection and data updates
    simulateConnection(connectionInfo) {
        // Show "discovering" state
        this.updateDeviceInfo("discovering");
        DeviceIcons.updateDeviceIcon("discovering");

        // Update connection button state
        this.handleConnectionStateChange(true);

        // Simulate a connection delay
        setTimeout(() => {
            // Generate sample device info based on driver type
            let deviceInfo = {
                hostname: connectionInfo.host,
                model: this.getModelNameForDriver(connectionInfo.driver_type),
                serial: `SN-${Math.floor(Math.random() * 10000)}`,
                os_version: this.getOSVersionForDriver(connectionInfo.driver_type),
                uptime: "3d 5h 42m"
            };

            // Update the UI with our simulated data
            this.updateDeviceInfo(deviceInfo);
            this.currentDevice = deviceInfo;
            DeviceIcons.updateDeviceIcon(deviceInfo);

            // Generate other telemetry data
            this.generateAndUpdateInterfaces(connectionInfo.driver_type);
            this.generateAndUpdateRouting();
            this.generateAndUpdateEnvironment();

            this.addLogEntry(`Connected to ${deviceInfo.hostname} successfully`);

            // Set up polling interval to simulate updates
            this.telemetryInterval = setInterval(() => {
                this.simulateDataUpdates();
            }, 10000);
        }, 2000);
    }

    getModelNameForDriver(driverType) {
        const models = {
            'ios': 'Cisco IOS Router 4431',
            'eos': 'Arista EOS 4.23.2F',
            'nxos_ssh': 'Cisco Nexus 9K',
            'junos': 'Juniper SRX 340',
            'linux': 'Linux Server x86_64'
        };
        return models[driverType] || 'Generic Device';
    }

    getOSVersionForDriver(driverType) {
        const versions = {
            'ios': 'IOS 16.9.3',
            'eos': 'EOS 4.23.2F',
            'nxos_ssh': 'NXOS 9.3(5)',
            'junos': 'Junos 19.4R1.10',
            'linux': 'Ubuntu 22.04 LTS'
        };
        return versions[driverType] || 'Unknown';
    }

    generateAndUpdateInterfaces(driverType) {
        const interfaceCount = 5 + Math.floor(Math.random() * 10);
        const interfaces = [];

        const prefixes = {
            'ios': 'GigabitEthernet',
            'eos': 'Ethernet',
            'nxos_ssh': 'Eth',
            'junos': 'ge-',
            'linux': 'eth'
        };

        const prefix = prefixes[driverType] || 'int';

        for (let i = 0; i < interfaceCount; i++) {
            const status = Math.random() > 0.2 ? 'UP' : 'DOWN';
            interfaces.push({
                name: `${prefix}${i}`,
                status: status
            });
        }

        this.updateInterfaces(interfaces);
        this.telemetryData.interfaces = interfaces;
    }

    generateAndUpdateRouting() {
        const routes = [
            {
                network: "0.0.0.0",
                mask: "0",
                next_hop: "10.0.0.1"
            }
        ];

        this.updateRoutingTable(routes);
        this.telemetryData.routingTable = routes;
    }

    generateAndUpdateEnvironment() {
        const environment = {
            cpu: {
                num_cpus: 4,
                average_usage: 15 + Math.random() * 15
            },
            memory: {
                total: 16 * 1024 * 1024 * 1024, // 16GB
                used: 4 * 1024 * 1024 * 1024 + Math.random() * 4 * 1024 * 1024 * 1024,
                usage_percent: 25 + Math.random() * 25
            },
            temperature: [
                {
                    location: "CPU",
                    temperature: 35 + Math.random() * 15,
                    alert: false,
                    critical: false
                },
                {
                    location: "System",
                    temperature: 30 + Math.random() * 10,
                    alert: false,
                    critical: false
                }
            ],
            power: [
                {
                    id: "PSU1",
                    status: true,
                    capacity: 1000,
                    output: 350 + Math.random() * 100
                }
            ],
            fans: [
                {
                    location: "FAN1",
                    status: true
                },
                {
                    location: "FAN2",
                    status: true
                }
            ]
        };

        this.updateEnvironmentDisplay(environment);
        this.telemetryData.environment = environment;
    }

    simulateDataUpdates() {
        // Randomly update one interface status
        if (this.telemetryData.interfaces.length) {
            const randomIndex = Math.floor(Math.random() * this.telemetryData.interfaces.length);
            const randomInterface = this.telemetryData.interfaces[randomIndex];

            if (Math.random() > 0.7) {
                randomInterface.status = randomInterface.status === 'UP' ? 'DOWN' : 'UP';
                this.updateInterfaces(this.telemetryData.interfaces);
                this.addLogEntry(`Interface ${randomInterface.name} changed to ${randomInterface.status}`);
            }
        }

        // Update CPU/memory usage
        if (this.telemetryData.environment) {
            const env = this.telemetryData.environment;

            // Update CPU usage
            if (env.cpu) {
                env.cpu.average_usage = 15 + Math.random() * 15;
            }

            // Update memory usage
            if (env.memory) {
                env.memory.used = 4 * 1024 * 1024 * 1024 + Math.random() * 4 * 1024 * 1024 * 1024;
                env.memory.usage_percent = 25 + Math.random() * 25;
            }

            // Update temperature
            if (env.temperature && env.temperature.length) {
                for (let temp of env.temperature) {
                    if (temp.location === "CPU") {
                        temp.temperature = 35 + Math.random() * 15;
                        // Simulate alert if too hot
                        temp.alert = temp.temperature > 45;
                        temp.critical = temp.temperature > 55;
                    }
                }
            }

            this.updateEnvironmentDisplay(env);
            this.addLogEntry("Updated environmental data");
        }
    }
}