class ThemeManager {
   constructor() {
       if (window.themeManager) {
           return window.themeManager;
       }
       window.themeManager = this;

       console.log('ThemeManager: Initializing...');
       this.styleElement = document.createElement('style');
       document.head.appendChild(this.styleElement);
       this.initialized = false;

       // Initialize immediately if possible
       this.initialize();

       // Connect to the WebChannel
       this.connectToBackend();
   }

   connectToBackend() {
       console.log('ThemeManager: Connecting to backend...');

       initializeSharedWebChannel((channel) => {
           console.log('ThemeManager: WebChannel initialized');
           if (channel.objects.messageBridge?.system_message) {
               // Set up message handler
               channel.objects.messageBridge.system_message.connect(this.handleSystemMessage.bind(this));
               console.log('ThemeManager: Connected to message bridge');

               // Request saved theme
               const initMessage = JSON.stringify({
                   target: "system",
                   type: "theme_manager_ready",
                   payload: null
               });
               channel.objects.messageBridge.handle_message(initMessage);
           } else {
               console.warn('ThemeManager: Message bridge not available in channel');
           }
       });
   }

   handleSystemMessage(target, type, payload) {
       console.log('ThemeManager: Received system message:', { target, type, payload });
       if (target === 'system' && type === 'theme') {
           console.log('ThemeManager: Processing theme change request');
           this.applyTheme(payload, true);
           // Update select element if it exists
           const themeSelect = document.getElementById('theme-select');
           if (themeSelect && themeSelect.value !== payload) {
               themeSelect.value = payload;
           }
       } else {
           console.log('ThemeManager: Ignoring non-theme message:', { target, type });
       }
   }

   initialize() {
       if (this.initialized) {
           console.warn('ThemeManager: Already initialized!');
           return;
       }

       console.log('ThemeManager: Starting initialization');

       // Verify theme constants are available
       if (!window.THEME_STYLES || !window.TERMINAL_THEMES || !window.THEME_COLORS) {
           console.error('ThemeManager: Theme constants are not loaded!', {
               styles: !!window.THEME_STYLES,
               terminal: !!window.TERMINAL_THEMES,
               colors: !!window.THEME_COLORS
           });
           return;
       }

       // Set up theme selector
       const themeSelect = document.getElementById('theme-select');
       if (themeSelect) {
           console.log('ThemeManager: Found theme selector');

           // Remove any existing listeners before adding new one
           const newListener = (e) => {
               console.log('ThemeManager: Theme selection changed to:', e.target.value);
               this.applyTheme(e.target.value, false);
           };
           themeSelect.removeEventListener('change', newListener);
           themeSelect.addEventListener('change', newListener);
       } else {
           console.error('ThemeManager: Theme selector element not found!');
       }

       this.initialized = true;
       console.log('ThemeManager: Initialization complete');
   }

applyTheme(themeName, fromBackend = false) {{
    console.log('ThemeManager: Applying theme:', themeName, 'from backend:', fromBackend);

    // Validate required global objects
    if (!window.THEME_STYLES || !window.TERMINAL_THEMES) {{
        console.error('ThemeManager: Theme constants are missing.');
        return;
    }}

    // Apply CSS theme styles
    this.styleElement.textContent = THEME_STYLES[themeName];

    // Get terminal theme and selection colors
    const terminalTheme = window.TERMINAL_THEMES[themeName]?.theme || {{}};
    const selectionBg = terminalTheme.selection || '#504945';
    const selectionFg = terminalTheme.selectionForeground || '#EBDBB2';

    // Apply terminal theme with selection colors
    this.applyTerminalTheme(terminalTheme, selectionBg, selectionFg);

    // Apply CSS variables for the theme
    this.applyThemeColors(themeName, selectionBg, selectionFg);

    // Apply selection styles directly to improve compatibility
    this.applySelectionStyles(selectionBg, selectionFg);

    // Update scrollbar and dynamic elements
    this.updateScrollbarStyles(themeName);
    this.updateDynamicElements();

    // Handle backend communication
    this.handleBackendCommunication(themeName, fromBackend);

    // Save preference and dispatch event
    localStorage.setItem('preferredTheme', themeName);
    window.dispatchEvent(new CustomEvent('themeChanged', {{ detail: {{ theme: themeName }} }}));
}}

// Helper method for applying selection styles directly
applySelectionStyles(bg, fg) {{
    if (!window.term) {{
        console.warn('ThemeManager: Cannot apply selection styles - terminal not initialized');
        return;
    }}

    try {{
        // Get current theme
        const currentTheme = window.term.getOption('theme') || {{}};

        // Create updated theme with selection colors
        const updatedTheme = {{
            ...currentTheme,
            selection: bg,
            selectionBackground: bg, // For compatibility with newer xterm.js versions
            selectionForeground: fg
        }};

        // Apply updated theme
        window.term.setOption('theme', updatedTheme);

        // Also apply as CSS variables for other UI elements
        document.documentElement.style.setProperty('--selection-background', bg);
        document.documentElement.style.setProperty('--selection-text', fg);

        console.log('ThemeManager: Applied selection styles successfully:', {{
            background: bg,
            text: fg
        }});
    }} catch (error) {{
        console.error('ThemeManager: Error applying selection styles:', error);
    }}
}}


   updateScrollbarStyles(themeName) {
       const theme = window.THEME_COLORS[themeName];
       if (!theme) return;

       const style = document.getElementById('scrollbar-style') || document.createElement('style');
       style.id = 'scrollbar-style';
       style.textContent = `
           ::-webkit-scrollbar {
               width: 8px;
               height: 8px;
           }
           ::-webkit-scrollbar-track {
               background: var(--scrollbar-track, var(--scrollbar-bg));
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

   updateDynamicElements() {
       document.querySelectorAll('.hud-panel-title').forEach((el) => {
           el.style.color = 'var(--text-secondary, var(--text))';
           el.style.background = 'var(--bg-primary, var(--background))';
       });

       document.querySelectorAll('.hud-panel::before').forEach((el) => {
           el.style.background = 'var(--bg-secondary, var(--secondary))';
           el.style.border = '1px solid var(--border-color, var(--border))';
       });

       document.querySelectorAll('.tab').forEach((el) => {
           el.style.color = 'var(--text-primary, var(--text))';
       });

       document.querySelectorAll('.tab.active').forEach((el) => {
           el.style.color = 'var(--accent-color, var(--success))';
           el.style.borderBottom = '2px solid var(--accent-color, var(--success))';
       });

       document.querySelectorAll('.chart-grid').forEach((el) => {
           el.style.backgroundImage = `
               linear-gradient(var(--grid-color, var(--grid)) 1px, transparent 1px),
               linear-gradient(90deg, var(--grid-color, var(--grid)) 1px, transparent 1px)
           `;
       });
   }

   getCurrentTheme() {
       return localStorage.getItem('preferredTheme') || 'cyber';
   }

   getTerminalTheme() {
       const theme = this.getCurrentTheme();
       console.log('ThemeManager: Getting terminal theme for:', theme);
       return TERMINAL_THEMES[theme];
   }
}

// Only create an instance if one doesn't exist
if (!window.themeManager) {
   new ThemeManager();
}

// Export the ThemeManager class (not instance) for module systems
if (typeof module !== 'undefined' && module.exports) {
   module.exports = ThemeManager;
}