#!/usr/bin/env python3
"""
termtel - A PyQt6 Terminal Emulator
"""
import os
import sys
import socket
import logging
import traceback
from pathlib import Path

import yaml

from termtel.helpers.theme_bootstrap import ThemeBootstrap
from termtel.widgets.qtssh_widget import Ui_Terminal
from termtel.widgets.session_navigator import SessionNavigator
# from termtel.widgets.TelemetryWidget import TelemetryWidget
from termtel.termtelwidgets.telemetry_widget import TelemetryWidget
from termtel.themes3 import ThemeLibrary, LayeredHUDFrame, ThemeMapper

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, \
    QInputDialog, QLineEdit, QStyleFactory
from PyQt6.QtCore import QUrl, QThread, Qt, QCoreApplication, pyqtSignal
from contextlib import closing
from typing import Optional, cast
import click
from termtel.helpers.settings import SettingsManager
from termtel.helpers.credslib import SecureCredentials

from termtel.widgets.setup import setup_menus
from termtel.widgets.terminal_tabs import TerminalTabWidget

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('termtel')

THEME_MAPPING = None
def initialize_sessions():
    sessions_dir = Path('./sessions')
    sessions_dir.mkdir(exist_ok=True)

    # Check for sessions.yaml
    sessions_file = sessions_dir / 'sessions.yaml'

    # Only write default config if file doesn't exist
    if not sessions_file.exists():
        default_config = '''- folder_name: Example
  sessions:
  - DeviceType: linux
    Model: Thinkstation 
    SerialNumber: ''
    SoftwareVersion: ''
    Vendor: Lenovo
    credsid: '1'
    display_name: T1000
    host: 10.0.0.104
    port: '22'
    '''
        # Write the default configuration to sessions.yaml
        try:
            with sessions_file.open('x') as f:
                f.write(default_config)
        except:
            with sessions_file.open("r") as fh:
                print(fh.read())

    return sessions_file



