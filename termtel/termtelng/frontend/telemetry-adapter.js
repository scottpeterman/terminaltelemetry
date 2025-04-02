
// Function to install the compatibility fix
function installTelemetryCompatibilityFix() {
    console.log("🔧 Installing Corrected Telemetry Compatibility Fix...");

    // Ensure telemetryApp exists
    if (!window.telemetryApp) {
        console.error("telemetryApp not found! Cannot install fix.");
        return false;
    }

    // Store the original sendToBackend function
    const originalSendToBackend = window.telemetryApp.sendToBackend;

    // Replace with our adapted version
    window.telemetryApp.sendToBackend = function(action, payload = {}) {
        // Log the original request
        console.log(`🔄 Original request: ${action}`, payload);

        // Check if this is a telemetry request that needs adaptation
        let adaptedAction = action;
        let adaptedPayload = payload;

        // Looking at message_router.py, these are the valid actions:
        // "get_device_info" - tries to call session.get_device_info()
        // "get_environment" - tries to call session.get_environment_data()

        // Map all telemetry requests to these valid actions
        switch (action) {
            case 'get_device_info':
                // This action exists in message_router.py
                adaptedAction = 'get_device_info';
                break;

            case 'get_interfaces':
                // Map to get_device_info to trigger collector
                console.log("Mapping 'get_interfaces' to 'get_device_info'");
                adaptedAction = 'get_device_info';
                break;

            case 'get_neighbors':
                // Map to get_device_info to trigger collector
                console.log("Mapping 'get_neighbors' to 'get_device_info'");
                adaptedAction = 'get_device_info';
                break;

            case 'get_routes':
                // Map to get_device_info to trigger collector
                console.log("Mapping 'get_routes' to 'get_device_info'");
                adaptedAction = 'get_device_info';
                break;

            case 'get_environment':
                // This action exists in message_router.py
                adaptedAction = 'get_environment';
                break;

            case 'requestAllTelemetry':
                // Use get_device_info which should trigger the collector
                console.log("Mapping 'requestAllTelemetry' to 'get_device_info'");
                adaptedAction = 'get_device_info';
                break;
        }

        // Log if we adapted anything
        if (action !== adaptedAction || JSON.stringify(payload) !== JSON.stringify(adaptedPayload)) {
            console.log(`⚙️ Adapted to: ${adaptedAction}`, adaptedPayload);
        }

        // Call the original function with potentially adapted parameters
        return originalSendToBackend.call(this, adaptedAction, adaptedPayload);
    };

    // Add a convenience method to trigger a full update
    window.telemetryApp.requestFullUpdate = function() {
        console.log("Requesting full telemetry update");
        this.sendToBackend('get_device_info', {});
    };

    // Fix the polling function to use the correct action
    if (window.telemetryApp.startPolling) {
        const originalStartPolling = window.telemetryApp.startPolling;
        window.telemetryApp.startPolling = function() {
            console.log("Using adapted polling function");

            // Call original startup logic
            originalStartPolling.call(this);

            // Clear any existing polling interval and set a new one
            if (this.pollingInterval) {
                clearInterval(this.pollingInterval);
            }

            // Initialize last update time
            this.lastUpdateTime = Date.now();

            // Set up a watchdog timer using the fixed action name
            this.pollingInterval = setInterval(() => {
                if (this.isConnected) {
                    const timeSinceLastUpdate = Date.now() - (this.lastUpdateTime || 0);

                    // If it's been more than 45 seconds since our last update, trigger a refresh
                    if (timeSinceLastUpdate > 45000) {
                        console.log("No updates received in 45+ seconds, sending refresh request");
                        this.sendToBackend('get_device_info', {}); // Use the correct action
                    }
                }
            }, 30000);

            // Trigger an immediate update
            this.sendToBackend('get_device_info', {});

            console.log("Adapted polling function initialized");
        };
    }

    // Fix the requestAllTelemetryData method
    if (window.telemetryApp.requestAllTelemetryData) {
        const originalRequestAllData = window.telemetryApp.requestAllTelemetryData;
        window.telemetryApp.requestAllTelemetryData = function() {
            console.log("Using adapted requestAllTelemetryData function");

            // Just send get_device_info instead of chaining requests
            this.sendToBackend('get_device_info', {});
            console.log("All telemetry requested via get_device_info");
        };
    }

    console.log("✅ Telemetry Compatibility Fix installed successfully");
    return true;
}

// Add a function to inspect TelemetrySession in the backend
function inspectBackendTelemetrySession() {
    console.log("Sending test message to inspect backend TelemetrySession...");

    // Create a custom message to trigger debug output on the backend
    const message = {
        session_id: 'telemetry',
        action: 'debug_info',
        payload: {}
    };

    // Send via message router - you'll need to check backend logs
    if (window.telemetryApp && window.telemetryApp.messageRouter) {
        window.telemetryApp.messageRouter.handle_frontend_message(JSON.stringify(message));
        console.log("Debug message sent - check backend logs");
        return "Debug message sent";
    } else {
        console.error("messageRouter not available");
        return "Error: messageRouter not available";
    }
}

// Auto-install the fix when the page loads
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        if (window.telemetryApp) {
            installTelemetryCompatibilityFix();
            // Trigger a manual re-connect if already connected
            if (window.telemetryApp.isConnected) {
                console.log("App already connected, triggering a manual update");
                window.telemetryApp.requestFullUpdate();
            }
        } else {
            console.warn("telemetryApp not found on page load, trying again in 1 second");
            setTimeout(() => {
                if (window.telemetryApp) {
                    installTelemetryCompatibilityFix();
                } else {
                    console.error("telemetryApp still not available after retry");
                }
            }, 1000);
        }
    }, 500);
});

// Export functions for manual use
window.telemetryFix = {
    install: installTelemetryCompatibilityFix,
    triggerUpdate: function() {
        if (window.telemetryApp) {
            window.telemetryApp.requestFullUpdate();
            return "Update triggered";
        }
        return "telemetryApp not available";
    },
    inspectBackend: inspectBackendTelemetrySession
};

console.log("🔧 Corrected Telemetry Compatibility Fix script loaded");