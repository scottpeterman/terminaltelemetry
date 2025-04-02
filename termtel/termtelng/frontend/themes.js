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
    'doom': {
    '--text-primary': '#FF7700',
    '--text-secondary': '#AA5500',
    '--accent-color': '#FF0000',
    '--bg-primary': '#000000',
    '--bg-secondary': '#3A0000',
    '--border-color': '#880000',
    '--grid-color': 'rgba(136, 0, 0, 0.3)',
    '--scrollbar-track': 'rgba(58, 0, 0, 0.8)',
    '--scrollbar-thumb': '#880000',
    '--scrollbar-thumb-hover': '#AA0000'
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
},
'solarized-dark': {
    '--text-primary': '#93a1a1',      // base1
    '--text-secondary': '#586e75',    // base01
    '--accent-color': '#268bd2',      // blue
    '--bg-primary': '#002b36',        // base03
    '--bg-secondary': '#073642',      // base02
    '--border-color': '#268bd2',      // blue
    '--grid-color': 'rgba(38, 139, 210, 0.1)',
    '--scrollbar-track': 'rgba(147, 161, 161, 0.1)',
    '--scrollbar-thumb': 'rgba(147, 161, 161, 0.3)',
    '--scrollbar-thumb-hover': 'rgba(147, 161, 161, 0.5)'
},

