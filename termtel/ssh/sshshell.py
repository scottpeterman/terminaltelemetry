from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from .sshshellreader import ShellReaderThread
from .ssh_key_config import SSHKeyConfig
from PyQt6.QtWidgets import QMessageBox
import paramiko
import warnings
import socket


class Backend(QObject):
    send_output = pyqtSignal(str)
    buffer = ""

    def __init__(self, host, username, password=None, port='22', key_path=None, parent_widget=None, parent=None):
        super().__init__(parent)
        self.parent_widget = parent_widget
        self.client = None
        self.channel = None
        self.reader_thread = None
        self.auth_method_used = None

        # Initialize SSH key config manager
        self.key_config = SSHKeyConfig()

        # Define preferred cipher, kex, and key settings for better compatibility
        self.cipher_settings = (
            "aes128-ctr",
            "aes192-ctr",
            "aes256-ctr",
            "aes128-gcm@openssh.com",
            "aes256-gcm@openssh.com",
            "chacha20-poly1305@openssh.com",
            "aes128-cbc",
            "aes192-cbc",
            "aes256-cbc",
            "3des-cbc",
        )

        self.kex_settings = (
            "diffie-hellman-group14-sha256",
            "diffie-hellman-group-exchange-sha256",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group14-sha1",
            "diffie-hellman-group-exchange-sha1",
            "diffie-hellman-group1-sha1",
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "curve25519-sha256",
            "curve25519-sha256@libssh.org",
        )

        self.key_settings = (
            "rsa-sha2-512",
            "rsa-sha2-256",
            "ssh-rsa",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
            "ssh-ed25519",
            "ssh-dss",
        )

        try:
            # Apply transport settings
            self._apply_transport_settings()

            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            host = str(host).strip()
            username = str(username).strip()
            port = int(port)

            # Check if password is blank and use key auth
            password = str(password).strip() if password else ""

            if password == "" and key_path is None:
                # Password is blank and no explicit key_path provided
                print(f"Password is blank, attempting key-based authentication")
                detected_key_path = self.key_config.get_key_path(host=host, username=username)

                if detected_key_path:
                    print(f"Found key in config: {detected_key_path}")
                    self._try_key_auth(host, port, username, detected_key_path)
                else:
                    self.notify("Authentication Error",
                                f"No password provided and no SSH key found in config.\n"
                                f"Please configure a key in ~/.ssh_manager/keys.json")
                    return
            elif key_path:
                # Explicit key_path was provided
                self._try_key_auth(host, port, username, key_path)
            else:
                # Password authentication
                available_methods = self._detect_available_auth_methods(host, port, username)
                auth_methods_to_try = ["password", "keyboard-interactive"]

                if available_methods:
                    auth_methods_to_try = [method for method in auth_methods_to_try if method in available_methods]
                    if not auth_methods_to_try:
                        print(f"No matching auth methods found, falling back to defaults")
                        auth_methods_to_try = ["password", "keyboard-interactive"]

                auth_success = False
                for auth_method in auth_methods_to_try:
                    if auth_success:
                        break

                    try:
                        if auth_method == "password":
                            print(f"Trying password authentication")
                            self._try_password_auth(host, port, username, password)
                            auth_success = True
                            self.auth_method_used = "password"
                        elif auth_method == "keyboard-interactive":
                            print(f"Trying keyboard-interactive authentication")
                            self._try_keyboard_interactive_auth(host, port, username, password)
                            auth_success = True
                            self.auth_method_used = "keyboard-interactive"
                    except (paramiko.AuthenticationException, paramiko.SSHException) as e:
                        print(f"Auth method {auth_method} failed: {e}")
                        continue

                if not auth_success:
                    self.notify("Login Failure", f"All authentication methods failed for {host}")
                    return

            # Get transport and set keepalive
            transport = self.client.get_transport()
            if transport:
                transport.set_keepalive(60)

                # Log negotiated security options for debugging
                print(f"✓ Transport acquired")
                print(f"  Negotiated cipher: {transport.remote_cipher}")
                print(f"  Negotiated MAC: {transport.remote_mac}")
                # KEX algorithm is stored differently in Paramiko
                if hasattr(transport, 'kex_algorithm'):
                    print(f"  Negotiated KEX: {transport.kex_algorithm}")
                elif hasattr(transport, '_agreed_kex_algorithm'):
                    print(f"  Negotiated KEX: {transport._agreed_kex_algorithm}")
                else:
                    print(f"  Negotiated KEX: (not available)")
            else:
                print("✗ ERROR: No transport available!")
                self.notify("Connection Error", "Failed to get transport from client")
                return

            print("Setting up shell...")
            self.setup_shell()
            print("✓ Backend initialization complete!")

        except Exception as e:
            self.notify("Connection Error", str(e))
            print(f"✗ Backend initialization failed: {e}")
            import traceback
            traceback.print_exc()

    def _apply_transport_settings(self):
        """Apply custom transport settings for better compatibility with network devices"""
        # Suppress deprecation warnings for legacy algorithms
        warnings.filterwarnings('ignore', category=DeprecationWarning, module='paramiko')

        # Get what Paramiko actually supports by checking the Transport class
        # Create a temporary transport to see what's available
        try:
            import paramiko.transport as transport_module

            # Check what's actually registered in Paramiko
            available_ciphers = list(transport_module.Transport._cipher_info.keys())
            available_kex = list(transport_module.Transport._kex_info.keys())
            available_keys = list(transport_module.Transport._key_info.keys())

            print(f"Paramiko supports:")
            print(f"  Ciphers: {', '.join(available_ciphers[:5])}... ({len(available_ciphers)} total)")
            print(f"  KEX: {', '.join(available_kex[:5])}... ({len(available_kex)} total)")
            print(f"  Keys: {', '.join(available_keys[:5])}... ({len(available_keys)} total)")

            # Filter our preferences to only what's available
            self.cipher_settings = tuple([c for c in self.cipher_settings if c in available_ciphers])
            self.kex_settings = tuple([k for k in self.kex_settings if k in available_kex])
            self.key_settings = tuple([k for k in self.key_settings if k in available_keys])

        except Exception as e:
            print(f"Warning: Could not detect available algorithms: {e}")
            print("Using default settings (may cause errors)")

        # Apply globally to paramiko Transport class
        paramiko.Transport._preferred_ciphers = self.cipher_settings
        paramiko.Transport._preferred_kex = self.kex_settings
        paramiko.Transport._preferred_keys = self.key_settings

        print(f"\nApplied transport settings:")
        print(f"  Ciphers: {', '.join(self.cipher_settings[:3])}... ({len(self.cipher_settings)} total)")
        print(f"  KEX: {', '.join(self.kex_settings[:3])}... ({len(self.kex_settings)} total)")
        print(f"  Keys: {', '.join(self.key_settings[:3])}... ({len(self.key_settings)} total)")

    def _detect_server_algorithms(self, host, port, timeout=5):
        """Detect what algorithms the server supports (with timeout)"""
        print(f"\n=== Detecting server algorithms for {host}:{port} ===")
        transport = None

        try:
            # Create socket with timeout to prevent hanging
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))

            transport = paramiko.Transport(sock)

            # Try to capture the KEX init packet
            # We need to hook in before start_client completes negotiation
            old_parse_kex_init = transport._parse_kex_init
            server_kex_data = {}

            def capture_kex_init(m):
                # Capture the server's proposals
                cookie = m.get_bytes(16)
                kex_algo_list = m.get_list()
                server_key_algo_list = m.get_list()
                client_encrypt_algo_list = m.get_list()
                server_encrypt_algo_list = m.get_list()
                client_mac_algo_list = m.get_list()
                server_mac_algo_list = m.get_list()
                client_compress_algo_list = m.get_list()
                server_compress_algo_list = m.get_list()

                server_kex_data['kex'] = kex_algo_list
                server_kex_data['server_key'] = server_key_algo_list
                server_kex_data['cipher_c2s'] = client_encrypt_algo_list
                server_kex_data['cipher_s2c'] = server_encrypt_algo_list
                server_kex_data['mac_c2s'] = client_mac_algo_list
                server_kex_data['mac_s2c'] = server_mac_algo_list

                # Call the original method
                m.rewind()  # Reset message position
                return old_parse_kex_init(m)

            transport._parse_kex_init = capture_kex_init
            transport.start_client(timeout=timeout)

            if server_kex_data:
                print("SERVER PROPOSES:")
                print(f"  Ciphers (c->s): {', '.join(server_kex_data['cipher_c2s'][:5])}")
                if len(server_kex_data['cipher_c2s']) > 5:
                    print(f"                  ... and {len(server_kex_data['cipher_c2s']) - 5} more")

                print(f"  Ciphers (s->c): {', '.join(server_kex_data['cipher_s2c'][:5])}")
                if len(server_kex_data['cipher_s2c']) > 5:
                    print(f"                  ... and {len(server_kex_data['cipher_s2c']) - 5} more")

                print(f"  KEX algorithms: {', '.join(server_kex_data['kex'][:5])}")
                if len(server_kex_data['kex']) > 5:
                    print(f"                  ... and {len(server_kex_data['kex']) - 5} more")

                print(f"  Host key types: {', '.join(server_kex_data['server_key'][:5])}")
                if len(server_kex_data['server_key']) > 5:
                    print(f"                  ... and {len(server_kex_data['server_key']) - 5} more")

                print(f"  MACs (c->s):    {', '.join(server_kex_data['mac_c2s'][:5])}")
                if len(server_kex_data['mac_c2s']) > 5:
                    print(f"                  ... and {len(server_kex_data['mac_c2s']) - 5} more")

                # Check for compatibility
                our_ciphers = set(self.cipher_settings)
                server_ciphers = set(server_kex_data['cipher_c2s'])
                common_ciphers = our_ciphers & server_ciphers

                our_kex = set(self.kex_settings)
                server_kex = set(server_kex_data['kex'])
                common_kex = our_kex & server_kex

                our_keys = set(self.key_settings)
                server_keys = set(server_kex_data['server_key'])
                common_keys = our_keys & server_keys

                print("\nCOMPATIBILITY CHECK:")
                if common_ciphers:
                    print(f"  ✓ Common ciphers: {', '.join(list(common_ciphers)[:5])}")
                else:
                    print(f"  ✗ WARNING: No common ciphers!")
                    print(f"    We have: {', '.join(list(our_ciphers)[:3])}")
                    print(f"    Server wants: {', '.join(list(server_ciphers)[:3])}")

                if common_kex:
                    print(f"  ✓ Common KEX:     {', '.join(list(common_kex)[:5])}")
                else:
                    print(f"  ✗ WARNING: No common KEX algorithms!")

                if common_keys:
                    print(f"  ✓ Common keys:    {', '.join(list(common_keys)[:5])}")
                else:
                    print(f"  ✗ WARNING: No common host key types!")

                print("=" * 60)
                return True
            else:
                print("Could not capture server's algorithm proposals")
                print("=" * 60)
                return False

        except socket.timeout:
            print(f"Timeout (connection took >{timeout}s)")
            print("=" * 60)
            return False
        except Exception as e:
            print(f"Detection failed: {e}")
            import traceback
            traceback.print_exc()
            print("=" * 60)
            return False
        finally:
            if transport and transport.is_active():
                try:
                    transport.close()
                except:
                    pass

    def _detect_available_auth_methods(self, host, port, username):
        """Detect available authentication methods from the server"""
        print(f"Detecting supported authentication methods for {host}")
        transport = None

        try:
            transport = paramiko.Transport((host, port))
            transport.start_client()

            try:
                transport.auth_none(username)
            except paramiko.ssh_exception.BadAuthenticationType as e:
                available_methods = e.allowed_types
                print(f"Server auth methods: {', '.join(available_methods)}")
                return available_methods

        except Exception as e:
            print(f"Auth detection error: {str(e)}")
        finally:
            if transport and transport.is_active():
                transport.close()

        return []

    def _try_key_auth(self, host, port, username, key_path):
        """Try authentication with RSA/ED25519/ECDSA key"""
        print(f"Trying key authentication with {key_path}")

        # Optional: Detect server algorithms (with timeout, won't hang)
        self._detect_server_algorithms(host, port, timeout=3)

        transport = None

        try:
            # Load the key first
            private_key = None
            key_type = None

            print("Loading SSH key...")

            # Try RSA key
            try:
                private_key = paramiko.RSAKey(filename=key_path.strip())
                key_type = "RSA"
            except (paramiko.ssh_exception.SSHException, paramiko.ssh_exception.PasswordRequiredException):
                pass

            # Try ED25519 key
            if private_key is None:
                try:
                    private_key = paramiko.Ed25519Key(filename=key_path.strip())
                    key_type = "ED25519"
                except (paramiko.ssh_exception.SSHException, paramiko.ssh_exception.PasswordRequiredException):
                    pass

            # Try ECDSA key
            if private_key is None:
                try:
                    private_key = paramiko.ECDSAKey(filename=key_path.strip())
                    key_type = "ECDSA"
                except (paramiko.ssh_exception.SSHException, paramiko.ssh_exception.PasswordRequiredException):
                    pass

            # Try DSS key
            if private_key is None:
                try:
                    private_key = paramiko.DSSKey(filename=key_path.strip())
                    key_type = "DSS"
                except (paramiko.ssh_exception.SSHException, paramiko.ssh_exception.PasswordRequiredException):
                    pass

            if private_key is None:
                raise paramiko.SSHException(f"Unable to load key from {key_path} (tried RSA, ED25519, ECDSA, DSS)")

            print(f"✓ Loaded {key_type} key successfully")
            print(f"Connecting to {host}:{port} with {key_type} key...")

            # Use client.connect() - it should use our global Transport settings
            self.client.connect(
                hostname=host,
                port=port,
                username=username,
                pkey=private_key,
                look_for_keys=False,
                allow_agent=False,
                timeout=10
            )

            print(f"✓ Connection established!")

            self.auth_method_used = "publickey"
            print(f"✓ Successfully authenticated with {key_type} key")

        except paramiko.ssh_exception.PasswordRequiredException:
            print(f"✗ Key requires passphrase")
            self.notify("Key Error", f"SSH key is encrypted and requires a passphrase.\nKey: {key_path}")
            raise
        except paramiko.AuthenticationException as e:
            print(f"✗ Authentication failed: {e}")
            self.notify("Login Failure", f"Key Authentication Failed: {host}\nKey: {key_path}\nError: {e}")
            raise
        except paramiko.SSHException as e:
            print(f"✗ SSH error: {e}")
            self.notify("Login Failure", f"Connection Failed: {host}\nReason: {e}")
            raise
        except Exception as e:
            print(f"✗ Unexpected error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.notify("Error", f"Key auth error: {str(e)}")
            raise

    def _try_password_auth(self, host, port, username, password):
        """Try password authentication"""
        try:
            self.client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False
            )
        except Exception as e:
            print(f"Password auth error: {e}")
            raise

    def _try_keyboard_interactive_auth(self, host, port, username, password):
        """Try keyboard-interactive authentication"""
        if self.client:
            self.client.close()

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        transport = paramiko.Transport((host, port))
        transport.start_client()

        def handler(title, instructions, prompt_list):
            print(f"Interactive auth: Received {len(prompt_list)} prompts")
            return [password] * len(prompt_list)

        try:
            transport.auth_interactive(username, handler)

            if transport.is_authenticated():
                self.client._transport = transport
            else:
                transport.close()
                raise paramiko.ssh_exception.AuthenticationException("Keyboard-interactive authentication failed")
        except Exception as e:
            if transport and transport.is_active():
                transport.close()
            raise

    def setup_shell(self):
        print("  → Invoking shell...")
        try:
            self.channel = self.client.invoke_shell("xterm")
            self.channel.set_combine_stderr(True)
            print("  ✓ Shell invoked successfully!")
        except Exception as e:
            print(f"  ✗ Shell invoke failed: {e}, falling back to pty...")
            transport = self.client.get_transport()
            if transport:
                options = transport.get_security_options()
                print(f"    Security options: {options}")

                self.channel = transport.open_session()
                self.channel.get_pty()
                self.channel.set_combine_stderr(True)
                print("  ✓ PTY session created")
            else:
                print("  ✗ No transport available for PTY!")
                return

        if self.channel is not None:
            print("  → Starting ShellReaderThread...")
            self.reader_thread = ShellReaderThread(self.channel, self.buffer, parent_widget=self.parent_widget)
            self.reader_thread.data_ready.connect(self.send_output)
            self.reader_thread.start()
            print("  ✓ ShellReaderThread started")
        else:
            print("  ✗ ERROR: Channel is None!")

    def notify(self, message, info):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(info)
        msg.setWindowTitle(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        retval = msg.exec()

    @pyqtSlot(str)
    def write_data(self, data):
        if self.channel and self.channel.send_ready():
            try:
                self.channel.send(data)
            except paramiko.SSHException as e:
                print(f"Error while writing to channel: {e}")
            except Exception as e:
                print(f"Channel error {e}")
                self.notify("Closed", "Connection is closed.")
                pass
        else:
            print("Error: Channel is not ready or doesn't exist")
            self.notify("Error", "Channel is not ready or doesn't exist")

    @pyqtSlot(str)
    def set_pty_size(self, data):
        if self.channel and self.channel.send_ready():
            try:
                cols = data.split("::")[0]
                cols = int(cols.split(":")[1])
                rows = data.split("::")[1]
                rows = int(rows.split(":")[1])
                self.channel.resize_pty(width=cols, height=rows)
                print(f"backend pty resize -> cols:{cols} rows:{rows}")
            except paramiko.SSHException as e:
                print(f"Error setting backend pty term size: {e}")
        else:
            print("Error: Channel is not ready or doesn't exist")

    def __del__(self):
        try:
            if self.reader_thread and self.reader_thread.isRunning():
                self.reader_thread.terminate()
        except:
            pass
        if self.channel:
            self.channel.close()

        if self.client:
            self.client.close()