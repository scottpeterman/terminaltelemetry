// Theme definitions and management system
window.THEME_COLORS = {
    'cyber': {
        '--text-primary': '#22D3EE',
        '--text-secondary': '#0EA5E9',
        '--accent-color': '#22D3EE',
        '--bg-primary': '#000000',
        '--bg-secondary': '#000000',
        '--border-color': '#22D3EE',
        '--grid-color': 'rgba(34, 211, 238, 0.1)',
        '--scrollbar-track': 'rgba(34, 211, 238, 0.1)',
        '--scrollbar-thumb': 'rgba(34, 211, 238, 0.3)',
        '--scrollbar-thumb-hover': 'rgba(34, 211, 238, 0.5)'
    },
    'crt-amber': {
        '--text-primary': '#FFB000',
        '--text-secondary': '#CC8800',
        '--accent-color': '#FFB000',
        '--bg-primary': '#000000',
        '--bg-secondary': '#000000',
        '--border-color': '#FFB000',
        '--grid-color': 'rgba(255, 176, 0, 0.1)',
        '--scrollbar-track': 'rgba(255, 176, 0, 0.1)',
        '--scrollbar-thumb': 'rgba(255, 176, 0, 0.3)',
        '--scrollbar-thumb-hover': 'rgba(255, 176, 0, 0.5)'
    },
    'crt-green': {
        '--text-primary': '#00FF00',
        '--text-secondary': '#00CC00',
        '--accent-color': '#00FF00',
        '--bg-primary': '#000000',
        '--bg-secondary': '#000000',
        '--border-color': '#00FF00',
        '--grid-color': 'rgba(0, 255, 0, 0.1)',
        '--scrollbar-track': 'rgba(0, 255, 0, 0.1)',
        '--scrollbar-thumb': 'rgba(0, 255, 0, 0.3)',
        '--scrollbar-thumb-hover': 'rgba(0, 255, 0, 0.5)'
    },
    'forest-green': {
        '--text-primary': '#4CAF50',
        '--text-secondary': '#388E3C',
        '--accent-color': '#4CAF50',
        '--bg-primary': '#000000',
        '--bg-secondary': '#000000',
        '--border-color': '#4CAF50',
        '--grid-color': 'rgba(76, 175, 80, 0.1)',
        '--scrollbar-track': 'rgba(76, 175, 80, 0.1)',
        '--scrollbar-thumb': 'rgba(76, 175, 80, 0.3)',
        '--scrollbar-thumb-hover': 'rgba(76, 175, 80, 0.5)'
    },
    'dark': {
        '--text-primary': '#E2E8F0',
        '--text-secondary': '#94A3B8',
        '--accent-color': '#3B82F6',
        '--bg-primary': '#000000',
        '--bg-secondary': '#000000',
        '--border-color': '#3B82F6',
        '--grid-color': 'rgba(59, 130, 246, 0.1)',
        '--scrollbar-track': 'rgba(226, 232, 240, 0.1)',
        '--scrollbar-thumb': 'rgba(226, 232, 240, 0.3)',
        '--scrollbar-thumb-hover': 'rgba(226, 232, 240, 0.5)'
    },
    'light': {
        '--text-primary': '#0F172A',
        '--text-secondary': '#475569',
        '--accent-color': '#3B82F6',
        '--bg-primary': '#F8FAFC',
        '--bg-secondary': '#F1F5F9',
        '--border-color': '#3B82F6',
        '--grid-color': 'rgba(59, 130, 246, 0.1)',
        '--scrollbar-track': 'rgba(15, 23, 42, 0.1)',
        '--scrollbar-thumb': 'rgba(15, 23, 42, 0.3)',
        '--scrollbar-thumb-hover': 'rgba(15, 23, 42, 0.5)'
    },
    'borland-light': {
    '--text-primary': '#FFFFFF',      // White text for primary - classic Borland
    '--text-secondary': '#FFFF55',    // Yellow for secondary text
    '--accent-color': '#FFFF55',      // Yellow for accents - classic Borland highlight
    '--bg-primary': '#0000AA',        // The exact classic Borland blue
    '--bg-secondary': '#0000AA',      // Keep consistent with primary for authentic look
    '--border-color': '#FFFFFF',      // White borders
    '--grid-color': 'rgba(255, 255, 255, 0.1)',
    '--scrollbar-track': 'rgba(255, 255, 255, 0.1)',
    '--scrollbar-thumb': 'rgba(255, 255, 255, 0.3)',
    '--scrollbar-thumb-hover': 'rgba(255, 255, 255, 0.5)'
}
};

