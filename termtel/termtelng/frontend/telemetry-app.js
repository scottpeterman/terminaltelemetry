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

                // Connect the message handler to receive messages from backend
                if (window.messageRouter.message_to_frontend) {
                    window.messageRouter.message_to_frontend.connect(handleMessage);
                    console.log("Connected global handleMessage to message_to_frontend signal");
                } else {
                    console.error("messageRouter.message_to_frontend signal not found");
                }

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

// Global message handler function - this is critical for QWebChannel
function handleMessage(message) {
    console.log("Global handleMessage received:", message);

    // Forward to telemetry app if available
    if (window.telemetryApp && window.telemetryApp.handleBackendMessage) {
        window.telemetryApp.handleBackendMessage(message);
    } else {
        console.warn("TelemetryApp not available to handle message");

        // Store messages until app is ready
        if (!window.pendingMessages) {
            window.pendingMessages = [];
        }
        window.pendingMessages.push(message);
        console.log("Message stored in pending queue, total:", window.pendingMessages.length);
    }
}

// Start waiting for WebChannel
waitForWebChannel();


// Main Telemetry Application Class
class TelemetryApp {
    constructor() {
        this.isConnected = false;
        this.currentDevice = null;
        this.telemetryData = {
            deviceInfo: null,
            interfaces: [],
            neighbors: [],
            routingTable: [],
            environment: null
        };
        this.messageRouter = null;
        this.pollingInterval = null;
        this.lastUpdateTime = null;  // Track when we last received an update
        this.initializeUI();
        this.setupEventListeners();

        // Check for messageRouter
        if (window.messageRouter) {
            console.log("Using global messageRouter");
            this.messageRouter = window.messageRouter;
            this.addLogEntry("Backend communication established immediately");

            // Process any pending messages
            this.processPendingMessages();
        } else {
            console.log("Waiting for messageRouter to become available");
            document.addEventListener('messageRouterReady', (event) => {
                console.log("Message router ready event received");
                this.messageRouter = event.detail.messageRouter;
                this.addLogEntry("Backend communication established");

                // Process any pending messages
                this.processPendingMessages();
            });
        }

        // Initialize with empty state
        this.updateDeviceInfo(null);
        this.addLogEntry("Telemetry system initialized");
    }

    // Process any messages that were received before the app was ready
    processPendingMessages() {
        if (window.pendingMessages && window.pendingMessages.length > 0) {
            console.log(`Processing ${window.pendingMessages.length} pending messages`);

            window.pendingMessages.forEach(message => {
                this.handleBackendMessage(message);
            });

            // Clear the queue
            window.pendingMessages = [];
            this.addLogEntry(`Processed ${window.pendingMessages.length} pending messages`);
        }
    }

    initializeWebChannel() {
        console.group("TelemetryApp: Initializing WebChannel");

        if (typeof QWebChannel !== 'undefined' && typeof qt !== 'undefined') {
            console.log("QWebChannel and qt are defined, initializing");

            new QWebChannel(qt.webChannelTransport, (channel) => {
                console.log("WebChannel connected, available objects:", Object.keys(channel.objects));

                this.messageRouter = channel.objects.messageRouter;
                if (this.messageRouter) {
                    console.log("Found messageRouter object");

                    // Explicitly bind our handler
                    const boundHandler = this.handleBackendMessage.bind(this);

                    // Check if message_to_frontend signal exists
                    if (typeof this.messageRouter.message_to_frontend === 'undefined') {
                        console.error("Error: message_to_frontend signal is undefined!");
                        this.addLogEntry("Error: Backend communication signal not available", "error");
                        return;
                    }

                    console.log("Signal message_to_frontend exists, connecting handler");

                    // Connect our handler
                    this.messageRouter.message_to_frontend.connect(boundHandler);

                    // Send a test ping to verify connectivity
                    console.log("Sending test ping");
                    this.sendToBackend('ping', { timestamp: new Date().toISOString() });

                    this.addLogEntry("Backend communication established");
                } else {
                    console.error("messageRouter not found in channel objects!");
                    this.addLogEntry("Error: Message router not available", "error");
                }
            });
        } else {
            console.error("QWebChannel or qt not defined!");
            this.addLogEntry("Error: QWebChannel not available", "error");
        }

        console.groupEnd();
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
            logContainer: document.getElementById('log-container')
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

        // We only use real connection mode now
        this.addLogEntry("Using real backend connection");
        console.log("running in real mode");

        // Debug info about message router
        console.log("Message router state:", this.messageRouter);

        this.connect(connectionInfo);
    }

