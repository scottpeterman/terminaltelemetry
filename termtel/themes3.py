from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
import importlib.resources

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QFrame, QVBoxLayout


@dataclass
class ThemeColors:
    # Core colors
    primary: str
    secondary: str
    background: str
    darker_bg: str
    lighter_bg: str
    text: str
    grid: str
    line: str
    border: str
    success: str
    error: str

    # Effects
    border_light: str
    corner_gap: str
    corner_bright: str

    # Transparencies
    panel_bg: str
    scrollbar_bg: str
    selected_bg: str

    # Buttons
    button_hover: str
    button_pressed: str
    chart_bg: str

    # Terminal configuration
    terminal: Optional[Dict[str, Any]] = None

    context_menu: Optional[Dict[str, Any]] = None



    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeColors':
        # Extract terminal configuration
        terminal_config = data.pop('terminal', None)

        # Create instance with core theme fields
        theme_fields = {k: v for k, v in data.items() if k in cls.__annotations__}
        instance = cls(**theme_fields)

        # Set terminal configuration
        instance.terminal = terminal_config

        return instance

    def to_dict(self) -> Dict[str, Any]:
        result = self.__dict__.copy()
        if self.terminal is None:
            result.pop('terminal', None)
        return result

class ThemeMapper:
    """Maps application themes to terminal themes with dictionary-like behavior"""

    def __init__(self, theme_library):
        self.theme_library = theme_library
        self._default_mappings = {
            "cyberpunk": "Cyberpunk",
            "dark_mode": "Dark",
            "light_mode": "Light",
            "retro_green": "Green",
            "retro_amber": "Amber",
            "neon_blue": "Neon"
        }
        # Cache the mapping to avoid regenerating it repeatedly
        self._mapping = None

    def _generate_mapping(self):
        """Generate mapping dictionary from theme library"""
        mapping = {}

        # Get all available themes
        for theme_name in self.theme_library.get_theme_names():
            theme = self.theme_library.get_theme(theme_name)

            # Check if theme has terminal config in JSON
            if hasattr(theme, 'terminal') and theme.terminal and hasattr(theme.terminal, 'theme'):
                terminal_theme = theme.terminal.theme.get('name', self._default_mappings.get(theme_name))
                if terminal_theme:
                    mapping[theme_name] = terminal_theme
            else:
                # Fall back to default mapping
                mapping[theme_name] = self._default_mappings.get(theme_name, "Cyberpunk")

        return mapping

    @property
    def mapping(self):
        """Lazy-load and cache the mapping"""
        if self._mapping is None:
            self._mapping = self._generate_mapping()
        return self._mapping

    def get(self, key, default=None):
        """Dictionary-style get method with default value"""
        return self.mapping.get(key, default)

    def __getitem__(self, key):
        """Dictionary-style bracket access"""
        return self.mapping[key]

    def __contains__(self, key):
        """Support for 'in' operator"""
        return key in self.mapping

    def __iter__(self):
        """Support for iteration"""
        return iter(self.mapping)

    def __len__(self):
        """Support for len()"""
        return len(self.mapping)

    def items(self):
        """Support for .items() method"""
        return self.mapping.items()

    def keys(self):
        """Support for .keys() method"""
        return self.mapping.keys()

    def values(self):
        """Support for .values() method"""
        return self.mapping.values()

    def refresh(self):
        """Force regeneration of the mapping"""
        self._mapping = None
        return self.mapping

