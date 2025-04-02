// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM content loaded, initializing application");

    // Copy corner SVGs
    const cornerSVG = document.querySelector('.hud-corner.top-left svg');
    if (cornerSVG) {
        const svg = cornerSVG.outerHTML;
        document.querySelectorAll('.hud-corner:not(.top-left)').forEach(corner => {
            corner.innerHTML = svg;
        });
        console.log("Corner SVGs copied");
    } else {
        console.warn("Top-left corner SVG not found");
    }

    // Check if QWebChannel is available
    if (typeof QWebChannel !== 'undefined') {
        console.log("QWebChannel is available");
    } else {
        console.warn("QWebChannel is not available, waiting for it to load");
        // Add a script to detect when QWebChannel becomes available
        const qwebChannelDetector = setInterval(() => {
            if (typeof QWebChannel !== 'undefined') {
                console.log("QWebChannel is now available");
                clearInterval(qwebChannelDetector);
                checkQtAndInitApp();
            }
        }, 100);
    }

    checkQtAndInitApp();
});

function checkQtAndInitApp() {
    // Check if qt is available
    if (typeof qt !== 'undefined') {
        console.log("Qt is available");
        if (typeof qt.webChannelTransport !== 'undefined') {
            console.log("qt.webChannelTransport is available");
        } else {
            console.warn("qt.webChannelTransport is not available, waiting for it");
            // Add a detector for when qt.webChannelTransport becomes available
            const transportDetector = setInterval(() => {
                if (typeof qt !== 'undefined' && typeof qt.webChannelTransport !== 'undefined') {
                    console.log("qt.webChannelTransport is now available");
                    clearInterval(transportDetector);
                    initializeApp();
                }
            }, 100);
            return;
        }
    } else {
        console.warn("Qt is not available, waiting for it to load");
        // Add a detector for when qt becomes available
        const qtDetector = setInterval(() => {
            if (typeof qt !== 'undefined') {
                console.log("Qt is now available");
                clearInterval(qtDetector);
                checkQtAndInitApp();
            }
        }, 100);
        return;
    }

    // If we reach here, both Qt and QWebChannel are available
    initializeApp();
}

function initializeApp() {
    // Ensure handleMessage function exists globally if not already defined
    if (typeof window.handleMessage !== 'function') {
        console.log("Creating global handleMessage function");
        window.handleMessage = function(message) {
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
        };
    }

    // Add a check to ensure TelemetryApp is defined
    if (typeof TelemetryApp !== 'undefined') {
        // Initialize the telemetry app
        console.log("Creating TelemetryApp instance");
        window.telemetryApp = new TelemetryApp();
        console.log("Telemetry app initialized successfully");

        // Process any pending messages
        if (window.pendingMessages && window.pendingMessages.length > 0) {
            console.log(`Processing ${window.pendingMessages.length} pending messages`);

            window.pendingMessages.forEach(message => {
                window.telemetryApp.handleBackendMessage(message);
            });

            // Clear the queue
            window.pendingMessages = [];
        }
    } else {
        console.error("Error: TelemetryApp class not found. Check if telemetry-app.js is loaded correctly.");

        // Try to load it again with a timeout
        setTimeout(() => {
            if (typeof TelemetryApp !== 'undefined') {
                console.log("TelemetryApp available after delay, initializing");
                window.telemetryApp = new TelemetryApp();
                console.log("Telemetry app initialized after delay");

                // Process any pending messages
                if (window.pendingMessages && window.pendingMessages.length > 0) {
                    console.log(`Processing ${window.pendingMessages.length} pending messages after delay`);

                    window.pendingMessages.forEach(message => {
                        window.telemetryApp.handleBackendMessage(message);
                    });

                    // Clear the queue
                    window.pendingMessages = [];
                }
            } else {
                console.error("Failed to initialize telemetry app after delay, TelemetryApp is still undefined");
            }
        }, 1000);
    }
}