// Terminal theme configurations
window.TERMINAL_THEMES = {
    'cyber': {
        foreground: '#22D3EE',
        background: '#000000',
        cursor: '#22D3EE',
        cursorAccent: '#0F172A',
        selection: 'rgba(34, 211, 238, 0.3)',
        black: '#1E293B',
        red: '#EF4444',
        green: '#22C55E',
        yellow: '#EAB308',
        blue: '#3B82F6',
        magenta: '#D946EF',
        cyan: '#06B6D4',
        white: '#F1F5F9',
        brightBlack: '#475569',
        brightRed: '#FCA5A5',
        brightGreen: '#86EFAC',
        brightYellow: '#FDE047',
        brightBlue: '#93C5FD',
        brightMagenta: '#F5D0FE',
        brightCyan: '#67E8F9',
        brightWhite: '#F8FAFC'
    },
    'crt-amber': {
        foreground: '#FFB000',
        background: '#000000',
        cursor: '#FFB000',
        cursorAccent: '#0D0D00',
        selection: 'rgba(255, 176, 0, 0.3)',
        black: '#1A1A00',
        red: '#CC8800',
        green: '#FFAA00',
        yellow: '#FFB000',
        blue: '#CC8800',
        magenta: '#CC8800',
        cyan: '#FFAA00',
        white: '#FFB000',
        brightBlack: '#997700',
        brightRed: '#FFB000',
        brightGreen: '#FFCC00',
        brightYellow: '#FFE000',
        brightBlue: '#FFB000',
        brightMagenta: '#FFB000',
        brightCyan: '#FFCC00',
        brightWhite: '#FFE000'
    },
    'crt-green': {
        foreground: '#00FF00',
        background: '#001100',
        cursor: '#00FF00',
        cursorAccent: '#001100',
        selection: 'rgba(0, 255, 0, 0.3)',
        black: '#002200',
        red: '#00CC00',
        green: '#00FF00',
        yellow: '#00FF00',
        blue: '#00CC00',
        magenta: '#00CC00',
        cyan: '#00FF00',
        white: '#00FF00',
        brightBlack: '#009900',
        brightRed: '#00FF00',
        brightGreen: '#33FF33',
        brightYellow: '#66FF66',
        brightBlue: '#00FF00',
        brightMagenta: '#00FF00',
        brightCyan: '#33FF33',
        brightWhite: '#66FF66'
    },
    'forest-green': {
        foreground: '#4CAF50',
        background: '#1B2819',
        cursor: '#4CAF50',
        cursorAccent: '#1B2819',
        selection: 'rgba(76, 175, 80, 0.3)',
        black: '#2E3B2B',
        red: '#FF5252',
        green: '#4CAF50',
        yellow: '#FFC107',
        blue: '#2196F3',
        magenta: '#9C27B0',
        cyan: '#009688',
        white: '#E8F5E9',
        brightBlack: '#388E3C',
        brightRed: '#FF8A80',
        brightGreen: '#69F0AE',
        brightYellow: '#FFE57F',
        brightBlue: '#64B5F6',
        brightMagenta: '#CE93D8',
        brightCyan: '#80CBC4',
        brightWhite: '#F1F8E9'
    },
    'dark': {
        foreground: '#E2E8F0',
        background: '#0F172A',
        cursor: '#E2E8F0',
        cursorAccent: '#0F172A',
        selection: 'rgba(226, 232, 240, 0.3)',
        black: '#1E293B',
        red: '#EF4444',
        green: '#22C55E',
        yellow: '#EAB308',
        blue: '#3B82F6',
        magenta: '#D946EF',
        cyan: '#06B6D4',
        white: '#F1F5F9',
        brightBlack: '#475569',
        brightRed: '#FCA5A5',
        brightGreen: '#86EFAC',
        brightYellow: '#FDE047',
        brightBlue: '#93C5FD',
        brightMagenta: '#F5D0FE',
        brightCyan: '#67E8F9',
        brightWhite: '#F8FAFC'
    },
    'light': {
        foreground: '#0F172A',
        background: '#F8FAFC',
        cursor: '#0F172A',
        cursorAccent: '#F8FAFC',
        selection: 'rgba(15, 23, 42, 0.3)',
        black: '#F1F5F9',
        red: '#DC2626',
        green: '#16A34A',
        yellow: '#CA8A04',
        blue: '#2563EB',
        magenta: '#C026D3',
        cyan: '#0891B2',
        white: '#0F172A',
        brightBlack: '#94A3B8',
        brightRed: '#EF4444',
        brightGreen: '#22C55E',
        brightYellow: '#EAB308',
        brightBlue: '#3B82F6',
        brightMagenta: '#D946EF',
        brightCyan: '#06B6D4',
        brightWhite: '#1E293B'
    },
    'borland-light': {
    foreground: '#FFFFFF',   // White text
    background: '#0000AA',   // Classic Borland blue
    cursor: '#FFFF55',      // Yellow cursor
    cursorAccent: '#0000AA', // Blue cursor accent
    selection: 'rgba(255, 255, 255, 0.3)',
    black: '#000000',
    red: '#FF5555',         // Bright red for errors/down status
    green: '#55FF55',       // Bright green for up status
    yellow: '#FFFF55',      // Classic Borland yellow
    blue: '#5555FF',        // Bright blue
    magenta: '#FF55FF',     // Bright magenta
    cyan: '#55FFFF',        // Bright cyan
    white: '#FFFFFF',       // White
    brightBlack: '#555555',  // Dark gray
    brightRed: '#FF5555',    // Keep consistent with normal red
    brightGreen: '#55FF55',  // Keep consistent with normal green
    brightYellow: '#FFFF55', // Keep consistent with normal yellow
    brightBlue: '#5555FF',   // Keep consistent with normal blue
    brightMagenta: '#FF55FF', // Keep consistent with normal magenta
    brightCyan: '#55FFFF',   // Keep consistent with normal cyan
    brightWhite: '#FFFFFF'   // Keep consistent with normal white
}
};

