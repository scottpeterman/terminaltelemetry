# widgets/credential_manager.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QMenu, QAbstractItemView, QWidget,
                             QInputDialog, QFileDialog, QCheckBox, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
import logging
import uuid
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import yaml

from termtel.helpers.credslib import SecureCredentials

logger = logging.getLogger(__name__)


class CredentialEditDialog(QDialog):
    """Dialog for adding/editing individual credentials with SSH key support."""

    def __init__(self, cred_data: Dict = None, parent=None):
        super().__init__(parent)
        self.cred_data = cred_data or {
            'uuid': str(uuid.uuid4()),
            'username': '',
            'password': '',
            'display_name': '',
            'key_path': ''
        }
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Edit Credential")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Create form layout
        form_layout = QFormLayout()

        # Display Name field
        self.display_name_input = QLineEdit(self.cred_data.get('display_name', ''))
        form_layout.addRow("Display Name:", self.display_name_input)

        # Username field
        self.username_input = QLineEdit(self.cred_data.get('username', ''))
        form_layout.addRow("Username:", self.username_input)

        # Password field
        self.password_input = QLineEdit(self.cred_data.get('password', ''))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        # SSH Key section
        key_group = QWidget()
        key_layout = QVBoxLayout(key_group)
        key_layout.setContentsMargins(0, 10, 0, 0)

        # Separator
        separator_label = QLabel("SSH Key Authentication (Optional)")
        separator_label.setStyleSheet("font-weight: bold; padding: 5px 0;")
        key_layout.addWidget(separator_label)

        # SSH Key file selector
        key_file_layout = QHBoxLayout()
        self.key_path_input = QLineEdit(self.cred_data.get('key_path', ''))
        self.key_path_input.setPlaceholderText("Path to SSH private key (e.g., ~/.ssh/id_rsa)")
        self.key_browse_btn = QPushButton("Browse...")
        self.key_browse_btn.clicked.connect(self.browse_key_file)

        key_file_layout.addWidget(QLabel("SSH Key:"))
        key_file_layout.addWidget(self.key_path_input)
        key_file_layout.addWidget(self.key_browse_btn)
        key_layout.addLayout(key_file_layout)

        # Info label
        info_label = QLabel(
            "Leave SSH Key blank to use password authentication or default keys from ~/.ssh_manager/keys.json")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 10px; font-style: italic; padding: 5px;")
        key_layout.addWidget(info_label)

        layout.addWidget(key_group)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def browse_key_file(self):
        """Open file dialog to select SSH key"""
        default_dir = str(Path.home() / ".ssh")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SSH Private Key",
            default_dir,
            "SSH Keys (id_rsa id_ed25519 id_ecdsa id_dsa);;All Files (*)"
        )

        if file_path:
            self.key_path_input.setText(file_path)

    def get_credentials(self) -> Dict:
        """Return the current credential data."""
        self.cred_data.update({
            'display_name': self.display_name_input.text(),
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'key_path': self.key_path_input.text().strip()
        })
        return self.cred_data