    // Modified connect method with connection fallback
    connect(connectionInfo) {
        console.group("TelemetryApp Connection");
        console.log("Connecting with info:", connectionInfo);

        // Set up a fallback in case we don't get the connected message
        if (this.connectionFallbackTimer) {
            clearTimeout(this.connectionFallbackTimer);
        }

        this.connectionFallbackTimer = setTimeout(() => {
            console.warn("⚠️ No 'connected' message received within timeout!");

            // If we still haven't processed a connection, force it
            if (!this.isConnected) {
                console.log("Forcing connection state via fallback");
                this.addLogEntry("Connection timeout - starting fallback protocol");
                this.handleConnectionStateChange(true); // This will start polling
            }
        }, 5000); // 5 second timeout

        // Send the actual connection request
        this.sendToBackend('connect', connectionInfo);
        console.log("Connection request sent");
        console.groupEnd();
    }

    // Disconnect from the device
    disconnect() {
        if (this.isConnected) {
            this.sendToBackend('disconnect', {});
        }
    }

    // Send message to the backend
    sendToBackend(action, payload = {}) {
        if (!this.messageRouter) {
            this.addLogEntry("Error: Message router not available", "error");
            console.error("Message router not available for action:", action);
            return;
        }

        const message = {
            session_id: 'telemetry',
            action: action,
            payload: payload
        };

        try {
            console.log("Sending to backend:", message);
            this.messageRouter.handle_frontend_message(JSON.stringify(message));
            this.addLogEntry(`Sent ${action} command to backend`);
        } catch (error) {
            console.error("Error sending message:", error);
            this.addLogEntry(`Error sending message to backend: ${error.message}`, "error");
        }
    }

    // Simplified startPolling method that doesn't request data but monitors for updates
    startPolling() {
        console.group("🔄 Telemetry Monitoring");
        console.log("%cStarting telemetry monitoring", "color: lime; font-weight: bold");
        this.addLogEntry("Starting telemetry monitoring");

        // Clear any existing polling interval
        this.stopPolling();

        // Initialize last update time
        this.lastUpdateTime = Date.now();

        // Set up a watchdog timer to check if we're still receiving updates
        this.pollingInterval = setInterval(() => {
            console.group("🔍 Telemetry Watchdog Check");

            if (this.isConnected) {
                const lastUpdateTime = this.lastUpdateTime || 0;
                const currentTime = Date.now();
                const timeSinceLastUpdate = currentTime - lastUpdateTime;

                console.log("Time since last update:", Math.round(timeSinceLastUpdate / 1000), "seconds");

                // If it's been more than 45 seconds since our last update, try to trigger a refresh
                if (timeSinceLastUpdate > 45000) {
                    console.log("%c⚠️ No updates received in 45+ seconds, sending ping", "color: yellow; font-weight: bold");
                    this.addLogEntry("No updates received, sending refresh request");

                    // Just send a simple ping to make sure connection is still alive
                    this.sendToBackend('get_device_info', {});
                } else {
                    console.log("%c✅ Telemetry updates are being received", "color: lime");
                }
            } else {
                console.log("%c❌ Not connected, watchdog inactive", "color: gray");
            }

            console.groupEnd();
        }, 30000);

        console.log("%cTelemetry monitoring started with 30s watchdog interval", "color: lime");
        console.groupEnd();
    }

    // Stop polling
    stopPolling() {
        if (this.pollingInterval) {
            console.log("Stopping telemetry polling");
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            this.addLogEntry("Stopped regular telemetry updates");
        }
    }