class ThemeLibrary:
    def __init__(self):
        self.themes: Dict[str, ThemeColors] = {}
        self._load_default_themes()  # Load hardcoded default theme first
        self._load_custom_themes()  # Then load any custom themes

    def _load_default_themes(self):
        """Load default built-in themes"""
        # Default cyberpunk theme
        cyberpunk = {
            "primary": "#0a8993",
            "secondary": "#065359",
            "background": "#111111",
            "darker_bg": "#1a1a1a",
            "lighter_bg": "#0ac0c8",
            "text": "#0affff",
            "grid": "#08a2a9",
            "line": "#ffff66",
            "border": "#0a8993",
            "success": "#0a8993",
            "error": "#ff4c4c",
            "border_light": "rgba(10, 255, 255, 0.5)",
            "corner_gap": "#010203",
            "corner_bright": "#0ff5ff",
            "panel_bg": "rgba(0, 0, 0, 0.95)",
            "scrollbar_bg": "rgba(6, 20, 22, 0.6)",
            "selected_bg": "rgba(10, 137, 147, 0.25)",
            "button_hover": "#08706e",
            "button_pressed": "#064d4a",
            "chart_bg": "rgba(6, 83, 89, 0.25)"
        }

        # Dark theme
        dark = {
            "primary": "#1f1f1f",
            "secondary": "#2b2b2b",
            "background": "#121212",
            "darker_bg": "#0d0d0d",
            "lighter_bg": "#eeeeee",
            "text": "#ffffff",
            "grid": "#2b2b2b",
            "line": "#3a86ff",
            "border": "#333333",
            "success": "#00e676",
            "error": "#ff1744",
            "border_light": "rgba(255, 255, 255, 0.4)",
            "corner_gap": "#121212",
            "corner_bright": "#ffffff",
            "panel_bg": "rgba(18, 18, 18, 0.98)",
            "scrollbar_bg": "rgba(33, 33, 33, 0.5)",
            "selected_bg": "rgba(255, 255, 255, 0.1)",
            "button_hover": "#333333",
            "button_pressed": "#444444",
            "chart_bg": "rgba(33, 33, 33, 0.2)"
        }

        # Add the default themes
        self.themes["cyberpunk"] = ThemeColors.from_dict(cyberpunk)
        self.themes["dark"] = ThemeColors.from_dict(dark)

    # In ThemeManager._load_custom_themes, modify to use relative path:

    def get_colors(self, theme_name: str) -> Dict[str, str]:
        """Return the color dictionary for the specified theme."""
        theme = self.get_theme(theme_name)
        if theme:
            return theme.to_dict()
        else:
            print(f"Colors for theme '{theme_name}' not found, returning default.")
            return self.get_theme("cyberpunk").to_dict()

    def get_chart_colors(self, theme_name: str) -> Dict[str, str]:
        """Alias for get_colors() for backwards compatibility."""
        return self.get_colors(theme_name)
    def _load_custom_themes(self):
        """Load custom themes from themes directory"""
        try:
            # Use relative path instead of home directory
            custom_themes_dir = Path("./themes")
            print(f"Loading themes from: {custom_themes_dir.absolute()}")

            # Create themes directory if it doesn't exist
            custom_themes_dir.mkdir(exist_ok=True)
            print("Themes directory created/verified")

            # Load all .json files from the themes directory
            if custom_themes_dir.exists():
                theme_files = list(custom_themes_dir.glob('*.json'))
                print(f"Found {len(theme_files)} theme files")

                for theme_file in custom_themes_dir.glob('*.json'):
                    try:
                        print(f"Loading theme from: {theme_file}")
                        with open(theme_file, 'r') as f:
                            theme_dict = json.load(f)
                            # Extract only the color-related fields
                            theme_colors = {k: v for k, v in theme_dict.items()
                                            if k in ThemeColors.__annotations__}
                            theme_name = theme_file.stem
                            self.themes[theme_name] = ThemeColors.from_dict(theme_colors)
                            print(f"Successfully loaded theme: {theme_name}")
                    except Exception as e:
                        print(f"Error loading theme {theme_file}: {e}")
        except Exception as e:
            print(f"Error in _load_custom_themes: {e}")
    def get_theme(self, theme_name: str) -> Optional[ThemeColors]:
        """Get a theme by name"""
        return self.themes.get(theme_name)

    def add_theme(self, name: str, theme: ThemeColors, save: bool = True) -> bool:
        """Add a new theme and optionally save it to disk"""
        try:
            self.themes[name] = theme
            if save:
                self._save_theme(name, theme)
            return True
        except Exception as e:
            print(f"Error adding theme {name}: {e}")
            return False

    def _save_theme(self, name: str, theme: ThemeColors):
        """Save a theme to the user's themes directory"""
        home = Path("./")
        themes_dir = home / 'themes'
        themes_dir.mkdir(exist_ok=True)

        theme_path = themes_dir / f"{name}.json"
        with open(theme_path, 'w') as f:
            json.dump(theme.to_dict(), f, indent=2)

    def get_theme_names(self) -> list[str]:
        """Get a list of all available theme names"""
        return list(self.themes.keys())

    def generate_stylesheet(self, theme: ThemeColors) -> str:
        """Generate Qt stylesheet from theme colors with WebEngine context menu support"""

        def make_opaque(color_string):
            """Convert any rgba color to fully opaque version"""
            if color_string.startswith('rgba('):
                # Extract RGB values from rgba(r, g, b, a)
                rgb_part = color_string[5:-1].split(',')[:3]  # Get just r, g, b
                return f"rgb({', '.join(rgb_part)})"
            return color_string

        # Get context menu colors, with fully opaque background
        if isinstance(theme, dict):
            # Create a temporary ThemeColors object from the dict
            from copy import deepcopy
            theme_dict = deepcopy(theme)
            temp_theme = ThemeColors()

            # Copy all attributes from the dict to the ThemeColors object
            for key, value in theme_dict.items():
                if key != 'terminal':  # Handle terminal separately
                    setattr(temp_theme, key, value)

            # Handle terminal specially since it's nested
            if 'terminal' in theme_dict:
                temp_theme.terminal = theme_dict['terminal']

            # Use the ThemeColors object instead
            theme = temp_theme

        context_menu = getattr(theme, 'context_menu', {}) or {
            'background': theme.secondary,
            'text': theme.text,
            'selected_bg': theme.selected_bg,
            'selected_text': theme.lighter_bg,
            'border': theme.border_light
        }

        # Force all menu colors to be opaque
        menu_bg = make_opaque(context_menu['background'])
        menu_text = make_opaque(context_menu['text'])
        menu_selected_bg = make_opaque(context_menu['selected_bg'])
        menu_selected_text = make_opaque(context_menu['selected_text'])
        menu_border = make_opaque(context_menu['border'])

        return f"""
            QMainWindow, QWidget {{
                background-color: {theme.background};
                color: {theme.text};
                font-family: "Courier New";
            }}
            QGroupBox {{
                border: 1px solid {theme.border_light};
                margin-top: 1.5em;
                padding: 15px;
            }}
            QGroupBox::title {{
                color: {theme.text};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QPushButton {{
                background-color: {theme.darker_bg};
                border: 1px solid {theme.border_light};
                padding: 5px 15px;
                color: {theme.text};
            }}
            QPushButton:hover {{
                background-color: {theme.button_hover} !important;
                border: 1px solid {theme.text};
            }}
            QPushButton:pressed {{
                background-color: {theme.button_pressed};
            }}
            QLineEdit, QTextEdit {{
                background-color: {theme.darker_bg};
                border: 1px solid {theme.border_light};
                color: {theme.text};
                padding: 5px;
            }}
            QTreeWidget {{
                background-color: {theme.darker_bg};
                border: 1px solid {theme.border_light};
                color: {theme.text};
            }}
            QTreeWidget::item:selected {{
                background-color: {theme.selected_bg};
            }}
            QComboBox {{
                background-color: {theme.darker_bg};
                border: 1px solid {theme.border_light};
                color: {theme.text};
                padding: 5px;
            }}
            QComboBox:drop-down {{
                border: none;
            }}
            QComboBox:down-arrow {{
                border: 2px solid {theme.text};
                width: 6px;
                height: 6px;
            }}
            QFrame {{
                border-color: {theme.border_light};
            }}
            QWebEngineView {{
                background: {theme.background};
            }}
            QMenu {{
                background-color: {menu_bg} !important;
                color: {menu_text};
                border: 1px solid {menu_border};
                padding: 5px;
            }}
            QMenu::item {{
                background-color: {menu_bg};
                padding: 5px 30px 5px 30px;
                border: 1px solid transparent;
            }}
            QMenu::item:selected {{
                background-color: {menu_selected_bg};
                color: {menu_selected_text};
            }}
            QMenu::separator {{
                height: 1px;
                background: {menu_border} !important;
                margin: 5px 0px 5px 0px;
            }}

            QScrollBar:vertical {{
                background-color: {theme.scrollbar_bg};
                width: 10px;
                margin: 0;
                border: none;
            }}

            QScrollBar::handle:vertical {{
                background: {theme.scrollbar_handle if hasattr(theme, 'scrollbar_handle') else theme.border_light};
                min-height: 20px;
                border-radius: 4px;
                border: none;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {theme.scrollbar_handle_hover if hasattr(theme, 'scrollbar_handle_hover') else theme.text};
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
                border: none;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: {theme.scrollbar_bg};
                border: none;
            }}
        """

    def apply_theme(self, widget, theme_name: str):
        """Apply a theme to a widget"""
        theme = self.get_theme(theme_name)
        if hasattr(widget, 'apply_theme') and callable(widget.apply_theme):
            # The widget has its own theme handling
            widget.apply_theme(self, theme_name)
            return
        if theme:
            stylesheet = self.generate_stylesheet(theme)
            widget.setStyleSheet(stylesheet)
        else:
            print(f"Theme '{theme_name}' not found")

    def generate_terminal_js(self, theme: ThemeColors) -> str:
        """Generate terminal theme JavaScript with improved xterm.js compatibility"""
        print(f"Generating terminal theme for {theme}")  # Debug log

        # First check if there's a terminal-specific theme
        if hasattr(theme, 'terminal') and theme.terminal and 'theme' in theme.terminal:
            print("Using terminal-specific theme")
            term_colors = theme.terminal['theme'].copy()

            # Handle scrollbar if it exists in terminal theme
            if 'scrollbar' in term_colors:
                scrollbar_colors = term_colors.pop('scrollbar')
            else:
                scrollbar_colors = {
                    'background': theme.background,
                    'thumb': theme.border_light,
                    'thumb_hover': theme.text
                }
        else:
            print("Falling back to main theme colors")
            # Fallback to main theme colors if no terminal theme exists
            term_colors = {
                'foreground': theme.text,
                'background': theme.background,
                'cursor': theme.text,
                'black': theme.darker_bg,
                'brightBlack': theme.darker_bg,
                'red': theme.error,
                'brightRed': theme.error,
                'green': theme.success,
                'brightGreen': theme.success,
                'yellow': theme.line,
                'brightYellow': theme.line,
                'blue': theme.primary,
                'brightBlue': theme.primary,
                'magenta': theme.secondary,
                'brightMagenta': theme.secondary,
                'cyan': theme.grid,
                'brightCyan': theme.grid,
                'white': theme.text,
                'brightWhite': theme.lighter_bg,
                'selectionBackground': theme.selected_bg,
                'selectionForeground': theme.lighter_bg,
            }

            print(json.dumps(term_colors, indent=2))
            scrollbar_colors = {
                'background': theme.background,
                'thumb': theme.border_light,
                'thumb_hover': theme.text
            }
        term_colors['selectionBackground'] = '#FF0000'  # Bright red
        term_colors['selectionForeground'] = '#FFFFFF'  # White
        print(f"Terminal colors: {term_colors}")  # Debug log
        print(f"Scrollbar colors: {scrollbar_colors}")  # Debug log

        js = f"""
        console.log('Applying terminal theme edited...', {json.dumps(term_colors)});

        // Set terminal options
        try {{
            term.setOption('theme', {json.dumps(term_colors)});
            term.setOption('fontFamily', 'Courier New');
            term.setOption('fontSize', 14);
            term.setOption('cursorBlink', true);

            console.log('Theme applied successfully', term.getOption('theme'));
        }} catch (e) {{
            console.error('Error applying theme:', e);
        }}

        // Update scrollbar styles
        if (!window.themeStyle) {{
            window.themeStyle = document.createElement('style');
            window.themeStyle.id = 'theme-scrollbar-style';
            document.head.appendChild(window.themeStyle);
        }}

        window.themeStyle.innerHTML = `
            body {{
                background-color: {theme.background};
                margin: 0;
                padding: 0;
            }}
            .xterm-viewport::-webkit-scrollbar {{
                width: 12px;
            }}
            .xterm-viewport::-webkit-scrollbar-track {{
                background: {scrollbar_colors['background']};
            }}
            .xterm-viewport::-webkit-scrollbar-thumb {{
                background: {scrollbar_colors['thumb']};
            }}
            .xterm-viewport::-webkit-scrollbar-thumb:hover {{
                background: {scrollbar_colors['thumb_hover']};
            }}
        `;

        // Force a terminal refresh
        term.refresh(0, term.rows - 1);

        // Log the current state
        console.log('Terminal state:', {{
            'theme': term.getOption('theme'),
            'fontSize': term.getOption('fontSize'),
            'fontFamily': term.getOption('fontFamily')
        }});
        """
        return js

    from PyQt6.QtCore import QTimer

    # def apply_theme_to_terminal(self, terminal, terminal_theme=None):
    #     """Apply theme to a terminal instance with a delay"""
    #
    #     def delayed_apply():
    #         print(f"Applying terminal theme: {terminal_theme}")  # Debug log
    #
    #         theme = self.get_theme(terminal_theme) if terminal_theme else self.get_theme("borland")
    #
    #         if not theme:
    #             print(f"Theme not found, falling back to cyberpunk")
    #             theme = self.get_theme("cyberpunk")
    #
    #         if hasattr(terminal, 'page'):
    #             js_theme = self.generate_terminal_js(theme)
    #             # Add debug logging
    #             print("Checking terminal readiness...")
    #             terminal.page.runJavaScript(
    #                 """
    #                 console.log('Terminal check:', {
    #                     termExists: typeof term !== 'undefined',
    #                     termNull: term === null
    #                 });
    #                 typeof term !== 'undefined' && term !== null
    #                 """,
    #                 lambda result: self.handle_theme_check(result, terminal, js_theme)
    #             )
    #         else:
    #             print("Terminal has no page() method")
    #
    #     # Create and start timer with 1000ms (1 second) delay
    #     timer = QTimer()
    #     timer.setSingleShot(True)
    #     timer.timeout.connect(delayed_apply)
    #     timer.start(2000)
    def handle_theme_check(self, is_ready: bool, terminal, theme_js: str):
        """Handle the terminal readiness check for theme application."""
        print(f"Terminal ready: {is_ready}")  # Debug log

        if is_ready:
            print("Applying theme JS...")
            print(theme_js)
            terminal.page.runJavaScript(
                theme_js,
                lambda result: print(f"Theme application completed: {result}")
            )
        # else:
        #     print("Terminal not ready, scheduling retry...")
        #     from PyQt6.QtCore import QTimer
        #     QTimer.singleShot(500, lambda: self.apply_theme_to_terminal(terminal))

