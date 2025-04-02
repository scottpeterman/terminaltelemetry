/**
 * Enhanced QWebChannel Debugger with Message Comparison
 * Helps diagnose differences between expected and actual message formats
 */

// Create the debugger namespace
window.QWebChannelDebugger = {
    // Debug settings
    settings: {
        enabled: true,
        logToConsole: true,
        maxStoredMessages: 100,
        compareRequests: true  // Added feature to compare requests
    },

    // Storage for messages
    messages: [],

    // Request comparison data
    requestComparison: {
        telemetryAppRequests: {},  // What telemetry-app.js sends
        sessionRequests: {}        // What sessions.js sends
    },

    // Install debugging on both systems
    install: function() {
        console.log("🔍 Enhanced QWebChannel Debugger - Installing...");

        // Check periodically if both systems are ready
        const checkInterval = setInterval(() => {
            if (window.telemetryApp && window.sessionManager) {
                clearInterval(checkInterval);
                this.setupDebugger();
            }
        }, 500);
    },

    // Setup the debugger once both systems are available
    setupDebugger: function() {
        console.log("🔍 Enhanced QWebChannel Debugger - Installing on multiple systems...");

        // Hook into telemetryApp
        if (window.telemetryApp) {
            this.hookTelemetryApp();
        }

        // Hook into sessionManager
        if (window.sessionManager) {
            this.hookSessionManager();
        }

        // Add debugging commands to window for console access
        window.telemetryDebug = {
            // Show recent messages
            showRecentMessages: () => this.showRecentMessages(),

            // Show all stored messages
            showAllMessages: () => this.showAllMessages(),

            // Find messages by action
            findMessagesByAction: (action) => this.findMessagesByAction(action),

            // Find messages by payload key
            findMessagesByPayloadKey: (key) => this.findMessagesByPayloadKey(key),

            // Inspect a specific message in detail
            inspectMessage: (index) => this.inspectMessage(index),

            // Check connection status
            connectionStatus: () => this.checkConnectionStatus(),

            // Clear message history
            clearMessages: () => this.clearMessages(),

            // Compare requests between systems
            compareRequests: () => this.compareRequestFormats(),

            // Send a test message from sessions.js format
            sendTestMessage: (action) => this.sendTestMessage(action),

            // Monitor backend responses
            monitorBackend: () => this.setupBackendMonitoring(),

            // Send a specific action with specific payload
            sendAction: (action, payload = {}) => this.sendAction(action, payload),
        };

        // Setup backend monitoring by default
        this.setupBackendMonitoring();

        console.log("🔍 Enhanced QWebChannel Debugger - Installed successfully");
        console.log("🔧 Available commands: telemetryDebug.showRecentMessages(), telemetryDebug.compareRequests(), etc.");
    },

    // Hook into telemetryApp
    hookTelemetryApp: function() {
        console.log("Hooking into telemetryApp...");

        // Store original sendToBackend
        const originalSend = window.telemetryApp.sendToBackend;

        // Override with our interceptor
        window.telemetryApp.sendToBackend = (action, payload = {}) => {
            // Record this format
            this.recordRequest('telemetryApp', action, payload);

            // Call original to maintain functionality
            return originalSend.call(window.telemetryApp, action, payload);
        };

        // Hook into the message handler
        const originalHandler = window.telemetryApp.handleBackendMessage;
        window.telemetryApp.handleBackendMessage = (message) => {
            // Process with our debugger
            this.processMessage(message, 'telemetryApp');

            // Call original handler
            return originalHandler.call(window.telemetryApp, message);
        };
    },

    // Hook into sessionManager
    hookSessionManager: function() {
        console.log("Hooking into sessionManager...");

        // Store original handleBackendMessage
        const originalHandler = window.sessionManager.handleBackendMessage;

        // Override with our interceptor
        window.sessionManager.handleBackendMessage = (message) => {
            // Process with our debugger
            this.processMessage(message, 'sessionManager');

            // Call original to maintain functionality
            return originalHandler.call(window.sessionManager, message);
        };

        // Hook into telemetry session
        if (window.sessionManager.sessions?.telemetry) {
            const telemetrySession = window.sessionManager.sessions.telemetry;
            const originalSend = telemetrySession.sendToBackend;

            telemetrySession.sendToBackend = (action, payload = {}) => {
                // Record this format
                this.recordRequest('sessionsTelemetry', action, payload);

                // Call original
                return originalSend.call(telemetrySession, action, payload);
            };
        }
    },

    // Setup monitoring of backend responses
    setupBackendMonitoring: function() {
        console.log("Setting up backend response monitoring...");

        // Only set up once
        if (this._backendMonitoringSetup) {
            console.log("Backend monitoring already set up");
            return "Backend monitoring already active";
        }

        // Find the messageRouter
        let messageRouter = null;
        if (window.telemetryApp && window.telemetryApp.messageRouter) {
            messageRouter = window.telemetryApp.messageRouter;
        } else if (window.sessionManager && window.sessionManager.messageRouter) {
            messageRouter = window.sessionManager.messageRouter;
        }

        if (!messageRouter) {
            console.error("Could not find messageRouter for monitoring");
            return "Error: messageRouter not found";
        }

        // Store original handler
        this._originalMessageToFrontend = messageRouter.message_to_frontend;

        // Create a proxy to monitor responses
        const responseMonitor = (message) => {
            this.logBackendResponse(message);

            // We're not actually handling the message, just monitoring
            return false;
        };

        // Connect our monitor
        messageRouter.message_to_frontend.connect(responseMonitor);

        this._backendMonitoringSetup = true;
        console.log("Backend response monitoring active");

        return "Backend response monitoring activated";
    },

    // Log backend responses
    logBackendResponse: function(message) {
        console.group("📥 BACKEND RESPONSE");
        console.log("⏱️ Time:", new Date().toISOString());

        try {
            // Try to parse if it's a string
            let data = message;
            if (typeof message === 'string') {
                data = JSON.parse(message);
                console.log("Parsed message:", data);

                // Log specific parts
                if (data.session_id) console.log("Session ID:", data.session_id);
                if (data.action) console.log("Action:", data.action);
                if (data.payload) {
                    console.log("Payload:", data.payload);
                    console.log("Payload keys:", Object.keys(data.payload));
                }
            } else {
                console.log("Raw message (not a string):", message);
            }
        } catch (e) {
            console.warn("Could not parse backend response:", e);
            console.log("Raw message:", message);
        }

        console.groupEnd();
    },

    // Record a request format for comparison
    recordRequest: function(source, action, payload) {
        const key = `${action}_${JSON.stringify(payload)}`;

        if (source === 'telemetryApp') {
            this.requestComparison.telemetryAppRequests[key] = {
                action,
                payload,
                time: new Date().toISOString()
            };
        } else if (source === 'sessionsTelemetry') {
            this.requestComparison.sessionRequests[key] = {
                action,
                payload,
                time: new Date().toISOString()
            };
        }
    },

    // Compare request formats between the two systems
    compareRequestFormats: function() {
        console.group("🔄 Request Format Comparison");

        console.log("telemetry-app.js sends these requests:");
        for (const key in this.requestComparison.telemetryAppRequests) {
            const req = this.requestComparison.telemetryAppRequests[key];
            console.log(`- ${req.action}:`, req.payload);
        }

        console.log("sessions.js sends these requests:");
        for (const key in this.requestComparison.sessionRequests) {
            const req = this.requestComparison.sessionRequests[key];
            console.log(`- ${req.action}:`, req.payload);
        }

        // Find differences
        console.log("Analyzing differences...");
        const telemetryAppActions = Object.values(this.requestComparison.telemetryAppRequests)
            .map(req => req.action);
        const sessionsActions = Object.values(this.requestComparison.sessionRequests)
            .map(req => req.action);

        // Actions only in telemetryApp
        const uniqueToTelemetryApp = telemetryAppActions.filter(
            action => !sessionsActions.includes(action)
        );

        // Actions only in sessions
        const uniqueToSessions = sessionsActions.filter(
            action => !telemetryAppActions.includes(action)
        );

        console.log("Actions only in telemetry-app.js:", uniqueToTelemetryApp);
        console.log("Actions only in sessions.js:", uniqueToSessions);

        console.groupEnd();

        return {
            telemetryAppRequests: this.requestComparison.telemetryAppRequests,
            sessionRequests: this.requestComparison.sessionRequests,
            uniqueToTelemetryApp,
            uniqueToSessions
        };
    },

    // Send a test message mimicking sessions.js format
    sendTestMessage: function(action) {
        console.group("🧪 Sending Test Message");

        // Find the messageRouter
        let messageRouter = null;
        if (window.sessionManager && window.sessionManager.messageRouter) {
            messageRouter = window.sessionManager.messageRouter;
        } else if (window.telemetryApp && window.telemetryApp.messageRouter) {
            messageRouter = window.telemetryApp.messageRouter;
        }

        if (!messageRouter) {
            console.error("Could not find messageRouter for test message");
            console.groupEnd();
            return "Error: messageRouter not found";
        }

        // Prepare test payloads based on action
        let payload = {};
        switch (action) {
            case 'get_device_info':
                // No special payload needed
                break;
            case 'get_interfaces':
                // No special payload needed
                break;
            case 'get_neighbors':
                // No special payload needed
                break;
            case 'get_routes':
                // No special payload needed
                break;
            case 'get_environment':
                // No special payload needed
                break;
            case 'requestAllTelemetryData':
                // This will send a comprehensive request
                action = 'requestFullTelemetry';
                break;
            default:
                console.warn(`Unknown test action: ${action}`);
                console.groupEnd();
                return `Error: Unknown test action ${action}`;
        }

        // Create the message using sessions.js format
        const message = {
            session_id: 'telemetry',
            action: action,
            payload: payload
        };

        // Send it
        console.log("Sending test message:", message);
        messageRouter.handle_frontend_message(JSON.stringify(message));

        console.log("Test message sent");
        console.groupEnd();

        return `Test message '${action}' sent successfully`;
    },

    // Send a specific action with custom payload
    sendAction: function(action, payload = {}) {
        console.group(`🚀 Sending Custom Action: ${action}`);

        // Find the messageRouter
        let messageRouter = null;
        if (window.sessionManager && window.sessionManager.messageRouter) {
            messageRouter = window.sessionManager.messageRouter;
        } else if (window.telemetryApp && window.telemetryApp.messageRouter) {
            messageRouter = window.telemetryApp.messageRouter;
        }

        if (!messageRouter) {
            console.error("Could not find messageRouter");
            console.groupEnd();
            return "Error: messageRouter not found";
        }

        // Create the message
        const message = {
            session_id: 'telemetry',
            action: action,
            payload: payload
        };

        // Send it
        console.log("Sending message:", message);
        messageRouter.handle_frontend_message(JSON.stringify(message));

        console.log("Message sent");
        console.groupEnd();

        return `Action '${action}' sent successfully`;
    },

    // Process and log an incoming message
    processMessage: function(message, source = 'unknown') {
        if (!this.settings.enabled) return;

        // Create debug info object
        const debugInfo = {
            timestamp: new Date().toISOString(),
            source: source,
            raw: message
        };

        // Try to parse the message if it's a string
        if (typeof message === 'string') {
            try {
                debugInfo.parsed = JSON.parse(message);
            } catch (e) {
                debugInfo.parseError = e.message;
            }
        } else {
            debugInfo.parsed = message;
        }

        // Store the message
        this.messages.unshift(debugInfo);

        // Limit stored messages
        if (this.messages.length > this.settings.maxStoredMessages) {
            this.messages.pop();
        }

        // Log to console if enabled
        if (this.settings.logToConsole) {
            this.logMessageToConsole(debugInfo);
        }
    },

    // Log a message to the console with formatting
    logMessageToConsole: function(debugInfo) {
        console.group(`📨 TELEMETRY MESSAGE (${debugInfo.source})`);
        console.log("⏱️ Time:", debugInfo.timestamp);

        // Log the raw message
        console.log("📝 Raw message:", debugInfo.raw);

        // If we have parsed data, log that too
        if (debugInfo.parsed) {
            const parsed = debugInfo.parsed;

            console.log("🔍 Parsed message:", parsed);

            // Log specific parts if available
            if (parsed.session_id) console.log("🆔 Session ID:", parsed.session_id);
            if (parsed.action) console.log("🎯 Action:", parsed.action);
            if (parsed.payload) {
                console.log("📦 Payload:", parsed.payload);
                console.log("📦 Payload keys:", Object.keys(parsed.payload));
            }
        }

        // If there was a parse error, log that
        if (debugInfo.parseError) {
            console.warn("⚠️ Parse error:", debugInfo.parseError);
        }

        console.groupEnd();
    },

    // Show the most recent messages
    showRecentMessages: function(count = 10) {
        const messages = this.messages.slice(0, count);

        console.group("📋 Recent Telemetry Messages");

        if (messages.length === 0) {
            console.log("No messages recorded yet");
        } else {
            messages.forEach((msg, i) => {
                console.group(`Message ${i + 1} - ${msg.timestamp} (${msg.source})`);
                if (msg.parsed) {
                    console.log("Action:", msg.parsed.action || "unknown");
                    console.log("Parsed:", msg.parsed);
                }
                console.log("Raw:", msg.raw);
                console.groupEnd();
            });
        }

        console.groupEnd();
        return `Displayed ${messages.length} messages. ${this.messages.length - count} more available.`;
    },

    // Show all stored messages
    showAllMessages: function() {
        console.group("📋 All Telemetry Messages");

        if (this.messages.length === 0) {
            console.log("No messages recorded yet");
        } else {
            this.messages.forEach((msg, i) => {
                console.group(`Message ${i + 1} - ${msg.timestamp} (${msg.source})`);
                if (msg.parsed) {
                    console.log("Action:", msg.parsed.action || "unknown");
                    console.log("Parsed:", msg.parsed);
                }
                console.log("Raw:", msg.raw);
                console.groupEnd();
            });
        }

        console.groupEnd();
        return `Displayed ${this.messages.length} messages.`;
    },

    // Find messages by action
    findMessagesByAction: function(action) {
        const matches = this.messages.filter(m => m.parsed && m.parsed.action === action);

        console.group(`📋 Messages with action: ${action}`);

        if (matches.length === 0) {
            console.log(`No messages found with action '${action}'`);
        } else {
            matches.forEach((msg, i) => {
                console.group(`Match ${i + 1} - ${msg.timestamp} (${msg.source})`);
                console.log("Parsed:", msg.parsed);
                console.log("Raw:", msg.raw);
                console.groupEnd();
            });
        }

        console.groupEnd();
        return `Found ${matches.length} messages with action '${action}'.`;
    },

    // Find messages by payload key
    findMessagesByPayloadKey: function(key) {
        const matches = this.messages.filter(m =>
            m.parsed && m.parsed.payload && Object.prototype.hasOwnProperty.call(m.parsed.payload, key)
        );

        console.group(`📋 Messages with payload key: ${key}`);

        if (matches.length === 0) {
            console.log(`No messages found with payload key '${key}'`);
        } else {
            matches.forEach((msg, i) => {
                console.group(`Match ${i + 1} - ${msg.timestamp} (${msg.source})`);
                console.log(`${key}:`, msg.parsed.payload[key]);
                console.log("Full payload:", msg.parsed.payload);
                console.log("Full message:", msg.parsed);
                console.groupEnd();
            });
        }

        console.groupEnd();
        return `Found ${matches.length} messages with payload key '${key}'.`;
    },

    // Inspect a specific message
    inspectMessage: function(index = 0) {
        if (index < 0 || index >= this.messages.length) {
            return `Invalid index. Available range: 0-${this.messages.length - 1}`;
        }

        const msg = this.messages[index];

        console.group(`📋 Message Inspection - ${msg.timestamp} (${msg.source})`);

        if (msg.parsed) {
            console.log("Session ID:", msg.parsed.session_id);
            console.log("Action:", msg.parsed.action);

            if (msg.parsed.payload) {
                console.group("Payload Structure");

                for (const key in msg.parsed.payload) {
                    const value = msg.parsed.payload[key];
                    const type = Array.isArray(value) ? `Array(${value.length})` : typeof value;
                    console.log(`${key}: ${type}`);
                }

                console.groupEnd();
                console.log("Full Payload:", msg.parsed.payload);
            }
        } else {
            console.log("Message not parsed successfully");
            if (msg.parseError) {
                console.warn("Parse error:", msg.parseError);
            }
            console.log("Raw message:", msg.raw);
        }

        console.groupEnd();
        return "Message inspection complete";
    },

    // Check connection status
    checkConnectionStatus: function() {
        console.group("📡 Telemetry Connection Status");

        // Check telemetryApp status
        if (window.telemetryApp) {
            console.log("telemetry-app.js:");
            console.log("  Connected:", window.telemetryApp.isConnected);
            console.log("  Message Router:", window.telemetryApp.messageRouter ? "Available" : "Not Available");
            console.log("  Last Update:", window.telemetryApp.lastUpdateTime ?
                new Date(window.telemetryApp.lastUpdateTime).toISOString() : "Never");
        }

        // Check sessions.js status
        if (window.sessionManager?.sessions?.telemetry) {
            console.log("sessions.js:");
            console.log("  Active:", window.sessionManager.sessions.telemetry.telemetryActive);
            console.log("  Message Router:", window.sessionManager.messageRouter ? "Available" : "Not Available");
            console.log("  Device State:", window.sessionManager.sessions.telemetry.deviceState);
        }

        console.groupEnd();

        return `Connection status checked`;
    },

    // Clear message history
    clearMessages: function() {
        const count = this.messages.length;
        this.messages = [];
        return `Cleared ${count} stored messages.`;
    }
};

// Auto-install when the file loads
document.addEventListener('DOMContentLoaded', function() {
    window.QWebChannelDebugger.install();
});

// Log that the debugger script has loaded
console.log("🔍 Enhanced QWebChannel Debugger loaded");