"""
Termtel - UI Setup Module
Handles menu system with proper theme signaling for telemetry widgets
"""
import sys
import yaml
from PyQt6.QtGui import QActionGroup, QAction, QDesktopServices
from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QFileDialog, QDialog,
    QVBoxLayout, QLabel, QWidget, QGroupBox, QPushButton, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QProcess, QProcessEnvironment, pyqtSignal
import logging
import os

from termtel.theme_launcher import launch_theme_editor
from termtel.widgets.credential_manager import CredentialManagerDialog
from termtel.widgets.lmtosession import LMDownloader
from termtel.widgets.nbtosession import App as NetboxExporter
from termtel.logo import get_themed_svg

logger = logging.getLogger('termtel.setup')

# Import main theme manager
try:
    from termtel.themes3 import ThemeLibrary
    MAIN_THEME_MANAGER_AVAILABLE = True
except ImportError:
    MAIN_THEME_MANAGER_AVAILABLE = False
    logger.warning("Main theme manager not available")


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About TerminalTelemetry")
        self.setMinimumSize(800, 600)

        # Get theme colors from parent window's theme manager
        theme_name = parent.theme if hasattr(parent, 'theme') else 'cyberpunk'
        theme_colors = parent.theme_manager.get_colors(theme_name) if hasattr(parent, 'theme_manager') else None

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        web_view = QWebEngineView()

        # Define colors based on theme or fallback to defaults
        if theme_colors:
            bg_color = theme_colors['background']
            text_color = theme_colors['text']
            highlight_color = theme_colors['primary']
            secondary_color = theme_colors['border']
            border_color = theme_colors['border']
        else:
            bg_color = "#1e1e1e"
            text_color = "#ffffff"
            highlight_color = "#0affff"
            secondary_color = "#888888"
            border_color = "#444444"

        # Get the themed SVG content
        try:
            if theme_colors:
                svg_content = get_themed_svg(theme_colors)
            else:
                svg_content = get_themed_svg()
        except ImportError:
            # Fallback SVG if the module isn't available
            svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500">
                <rect width="500" height="500" fill="''' + bg_color + '''"/>
                <circle cx="250" cy="250" r="150" fill="none" stroke="''' + highlight_color + '''" stroke-width="5"/>
                <path d="M250 100 L400 350 L100 350 Z" fill="none" stroke="''' + text_color + '''" stroke-width="5"/>
                <text x="40" y="50" fill="''' + text_color + '''" font-family="monospace" font-size="16" font-weight="bold">SSH</text>
            </svg>'''

        # Embed the SVG in the HTML content
        about_html = f"""
        <html>
        <head>
            <style>
                body {{
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px 40px;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                }}
                .logo-container {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .logo {{
                    width: 200px;
                    height: 200px;
                    margin: 0 auto;
                }}
                h1 {{
                    color: {text_color};
                    text-align: center;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                h2 {{
                    color: {text_color};
                    margin-top: 25px;
                }}
                h3 {{
                    color: {text_color};
                    margin-top: 20px;
                    font-size: 1.2em;
                }}
                .subtitle {{
                    color: {text_color};
                    text-align: center;
                    font-size: 1.1em;
                    margin-bottom: 30px;
                }}
                .feature-list {{
                    list-style-type: none;
                    padding: 0;
                }}
                .feature-list li {{
                    margin: 10px 0;
                    padding-left: 25px;
                    position: relative;
                }}
                .feature-list li:before {{
                    content: "";
                    color: {text_color};
                    position: absolute;
                    left: 0;
                }}
                .highlight {{
                    color: {text_color};
                }}
                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    color: {secondary_color};
                    border-top: 1px solid {border_color};
                    padding-top: 20px;
                }}
                .code {{
                    background: rgba(0,0,0,0.2);
                    padding: 10px;
                    border-radius: 4px;
                    margin: 15px 0;
                    font-family: monospace;
                }}
                .svg-container {{
            width: 100px;
            height: 100px;
            margin: 0 auto;
        }}
        
        .svg-container svg {{
            width: 100%;
            height: 100%;
        }}

        ::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}
        ::-webkit-scrollbar-track {{
            background: {bg_color};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {border_color};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {border_color};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-corner {{
            background: {bg_color};
        }}
                </style>
        </head>
        <body>
            <div class="container">
                <!-- SVG Logo -->
                <div class="svg svg-container logo-container">
                    {svg_content}
                </div>

                <h1>TerminalTelemetry</h1>
                <div class="subtitle">A minimalist, cyber-inspired terminal emulator with modern features</div>

                <h2>Key Features</h2>
                <div class="feature-list">
                    <h3>Modern Terminal Emulator</h3>
                    <ul>
                        <li>Multi-session support with tabbed interface</li>
                        <li>Customizable themes (Cyberpunk, Dark Mode, Light Mode, Retro Green, Retro Amber, Neon Blue)</li>
                        <li>Session management and quick connect functionality</li>
                        <li>Secure credential storage</li>
                    </ul>

                     <h3>Theme System</h3>
                    <ul>
                        <li>Dynamic JSON-based themes</li>
                        <li>Live theme preview and hot-reload</li>
                        <li>Custom theme creation support</li>
                    </ul>
                    <div class="code">
                    To install themes:
                    1. Download themes.zip from View > Theme > Download Themes
                    2. Extract to 'themes' directory
                    3. Click View > Theme > Reload Themes
                    </div>

                    <h3>Security Features</h3>
                    <ul>
                        <li>PBKDF2-HMAC-SHA256 key derivation (480,000 iterations)</li>
                        <li>Fernet (AES-128-CBC) encryption with HMAC authentication</li>
                        <li>Platform-specific secure storage locations</li>
                        <li>Machine-specific binding</li>
                        <li>Rate-limited authentication</li>
                        <li>Cross-platform secure credential management</li>
                        <li>Zero plaintext storage of sensitive data</li>
                    </ul>
                </div>

                <div class="footer">
                    <p>Author: Scott Peterman (github.com/scottpeterman)</p>
                    <p>Licensed under GNU General Public License v3 (GPLv3)</p>
                </div>
            </div>
        </body>
        </html>
        """
        web_view.setHtml(about_html)
        layout.addWidget(web_view)
        self.setLayout(layout)

        # Apply the parent's theme to the dialog
        if hasattr(parent, 'theme_manager'):
            parent.theme_manager.apply_theme(self, theme_name)


def setup_menus(window):
    """Setup menu system for the main window"""
    menubar = window.menuBar()

    # File Menu
    file_menu = menubar.addMenu("&File")
    open_action = file_menu.addAction("&Open Sessions...")
    open_action.triggered.connect(lambda: handle_open_sessions(window))
    file_menu.addSeparator()
    exit_action = file_menu.addAction("E&xit")
    exit_action.triggered.connect(window.close)

    # View Menu
    view_menu = menubar.addMenu("&View")

    # Create Themes submenu with dynamic theme loading
    themes_menu = view_menu.addMenu("Theme")
    theme_group = QActionGroup(window)
    theme_group.setExclusive(True)

    # Get available themes from ThemeLibrary
    available_themes = window.theme_manager.get_theme_names()

    # Create theme actions with safe theme switching
    for theme_name in available_themes:
        # Convert theme name to display name (e.g., "dark_mode" -> "Dark Mode")
        display_name = theme_name.replace('_', ' ').title()

        theme_action = QAction(display_name, window)
        theme_action.setCheckable(True)
        theme_action.setChecked(theme_name == window.theme)
        theme_action.triggered.connect(
            lambda checked, t=theme_name: safe_switch_theme(window, t)
        )

        theme_group.addAction(theme_action)
        themes_menu.addAction(theme_action)

    # Add theme reload action
    themes_menu.addSeparator()
    theme_editor_action = themes_menu.addAction("Theme Editor")
    theme_editor_action.triggered.connect(lambda: launch_theme_editor(window))

    reload_themes = themes_menu.addAction("Reload Themes")
    reload_themes.triggered.connect(lambda: reload_theme_menu(window, themes_menu, theme_group))
    download_themes = themes_menu.addAction("Download Themes")
    download_themes.triggered.connect(
        lambda: QDesktopServices.openUrl(
            QUrl("https://raw.githubusercontent.com/scottpeterman/terminaltelemetry/main/themes.zip")
        )
    )
    credentials_action = view_menu.addAction("&Credentials")
    credentials_action.triggered.connect(lambda: show_credentials_dialog(window))

    # Tools Menu
    tools_menu = menubar.addMenu("&Tools")
    serial_terminal_action = tools_menu.addAction("Serial &Terminal")
    serial_terminal_action.triggered.connect(
        lambda: window.terminal_tabs.create_serial_terminal_tab("Serial Terminal")
    )
    netbox_action = tools_menu.addAction("&Netbox Import")
    netbox_action.triggered.connect(lambda: show_netbox_importer(window))

    lm_action = tools_menu.addAction("&LogicMonitor Import")
    lm_action.triggered.connect(lambda: show_logicmonitor_importer(window))

    # Use safe telemetry tab creation
    telemetry_action = tools_menu.addAction('Telemetry Dashboard')
    telemetry_action.triggered.connect(lambda: safe_create_telemetry_tab(window))

    manage_sessions_action = tools_menu.addAction('Manage Sessions')
    manage_sessions_action.triggered.connect(lambda: show_session_manager(window))

    # Add separator before distractions menu
    tools_menu.addSeparator()

    # Add Distractions submenu
    distractions_menu = tools_menu.addMenu("Distractions")
    distractions_menu.setObjectName("menu_distractions")

    # Add Notepad action
    notepad_action = distractions_menu.addAction("Notepad")
    notepad_action.triggered.connect(
        lambda: window.terminal_tabs.create_text_editor_tab("Notepad")
    )

    diff_tool_action = distractions_menu.addAction("Diff Tool")
    diff_tool_action.triggered.connect(
        lambda: window.terminal_tabs.create_diff_tool_tab("Diff Tool")
    )

    space_debris = distractions_menu.addAction("Space Debris")
    space_debris.triggered.connect(
        lambda: window.terminal_tabs.create_game_tab("Space Debris")
    )

    doom_action = distractions_menu.addAction("Doom")
    doom_action.triggered.connect(
        lambda: window.terminal_tabs.create_doom_tab("Doom")
    )

    # Help Menu
    help_menu = menubar.addMenu("&Help")
    about_action = help_menu.addAction("&About")
    about_action.triggered.connect(lambda: show_about_dialog(window))

def safe_switch_theme(window, theme_name):
    """
    Safe theme switching that handles both old and new telemetry properly
    """
    print(f" Safe theme switch to: {theme_name}")

    try:
        # Apply theme to main window using existing method
        if hasattr(window, 'switch_theme'):
            try:
                window.switch_theme(theme_name)
            except Exception as e:
                print(f"️ Error in main switch_theme: {e}")
                # Fallback: apply directly if switch_theme fails
                if hasattr(window, 'theme_manager'):
                    window.theme_manager.apply_theme(window, theme_name)
                    window.theme = theme_name

        # Handle new telemetry widgets
        if hasattr(window, 'telemetry_widgets'):
            for widget in window.telemetry_widgets:
                try:
                    if hasattr(widget, 'set_theme_from_parent'):
                        widget.set_theme_from_parent(theme_name)
                    elif hasattr(widget, '_apply_theme'):
                        widget._apply_theme(theme_name)
                except Exception as e:
                    print(f"️ Could not apply theme to telemetry widget: {e}")

        # Emit theme change signal for other components
        if hasattr(window, 'theme_changed'):
            window.theme_changed.emit(theme_name)

        print(f" Theme switch to {theme_name} completed")

    except Exception as e:
        print(f" Error in safe_switch_theme: {e}")
        QMessageBox.warning(
            window,
            "Theme Switch Warning",
            f"Theme change partially failed: {str(e)}"
        )


def safe_create_telemetry_tab(window):
    """
    Safe telemetry tab creation with theme manager registration
    """
    try:
        # Initialize telemetry theme manager if this is the first telemetry tab
        if  not hasattr(window, 'telemetry_theme_manager'):
            # window.telemetry_theme_manager = TelemetryWidgetThemeManager(window)
            print(" Initialized telemetry theme manager")

        # Create telemetry tab using existing method
        if hasattr(window.terminal_tabs, 'create_telemetry_tab'):
            tab = window.terminal_tabs.create_telemetry_tab("Telemetry")

            # Register with theme manager if it's a new-style widget
            if (hasattr(window, 'telemetry_theme_manager')):

                telemetry_widget = None

                # Find the telemetry widget in the tab
                if hasattr(tab, 'telemetry_widget'):
                    telemetry_widget = tab.telemetry_widget
                elif hasattr(tab, 'set_theme_from_parent'):
                    telemetry_widget = tab

                if telemetry_widget:
                    try:
                        window.telemetry_theme_manager.register_telemetry_widget(telemetry_widget)
                        print(" Registered telemetry widget with theme manager")

                        # Apply current theme to new widget
                        if hasattr(window, 'theme'):
                            telemetry_widget.set_theme_from_parent(window.theme)

                    except Exception as e:
                        print(f"️ Could not register telemetry widget: {e}")
        else:
            # Fallback to old method
            window.terminal_tabs.create_telemetry_tab("Telemetry")

    except Exception as e:
        print(f" Error creating telemetry tab: {e}")
        QMessageBox.warning(window, "Telemetry Error", f"Could not create telemetry tab: {str(e)}")


def reload_theme_menu(window, themes_menu, theme_group):
    """Reload the themes menu with current themes from ThemeLibrary"""
    # Clear existing theme actions
    for action in theme_group.actions():
        themes_menu.removeAction(action)
        theme_group.removeAction(action)

    # Reload themes from library
    window.theme_manager._load_custom_themes()

    # Add new theme actions with safe switching
    available_themes = window.theme_manager.get_theme_names()
    for theme_name in available_themes:
        display_name = theme_name.replace('_', ' ').title()
        theme_action = QAction(display_name, window)
        theme_action.setCheckable(True)
        theme_action.setChecked(theme_name == window.theme)
        theme_action.triggered.connect(
            lambda checked, t=theme_name: safe_switch_theme(window, t)
        )
        theme_group.addAction(theme_action)
        themes_menu.insertAction(themes_menu.actions()[-2], theme_action)  # Insert before separator


def show_session_manager(window):
    """Launch the session manager dialog"""
    from termtel.widgets.session_editor import SessionEditorDialog

    dialog = SessionEditorDialog(window, session_file=window.session_file_with_path)
    if dialog.exec() == dialog.DialogCode.Accepted:
        try:
            with open(window.session_file_with_path) as f:
                sessions_data = yaml.safe_load(f)
                window.session_navigator.load_sessions(file_content_to_load=sessions_data)
        except Exception as e:
            logger.error(f"Failed to load sessions: {str(e)}")


def show_netbox_importer(window):
    """Show the Netbox to Session importer"""
    try:
        dialog = NetboxExporter(window)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.show()
    except Exception as e:
        logger.error(f"Error showing Netbox importer: {e}")


def handle_open_sessions(window):
    """Handle opening a new sessions file"""
    try:
        file_name, _ = QFileDialog.getOpenFileName(
            window,
            "Open Sessions File",
            "",
            "YAML Files (*.yaml);;All Files (*)"
        )
        if file_name:
            logger.info(f"Opening sessions file: {file_name}")
            window.session_file = file_name
            window.load_sessions()
    except Exception as e:
        logger.error(f"Error opening sessions file: {e}")


def show_credentials_dialog(window):
    """Show the credentials management dialog"""
    try:
        dialog = CredentialManagerDialog(window)
        dialog.credentials_updated.connect(window.session_navigator.load_sessions)
        dialog.exec()
    except Exception as e:
        logger.error(f"Error showing credentials dialog: {e}")


def show_about_dialog(window):
    """Show the about dialog"""
    try:
        dialog = AboutDialog(window)
        dialog.exec()
    except Exception as e:
        logger.error(f"Error showing about dialog: {e}")


def show_logicmonitor_importer(window):
    """Show the LogicMonitor to Session importer"""
    try:
        window.lmdialog = LMDownloader(window)
        window.lmdialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        window.lmdialog.show()
    except Exception as e:
        logger.error(f"Error showing LogicMonitor importer: {e}")


def safe_close_telemetry_tab(window, tab_widget):
    """
    Safe cleanup when closing telemetry tabs
    Call this when a telemetry tab is closed
    """
    try:
        if hasattr(window, 'telemetry_widgets'):
            # Remove from telemetry widgets list
            if hasattr(tab_widget, 'telemetry_widget') and tab_widget.telemetry_widget in window.telemetry_widgets:
                window.telemetry_widgets.remove(tab_widget.telemetry_widget)
            elif hasattr(tab_widget, 'set_theme_from_parent') and tab_widget in window.telemetry_widgets:
                window.telemetry_widgets.remove(tab_widget)

        # Call cleanup on telemetry widget if it has one
        if hasattr(tab_widget, 'telemetry_widget') and hasattr(tab_widget.telemetry_widget, 'cleanup'):
            tab_widget.telemetry_widget.cleanup()
        elif hasattr(tab_widget, 'cleanup'):
            tab_widget.cleanup()

    except Exception as e:
        print(f"️ Error during telemetry tab cleanup: {e}")