// Solarized Light theme
'solarized-light': {
    '--text-primary': '#586e75',      // base01
    '--text-secondary': '#93a1a1',    // base1
    '--accent-color': '#268bd2',      // blue
    '--bg-primary': '#fdf6e3',        // base3
    '--bg-secondary': '#eee8d5',      // base2
    '--border-color': '#268bd2',      // blue
    '--grid-color': 'rgba(38, 139, 210, 0.1)',
    '--scrollbar-track': 'rgba(88, 110, 117, 0.1)',
    '--scrollbar-thumb': 'rgba(88, 110, 117, 0.3)',
    '--scrollbar-thumb-hover': 'rgba(88, 110, 117, 0.5)'
},
'nord': {
    '--text-primary': '#D8DEE9',
    '--text-secondary': '#81A1C1',
    '--accent-color': '#88C0D0',
    '--bg-primary': '#2E3440',
    '--bg-secondary': '#3B4252',
    '--border-color': '#88C0D0',
    '--grid-color': 'rgba(136, 192, 208, 0.1)',
    '--scrollbar-track': 'rgba(216, 222, 233, 0.1)',
    '--scrollbar-thumb': 'rgba(216, 222, 233, 0.3)',
    '--scrollbar-thumb-hover': 'rgba(216, 222, 233, 0.5)'
},
'gruvbox-dark': {
    '--text-primary': '#EBDBB2',      // Light0/Fg
    '--text-secondary': '#928374',    // Gray
    '--accent-color': '#B8BB26',      // Bright Green
    '--bg-primary': '#282828',        // Dark0/Bg
    '--bg-secondary': '#3C3836',      // Dark1
    '--border-color': '#B8BB26',      // Bright Green
    '--grid-color': 'rgba(184, 187, 38, 0.1)',
    '--scrollbar-track': 'rgba(235, 219, 178, 0.1)',
    '--scrollbar-thumb': 'rgba(235, 219, 178, 0.3)',
    '--scrollbar-thumb-hover': 'rgba(235, 219, 178, 0.5)'
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
    'doom': {
    foreground: '#FF7700',
    background: '#000000',
    cursor: '#FF0000',
    cursorAccent: '#000000',
    selection: '#550000',
    black: '#000000',
    red: '#AA0000',
    green: '#AA5500',
    yellow: '#FF7700',
    blue: '#550000',
    magenta: '#FF0000',
    cyan: '#FFAA00',
    white: '#FFCC00',
    brightBlack: '#3A0000',
    brightRed: '#FF3333',
    brightGreen: '#DD7700',
    brightYellow: '#FFAA55',
    brightBlue: '#880000',
    brightMagenta: '#FF5555',
    brightCyan: '#FFCC77',
    brightWhite: '#FFDDAA'
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
},'solarized-dark': {
        foreground: '#93a1a1',
        background: '#002b36',
        cursor: '#93a1a1',
        cursorAccent: '#002b36',
        selection: 'rgba(147, 161, 161, 0.3)',
        black: '#073642',
        red: '#dc322f',
        green: '#859900',
        yellow: '#b58900',
        blue: '#268bd2',
        magenta: '#d33682',
        cyan: '#2aa198',
        white: '#eee8d5',
        brightBlack: '#002b36',
        brightRed: '#cb4b16',
        brightGreen: '#586e75',
        brightYellow: '#657b83',
        brightBlue: '#839496',
        brightMagenta: '#6c71c4',
        brightCyan: '#93a1a1',
        brightWhite: '#fdf6e3'
    },
    'solarized-light': {
        foreground: '#586e75',
        background: '#fdf6e3',
        cursor: '#586e75',
        cursorAccent: '#fdf6e3',
        selection: 'rgba(88, 110, 117, 0.3)',
        black: '#eee8d5',
        red: '#dc322f',
        green: '#859900',
        yellow: '#b58900',
        blue: '#268bd2',
        magenta: '#d33682',
        cyan: '#2aa198',
        white: '#073642',
        brightBlack: '#93a1a1',
        brightRed: '#cb4b16',
        brightGreen: '#586e75',
        brightYellow: '#657b83',
        brightBlue: '#839496',
        brightMagenta: '#6c71c4',
        brightCyan: '#002b36',
        brightWhite: '#002b36'
    },
    'nord': {
        foreground: '#D8DEE9',
        background: '#2E3440',
        cursor: '#D8DEE9',
        cursorAccent: '#2E3440',
        selection: 'rgba(216, 222, 233, 0.3)',
        black: '#3B4252',
        red: '#BF616A',
        green: '#A3BE8C',
        yellow: '#EBCB8B',
        blue: '#81A1C1',
        magenta: '#B48EAD',
        cyan: '#88C0D0',
        white: '#E5E9F0',
        brightBlack: '#4C566A',
        brightRed: '#BF616A',
        brightGreen: '#A3BE8C',
        brightYellow: '#EBCB8B',
        brightBlue: '#81A1C1',
        brightMagenta: '#B48EAD',
        brightCyan: '#8FBCBB',
        brightWhite: '#ECEFF4'
    },
    'gruvbox-dark': {
    foreground: '#EBDBB2',
    background: '#282828',
    cursor: '#EBDBB2',
    cursorAccent: '#282828',
    selection: 'rgba(235, 219, 178, 0.3)',
    black: '#282828',       // dark0
    red: '#CC241D',        // red
    green: '#98971A',      // green
    yellow: '#D79921',     // yellow
    blue: '#458588',       // blue
    magenta: '#B16286',    // purple
    cyan: '#689D6A',       // aqua
    white: '#A89984',      // gray
    brightBlack: '#928374', // gray
    brightRed: '#FB4934',   // bright red
    brightGreen: '#B8BB26', // bright green
    brightYellow: '#FABD2F',// bright yellow
    brightBlue: '#83A598',  // bright blue
    brightMagenta: '#D3869B',// bright purple
    brightCyan: '#8EC07C',  // bright aqua
    brightWhite: '#EBDBB2'  // light0
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
    'doom': `
    .interface-row { border-bottom: 1px solid rgba(136, 0, 0, 0.3); }
    .interface-name { color: #FF7700; }
    .interface-status.up { color: #AA5500; }
    .interface-status.down { color: #FF0000; }
    .tabs .tab { border-color: #880000; }
    .tabs .tab.active { background: rgba(255, 0, 0, 0.2); }
    .tabs .tab:hover { background: rgba(255, 0, 0, 0.3); }
    .button-group button { background: #3A0000; border-color: #880000; }
    .button-group button:hover { background: #550000; }
    .button-group button:active { background: #880000; }
    .scrollable-region { background-color: rgba(33, 0, 0, 0.95); border-color: #880000; }
    .hud-panel-title { color: #AA5500; }
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
`,
'solarized-dark': `
        .interface-row { border-bottom: 1px solid rgba(147, 161, 161, 0.2); }
        .interface-name { color: #93a1a1; }
        .interface-status.up { color: #859900; }
        .interface-status.down { color: #dc322f; }
        .tabs .tab { border-color: #268bd2; }
        .tabs .tab.active { background: rgba(38, 139, 210, 0.1); }
    `,
    'solarized-light': `
        .interface-row { border-bottom: 1px solid rgba(88, 110, 117, 0.2); }
        .interface-name { color: #586e75; }
        .interface-status.up { color: #859900; }
        .interface-status.down { color: #dc322f; }
        .tabs .tab { border-color: #268bd2; }
        .tabs .tab.active { background: rgba(38, 139, 210, 0.1); }
    `,
    'nord': `
        .interface-row { border-bottom: 1px solid rgba(216, 222, 233, 0.2); }
        .interface-name { color: #D8DEE9; }
        .interface-status.up { color: #A3BE8C; }
        .interface-status.down { color: #BF616A; }
        .tabs .tab { border-color: #88C0D0; }
        .tabs .tab.active { background: rgba(136, 192, 208, 0.1); }
    `,'gruvbox-dark': `
    .interface-row { border-bottom: 1px solid rgba(235, 219, 178, 0.2); }
    .interface-name { color: #EBDBB2; }
    .interface-status.up { color: #B8BB26; }     // bright green
    .interface-status.down { color: #FB4934; }   // bright red
    .tabs .tab { border-color: #B8BB26; }
    .tabs .tab.active { background: rgba(184, 187, 38, 0.1); }
    .tabs .tab:hover { background: rgba(184, 187, 38, 0.2); }
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

// ThemeUtils: A utility for managing themes in the application
window.ThemeUtils = {
    // Theme stylesheet element
    styleElement: null,
    // The current theme
    currentTheme: 'cyber',

    // Initialize the theme system
    init: function() {
        console.log('Initializing ThemeUtils');

        // Create a style element for dynamic theme styles
        this.styleElement = document.createElement('style');
        this.styleElement.id = 'theme-styles';
        document.head.appendChild(this.styleElement);

        // Load the theme from localStorage if available
        const savedTheme = localStorage.getItem('telemetry-theme');
        if (savedTheme && window.THEME_COLORS[savedTheme]) {
            this.currentTheme = savedTheme;
        }

        // Apply the theme
        this.applyTheme(this.currentTheme);

        // Set up the theme selector
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            // Set the select to the current theme
            themeSelect.value = this.currentTheme;

            // Add event listener for theme changes
            themeSelect.addEventListener('change', (e) => {
                this.applyTheme(e.target.value);
            });

            console.log('Theme selector initialized with theme:', this.currentTheme);
        } else {
            console.error('Theme selector element not found');
        }
    },

    // Apply a theme by name
    applyTheme: function(themeName) {
        console.log('Applying theme:', themeName);

        if (!window.THEME_COLORS[themeName]) {
            console.error('Theme not found:', themeName);
            return;
        }

        // Store the current theme
        this.currentTheme = themeName;
        localStorage.setItem('telemetry-theme', themeName);

        // Get the colors for this theme
        const colors = window.THEME_COLORS[themeName];
        console.log(colors);

        // Update CSS variables
        const root = document.documentElement;
        for (const [key, value] of Object.entries(colors)) {
            root.style.setProperty(key, value);
        }

        // Generate and apply scrollbar style based on theme colors
        const scrollbarStyle = this.generateScrollbarStyles(colors);

        // Apply theme styles including scrollbar styles
        this.styleElement.textContent = (window.THEME_STYLES[themeName] || '') + scrollbarStyle;

        // Explicitly set the HUD panel backgrounds to the secondary background color
        const hudPanelBackgrounds = document.querySelectorAll('.hud-panel-background');
        const hudPanelContents = document.querySelectorAll('.hud-panel-content');
        const scrollableRegions = document.querySelectorAll('.scrollable-region');
        const secondaryBgColor = colors['--bg-secondary'];
        const primaryBgColor = colors['--bg-primary'];

        // Apply secondary background to panel backgrounds
        hudPanelBackgrounds.forEach(panel => {
            panel.style.backgroundColor = secondaryBgColor;
        });

        // Apply primary background to panel contents
        hudPanelContents.forEach(content => {
            content.style.backgroundColor = primaryBgColor;
        });

        // Apply secondary background to scrollable regions
        scrollableRegions.forEach(region => {
            region.style.backgroundColor = secondaryBgColor;
        });

        // Update terminal theme if applicable
        if (window.terminalInstance && window.TERMINAL_THEMES[themeName]) {
            window.terminalInstance.setOption('theme', window.TERMINAL_THEMES[themeName]);
        }

        // Dispatch a theme changed event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: themeName }
        }));

        console.log('Theme applied:', themeName);
    },

    // Generate WebKit scrollbar styles based on theme colors
    generateScrollbarStyles: function(colors) {
        // Extract color values for scrollbar styling
        const thumbColor = colors['--border-color'] || '#ff0000';
        const trackColor = colors['--bg-secondary'] || '#000000';
        const hoverColor = colors['--accent-secondary'] || '#ff6600';

        return `
            /* WebKit scrollbar styling */
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }

            ::-webkit-scrollbar-track {
                background: ${trackColor};
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb {
                background: ${thumbColor};
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: ${hoverColor};
            }

            ::-webkit-scrollbar-corner {
                background: ${trackColor};
            }

            /* Ensures consistent scrollbar styling in all scrollable elements */
            .scrollable-region, .hud-panel-content {
                scrollbar-width: thin;
                scrollbar-color: ${thumbColor} ${trackColor};
            }
        `;
    },

    // Get the current theme name
    getCurrentTheme: function() {
        return this.currentTheme;
    }
};

// Initialize the theme system when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    window.ThemeUtils.init();
});