/**
 * corner-designs.js
 *
 * A collection of SVG corner designs for use with UI panels
 * Compatible with theme systems that use SVG for corner elements
 */

// Corner Design Library
window.CornerDesigns = {
    // Original/Classic designs
    classic: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 40 0 L 100 0 L 100 10 L 45 10 L 10 45 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
        </svg>
    `,

    doubleLine: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 40 0 L 100 0 L 100 10 L 45 10 L 10 45 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
            <path d="M 0 50 L 50 0 L 100 0 L 100 20 L 55 20 L 20 55 L 20 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1" opacity="0.5"/>
        </svg>
    `,

    cyberCircuit: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 40 0 L 100 0 L 100 10 L 45 10 L 10 45 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
            <path d="M 0 45 L 35 10 M 45 10 L 95 10" fill="none" stroke="currentColor" stroke-width="1" opacity="0.5"/>
            <circle cx="40" cy="10" r="2" fill="currentColor"/>
            <path d="M 55 10 L 65 0 M 75 10 L 85 0" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
        </svg>
    `,

    jagged: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 10 30 L 20 20 L 30 10 L 40 0 L 100 0 L 100 10 L 45 10 L 35 20 L 25 30 L 15 40 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
        </svg>
    `,

    rounded: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 C 0 20, 20 0, 40 0 L 100 0 L 100 10 L 45 10 C 30 10, 10 30, 10 45 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
        </svg>
    `,

    pixel: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 0 30 L 10 30 L 10 20 L 20 20 L 20 10 L 30 10 L 30 0 L 100 0 L 100 10 L 40 10 L 40 20 L 30 20 L 30 30 L 20 30 L 20 40 L 10 40 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
        </svg>
    `,

    minimalist: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 30 L 30 0 L 100 0 L 100 5 L 35 5 L 5 35 L 5 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
        </svg>
    `,

    dotMatrix: `
        <svg viewBox="0 0 100 100">
            <circle cx="10" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="20" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="30" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="40" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="50" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="60" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="70" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="80" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="90" cy="10" r="1.5" fill="currentColor"/>
            <circle cx="10" cy="20" r="1.5" fill="currentColor"/>
            <circle cx="10" cy="30" r="1.5" fill="currentColor"/>
            <circle cx="10" cy="40" r="1.5" fill="currentColor"/>
            <circle cx="10" cy="50" r="1.5" fill="currentColor"/>
            <circle cx="10" cy="60" r="1.5" fill="currentColor"/>
            <circle cx="10" cy="70" r="1.5" fill="currentColor"/>
            <circle cx="10" cy="80" r="1.5" fill="currentColor"/>
            <circle cx="10" cy="90" r="1.5" fill="currentColor"/>
            <circle cx="20" cy="20" r="1.5" fill="currentColor"/>
            <circle cx="30" cy="30" r="1.5" fill="currentColor"/>
        </svg>
    `,

    // Klingon-inspired designs
    klingonD: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 10 30 C 20 20, 30 0, 50 0 L 100 0 L 100 15 L 60 15 C 40 15, 20 30, 15 40 L 15 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>
        </svg>
    `,

    klingonT: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 30 L 15 15 L 30 0 L 100 0 L 100 15 L 45 15 L 30 30 L 15 45 L 15 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M 30 15 L 50 30" fill="none" stroke="currentColor" stroke-width="1.5"/>
        </svg>
    `,

    klingonS: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 20 20 L 40 0 L 100 0 L 100 15 L 50 15 L 35 30 C 25 40, 20 45, 15 55 L 15 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M 35 15 C 45 25, 40 35, 25 40" fill="none" stroke="currentColor" stroke-width="1.5"/>
        </svg>
    `,

    klingon4: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 40 0 L 100 0 L 100 15 L 50 15 L 15 50 L 15 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M 30 15 L 15 30" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M 50 15 L 30 35" fill="none" stroke="currentColor" stroke-width="1.5"/>
        </svg>
    `,

    klingonNg: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 50 C 0 30, 15 15, 30 0 L 100 0 L 100 15 L 40 15 C 25 25, 15 35, 15 50 L 15 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M 40 15 C 45 25, 35 35, 25 30" fill="none" stroke="currentColor" stroke-width="1.5"/>
        </svg>
    `,

    klingonTlh: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 20 20 L 40 0 L 100 0 L 100 15 L 45 15 L 30 30 L 15 45 L 15 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M 30 15 L 40 40 L 20 30" fill="none" stroke="currentColor" stroke-width="1.5"/>
        </svg>
    `,

    // New sci-fi designs
    neonGrid: `
        <svg viewBox="0 0 100 100">
            <defs>
                <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="1.5" result="blur"/>
                    <feMerge>
                        <feMergeNode in="blur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <path d="M 0 40 L 40 0 L 100 0 L 100 10 L 45 10 L 10 45 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1" filter="url(#glow)"/>
            <path d="M 10 10 H 30 V 30 H 10 Z" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.7"/>
            <path d="M 15 15 H 25 V 25 H 15 Z" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.4"/>
        </svg>
    `,

    quantumFlux: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 Q 20 20, 40 0 L 100 0 L 100 10 Q 60 30, 10 45 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
            <path d="M 0 35 Q 15 25, 35 10" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.6"/>
            <path d="M 45 10 Q 60 20, 90 10" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.6"/>
        </svg>
    `,

    hexTech: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 40 0 L 100 0 L 100 10 L 45 10 L 10 45 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
            <path d="M 10 10 L 20 5 L 30 10 L 30 20 L 20 25 L 10 20 Z" fill="none" stroke="currentColor" stroke-width="0.5"/>
            <circle cx="20" cy="15" r="2" fill="currentColor" opacity="0.8"/>
        </svg>
    `,

    orbitalRing: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 C 10 20, 30 0, 50 0 L 100 0 L 100 10 C 70 10, 30 30, 10 50 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
            <path d="M 20 20 C 30 10, 40 10, 50 20" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.5"/>
            <circle cx="35" cy="15" r="1" fill="currentColor"/>
        </svg>
    `,

    pulseWave: `
        <svg viewBox="0 0 100 100">
            <path d="M 0 40 L 40 0 L 100 0 L 100 10 L 45 10 L 10 45 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1"/>
            <path d="M 10 35 L 20 25 L 30 35 L 40 25" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.7"/>
            <path d="M 50 10 L 60 20 L 70 10" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.5"/>
        </svg>
    `,

    glowCircuit: `
        <svg viewBox="0 0 100 100">
            <defs>
                <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="1.5" result="blur"/>
                    <feMerge>
                        <feMergeNode in="blur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <path d="M 0 40 L 40 0 L 100 0 L 100 10 L 45 10 L 10 45 L 10 100 L 0 100 Z" fill="none" stroke="currentColor" stroke-width="1" filter="url(#glow)"/>
            <path d="M 0 45 L 35 10 M 45 10 L 95 10" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.5"/>
            <circle cx="40" cy="10" r="2" fill="currentColor" filter="url(#glow)"/>
        </svg>
    `
};

/**
 * Corner Utility functions for theme integration
 */
window.CornerUtils = {
    /**
     * Initialize corners with a specified design
     * @param {string} designName - Name of the corner design to use
     */
    initializeCorners(designName = 'classic') {
        console.log(`CornerUtils: Initializing corners with design: ${designName}`);

        // Get the requested corner design or fallback to classic
        const cornerSvgHtml = window.CornerDesigns[designName] || window.CornerDesigns.classic;

        // Add appropriate SVG to all corner elements
        const cornerElements = document.querySelectorAll('.hud-corner');
cornerElements.forEach(corner => {
    corner.innerHTML = cornerSvgHtml;
});

        console.log(`CornerUtils: Initialized ${cornerElements.length} corner elements`);
    },

    /**
     * Map theme names to corner designs
     * @param {string} themeName - Name of the theme to get corner design for
     * @returns {string} - Name of the corner design for this theme
     */
    getCornerDesignForTheme(themeName) {
        // Map themes to corner designs
const themeCornerMap = {
    'cyber': 'hexTech',             // Futuristic, neon-glow tech
    'crt-amber': 'neonGrid',            // Vintage CRT with grid details
    'crt-green': 'pulseWave',           // Green phosphor flicker + waveform
    'doom': 'klingonTlh',               // Aggressive, angular battle aesthetic
    'forest-green': 'klingonD',         // Harsh but nature-inspired tones
    'dark': 'minimalist',               // Clean, no distractions
    'light': 'rounded',                 // Soft and smooth edges
    'borland-light': 'glowCircuit',         // Nerdy and retro, but high detail
    'solarized-dark': 'klingonS',       // Subtle brutality with contrast
    'solarized-light': 'klingon4',      // Technical and symmetrical
    'nord': 'orbitalRing',              // Cool and minimal, celestial
    'gruvbox-dark': 'pixel',            // Pixelated retro command-line
    'klingon': 'klingonTlh',            // Default Klingon mode
    'neon': 'glowCircuit',              // Electric circuit path aesthetic
    'quantum': 'quantumFlux'            // Sci-fi, waveform complexity
};

        return themeCornerMap[themeName] || 'classic';
    },

    /**
     * Integration with ThemeUtils
     * Call this to add corner functionality to ThemeUtils
     */
    integrateWithThemeUtils() {
        if (window.ThemeUtils) {
            console.log('CornerUtils: Integrating with ThemeUtils');

            // Store the original applyTheme method
            const originalApplyTheme = window.ThemeUtils.applyTheme;

            // Replace with corner-aware version
            window.ThemeUtils.applyTheme = function(themeName) {
                // Call the original theme application first
                originalApplyTheme.call(window.ThemeUtils, themeName);

                // Then update corners based on the theme
                const cornerDesign = window.CornerUtils.getCornerDesignForTheme(themeName);
                window.CornerUtils.initializeCorners(cornerDesign);
            };

            // Add initialization to ThemeUtils.init
            const originalInit = window.ThemeUtils.init;
            window.ThemeUtils.init = function() {
                // Call original initialization
                originalInit.call(window.ThemeUtils);

                // Initialize corners based on current theme
                const currentTheme = window.ThemeUtils.getCurrentTheme();
                const cornerDesign = window.CornerUtils.getCornerDesignForTheme(currentTheme);
                window.CornerUtils.initializeCorners(cornerDesign);
            };

            console.log('CornerUtils: Successfully integrated with ThemeUtils');
        } else {
            console.warn('CornerUtils: ThemeUtils not found, integration skipped');
        }
    }
};

// Auto-initialize on page load if ThemeUtils exists
document.addEventListener('DOMContentLoaded', function() {
    if (window.ThemeUtils) {
        window.CornerUtils.integrateWithThemeUtils();
    } else {
        // Standalone initialization if ThemeUtils doesn't exist
        window.CornerUtils.initializeCorners('classic');
    }
});

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CornerDesigns: window.CornerDesigns,
        CornerUtils: window.CornerUtils
    };
}