// CSS styles for each theme
window.THEME_STYLES = {
    'cyber': `
        .interface-row { border-bottom: 1px solid rgba(34, 211, 238, 0.2); }
        .interface-name { color: #22D3EE; }
        .interface-status.up { color: #22C55E; }
        .interface-status.down { color: #EF4444; }
        .tabs .tab { border-color: #22D3EE; }
        .tabs .tab.active { background: rgba(34, 211, 238, 0.1); }
    `,
    'crt-amber': `
        .interface-row { border-bottom: 1px solid rgba(255, 176, 0, 0.2); }
        .interface-name { color: #FFB000; }
        .interface-status.up { color: #FFAA00; }
        .interface-status.down { color: #CC8800; }
        .tabs .tab { border-color: #FFB000; }
        .tabs .tab.active { background: rgba(255, 176, 0, 0.1); }
    `,
    'crt-green': `
        .interface-row { border-bottom: 1px solid rgba(0, 255, 0, 0.2); }
        .interface-name { color: #00FF00; }
        .interface-status.up { color: #00FF00; }
        .interface-status.down { color: #00CC00; }
        .tabs .tab { border-color: #00FF00; }
        .tabs .tab.active { background: rgba(0, 255, 0, 0.1); }
    `,
    'forest-green': `
        .interface-row { border-bottom: 1px solid rgba(76, 175, 80, 0.2); }
        .interface-name { color: #4CAF50; }
        .interface-status.up { color: #69F0AE; }
        .interface-status.down { color: #FF5252; }
        .tabs .tab { border-color: #4CAF50; }
        .tabs .tab.active { background: rgba(76, 175, 80, 0.1); }
    `,
    'dark': `
        .interface-row { border-bottom: 1px solid rgba(226, 232, 240, 0.2); }
        .interface-name { color: #E2E8F0; }
        .interface-status.up { color: #22C55E; }
        .interface-status.down { color: #EF4444; }
        .tabs .tab { border-color: #3B82F6; }
        .tabs .tab.active { background: rgba(59, 130, 246, 0.1); }
    `,
    'light': `
        .interface-row { border-bottom: 1px solid rgba(15, 23, 42, 0.2); }
        .interface-name { color: #0F172A; }
        .interface-status.up { color: #16A34A; }
        .interface-status.down { color: #DC2626; }
        .tabs .tab { border-color: #3B82F6; }
        .tabs .tab.active { background: rgba(59, 130, 246, 0.1); }
    `,
    'borland-light': `
    .interface-row { border-bottom: 1px solid rgba(255, 255, 255, 0.2); }
    .interface-name { color: #FFFFFF; }
    .interface-status.up { color: #55FF55; }
    .interface-status.down { color: #FF5555; }
    .tabs .tab { border-color: #FFFFFF; }
    .tabs .tab.active { background: rgba(255, 255, 255, 0.1); }
    .tabs .tab:hover { background: rgba(255, 255, 255, 0.2); }
`
};