class termtelWindow(QMainWindow):
    credentials_unlocked = pyqtSignal()

    def __init__(self, theme: str = "cyberpunk", session_file: str = "sessions.yaml"):
        super().__init__()
        self.setWindowTitle("TerminalTelemetry")
        # self.server_thread: Optional[FastAPIServer] = None
        self.port = self.find_free_port()
        self.theme = theme
        self.theme_manager = ThemeLibrary()
        self.session_file = session_file
        self.cred_manager = SecureCredentials()
        self.settings_manager = SettingsManager()
        self.setup_themes()

        # Override theme with saved preference if it exists
        self.theme = self.settings_manager.get_app_theme()
        self.master_password = None
        # Initialize UI before applying theme
        self.init_ui()

        self.theme_manager.apply_theme(self, self.theme)
        self.initialize_credentials()


        # self.start_server()
        self.session_navigator.connect_requested.connect(self.handle_session_connect)

    def launch_telemetry(self):
        pass

    def setup_themes(self):
        """Set up theme system with one-time auto-bootstrap"""
        try:
            from termtel.helpers.resource_manager import resource_manager

            # Set up themes directory
            themes_dir = Path('./themes')

            # Initialize theme bootstrap
            self.theme_bootstrap = ThemeBootstrap(resource_manager, themes_dir)

            # Check if this is first run
            if not self.theme_bootstrap._is_bootstrap_complete():
                logger.info("First run detected - bootstrapping themes from package...")
                results = self.theme_bootstrap.bootstrap_themes()

                if results:
                    successful = sum(results.values())
                    total = len(results)
                    logger.info(f"First-run theme setup: {successful}/{total} themes installed")

                    # Update theme manager to scan the populated directory
                    if hasattr(self.theme_manager, 'rescan_themes'):
                        self.theme_manager.rescan_themes()
                    print(f"Initial themes bootstrapped, restart application")
                    sys.exit(0)
            else:
                logger.info("Theme bootstrap already completed - using existing user themes")
                # Still rescan in case user added themes manually
                if hasattr(self.theme_manager, 'rescan_themes'):
                    self.theme_manager.rescan_themes()

        except Exception as e:
            logger.error(f"Theme setup failed: {e}")
            # Continue with basic themes only

    def load_saved_settings(self):
        """Load and apply saved settings."""
        # Apply window geometry if saved
        nav_width = self.settings_manager.get('navigation', 'tree_width', 250)
        if nav_width != 250:  # Only update if different from default
            sizes = self.splitter.sizes()
            total_width = sum(sizes)
            term_width = total_width - nav_width
            self.splitter.setSizes([nav_width, term_width])

        # Apply terminal settings
        term_settings = self.settings_manager.get_section('terminal')
        if term_settings:
            self.terminal_tabs.apply_settings(term_settings)

    def apply_dark_palette(self):
        """Apply dark color palette to the application."""
        dark_palette = QPalette()

        # Base colors
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        app = cast(QApplication, QApplication.instance())
        if app is not None:
            app.setPalette(dark_palette)

    def apply_light_palette(self):
        """Apply an improved light color palette to the application."""
        light_palette = QPalette()

        # Define colors
        background = QColor(248, 248, 248)  # Soft white background
        panel_background = QColor(240, 240, 240)  # Slightly darker for panels
        text = QColor("#000000")  # Soft black for text
        highlight = QColor(0, 120, 215)  # Windows-style blue for selection
        inactive_text = QColor(119, 119, 119)  # Grey for disabled items

        # Base interface colors
        light_palette.setColor(QPalette.ColorRole.Window, background)
        light_palette.setColor(QPalette.ColorRole.WindowText, text)
        light_palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
        light_palette.setColor(QPalette.ColorRole.AlternateBase, panel_background)
        light_palette.setColor(QPalette.ColorRole.Text, text)
        light_palette.setColor(QPalette.ColorRole.Button, panel_background)
        light_palette.setColor(QPalette.ColorRole.ButtonText, text)

        # Selection and highlighting
        light_palette.setColor(QPalette.ColorRole.Highlight, highlight)
        light_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

        # Tooltips
        light_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        light_palette.setColor(QPalette.ColorRole.ToolTipText, text)

        # Links
        light_palette.setColor(QPalette.ColorRole.Link, highlight)
        light_palette.setColor(QPalette.ColorRole.LinkVisited, QColor(0, 100, 200))

        # Disabled state colors
        light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, inactive_text)
        light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, inactive_text)
        light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, inactive_text)

        app = cast(QApplication, QApplication.instance())
        if app is not None:
            app.setPalette(light_palette)

            # Apply additional styling for specific widgets
            app.setStyleSheet("""
                QTreeView {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    padding: 5px;
                    color: #333333;
                }
                QTreeView::item {
                    padding: 5px;
                    border-radius: 2px;
                }
                QTreeView::item:hover {
                    background-color: #f5f5f5;
                }
                QTreeView::item:selected {
                    background-color: #0078d7;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #f8f8f8;
                    color: #333333;
                    padding: 5px;
                    border: none;
                    border-bottom: 1px solid #e0e0e0;
                }
                QLineEdit {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 2px;
                    padding: 5px;
                    color: #333333;
                }
                QLineEdit:focus {
                    border: 1px solid #0078d7;
                }
                QPushButton {
                    background-color: #f8f8f8;
                    border: 1px solid #e0e0e0;
                    border-radius: 2px;
                    padding: 5px 15px;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                    border: 1px solid #d0d0d0;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
                QSplitter::handle {
                    background-color: #e0e0e0;
                    width: 1px;
                }
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    border-top: none;
                }
                QTabBar::tab {
                    background-color: #f8f8f8;
                    color: #333333;
                    padding: 8px 12px;
                    border: 1px solid #e0e0e0;
                    border-bottom: none;
                    margin-right: 2px;
                }
                QTabBar::tab:hover {
                    background-color: #f0f0f0;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 1px solid white;
                }
                QMenuBar {
                    background-color: #f8f8f8;
                    color: #333333;
                    border-bottom: 1px solid #e0e0e0;
                }
                QMenuBar::item:selected {
                    background-color: #f0f0f0;
                }
                QMenu {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #e0e0e0;
                }
                QMenu::item:selected {
                    background-color: #f0f0f0;
                }
                QScrollBar:vertical {
                    background: #f8f8f8;
                    width: 14px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #d0d0d0;
                    min-height: 20px;
                    border-radius: 7px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #b0b0b0;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)


    def init_ui(self):
        self.setWindowTitle('TerminalTelemetry')
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        width = int(screen_geometry.width() * 0.8)
        self.width = width
        height = int(screen_geometry.height() * 0.7)
        center_point = screen_geometry.center()
        self.setGeometry(center_point.x() - width // 2, center_point.y() - height // 2, width, height)
        self.setMinimumSize(800, 500)  # Reasonable minimum size
        self.main_frame = LayeredHUDFrame(self, theme_manager=self.theme_manager, theme_name=self.theme)
        self.setCentralWidget(self.main_frame)

        # Main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_frame.content_layout.addWidget(self.main_splitter)

        # Left side container
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Terminal section splitter
        self.terminal_splitter = QSplitter(Qt.Orientation.Horizontal)
        left_layout.addWidget(self.terminal_splitter)

        # Session Navigator
        nav_frame = LayeredHUDFrame(self, theme_manager=self.theme_manager, theme_name=self.theme)
        self.session_navigator = SessionNavigator(parent=self, cred_manager=self.cred_manager)
        nav_layout = QVBoxLayout()
        nav_frame.content_layout.addLayout(nav_layout)
        nav_layout.addWidget(self.session_navigator)
        nav_frame.setMinimumWidth(150)
        nav_frame.setMaximumWidth(400)
        self.terminal_splitter.addWidget(nav_frame)

        # Terminal Tabs
        term_frame = LayeredHUDFrame(self, theme_manager=self.theme_manager, theme_name=self.theme)
        self.terminal_tabs = TerminalTabWidget(self.port, parent=self)
        term_layout = QVBoxLayout()
        term_frame.content_layout.addLayout(term_layout)
        term_layout.addWidget(self.terminal_tabs)
        self.terminal_splitter.addWidget(term_frame)

        # Add left container to main splitter
        self.main_splitter.addWidget(left_container)

        # Add telemetry panel
        self.telemetry_frame = LayeredHUDFrame(self, theme_manager=self.theme_manager, theme_name=self.theme)
        # self.telemetry = DeviceDashboardWidget(parent=self)
        telemetry_layout = QVBoxLayout()
        self.telemetry_frame.content_layout.addLayout(telemetry_layout)
        # telemetry_layout.addWidget(self.telemetry)
        # self.main_splitter.addWidget(self.telemetry_frame)

        # Set initial telemetry visibility from settings
        telemetry_visible = self.settings_manager.get_view_setting('telemetry_visible', True)
        self.telemetry_frame.setVisible(telemetry_visible)

        # Set proportions
        self.main_splitter.setSizes([int(width * 0.6), int(width * 0.4)])
        self.terminal_splitter.setSizes([250, width - 250])
        setup_menus(self)

    # In termtel.py, add this import
    # def launch_telemetry(window):
    #     """Launch the telemetry interface in a tab"""
    #     try:
    #         # Check if telemetry tab already exists
    #         for i in range(window.terminal_tabs.count()):
    #             if "Telemetry" in window.terminal_tabs.tabText(i):
    #                 # Tab already exists, just select it
    #                 window.terminal_tabs.setCurrentIndex(i)
    #                 return
    #
    #         # Create new telemetry tab
    #         frontend_path = Path(__file__).parent / 'termtelng' / 'frontend'
    #         telemetry_widget = TelemetryWidget(parent=window, base_path=frontend_path)
    #
    #         # Connect cleanup signal
    #         telemetry_widget.cleanup_requested.connect(window.handle_telemetry_cleanup)
    #
    #         # Add tab with an icon if available
    #         try:
    #             from PyQt6.QtGui import QIcon
    #             icon_path = Path(__file__).parent / 'termtelng' / 'frontend' / 'radar.svg'
    #
    #             if icon_path.exists():
    #                 tab_icon = QIcon(str(icon_path))
    #                 index = window.terminal_tabs.addTab(telemetry_widget, tab_icon, "Telemetry")
    #             else:
    #                 index = window.terminal_tabs.addTab(telemetry_widget, "Telemetry")
    #
    #             window.terminal_tabs.setTabToolTip(index, "Terminal Telemetry Dashboard")
    #             window.terminal_tabs.setCurrentIndex(index)  # Switch to the new tab
    #
    #             # Store reference if needed for cleanup
    #             if not hasattr(window, 'telemetry_widgets'):
    #                 window.telemetry_widgets = []
    #             window.telemetry_widgets.append(telemetry_widget)
    #
    #         except Exception as e:
    #             logger.error(f"Error adding telemetry tab: {e}")
    #             traceback.print_exc()
    #
    #     except Exception as e:
    #         logger.error(f"Failed to launch telemetry: {e}")
    #         traceback.print_exc()
    #         QMessageBox.warning(window, "Error", f"Failed to launch telemetry: {e}")

    # Then in the termtelWindow class, add this method
    def add_telemetry_tab(self):
        """Add a terminal telemetry tab to the terminal tabs"""
        try:
            # Create the path to frontend files
            frontend_path = Path(__file__).parent / 'termtelng' / 'frontend'

            # Create the telemetry widget
            # telemetry_widget = TelemetryWidget(parent=self, base_path=frontend_path)

            telemetry_widget = TelemetryWidget()
            # Connect cleanup signal
            # telemetry_widget.cleanup_requested.connect(self.handle_telemetry_cleanup)

            # Add tab with an icon if available
            from PyQt6.QtGui import QIcon
            icon_path = Path(__file__).parent / 'termtelng' / 'frontend' / 'radar.svg'

            if icon_path.exists():
                tab_icon = QIcon(str(icon_path))
                index = self.terminal_tabs.addTab(telemetry_widget, tab_icon, "Telemetry")
            else:
                index = self.terminal_tabs.addTab(telemetry_widget, "Telemetry")

            self.terminal_tabs.setTabToolTip(index, "Terminal Telemetry Dashboard")

            # Store reference
            self.telemetry_widget = telemetry_widget

        except Exception as e:
            logger.error(f"Failed to add telemetry tab: {e}")
            traceback.print_exc()

    def handle_telemetry_cleanup(self):
        """Handle cleanup notification from telemetry widget"""
        try:
            logger.info("Telemetry cleanup requested")

            # Call the synchronous cleanup method directly
            if hasattr(self.telemetry_widget, 'cleanup'):
                self.telemetry_widget.cleanup()

        except Exception as e:
            logger.error(f"Error during telemetry cleanup: {e}")
            traceback.print_exc()

    # In termtel.py, modify the switch_theme method:

    def switch_theme(self, theme_name: str):
        """Override switch_theme to handle both UI and terminal theming."""
        # Update main theme
        self.theme = theme_name
        self.theme_manager.apply_theme(self, theme_name)

        # Save the theme preference
        self.settings_manager.set_app_theme(theme_name)

        # Update all frames
        self.main_frame.set_theme(theme_name)
        for frame in self.findChildren(LayeredHUDFrame):
            frame.set_theme(theme_name)

        # Update session navigator
        self.session_navigator.update_theme(theme_name)

        # Update terminal tabs with the actual theme name
        self.terminal_tabs.update_theme(theme_name)

        # Update telemetry tabs if they exist
        if hasattr(self, 'telemetry_widgets'):
            for telemetry_widget in self.telemetry_widgets:
                telemetry_widget.update_theme(theme_name)
        elif hasattr(self, 'telemetry_widget'):
            self.telemetry_widget.update_theme(theme_name)

        self.terminal_tabs.update_all_theme_aware_widgets(theme_name)

        # Update the application palette based on theme
        if theme_name in ['light_mode']:
            self.apply_light_palette()
        else:
            self.apply_dark_palette()

    # In TerminalTabWidget:
    def update_theme(self, theme_name: str):
        """Update terminal themes."""
        self.current_term_theme = theme_name

        # Update all terminal instances
        for i in range(self.count()):
            tab = self.widget(i)
            if tab:
                terminal = tab.findChild(Ui_Terminal)
                if terminal:
                    # Use the theme manager directly
                    self.parent.theme_manager.apply_theme_to_terminal(terminal, theme_name)
    def handle_session_connect(self, connection_data):
        """Handle connection request."""
        logger.info(f"Connecting to: {connection_data['host']}:{connection_data['port']}")
        # TODO : Error trapping here
        try:
            self.terminal_tabs.create_terminal(connection_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize session to {connection_data['host']}:{connection_data['port']} \nError: {e}")
            print(f"New session failed: {e}")
            traceback.print_exc()
    def find_free_port(self) -> int:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
            logger.info(f"Found available port: {port}")
            return port

    def reset_master_password(self):
        """Reset the master password and recreate credential store."""
        try:
            # Confirm reset
            confirm = QMessageBox.question(
                self,
                "Confirm Reset",
                "WARNING: Resetting the master password will make all saved passwords inaccessible.\n\n"
                "Are you sure you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if confirm != QMessageBox.StandardButton.Yes:
                # Return to password dialog
                self.initialize_credentials()
                return

            # Get new password
            password, ok = QInputDialog.getText(
                self,
                "Set New Master Password",
                "Enter a new master password:",
                QLineEdit.EchoMode.Password
            )

            if not ok or not password:
                # Return to password dialog
                self.initialize_credentials()
                return

            # Confirm new password
            confirm_password, ok = QInputDialog.getText(
                self,
                "Confirm New Master Password",
                "Confirm your new master password:",
                QLineEdit.EchoMode.Password
            )

            if not ok or confirm_password != password:
                QMessageBox.warning(self, "Password Mismatch", "The passwords you entered do not match.")
                # Return to password dialog
                self.initialize_credentials()
                return

            # Reset credentials
            if self.cred_manager.reset_credentials(password):
                self.master_password = password
                QMessageBox.information(
                    self,
                    "Success",
                    "Master password reset successfully. All saved credentials have been cleared."
                )
                self.credentials_unlocked.emit()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to reset master password. Please restart the application."
                )
                QCoreApplication.instance().quit()

        except Exception as e:
            logger.error(f"Failed to reset master password: {e}")
            QMessageBox.critical(self, "Error", f"Failed to reset master password: {e}")
            QCoreApplication.instance().quit()

    def initialize_credentials(self):
        """Initialize the credential system with strict authentication."""
        try:
            # Check if credential store exists
            if not self.cred_manager.is_initialized:
                # First-time setup
                password, ok = QInputDialog.getText(
                    self,
                    "Set Master Password",
                    "No credential store found. Enter a master password to create one:",
                    QLineEdit.EchoMode.Password
                )

                if not ok or not password:
                    QMessageBox.warning(
                        self,
                        "Application Exit",
                        "A master password is required to use this application.\nThe application will now close."
                    )
                    # Force immediate termination
                    sys.exit(1)

                # Create credential store with new password
                if not self.cred_manager.setup_new_credentials(password):
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to initialize credentials. The application will now close."
                    )
                    sys.exit(1)

                self.master_password = password
                self.credentials_unlocked.emit()
            else:
                # Existing credential store - create a separate dialog
                from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

                class PasswordDialog(QDialog):
                    def __init__(self, parent=None):
                        super().__init__(parent)
                        self.setWindowTitle("Unlock Credentials")
                        self.attempts = 0
                        self.max_attempts = 3
                        self.password = ""
                        self.setup_ui()

                    def setup_ui(self):
                        layout = QVBoxLayout()

                        # Add message
                        self.message = QLabel(
                            f"Enter master password ({self.max_attempts - self.attempts} attempts remaining):")
                        layout.addWidget(self.message)

                        # Add password field
                        self.password_field = QLineEdit()
                        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
                        layout.addWidget(self.password_field)

                        # Add buttons
                        button_layout = QHBoxLayout()

                        # Cancel button
                        cancel_button = QPushButton("Cancel")
                        cancel_button.clicked.connect(self.reject)
                        button_layout.addWidget(cancel_button)

                        # Reset button
                        reset_button = QPushButton("Reset Password")
                        reset_button.clicked.connect(lambda: self.done(2))  # Return code 2 for reset
                        button_layout.addWidget(reset_button)

                        # OK button
                        ok_button = QPushButton("OK")
                        ok_button.clicked.connect(self.try_password)
                        self.password_field.returnPressed.connect(self.try_password)  # Enter key
                        button_layout.addWidget(ok_button)

                        layout.addLayout(button_layout)
                        self.setLayout(layout)

                    def try_password(self):
                        self.password = self.password_field.text()
                        self.accept()

                # Create and show the password dialog
                password_dialog = PasswordDialog(self)

                while password_dialog.attempts < password_dialog.max_attempts:
                    result = password_dialog.exec()

                    if result == QDialog.DialogCode.Accepted:
                        # Try to unlock
                        if self.cred_manager.unlock(password_dialog.password):
                            self.master_password = password_dialog.password
                            self.credentials_unlocked.emit()
                            return
                        else:
                            password_dialog.attempts += 1
                            if password_dialog.attempts < password_dialog.max_attempts:
                                password_dialog.message.setText(
                                    f"Invalid password. {password_dialog.max_attempts - password_dialog.attempts} attempts remaining:")
                                password_dialog.password_field.clear()
                            else:
                                QMessageBox.critical(
                                    self,
                                    "Access Denied",
                                    "Maximum password attempts exceeded.\nThe application will now close."
                                )
                                sys.exit(1)

                    elif result == QDialog.DialogCode.Rejected:
                        # User cancelled
                        QMessageBox.warning(
                            self,
                            "Application Exit",
                            "Authentication is required to use this application.\nThe application will now close."
                        )
                        sys.exit(1)

                    elif result == 2:  # Reset password code
                        self.reset_master_password()
                        return

        except Exception as e:
            logger.error(f"Failed to initialize credentials: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to initialize credentials: {e}\nThe application will now close."
            )
            sys.exit(1)

    def start_server(self):
        try:
            pass
            # settings['theme'] = self.theme
            # settings['sessionfile'] = self.session_file
            #
            # # self.server_thread = FastAPIServer(app, self.port)
            # # self.server_thread.start()
            #
            # # Load sessions after server starts
            # from PyQt6.QtCore import QTimer
            # QTimer.singleShot(1000, self.load_sessions)
            # logger.info(f"Server started on port {self.port}")

        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            self.close()

    def load_sessions(self):
        """Load sessions from the YAML file."""
        try:
            with open(self.session_file) as f:
                sessions_data = yaml.safe_load(f)
            self.session_navigator.load_sessions(sessions_data)
        except Exception as e:
            logger.error(f"Failed to load sessions: {str(e)}")

    def closeEvent(self, event):
        """Handle application closure."""
        # Clean up terminals
        if hasattr(self, 'terminal_tabs'):
            self.terminal_tabs.cleanup_all()
        if hasattr(self, 'telemetry_widgets'):
            for telemetry_widget in self.telemetry_widgets:
                try:
                    telemetry_widget.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up telemetry widget: {e}")

            # Clean up main telemetry widget if it exists
        if hasattr(self, 'telemetry_widget'):
            try:
                self.telemetry_widget.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up telemetry widget: {e}")
        # Shut down server
        # if self.server_thread and self.server_thread.isRunning():
        #     logger.info("Shutting down server...")
        #     self.server_thread.terminate()
        #     self.server_thread.wait()
        event.accept()


def setup_logging():
    """Configure logging to write to a file instead of stdout."""
    log_dir = Path.home() / "./termtel" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "termtel.log"
    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def redirect_output():
    """Redirect stdout and stderr to devnull when running in GUI mode."""
    if hasattr(sys, 'frozen'):  # Running as compiled executable
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    else:  # Running from pythonw
        if sys.executable.endswith('pythonw.exe'):
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')


def main():
    """termtel - A modern terminal emulator."""

    # Import Qt classes at the top to avoid scoping issues
    from PyQt6.QtWidgets import QApplication, QMessageBox

    # CRITICAL: Install global exception handler FIRST (before any other code)
    import time
    import traceback
    from pathlib import Path

    def global_exception_handler(exc_type, exc_value, exc_traceback):
        """Handle all unhandled exceptions - critical for pythonw.exe debugging"""

        # Skip keyboard interrupts (let them work normally)
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Create crash log in user's home directory
        crash_log = Path.home() / "termtel_crash.log"

        try:
            with open(crash_log, "a", encoding='utf-8') as f:
                f.write(f"\n{'=' * 60}\n")
                f.write(f"TERMTEL CRASH - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'=' * 60}\n")
                f.write(f"Python Executable: {sys.executable}\n")
                f.write(f"Running under pythonw: {sys.executable.endswith('pythonw.exe')}\n")
                f.write(f"Working Directory: {os.getcwd()}\n")
                f.write(f"Exception Type: {exc_type.__name__}\n")
                f.write(f"Exception Message: {exc_value}\n")
                f.write(f"\nFull Traceback:\n")
                f.write("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                f.write(f"\n{'=' * 60}\n\n")
        except Exception as log_error:
            # If we can't write to the log file, try a backup location
            try:
                backup_log = Path("termtel_crash_backup.log")
                with open(backup_log, "a", encoding='utf-8') as f:
                    f.write(f"CRASH: {exc_type.__name__}: {exc_value}\n")
                    f.write(f"Log error: {log_error}\n")
            except:
                pass  # Last resort: fail silently

        # Try to show error dialog if Qt is available
        try:
            existing_app = QApplication.instance()
            if existing_app:
                error_msg = (
                    f"TermTel has encountered a critical error:\n\n"
                    f"{exc_type.__name__}: {exc_value}\n\n"
                    f"Details have been logged to:\n{crash_log}\n\n"
                    f"Please report this error with the log file contents."
                )
                QMessageBox.critical(None, "TermTel Critical Error", error_msg)
            else:
                # Qt not available, try creating minimal app for the dialog
                temp_app = QApplication(sys.argv)
                QMessageBox.critical(None, "TermTel Critical Error",
                                     f"Critical error occurred. Check {crash_log} for details.")
                temp_app.quit()
        except Exception:
            pass  # If Qt dialog fails, continue silently

        # Also try to write to stderr if it exists (for console debugging)
        try:
            if sys.stderr:
                print(f"\nCRITICAL ERROR: {exc_type.__name__}: {exc_value}", file=sys.stderr)
                print(f"Details logged to: {crash_log}", file=sys.stderr)
        except:
            pass

    # Install the global exception handler
    sys.excepthook = global_exception_handler

    # Create a startup logger for this session
    startup_log = Path.home() / "termtel_startup.log"

    try:
        # Set up logging before anything else
        setup_logging()

        # Log startup information
        startup_logger = logging.getLogger('termtel.startup')
        startup_logger.info("=" * 50)
        startup_logger.info(f"TERMTEL STARTUP - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        startup_logger.info(f"Python: {sys.version}")
        startup_logger.info(f"Executable: {sys.executable}")
        startup_logger.info(f"Running under pythonw: {sys.executable.endswith('pythonw.exe')}")
        startup_logger.info(f"stdout available: {sys.stdout is not None}")
        startup_logger.info(f"stderr available: {sys.stderr is not None}")
        startup_logger.info(f"Working directory: {os.getcwd()}")

        # Redirect output if running in GUI mode
        startup_logger.info("Redirecting output...")
        redirect_output()

        startup_logger.info("Initializing sessions...")
        initialize_sessions()

        startup_logger.info("Creating QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("termtel")

        # Install Qt-specific error handling
        def qt_message_handler(msg_type, context, message):
            """Handle Qt framework messages"""
            qt_logger = logging.getLogger('termtel.qt')
            if msg_type == 0:  # QtDebugMsg
                qt_logger.debug(f"Qt: {message}")
            elif msg_type == 1:  # QtWarningMsg
                qt_logger.warning(f"Qt: {message}")
            elif msg_type == 2:  # QtCriticalMsg
                qt_logger.error(f"Qt Critical: {message}")
            elif msg_type == 3:  # QtFatalMsg
                qt_logger.critical(f"Qt Fatal: {message}")
                # Qt fatal errors should trigger our crash handler
                raise RuntimeError(f"Qt Fatal Error: {message}")

        # Install Qt message handler (if available in PyQt6)
        try:
            from PyQt6.QtCore import qInstallMessageHandler
            qInstallMessageHandler(qt_message_handler)
            startup_logger.info("Qt message handler installed")
        except ImportError:
            startup_logger.warning("Qt message handler not available")

        theme = "cyberpunk"
        startup_logger.info(f"Setting theme: {theme}")

        # Create theme manager instance
        startup_logger.info("Creating theme manager...")
        theme_manager = ThemeLibrary()

        # Validate theme
        if theme not in theme_manager.themes:
            startup_logger.warning(f"Theme '{theme}' not found, using 'cyberpunk'")
            logging.warning(f"Theme '{theme}' not found, using 'cyberpunk'")
            theme = 'cyberpunk'

        startup_logger.info("Creating main window...")
        window = termtelWindow(theme=theme)

        startup_logger.info("Showing main window...")
        window.show()

        startup_logger.info("Starting Qt event loop...")
        result = app.exec()

        startup_logger.info(f"Application exited normally with code: {result}")
        return result

    except Exception as e:
        # This catch block handles exceptions in the startup process itself
        error_msg = f"Fatal error during startup: {e}"

        # Log to file
        try:
            with open(startup_log, "a", encoding='utf-8') as f:
                f.write(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - STARTUP FAILURE\n")
                f.write(f"Error: {error_msg}\n")
                f.write(traceback.format_exc())
                f.write("\n" + "=" * 50 + "\n")
        except:
            pass

        # Log using logging system if available
        try:
            logging.exception("Fatal error in main")
        except:
            pass

        # Try to show error dialog
        try:
            existing_app = QApplication.instance()
            if existing_app:
                app = existing_app
            else:
                app = QApplication(sys.argv)
            QMessageBox.critical(None, "Startup Error",
                                 f"TermTel failed to start:\n\n{error_msg}\n\nCheck {startup_log} for details.")
        except Exception as dialog_error:
            # If showing dialog fails, just continue silently
            pass

        # Re-raise to trigger global exception handler
        raise


if __name__ == '__main__':
    sys.exit(main())