    // Request all telemetry data from the backend
    requestAllTelemetryData() {
        console.log("Requesting telemetry update");
        this.addLogEntry("Requesting telemetry data update");

        // Only request device info - the backend's TelemetryCollector will handle the rest
        this.requestDeviceInfo()
            .then(deviceInfo => {
                if (!deviceInfo || !deviceInfo.hostname || deviceInfo.hostname === 'Unknown') {
                    throw new Error('Invalid device info');
                }
                this.addLogEntry("Device info received, waiting for complete telemetry update");
            })
            .catch(error => {
                console.error("Telemetry request failed:", error);
                this.addLogEntry(`Telemetry request failed: ${error.message}`, "error");

                // If we had a serious error, stop polling
                if (error.message === 'Invalid device info') {
                    this.stopPolling();
                    this.handleConnectionStateChange(false);
                }
            });
    }

    // Request specific telemetry data with promise
    requestDataWithPromise(action, payloadKey, timeout = 10000) {
        return new Promise((resolve, reject) => {
            if (!this.messageRouter) {
                reject(new Error("Message router not available"));
                return;
            }

            // Set up response handler
            const checkResponse = (message) => {
                try {
                    let data = message;
                    if (typeof message === 'string') {
                        data = JSON.parse(message);
                    }

                    // Check if this message contains the data we're waiting for
                    if (data.session_id === 'telemetry' &&
                        data.action === 'telemetry_update' &&
                        data.payload[payloadKey] !== undefined) {

                        // Disconnect the handler
                        if (this.messageRouter.message_to_frontend &&
                            this.messageRouter.message_to_frontend.disconnect) {
                            this.messageRouter.message_to_frontend.disconnect(checkResponse);
                        }

                        resolve(data.payload[payloadKey]);
                    }
                } catch (e) {
                    console.error(`Error processing ${action} response:`, e);
                }
            };

            // Connect the response handler
            if (this.messageRouter.message_to_frontend &&
                this.messageRouter.message_to_frontend.connect) {
                this.messageRouter.message_to_frontend.connect(checkResponse);
            }

            // Send the request
            this.sendToBackend(action);

            // Set timeout to prevent hanging
            setTimeout(() => {
                // Disconnect the handler
                if (this.messageRouter.message_to_frontend &&
                    this.messageRouter.message_to_frontend.disconnect) {
                    this.messageRouter.message_to_frontend.disconnect(checkResponse);
                }

                reject(new Error(`${action} timeout`));
            }, timeout);
        });
    }

    requestDeviceInfo() {
        return this.requestDataWithPromise('get_device_info', 'device_info');
    }