class LayeredHUDFrame(QFrame):
    def __init__(self, parent=None, theme_manager=None, theme_name="cyberpunk"):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.theme_name = theme_name
        self.setup_ui()
        if theme_manager:
            self.update_theme_colors()

    def setup_ui(self):
        # Main content layout
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(1, 1, 1, 1)

        # Create corner lines (bright)
        self.corner_lines = []
        for i in range(8):
            line = QFrame(self)
            if i < 4:  # Horizontal corner pieces
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFixedHeight(1)
            else:  # Vertical corner pieces
                line.setFrameShape(QFrame.Shape.VLine)
                line.setFixedWidth(1)
            self.corner_lines.append(line)

        # Create connecting lines (dim)
        self.connecting_lines = []
        for i in range(4):
            line = QFrame(self)
            if i < 2:  # Horizontal connectors
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFixedHeight(1)
            else:  # Vertical connectors
                line.setFrameShape(QFrame.Shape.VLine)
                line.setFixedWidth(1)
            self.connecting_lines.append(line)

        self.setStyleSheet("background-color: transparent;")

        # Set initial colors (will be overridden if theme_manager is provided)
        self.update_line_colors("#0f969e", "rgba(15, 150, 158, 0.3)")

    def update_theme_colors(self):
        """Update colors based on current theme"""
        if self.theme_manager:
            # Get theme colors - handle both old and new theme managers
            if hasattr(self.theme_manager, 'get_colors'):
                # New ThemeLibrary way
                colors = self.theme_manager.get_colors(self.theme_name)
            else:
                # Fallback for old theme manager
                colors = self.theme_manager.get_chart_colors(self.theme_name)

            if isinstance(colors, dict):
                # Get colors directly from dict
                bright_color = colors.get('corner_bright', colors.get('border', '#0f969e'))
                dim_color = colors.get('border_light', 'rgba(15, 150, 158, 0.3)')
            else:
                # Handle ThemeColors dataclass
                bright_color = getattr(colors, 'corner_bright', getattr(colors, 'border', '#0f969e'))
                dim_color = getattr(colors, 'border_light', 'rgba(15, 150, 158, 0.3)')

            # Convert hex to rgba if needed
            if bright_color.startswith('#'):
                r = int(bright_color[1:3], 16)
                g = int(bright_color[3:5], 16)
                b = int(bright_color[5:7], 16)
                dim_color = f"rgba({r}, {g}, {b}, 0.4)"

            self.update_line_colors(bright_color, dim_color)

    def update_line_colors(self, bright_color, dim_color):
        """Update line colors with provided colors"""
        # Update corner lines (bright)
        for line in self.corner_lines:
            line.setStyleSheet(f"background-color: {bright_color};")

        # Update connecting lines (dim)
        for line in self.connecting_lines:
            line.setStyleSheet(f"background-color: {dim_color};")

    def set_theme(self, theme_name):
        """Change the theme of the frame"""
        self.theme_name = theme_name
        self.update_theme_colors()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = self.width(), self.height()
        corner_length = 20  # Length of bright corner pieces

        # Top-left corner
        self.corner_lines[0].setGeometry(0, 0, corner_length, 1)  # Horizontal
        self.corner_lines[4].setGeometry(0, 0, 1, corner_length)  # Vertical

        # Top-right corner
        self.corner_lines[1].setGeometry(w - corner_length, 0, corner_length, 1)  # Horizontal
        self.corner_lines[5].setGeometry(w - 1, 0, 1, corner_length)  # Vertical

        # Bottom-left corner
        self.corner_lines[2].setGeometry(0, h - 1, corner_length, 1)  # Horizontal
        self.corner_lines[6].setGeometry(0, h - corner_length, 1, corner_length)  # Vertical

        # Bottom-right corner
        self.corner_lines[3].setGeometry(w - corner_length, h - 1, corner_length, 1)  # Horizontal
        self.corner_lines[7].setGeometry(w - 1, h - corner_length, 1, corner_length)  # Vertical

        # Connecting lines (dim)
        # Top
        self.connecting_lines[0].setGeometry(corner_length, 0, w - 2 * corner_length, 1)
        # Bottom
        self.connecting_lines[1].setGeometry(corner_length, h - 1, w - 2 * corner_length, 1)
        # Left
        self.connecting_lines[2].setGeometry(0, corner_length, 1, h - 2 * corner_length)
        # Right
        self.connecting_lines[3].setGeometry(w - 1, corner_length, 1, h - 2 * corner_length)