// Add global theme change event listener
window.addEventListener('themeChanged', (event) => {
    const themeName = event.detail.theme;

    // Update device icons if they exist
    if (window.DeviceIcons && typeof window.DeviceIcons.applyThemeColor === 'function') {
        window.DeviceIcons.applyThemeColor();
    }

    // Update any charts that exist
    const charts = Object.values(Chart.instances);
    charts.forEach(chart => {
        const style = getComputedStyle(document.documentElement);
        const textColor = style.getPropertyValue('--text-primary').trim();
        const gridColor = style.getPropertyValue('--grid-color').trim();
        const accentColor = style.getPropertyValue('--accent-color').trim();

        // Update chart colors
        chart.options.scales.y.grid.color = gridColor;
        chart.options.scales.y.ticks.color = textColor;
        chart.options.scales.x.grid.color = gridColor;
        chart.options.scales.x.ticks.color = textColor;
        chart.options.plugins.legend.labels.color = textColor;

        // Update dataset colors
        if (chart.data.datasets.length > 0) {
            chart.data.datasets.forEach(dataset => {
                dataset.borderColor = accentColor;
                dataset.pointBackgroundColor = accentColor;
            });
        }

        chart.update('none'); // Update without animation
    });
});

// Theme utility functions
window.ThemeUtils = {
    // Initialize theme system
    init() {
        // Set up theme from localStorage or default
        const savedTheme = localStorage.getItem('preferredTheme') || 'cyber';
        this.applyTheme(savedTheme);

        // Set up theme selector
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.value = savedTheme;
        }
    },

    // Apply a theme by name
    applyTheme(themeName) {
        if (!window.THEME_COLORS[themeName]) {
            console.warn(`Theme '${themeName}' not found, falling back to cyber`);
            themeName = 'cyber';
        }

        // Store theme preference
        localStorage.setItem('preferredTheme', themeName);

        // Apply CSS custom properties
        const colors = window.THEME_COLORS[themeName];
        Object.entries(colors).forEach(([property, value]) => {
            document.documentElement.style.setProperty(property, value);
        });

        // Apply theme styles
        const styleElement = document.getElementById('theme-styles');
        if (!styleElement) {
            const newStyle = document.createElement('style');
            newStyle.id = 'theme-styles';
            document.head.appendChild(newStyle);
        }
        const styleContent = window.THEME_STYLES[themeName] || '';
        document.getElementById('theme-styles').textContent = styleContent;

        // Update terminal theme if terminal exists
        if (window.sessionManager?.sessions?.terminal?.term) {
            const terminalTheme = window.TERMINAL_THEMES[themeName];
            if (terminalTheme) {
                window.sessionManager.sessions.terminal.term.setOption('theme', terminalTheme);
            }
        }

        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: themeName }
        }));
    },

    // Get current theme name
    getCurrentTheme() {
        return localStorage.getItem('preferredTheme') || 'cyber';
    },

    // Check if current theme is a dark theme
    isDarkTheme() {
        const currentTheme = this.getCurrentTheme();
        return !['light'].includes(currentTheme);
    },

    // Get a specific color from current theme
    getThemeColor(colorVar) {
        return getComputedStyle(document.documentElement)
            .getPropertyValue(colorVar)
            .trim();
    }
};

// Initialize theme system when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.ThemeUtils.init();
});

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        THEME_COLORS: window.THEME_COLORS,
        TERMINAL_THEMES: window.TERMINAL_THEMES,
        THEME_STYLES: window.THEME_STYLES,
        ThemeUtils: window.ThemeUtils
    };
}