class CredentialManagerDialog(QDialog):
    """Main dialog for managing credentials with SSH key support."""

    credentials_updated = pyqtSignal()  # Signal when credentials are modified

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cred_manager = SecureCredentials()
        self.setup_ui()
        self.initialize_and_load()

    def setup_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Credential Manager")
        self.setModal(True)
        self.resize(900, 400)

        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        # Left side buttons
        left_buttons = QHBoxLayout()
        add_button = QPushButton("Add Credential")
        add_button.clicked.connect(self.add_credential)
        left_buttons.addWidget(add_button)

        # Right side buttons
        right_buttons = QHBoxLayout()
        import_button = QPushButton("Import...")
        import_button.clicked.connect(self.import_credentials)
        export_button = QPushButton("Export...")
        export_button.clicked.connect(self.export_credentials)

        right_buttons.addWidget(import_button)
        right_buttons.addWidget(export_button)

        toolbar.addLayout(left_buttons)
        toolbar.addStretch()
        toolbar.addLayout(right_buttons)

        layout.addLayout(toolbar)

        # Credentials table
        self.creds_table = QTableWidget()
        self.creds_table.setColumnCount(4)  # Added SSH Key column
        self.creds_table.setHorizontalHeaderLabels(["Display Name", "Username", "Password", "SSH Key"])
        self.creds_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.creds_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.creds_table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.creds_table)

        # Bottom buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def show_context_menu(self, position):
        """Show context menu for credential entries."""
        menu = QMenu()
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)

        edit_action.triggered.connect(self.edit_credential)
        delete_action.triggered.connect(self.delete_credential)

        menu.addAction(edit_action)
        menu.addAction(delete_action)

        menu.exec(self.creds_table.viewport().mapToGlobal(position))

    def initialize_and_load(self):
        """Initialize the credential system and load credentials."""
        try:
            if not self.cred_manager.is_initialized:
                if not self.initialize_credentials():
                    self.reject()
                    return

            if not self.cred_manager.is_unlocked():
                if not self.unlock_credentials():
                    self.reject()
                    return

            try:
                self.load_credentials()
            except Exception as e:
                logger.error(f"Failed to load credentials file: {e}")
                reply = QMessageBox.question(
                    self,
                    "Corrupt Credentials",
                    "The credentials file appears to be corrupt or invalid.\n\n"
                    "Would you like to:\n"
                    "Yes - Delete and create new credentials file\n"
                    "No - Exit credential manager",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        creds_path = self.cred_manager.config_dir / "credentials.yaml"
                        if creds_path.exists():
                            creds_path.unlink()

                        self.cred_manager.save_credentials([], creds_path)
                        self.load_credentials()

                        QMessageBox.information(
                            self,
                            "Reset Complete",
                            "Credentials file has been reset. You can now add new credentials."
                        )
                    except Exception as e2:
                        logger.error(f"Failed to reset credentials: {e2}")
                        QMessageBox.critical(
                            self,
                            "Error",
                            f"Failed to reset credentials: {e2}"
                        )
                        self.reject()
                else:
                    self.reject()

        except Exception as e:
            logger.error(f"Failed to initialize and load: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize: {e}")
            self.reject()

    def load_credentials(self):
        """Load credentials into the table."""
        try:
            creds_path = self.cred_manager.config_dir / "credentials.yaml"

            if not creds_path.exists():
                self.cred_manager.save_credentials([], creds_path)
                self.creds_table.setRowCount(0)
                return

            creds_list = self.cred_manager.load_credentials(creds_path)

            self.creds_table.setRowCount(len(creds_list))
            for row, cred in enumerate(creds_list):
                display_name_item = QTableWidgetItem(cred['display_name'])
                username_item = QTableWidgetItem(cred['username'])
                password_item = QTableWidgetItem('********')

                # Show key path or empty
                key_path = cred.get('key_path', '')
                if key_path:
                    # Show just the filename or last part of path
                    key_display = Path(key_path).name
                    key_item = QTableWidgetItem(f"🔑 {key_display}")
                else:
                    key_item = QTableWidgetItem("")

                # Store the full credential data in the first column
                display_name_item.setData(Qt.ItemDataRole.UserRole, cred)

                self.creds_table.setItem(row, 0, display_name_item)
                self.creds_table.setItem(row, 1, username_item)
                self.creds_table.setItem(row, 2, password_item)
                self.creds_table.setItem(row, 3, key_item)

            self.creds_table.resizeColumnsToContents()

        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise

    def initialize_credentials(self) -> bool:
        """Initialize the credential system with a new master password."""
        reply = QMessageBox.question(
            self,
            "Initialize Credentials",
            "No credential store found. Would you like to create one?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            password, ok = QInputDialog.getText(
                self,
                "Set Master Password",
                "Enter master password:",
                QLineEdit.EchoMode.Password
            )

            if ok and password:
                return self.cred_manager.setup_new_credentials(password)

        return False

    def unlock_credentials(self) -> bool:
        """Unlock the credential system."""
        password, ok = QInputDialog.getText(
            self,
            "Unlock Credentials",
            "Enter master password:",
            QLineEdit.EchoMode.Password
        )

        if ok and password:
            return self.cred_manager.unlock(password)

        return False

    def add_credential(self):
        """Add a new credential."""
        dialog = CredentialEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                cred_data = dialog.get_credentials()

                creds_path = self.cred_manager.config_dir / "credentials.yaml"
                creds_list = self.cred_manager.load_credentials(creds_path)

                creds_list.append(cred_data)

                self.cred_manager.save_credentials(creds_list, creds_path)
                self.load_credentials()
                self.credentials_updated.emit()

            except Exception as e:
                logger.error(f"Failed to add credential: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add credential: {e}")

    def edit_credential(self):
        """Edit the selected credential."""
        current_row = self.creds_table.currentRow()
        if current_row >= 0:
            cred_data = self.creds_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)

            dialog = CredentialEditDialog(cred_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    updated_cred = dialog.get_credentials()

                    creds_path = self.cred_manager.config_dir / "credentials.yaml"
                    creds_list = self.cred_manager.load_credentials(creds_path)

                    for i, cred in enumerate(creds_list):
                        if cred['uuid'] == updated_cred['uuid']:
                            creds_list[i] = updated_cred
                            break

                    self.cred_manager.save_credentials(creds_list, creds_path)
                    self.load_credentials()
                    self.credentials_updated.emit()

                except Exception as e:
                    logger.error(f"Failed to update credential: {e}")
                    QMessageBox.critical(self, "Error", f"Failed to update credential: {e}")

    def delete_credential(self):
        """Delete the selected credential."""
        current_row = self.creds_table.currentRow()
        if current_row >= 0:
            cred_data = self.creds_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)

            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the credential for {cred_data['display_name']}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    creds_path = self.cred_manager.config_dir / "credentials.yaml"
                    creds_list = self.cred_manager.load_credentials(creds_path)
                    creds_list = [c for c in creds_list if c['uuid'] != cred_data['uuid']]

                    self.cred_manager.save_credentials(creds_list, creds_path)
                    self.load_credentials()
                    self.credentials_updated.emit()

                except Exception as e:
                    logger.error(f"Failed to delete credential: {e}")
                    QMessageBox.critical(self, "Error", f"Failed to delete credential: {e}")

    def export_credentials(self):
        """Export credentials to an encrypted file."""
        try:
            if not self.cred_manager.is_unlocked():
                if not self.unlock_credentials():
                    return

            password, ok = QInputDialog.getText(
                self,
                "Export Password",
                "Enter a password to protect the exported credentials:",
                QLineEdit.EchoMode.Password
            )

            if not ok or not password:
                return

            export_manager = SecureCredentials("TermtelExport")
            if not export_manager.setup_new_credentials(password):
                raise Exception("Failed to initialize export encryption")

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Credentials",
                str(Path.home() / "termtel_credentials.yaml"),
                "YAML Files (*.yaml);;All Files (*.*)"
            )

            if not file_path:
                return

            creds_path = self.cred_manager.config_dir / "credentials.yaml"
            creds_list = self.cred_manager.load_credentials(creds_path)

            export_path = Path(file_path)
            export_manager.save_credentials(creds_list, export_path)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Credentials exported successfully to:\n{file_path}\n\n"
                f"Keep the export password safe - you'll need it to import these credentials."
            )

        except Exception as e:
            logger.error(f"Failed to export credentials: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export credentials: {e}")

    def import_credentials(self):
        """Import credentials from an encrypted file."""
        try:
            if not self.cred_manager.is_unlocked():
                if not self.unlock_credentials():
                    return

            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Credentials",
                str(Path.home()),
                "YAML Files (*.yaml);;All Files (*.*)"
            )

            if not file_path:
                return

            password, ok = QInputDialog.getText(
                self,
                "Import Password",
                "Enter the password for the exported credentials:",
                QLineEdit.EchoMode.Password
            )

            if not ok or not password:
                return

            import_manager = SecureCredentials("TermtelExport")
            if not import_manager.unlock(password):
                QMessageBox.critical(self, "Import Error", "Invalid import password")
                return

            import_path = Path(file_path)
            imported_creds = import_manager.load_credentials(import_path)

            if not imported_creds:
                QMessageBox.warning(self, "Import Warning", "No credentials found in import file")
                return

            reply = QMessageBox.question(
                self,
                "Confirm Import",
                f"Found {len(imported_creds)} credentials to import.\n\n"
                f"Do you want to:\n"
                f"Yes - Add to existing credentials\n"
                f"No - Replace all existing credentials",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return

            current_creds = []
            if reply == QMessageBox.StandardButton.Yes:
                creds_path = self.cred_manager.config_dir / "credentials.yaml"
                current_creds = self.cred_manager.load_credentials(creds_path)

                for cred in imported_creds:
                    cred['uuid'] = str(uuid.uuid4())

                final_creds = current_creds + imported_creds
            else:
                final_creds = imported_creds

            creds_path = self.cred_manager.config_dir / "credentials.yaml"
            self.cred_manager.save_credentials(final_creds, creds_path)

            self.load_credentials()
            self.credentials_updated.emit()

            QMessageBox.information(
                self,
                "Import Complete",
                f"Successfully imported {len(imported_creds)} credentials."
            )

        except Exception as e:
            logger.error(f"Failed to import credentials: {e}")
            QMessageBox.critical(self, "Import Error", f"Failed to import credentials: {e}")