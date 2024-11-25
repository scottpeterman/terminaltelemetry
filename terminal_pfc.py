import socket
import threading
from tkinter import messagebox, ttk
import tkinter as tk  # Correct import for tkinter
from terminal import Terminal


class ConnectionTester:
    @staticmethod
    def test_connection(host, port, timeout=5):
        """
        Test if a connection can be established to the given host and port.

        Args:
            host (str): The hostname or IP address to test
            port (int): The port number to test
            timeout (int): Connection timeout in seconds

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except (socket.gaierror, socket.error) as e:
            return False


class TerminalWithPrecheck(Terminal):
    def __init__(self, master=None, ssh_config=None, log_file=None, font_size=10, *args, **kwargs):
        # Store the parent window reference for showing dialog
        self.master_window = master

        # Verify connection before proceeding
        if not self._verify_connection(ssh_config):
            raise ConnectionError(f"Unable to connect to {ssh_config['hostname']}:{ssh_config['port']}")

        # Call parent constructor if connection check passes
        super().__init__(master, ssh_config, log_file, font_size, *args, **kwargs)

    def _verify_connection(self, ssh_config):
        """
        Verify connection before attempting SSH.
        Returns True if connection is possible, False otherwise.
        """
        host = ssh_config['hostname']
        port = ssh_config['port']

        # Create and show a "Testing Connection" dialog
        dialog = self._create_testing_dialog()

        # Run the connection test in a separate thread
        test_result = [False]  # Using list to store result from thread

        def test_connection():
            test_result[0] = ConnectionTester.test_connection(host, port)
            self.master_window.after(0, dialog.destroy)  # Destroy dialog on main thread

        # Start connection test in separate thread
        thread = threading.Thread(target=test_connection)
        thread.daemon = True
        thread.start()

        # Show dialog while testing
        dialog.grab_set()
        self.master_window.wait_window(dialog)

        if not test_result[0]:
            messagebox.showerror(
                "Connection Failed",
                f"Could not connect to {host}:{port}.\nPlease verify the host is reachable and the port is open."
            )

        return test_result[0]

    def _create_testing_dialog(self):
        """Create a simple dialog showing 'Testing Connection'"""
        dialog = tk.Toplevel(self.master_window)
        dialog.title("Connecting")
        dialog.transient(self.master_window)
        dialog.resizable(False, False)

        # Center the dialog
        window_width = 250
        window_height = 100
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        dialog.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Add message
        ttk.Label(
            dialog,
            text="Testing Connection...\nPlease wait.",
            justify='center',
            padding=20
        ).pack(expand=True)

        return dialog