def generate_terminal_themes(theme_library):
    """Convert JSON theme files into terminal_themes format for xterm.js 5.5."""
    terminal_themes = {}

    for theme_name in theme_library.get_theme_names():
        theme = theme_library.get_theme(theme_name)
        if not theme:
            continue

        # Check if theme has terminal colors defined first
        if hasattr(theme, 'terminal') and theme.terminal and 'theme' in theme.terminal:
            print(f"Using terminal colors for {theme_name}")
            # Use terminal colors directly
            term_colors = theme.terminal['theme'].copy()
            # Remove scrollbar from term_colors if it exists
            if 'scrollbar' in term_colors:
                scrollbar_colors = term_colors.pop('scrollbar')
            else:
                scrollbar_colors = {
                    'background': theme.background,
                    'thumb': theme.border_light,
                    'thumb_hover': theme.text
                }
        else:
            print(f"Using fallback colors for {theme_name}")
            # Fallback to theme colors if no terminal colors defined
            term_colors = {
                'foreground': theme.text,
                'background': theme.background,
                'cursor': theme.line,
                'black': theme.darker_bg,
                'red': theme.error,
                'green': theme.success,
                'yellow': theme.line,
                'blue': theme.primary,
                'magenta': theme.secondary,
                'cyan': theme.grid,
                'white': theme.text,
                'brightBlack': theme.darker_bg,
                'brightRed': theme.error,
                'brightGreen': theme.success,
                'brightYellow': theme.line,
                'brightBlue': theme.primary,
                'brightMagenta': theme.secondary,
                'brightCyan': theme.grid,
                'brightWhite': theme.lighter_bg
            }
            scrollbar_colors = {
                'background': theme.background,
                'thumb': theme.border_light,
                'thumb_hover': theme.text
            }

        # Always set explicit selection colors that will work well
        selection_bg = '#504945'  # Dark gray
        selection_fg = '#EBDBB2'  # Light cream

        # Add selection colors to term_colors
        term_colors['selection'] = selection_bg
        term_colors['selectionBackground'] = selection_bg
        term_colors['selectionForeground'] = selection_fg

        # Generate the JavaScript theme application code
        js_code = f"""
        console.log('Applying terminal theme for {theme_name} to xterm.js 5.5...');

        try {{
            // Define the complete theme object
            const terminalTheme = {json.dumps(term_colors)};

            // Log the selection colors we're applying
            console.log('Setting selection colors:', {{
                selection: '{selection_bg}',
                selectionForeground: '{selection_fg}'
            }});

            // Apply theme to terminal
            if (term && term.options) {{
                // Modern xterm.js 5.x approach
                term.options.theme = terminalTheme;

                // Font settings
                term.options.fontFamily = 'Courier New';
                term.options.fontSize = 14;
                term.options.cursorBlink = true;

                console.log('Applied theme using term.options');
            }} else if (term && term.setOption) {{
                // Fallback to older approach
                term.setOption('theme', terminalTheme);
                term.setOption('fontFamily', 'Courier New');
                term.setOption('fontSize', 14);
                term.setOption('cursorBlink', true);

                console.log('Applied theme using term.setOption');
            }} else {{
                console.error('Cannot find appropriate method to set terminal options');
            }}

            // Apply CSS to ensure selection is styled correctly
            const selectionStyle = document.createElement('style');
            selectionStyle.textContent = `
                .xterm-selection-layer .xterm-selection {{
                    background-color: {selection_bg} !important;
                    opacity: 0.6;
                }}
                .xterm-selection-layer .xterm-selection.xterm-focus {{
                    opacity: 0.8;
                }}
                .xterm-selection-layer .xterm-selection.xterm-focus .xterm-selection-top-left,
                .xterm-selection-layer .xterm-selection.xterm-focus .xterm-selection-top-right,
                .xterm-selection-layer .xterm-selection.xterm-focus .xterm-selection-bottom-left,
                .xterm-selection-layer .xterm-selection.xterm-focus .xterm-selection-bottom-right {{
                    background-color: {selection_bg} !important;
                }}
            `;
            document.head.appendChild(selectionStyle);
        }} catch (e) {{
            console.error('Error applying theme:', e);
        }}

        // Apply scrollbar styles
        try {{
            if (!window.themeStyle) {{
                window.themeStyle = document.createElement('style');
                window.themeStyle.id = 'theme-scrollbar-style';
                document.head.appendChild(window.themeStyle);
            }}

            window.themeStyle.innerHTML = `
                body {{
                    background-color: {theme.background};
                    margin: 0;
                    padding: 0;
                }}
                .xterm-viewport::-webkit-scrollbar {{
                    width: 12px;
                }}
                .xterm-viewport::-webkit-scrollbar-track {{
                    background: {scrollbar_colors['background']};
                }}
                .xterm-viewport::-webkit-scrollbar-thumb {{
                    background: {scrollbar_colors['thumb']};
                }}
                .xterm-viewport::-webkit-scrollbar-thumb:hover {{
                    background: {scrollbar_colors['thumb_hover']};
                }}
            `;

            // Set CSS variables for consistency
            document.documentElement.style.setProperty('--selection-background', '{selection_bg}');
            document.documentElement.style.setProperty('--selection-text', '{selection_fg}');
        }} catch (e) {{
            console.error('Error applying scrollbar styles:', e);
        }}

        // Force a terminal refresh
        try {{
            // Refresh the terminal display
            if (term && term.refresh) {{
                term.refresh(0, term.rows - 1);
            }}

            // Apply fitting if available
            if (typeof fitAddon !== 'undefined' && fitAddon.fit) {{
                fitAddon.fit();
            }}

            console.log('Terminal refresh completed');
        }} catch (e) {{
            console.error('Error in final terminal refresh:', e);
        }}
        """

        # Add to terminal_themes dictionary
        terminal_themes[theme_name] = {
            "js": js_code
        }

    return terminal_themes