    // Enhanced handleBackendMessage with extensive debugging for telemetry_update
    handleBackendMessage(message) {
        console.group("⭐ Backend Message Handler ⭐");
        console.log("%cRaw message received:", "color: blue; font-weight: bold", message);

        try {
            // Parse the message if it's a string
            let data = message;
            if (typeof message === 'string') {
                data = JSON.parse(message);
                console.log("%cParsed JSON message:", "color: green", data);
            } else {
                console.log("%cMessage already an object:", "color: orange", data);
            }

            // Log important message properties
            console.log("%cSession ID:", "font-weight: bold", data.session_id);
            console.log("%cAction:", "font-weight: bold", data.action);
            if (data.payload) {
                console.log("%cPayload keys:", "font-weight: bold", Object.keys(data.payload));
            }

            // Check if this message is for telemetry
            if (data.session_id !== 'telemetry') {
                console.log("%cIgnoring message for non-telemetry session:", "color: gray", data.session_id);
                console.groupEnd();
                return;
            }

            switch (data.action) {
                case 'connected':
                    console.log("%c★★★ CONNECTED MESSAGE RECEIVED! ★★★", "color: lime; background: black; font-size: 14px; padding: 4px");
                    console.log("Connected payload:", data.payload);

                    this.handleConnectionStateChange(true);
                    this.addLogEntry("Connected to device successfully");
                    break;

                case 'disconnected':
                    console.log("%c⚠️ DISCONNECTION EVENT RECEIVED!", "color: yellow; background: black; font-size: 14px; padding: 4px");
                    this.handleConnectionStateChange(false);
                    this.addLogEntry("Disconnected from device");
                    break;

                case 'telemetry_update':
                    console.log("%c📊 TELEMETRY UPDATE RECEIVED!", "color: cyan; background: black; font-size: 14px; padding: 4px");

                    // Record last update time
                    this.lastUpdateTime = Date.now();

                    // Check what data is included
                    if (data.payload) {
                        console.log("Telemetry update includes:", Object.keys(data.payload).join(", "));

                        if (data.payload.device_info) {
                            console.log("Device info present:", data.payload.device_info);
                        }

                        if (data.payload.interfaces) {
                            console.log(`Interfaces present: ${data.payload.interfaces.length} items`);
                        }

                        if (data.payload.neighbors) {
                            console.log(`Neighbors present: ${data.payload.neighbors.length} items`);
                        }

                        if (data.payload.routing_table) {
                            console.log(`Routing table present: ${data.payload.routing_table.length} items`);
                        }

                        if (data.payload.environment) {
                            console.log("Environment data present:", Object.keys(data.payload.environment));
                        }
                    }

                    this.processUpdateData(data.payload);
                    console.log("%cTelemetry data processed successfully", "color: lime");
                    break;

                case 'error':
                    console.error("%c❌ ERROR FROM BACKEND:", "color: red; font-weight: bold", data.payload);
                    this.addLogEntry(`Error: ${data.payload.message}`, "error");
                    break;

                default:
                    console.log("%cUnknown action received:", "color: orange", data.action);
                    this.addLogEntry(`Received unknown action: ${data.action}`);
            }
        } catch (error) {
            console.error("%c💥 ERROR PROCESSING MESSAGE:", "color: red; font-weight: bold", error);
            console.error("Original message:", message);
            this.addLogEntry(`Error handling message: ${error.message}`, "error");
        }

        console.groupEnd();
    }

    // Enhanced processUpdateData method with detailed logging
    processUpdateData(payload) {
        console.group("📊 Processing Telemetry Update");
        console.log("Full payload:", payload);

        // Update last update timestamp
        this.lastUpdateTime = Date.now();
        console.log("Updated lastUpdateTime:", new Date(this.lastUpdateTime).toLocaleTimeString());

        // Process device info
        if (payload.device_info) {
            console.log("%cProcessing device info:", "color: cyan; font-weight: bold", payload.device_info);
            this.telemetryData.deviceInfo = payload.device_info;
            this.updateDeviceInfo(payload.device_info);
            DeviceIcons.updateDeviceIcon(payload.device_info);
            this.addLogEntry(`Device info updated: ${payload.device_info.hostname}`);
        } else {
            console.log("%cNo device info in payload", "color: orange");
        }

        // Process interfaces
        if (payload.interfaces) {
            console.log("%cProcessing interfaces:", "color: cyan; font-weight: bold",
                `${payload.interfaces.length} interfaces`);
            this.telemetryData.interfaces = payload.interfaces;
            this.updateInterfaces(payload.interfaces);
            this.addLogEntry(`Updated ${payload.interfaces.length} interfaces`);
        } else {
            console.log("%cNo interfaces in payload", "color: orange");
        }

        // Process neighbors
        if (payload.neighbors) {
            console.log("%cProcessing neighbors:", "color: cyan; font-weight: bold",
                `${payload.neighbors.length} neighbors`);
            this.telemetryData.neighbors = payload.neighbors;
            this.updateNeighbors(payload.neighbors);
            this.addLogEntry(`Updated ${payload.neighbors.length} neighbors`);
        } else {
            console.log("%cNo neighbors in payload", "color: orange");
        }

        // Process routing table
        if (payload.routing_table) {
            console.log("%cProcessing routing table:", "color: cyan; font-weight: bold",
                `${payload.routing_table.length} routes`);
            this.telemetryData.routingTable = payload.routing_table;
            this.updateRoutingTable(payload.routing_table);
            this.addLogEntry(`Updated ${payload.routing_table.length} routes`);
        } else {
            console.log("%cNo routing table in payload", "color: orange");
        }

        // Process environment data
        if (payload.environment) {
            console.log("%cProcessing environment data:", "color: cyan; font-weight: bold",
                Object.keys(payload.environment));
            this.telemetryData.environment = payload.environment;
            this.updateEnvironmentDisplay(payload.environment);
            this.addLogEntry("Updated environment data");
        } else {
            console.log("%cNo environment data in payload", "color: orange");
        }

        // After processing all data, ensure we're showing connected state
        if (payload.device_info) {
            console.log("%cUpdating connection state based on device info", "color: lime");
            this.handleConnectionStateChange(true);
        }

        console.log("%cTelemetry update processing complete", "color: lime; font-weight: bold");
        console.groupEnd();
    }

    // Updated handleConnectionStateChange to only start polling when connecting
    handleConnectionStateChange(isConnected) {
        console.group("Connection State Change");
        console.log("Changing connection state to:", isConnected);

        // Update state
        const wasConnected = this.isConnected;
        this.isConnected = isConnected;

        // Clear connection fallback timer if it exists
        if (this.connectionFallbackTimer) {
            clearTimeout(this.connectionFallbackTimer);
            this.connectionFallbackTimer = null;
            console.log("Cleared connection fallback timer");
        }

        if (isConnected) {
            // Only start polling if we're connecting and not already connected
            if (!wasConnected) {
                console.log("Starting polling (connection state change)");
                this.startPolling();
            } else {
                console.log("Already connected, not restarting polling");
            }
        } else {
            // Make sure polling is stopped when disconnecting
            console.log("Stopping polling (disconnection)");
            this.stopPolling();
        }

        // Update UI
        if (this.elements.connectBtn) {
            this.elements.connectBtn.textContent = isConnected ? 'Disconnect' : 'Connect';
            this.elements.connectBtn.classList.toggle('connected', isConnected);
            console.log("Updated connect button UI");
        } else {
            console.error("Connect button element not found");
        }

        // Log state change
        this.addLogEntry(`Connection state: ${isConnected ? 'Connected' : 'Disconnected'}`);
        console.groupEnd();
    }

    // Update device info display
    updateDeviceInfo(info) {
        try {
            if (!this.elements.deviceInfo) {
                console.error("Device info elements not found");
                return;
            }

            console.log("Updating device info with:", info);

            if (info === "discovering") {
                // Set discovering state
                this.elements.deviceInfo.forEach(element => {
                    const labelText = element.textContent.split(':')[0];
                    element.innerHTML = `${labelText}: <span>Discovering...</span>`;
                    console.log(`Set element ${element.dataset.device} to Discovering...`);
                });
            } else if (info === null) {
                // Set unknown state
                this.elements.deviceInfo.forEach(element => {
                    const labelText = element.textContent.split(':')[0];
                    element.innerHTML = `${labelText}: <span>Unknown</span>`;
                    console.log(`Set element ${element.dataset.device} to Unknown`);
                });
            } else if (info && typeof info === 'object') {
                // Update with actual device info
                this.elements.deviceInfo.forEach(element => {
                    const key = element.dataset.device;
                    if (key && info.hasOwnProperty(key)) {
                        const labelText = element.textContent.split(':')[0];
                        element.innerHTML = `${labelText}: <span>${info[key]}</span>`;
                        console.log(`Updated ${key} to ${info[key]}`);
                    } else {
                        console.log(`Skipping element with key ${key}, not found in info`);
                    }
                });

                // Set connected state
                this.handleConnectionStateChange(true);
            }
        } catch (error) {
            console.error("Error updating device info:", error);
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
}

// Make TelemetryApp globally available
window.TelemetryApp = TelemetryApp;