def generate_telemetry_theme_json(theme_colors):
    """
    Convert a ThemeColors object to JSON format for the telemetry widget

    Args:
        theme_colors: ThemeColors instance

    Returns:
        dict: Theme data in the format expected by telemetry_theme.js
    """
    # Map ThemeColors properties to telemetry theme CSS variables
    telemetry_theme = {
        '--text-primary': theme_colors.text,
        '--text-secondary': theme_colors.grid,
        '--bg-primary': theme_colors.background,
        '--bg-secondary': theme_colors.darker_bg,
        '--border-color': theme_colors.border_light,
        '--accent-color': theme_colors.primary,
        '--scrollbar-track': theme_colors.scrollbar_bg,
        '--scrollbar-thumb': theme_colors.border,
        '--scrollbar-thumb-hover': theme_colors.text,
        '--success-color': theme_colors.success,
        '--error-color': theme_colors.error,
        '--chart-line': theme_colors.line,
        '--chart-grid': theme_colors.grid
    }

    # Create a corresponding terminal theme
    terminal_theme = {}
    if hasattr(theme_colors, 'terminal') and theme_colors.terminal:
        terminal_theme = theme_colors.terminal.get('theme', {})
    else:
        # Map from app theme to terminal theme
        terminal_theme = {
            'foreground': theme_colors.text,
            'background': theme_colors.background,
            'cursor': theme_colors.text,
            'black': theme_colors.darker_bg,
            'red': theme_colors.error,
            'green': theme_colors.success,
            'yellow': theme_colors.line,
            'blue': theme_colors.primary,
            'magenta': theme_colors.secondary,
            'cyan': theme_colors.grid,
            'white': theme_colors.text,
            'brightBlack': theme_colors.darker_bg,
            'brightRed': theme_colors.error,
            'brightGreen': theme_colors.success,
            'brightYellow': theme_colors.line,
            'brightBlue': theme_colors.primary,
            'brightMagenta': theme_colors.secondary,
            'brightCyan': theme_colors.grid,
            'brightWhite': theme_colors.lighter_bg,
            'selectionBackground': theme_colors.selected_bg
        }

    # Return the complete theme data
    return {
        'css_vars': telemetry_theme,
        'terminal': terminal_theme,
        'cornerStyle': get_corner_style_for_theme(theme_colors)
    }


def get_corner_style_for_theme(theme_colors):
    """
    Determine appropriate corner style based on theme characteristics

    Args:
        theme_colors: ThemeColors instance

    Returns:
        str: Name of the corner style for the theme
    """
    # This mapping is a heuristic - customize based on your preferences
    # Analyze theme characteristics to choose appropriate corner style
    if theme_colors.background.startswith('#0'):
        # Cyber themes with dark blue/green backgrounds
        return 'hexTech'
    elif theme_colors.text.startswith('#00ff'):
        # Neon cyan text themes
        return 'glowCircuit'
    elif theme_colors.text.startswith('#00f'):
        # Neon blue text themes
        return 'quantumFlux'
    elif '#00' in theme_colors.text:
        # Green text themes
        return 'pulseWave'
    elif theme_colors.text.startswith('#f'):
        # Amber/orange text themes
        return 'neonGrid'
    elif theme_colors.background.startswith('#1'):
        # Dark themes
        return 'minimalist'
    else:
        # Light themes
        return 'rounded'