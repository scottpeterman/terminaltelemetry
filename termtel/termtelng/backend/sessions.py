import traceback
from typing import Optional, Dict, Any

import napalm
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import asyncio
import json
import logging
import paramiko
import os
from termtel.termtelng.backend.linux_driver import LinuxDriver

logger = logging.getLogger(__name__)


class BaseSession(QObject):
    """Base class for all session types"""
    message_ready = pyqtSignal(str)

    def __init__(self, session_id):
        super().__init__()
        self.session_id = session_id
        self.queue = asyncio.Queue()
        self._active = False

    def send_message(self, action: str, payload: dict):
        message = {
            "session_id": self.session_id,
            "action": action,
            "payload": payload
        }
        print(message)
        self.message_ready.emit(json.dumps(message))


class SSHSession(BaseSession):
    """Handles SSH terminal sessions with support for legacy cipher suites"""

    def __init__(self, session_id: str):
        super().__init__(session_id)
        self.client = None
        self.channel = None
        self.session_id = session_id
        self._active = False

        # Configure Paramiko's preferred algorithms
        paramiko.Transport._preferred_kex = (
            "diffie-hellman-group14-sha1",
            "diffie-hellman-group-exchange-sha1",
            "diffie-hellman-group-exchange-sha256",
            "diffie-hellman-group1-sha1",
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "curve25519-sha256",
            "curve25519-sha256@libssh.org",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512"
        )

        paramiko.Transport._preferred_ciphers = (
            "aes128-cbc",
            "aes128-ctr",
            "aes192-ctr",
            "aes256-ctr",
            "aes256-cbc",
            "3des-cbc",
            "aes192-cbc",
            "aes256-gcm@openssh.com",
            "aes128-gcm@openssh.com",
            "chacha20-poly1305@openssh.com",
            "aes256-gcm",
            "aes128-gcm"
        )

        paramiko.Transport._preferred_keys = (
            "ssh-rsa",
            "ssh-dss",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
            "ssh-ed25519",
            "rsa-sha2-256",
            "rsa-sha2-512"
        )

    async def connect(self, host: str, username: str,
                      password: Optional[str] = None,
                      key_path: Optional[str] = None) -> None:
        """Establish SSH connection with legacy cipher support"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect with modified defaults and disabled key searching
            await asyncio.to_thread(
                self.client.connect,
                hostname=host,
                username=username,
                password=password,
                key_filename=key_path if key_path else None,
                look_for_keys=False,
                allow_agent=False,
                timeout=30
            )

            # Request a PTY terminal
            self.channel = self.client.invoke_shell(term='xterm')
            self.channel.set_combine_stderr(True)

            # Set active flag for read loop
            self._active = True
            print(f"ssh session connected - terminal")
            self.send_message("connected", {"status": "success"})

            # Start reading output
            await asyncio.create_task(self._read_output())


        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.send_message("error", {"message": str(e)})
            raise

    async def handle_data(self, payload: Dict[str, Any]) -> None:
        """Handle incoming terminal data"""
        if self.channel and self.channel.active:
            try:
                text = payload.get("text", "")
                self.channel.send(text)
            except Exception as e:
                logger.error(f"Failed to send data: {e}")
                self.send_message("error", {"message": str(e)})

    async def handle_resize(self, payload: Dict[str, Any]) -> None:
        """Handle terminal resize events"""
        print(f"handle_resize: {payload}")
        if self.channel and self.channel.active:
            try:
                cols = payload.get('cols', 80)
                rows = payload.get('rows', 24)
                self.channel.resize_pty(width=cols - 4, height=rows)
            except Exception as e:
                logger.error(f"Failed to resize PTY: {e}")

    async def _read_output(self) -> None:
        """Read and forward SSH output"""
        while self._active and self.channel:
            try:
                data = await asyncio.to_thread(self.channel.recv, 1024)
                if not data:  # Connection closed
                    break
                self.send_message("data", {"text": data.decode()})
            except Exception as e:
                logger.error(f"Read error: {e}")
                break

        # If we break out of the loop and were still active, there was an error
        if self._active:
            await self.disconnect()

    async def disconnect(self, message=None) -> None:
        """Disconnect SSH session"""
        self._active = False
        if self.channel:
            self.channel.close()
        if self.client:
            self.client.close()
        self.send_message("disconnected", {"status": "success"})

    async def stop(self) -> None:
        """Stop the session"""
        await self.disconnect()


class TelemetryCollector(QThread):
    telemetry_ready = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, device, parent=None):
        super().__init__(parent)
        self.device = device
        self._is_running = False

    def run(self):
        self._is_running = True
        while self._is_running:
            try:
                # Initialize empty update_data with default values
                update_data = {
                    "device_info": {},
                    "interfaces": [],
                    "neighbors": [],
                    "routing_table": [],
                    "environment": {}
                }

                # Get device info first with retry mechanism
                device_info = self.collect_device_info()
                if device_info:
                    update_data["device_info"] = device_info

                # Get interfaces - Wrapped in try/except for fault tolerance
                try:
                    print("retrieving interfaces via cli")
                    interfaces = self.device.get_interfaces()
                    processed_interfaces = [
                        {
                            "name": name,
                            "status": "UP" if details.get("is_up") else "DOWN"
                        }
                        for name, details in interfaces.items()
                    ]
                    update_data["interfaces"] = processed_interfaces
                except Exception as e:
                    print(f"Error collecting interface data: {e}")
                    logger.warning(f"Failed to collect interface data: {e}")
                    # Continue with other data collection

                # Get neighbors - Wrapped in try/except for fault tolerance
                try:
                    neighbors = self.device.get_lldp_neighbors_detail()
                    processed_neighbors = [
                        {
                            "local_port": port,
                            "neighbor": neighbor.get("remote_system_name", "Unknown"),
                            "remote_port": neighbor.get("remote_port", "Unknown")
                        }
                        for port, port_neighbors in neighbors.items()
                        for neighbor in port_neighbors
                    ]
                    update_data["neighbors"] = processed_neighbors
                except Exception as e:
                    print(f"Error collecting neighbor data: {e}")
                    logger.warning(f"Failed to collect neighbor data: {e}")
                    # Continue with other data collection

                # Get routes - Wrapped in try/except for fault tolerance
                try:
                    route_details = self.device.get_route_to(destination="0.0.0.0/0")
                    routes = []
                    for protocol_details in route_details.values():
                        for route in protocol_details:
                            routes.append({
                                "network": route.get("destination", "0.0.0.0"),
                                "mask": route.get("prefix_length", "0"),
                                "next_hop": route.get("next_hop", "")
                            })
                    update_data["routing_table"] = routes
                except Exception as e:
                    print(f"Error collecting routing data: {e}")
                    logger.warning(f"Failed to collect routing data: {e}")
                    # Continue with other data collection

                # Get environment data - Wrapped in try/except for fault tolerance
                try:
                    update_data["environment"] = self.collect_environment_data()
                except Exception as e:
                    print(f"Error collecting environment data: {e}")
                    logger.warning(f"Failed to collect environment data: {e}")
                    # Continue with other data collection

                # Only emit data if we have at least device info
                if update_data["device_info"]:
                    self.telemetry_ready.emit(update_data)
                else:
                    self.error_signal.emit("Failed to collect minimum required telemetry data")

            except Exception as e:
                traceback.print_exc()
                self.error_signal.emit(f"Error in telemetry collection cycle: {str(e)}")

            # Sleep for 30 seconds before next collection
            if self._is_running:
                print("\nWaiting 30 seconds before next telemetry collection...")
                self.sleep(30)

    def collect_device_info(self):
        """Collect device information with retry mechanism"""
        for attempt in range(6):  # max_retries = 6
            try:
                print(f"\nAttempting to get device info (attempt {attempt + 1}/6)...")
                facts = self.device.get_facts()

                # Handle Linux case specially - facts might be different
                if "unknown" in facts.get('hostname', 'unknown'):
                    # For Linux, try alternative method
                    try:
                        # This could be a custom implementation for Linux
                        hostname = facts.get('hostname', 'unknown')
                        if hostname == 'unknown':
                            # Try to get hostname via shell command for Linux
                            if hasattr(self.device, 'send_command'):
                                hostname = self.device.send_command('hostname').strip()

                        # If we still don't have a hostname, raise an error
                        if hostname == 'unknown':
                            raise ValueError('Hostname could not be determined')

                        # Construct basic device info for Linux
                        uptime_seconds = facts.get("uptime", 0)
                        days = int(uptime_seconds // 86400)
                        hours = int((uptime_seconds % 86400) // 3600)
                        minutes = int((uptime_seconds % 3600) // 60)

                        return {
                            "hostname": hostname,
                            "model": facts.get("model", "Linux VM"),
                            "serial": facts.get("serial_number", "N/A"),
                            "os_version": facts.get("os_version", "Linux"),
                            "uptime": f"{days}d {hours}h {minutes}m"
                        }
                    except Exception as linux_e:
                        print(f"Linux-specific info retrieval failed: {linux_e}")
                        # Continue with retry loop

                uptime_seconds = facts.get("uptime", 0)
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)

                device_info = {
                    "hostname": facts.get("hostname", "unknown"),
                    "model": facts.get("model", "unknown"),
                    "serial": facts.get("serial_number", "unknown"),
                    "os_version": facts.get("os_version", "unknown"),
                    "uptime": f"{days}d {hours}h {minutes}m"
                }
                print("Successfully got device info!")
                return device_info  # Success, return device info

            except ValueError as e:
                if "not enough values to unpack" in str(e):
                    print(f"\nSession confusion detected on attempt {attempt + 1}: {e}")
                    if attempt < 5:  # max_retries - 1
                        delay = 1 * (2 ** attempt)  # Exponential backoff
                        print(f"Waiting {delay} seconds before next attempt...")
                        self.sleep(delay)
                else:
                    print(f"\nValue error on attempt {attempt + 1}: {e}")

            except Exception as e:
                print(f"\nError on attempt {attempt + 1}: {e}")
                if attempt < 5:
                    delay = 1 * (2 ** attempt)
                    print(f"Waiting {delay} seconds before next attempt...")
                    self.sleep(delay)

        # If we get here, all attempts failed
        print("Failed to get device info after max retries")
        return None

    def collect_environment_data(self):
        """Collect environment data with Linux-specific handling"""
        try:
            environment = self.device.get_environment()
            if not environment:
                # For Linux, environment might be empty or None
                # Try to construct our own environment data for Linux
                if hasattr(self.device, 'send_command'):
                    try:
                        # Try to get CPU info for Linux
                        cpu_output = self.device.send_command("top -bn1 | grep 'Cpu(s)'").strip()
                        cpu_usage = 0.0
                        if cpu_output:
                            # Parse CPU usage from top output
                            try:
                                cpu_parts = cpu_output.split(',')
                                if len(cpu_parts) > 0:
                                    user_part = cpu_parts[0].strip()
                                    if 'us' in user_part:
                                        cpu_usage = float(user_part.split()[1].replace('us', ''))
                            except Exception as parse_e:
                                print(f"Error parsing CPU usage: {parse_e}")

                        # Try to get memory info for Linux
                        mem_output = self.device.send_command("free -m").strip()
                        mem_total = 0
                        mem_used = 0
                        if mem_output:
                            # Parse memory usage from free output
                            try:
                                mem_lines = mem_output.split('\n')
                                if len(mem_lines) > 1:
                                    mem_parts = mem_lines[1].split()
                                    if len(mem_parts) > 2:
                                        mem_total = int(mem_parts[1])
                                        mem_used = int(mem_parts[2])
                            except Exception as parse_e:
                                print(f"Error parsing memory usage: {parse_e}")

                        # Construct environment data for Linux
                        return {
                            'cpu': {
                                'average_usage': cpu_usage,
                                'num_cpus': 1
                            },
                            'memory': {
                                'total': mem_total * 1024 * 1024,  # Convert MB to bytes
                                'used': mem_used * 1024 * 1024,  # Convert MB to bytes
                                'usage_percent': (mem_used / mem_total * 100) if mem_total > 0 else 0
                            },
                            'temperature': [],  # Empty for Linux VMs
                            'power': [],  # Empty for Linux VMs
                            'fans': []  # Empty for Linux VMs
                        }
                    except Exception as linux_env_e:
                        print(f"Error collecting Linux environment data: {linux_env_e}")
                        # Return minimal environment data
                        return {
                            'cpu': {},
                            'memory': {},
                            'temperature': [],
                            'power': [],
                            'fans': []
                        }

                # If we can't get Linux-specific data, return empty structure
                return {
                    'cpu': {},
                    'memory': {},
                    'temperature': [],
                    'power': [],
                    'fans': []
                }

            # Process environment data from napalm
            processed_env = {}

            # Process CPU data with safety checks
            cpu_info = {}
            if 'cpu' in environment and environment['cpu']:
                cpu_data = environment['cpu']
                if isinstance(cpu_data, dict):
                    # Extract CPU usage safely
                    cpu_usages = []
                    for cpu_id, cpu in cpu_data.items():
                        if isinstance(cpu, dict) and '%usage' in cpu:
                            try:
                                cpu_usages.append(float(cpu['%usage']))
                            except (ValueError, TypeError):
                                # Skip invalid values
                                pass

                    if cpu_usages:
                        cpu_info['average_usage'] = sum(cpu_usages) / len(cpu_usages)
                        cpu_info['num_cpus'] = len(cpu_usages)

            # Process Memory data with safety checks
            memory_info = {}
            if 'memory' in environment and environment['memory']:
                mem = environment['memory']
                if isinstance(mem, dict):
                    # Extract memory data safely
                    mem_total = mem.get('available_ram', 0)
                    mem_used = mem.get('used_ram', 0)

                    # Validate memory values
                    try:
                        mem_total = int(mem_total)
                        mem_used = int(mem_used)
                    except (ValueError, TypeError):
                        mem_total = 0
                        mem_used = 0

                    memory_info['total'] = mem_total
                    memory_info['used'] = mem_used
                    if mem_total > 0:
                        memory_info['usage_percent'] = (mem_used / mem_total) * 100

            # Process temperature data safely
            temperature_data = []
            if 'temperature' in environment and environment['temperature']:
                temp_data = environment['temperature']
                if isinstance(temp_data, dict):
                    for loc, data in temp_data.items():
                        if isinstance(data, dict):
                            try:
                                temperature_data.append({
                                    'location': loc,
                                    'temperature': data.get('temperature', 0),
                                    'alert': data.get('is_alert', False),
                                    'critical': data.get('is_critical', False)
                                })
                            except Exception:
                                # Skip invalid temperature entries
                                pass

            # Process power data safely
            power_data = []
            if 'power' in environment and environment['power']:
                power_info = environment['power']
                if isinstance(power_info, dict):
                    for psu_id, data in power_info.items():
                        if isinstance(data, dict):
                            try:
                                power_data.append({
                                    'id': psu_id,
                                    'status': data.get('status', False),
                                    'capacity': data.get('capacity', 0),
                                    'output': data.get('output', 0)
                                })
                            except Exception:
                                # Skip invalid power entries
                                pass

            # Process fan data safely
            fan_data = []
            if 'fans' in environment and environment['fans']:
                fan_info = environment['fans']
                if isinstance(fan_info, dict):
                    for loc, data in fan_info.items():
                        if isinstance(data, dict):
                            try:
                                fan_data.append({
                                    'location': loc,
                                    'status': data.get('status', False)
                                })
                            except Exception:
                                # Skip invalid fan entries
                                pass

            processed_env = {
                'cpu': cpu_info,
                'memory': memory_info,
                'temperature': temperature_data,
                'power': power_data,
                'fans': fan_data
            }

            return processed_env

        except Exception as e:
            print(f"Error in collect_environment_data: {e}")
            # Return empty environment structure on error
            return {
                'cpu': {},
                'memory': {},
                'temperature': [],
                'power': [],
                'fans': []
            }


class TelemetrySession(BaseSession):
    def __init__(self, session_id):
        super().__init__(session_id)
        self.device = None
        self._active = False
        self.refresh_rate = 30  # seconds
        self.collector = None  # Track collector instance
        self.device_type = None  # Store the device type for special handling

    async def connect(self, host, username, password=None, driver_type="linux"):
        """Establish Napalm connection to device"""
        try:
            # Configure logging for Netmiko to reduce noise
            logging.getLogger('netmiko').setLevel(logging.WARNING)
            logging.getLogger('paramiko').setLevel(logging.WARNING)

            # Store device type for later use
            self.device_type = driver_type

            # Get the appropriate Napalm driver
            driver_map = {
                "ios": napalm.get_network_driver("ios"),
                "eos": napalm.get_network_driver("eos"),
                "nxos_ssh": napalm.get_network_driver("nxos_ssh"),
                "junos": napalm.get_network_driver("junos"),
                "linux": LinuxDriver
            }

            if driver_type not in driver_map:
                raise ValueError(f"Unsupported driver type: {driver_type}")

            driver = driver_map[driver_type]

            # Define base optional arguments with adjusted timeouts
            optional_args = {
                'port': 22,
                'timeout': 120,  # Increased global timeout
                'keepalive': 30,
                'auto_rollback_on_error': True,
                'netmiko_options': {
                    'timeout': 120,  # Connection timeout
                    'global_delay_factor': 2,  # Multiplier for all delays
                    'read_timeout_override': 90,  # Override for read operations
                    'fast_cli': False,  # Disable fast_cli for reliability
                    'session_timeout': 120,  # Session timeout
                    'session_log': None,
                    'conn_timeout': 60,  # Connection establishment timeout
                }
            }

            # Platform-specific configurations
            if driver_type == "eos":
                optional_args.update({
                    'transport': 'ssh',
                    'port': 22,
                    'allow_agent': False,
                    'enable_mode': True,
                    'use_keys': False,
                    'key_file': None,
                    'netmiko_options': {
                        'global_delay_factor': 2,
                        'read_timeout_override': 120,
                        'expect_string': r'[>#]',  # More permissive prompt pattern
                        'fast_cli': False
                    }
                })
            elif driver_type == "nxos_ssh":
                optional_args['netmiko_options'].update({
                    'global_delay_factor': 3,
                    'read_timeout_override': 120
                })
            elif driver_type == "ios":
                optional_args['netmiko_options'].update({
                    'global_delay_factor': 3,
                    'command_timeout': 90
                })
            elif driver_type == "linux":
                # Linux-specific options
                optional_args.update({
                    'timeout': 180,  # Even longer timeout for Linux
                    'netmiko_options': {
                        'global_delay_factor': 3,
                        'read_timeout_override': 150,
                        'timeout': 150,
                    }
                })

            self.device = driver(
                hostname=host,
                username=username,
                password=password,
                optional_args=optional_args
            )

            print(f"napalm session connected - {driver_type}")

            # Open connection in a separate thread to avoid blocking
            try:
                await asyncio.to_thread(self.device.open)
                self._active = True
                self.send_message("connected", {"status": "success"})

                # Start monitoring after successful connection
                await self.collect_all_telemetry()
            except Exception as open_e:
                # Special handling for Linux driver which might have different behavior
                if driver_type == "linux":
                    print(f"Linux driver connection issue: {open_e}")
                    # Try alternative connection method for Linux if available
                    try:
                        # This would be a custom implementation for Linux
                        if hasattr(self.device, 'alternate_connect'):
                            await asyncio.to_thread(self.device.alternate_connect)
                            self._active = True
                            self.send_message("connected", {"status": "success"})
                            await self.collect_all_telemetry()
                        else:
                            raise open_e  # Re-raise if no alternate method
                    except Exception as alt_e:
                        raise Exception(f"Linux connection failed: {alt_e}")
                else:
                    # For non-Linux devices, re-raise the exception
                    raise open_e

        except Exception as e:
            error_msg = f"Napalm connection failed: {str(e)}"
            print(error_msg)
            self.send_message("error", {"message": error_msg})
            if self.device:
                try:
                    await asyncio.to_thread(self.device.close)
                except Exception:
                    pass
                self.device = None

    async def collect_all_telemetry(self):
        """Collect and send all telemetry data in sequence"""
        try:
            # Only start a new collector if one isn't already running
            if self.collector is None or not self.collector.isRunning():
                if self.collector is not None:
                    # Clean up any previous collector
                    try:
                        self.collector.telemetry_ready.disconnect()
                        self.collector.error_signal.disconnect()
                    except Exception as e:
                        print(f"Error disconnecting signals: {e}")
                    self.collector = None

                # Create and start new collector
                try:
                    self.collector = TelemetryCollector(self.device)
                    self.collector.telemetry_ready.connect(self._handle_telemetry_data)
                    self.collector.error_signal.connect(self._handle_telemetry_error)
                    self.collector.start()
                except Exception as collector_e:
                    error_msg = f"Error starting telemetry collector: {str(collector_e)}"
                    logger.error(error_msg)
                    self.send_message("error", {"message": error_msg})

                    # Send minimal telemetry if collector fails to start
                    self._send_minimal_telemetry()
            else:
                logger.debug("Telemetry collector already running")

        except Exception as e:
            error_msg = f"Error in collect_all_telemetry: {str(e)}"
            logger.error(error_msg)
            self.send_message("error", {"message": error_msg})

            # Try to send minimal telemetry even if there's an error
            self._send_minimal_telemetry()

    def _send_minimal_telemetry(self):
        """Send minimal telemetry data when full collection fails"""
        try:
            # Minimal device info
            device_info = {
                "hostname": "unknown",
                "model": "unknown",
                "serial": "unknown",
                "os_version": self.device_type or "unknown",
                "uptime": "unknown"
            }

            # Try to get at least the hostname
            if self.device and hasattr(self.device, 'send_command'):
                try:
                    hostname = self.device.send_command('hostname').strip()
                    if hostname:
                        device_info["hostname"] = hostname
                except Exception:
                    pass

            # Create minimal telemetry update
            minimal_data = {
                "device_info": device_info,
                "interfaces": [],
                "neighbors": [],
                "routing_table": [],
                "environment": {
                    'cpu': {},
                    'memory': {},
                    'temperature': [],
                    'power': [],
                    'fans': []
                }
            }

            # Send minimal data
            self.send_message("telemetry_update", minimal_data)

        except Exception as e:
            logger.error(f"Error sending minimal telemetry: {e}")

    async def disconnect(self, args=None):
        """Disconnect from device"""
        self._active = False

        # Clean up collector if it exists
        if self.collector is not None:
            try:
                if self.collector.isRunning():
                    self.collector._is_running = False  # Signal the collector to stop
                    self.collector.quit()
                    self.collector.wait()
                self.collector.telemetry_ready.disconnect()
                self.collector.error_signal.disconnect()
            except Exception as e:
                logger.error(f"Error cleaning up collector: {e}")
            self.collector = None

        if self.device:
            try:
                await asyncio.to_thread(self.device.close)
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            self.device = None
        self.send_message("disconnected", {"status": "success"})

    def _handle_telemetry_data(self, data):
        """Handle telemetry data from collector"""
        if self._active:  # Only process data if session is still active
            # Sanitize data before sending to ensure it's valid JSON
            sanitized_data = self._sanitize_data(data)
            self.send_message("telemetry_update", sanitized_data)

    def _handle_telemetry_error(self, error_msg):
        """Handle telemetry error from collector"""
        if self._active:  # Only process errors if session is still active
            logger.error(error_msg)
            self.send_message("error", {"message": error_msg})

            # Try to send minimal telemetry on error
            self._send_minimal_telemetry()

    def _sanitize_data(self, data):
        """Ensure data is valid for JSON serialization"""
        if isinstance(data, dict):
            result = {}
            for k, v in data.items():
                try:
                    # Skip keys that start with underscore (private)
                    if isinstance(k, str) and k.startswith('_'):
                        continue

                    # Sanitize value
                    result[k] = self._sanitize_data(v)
                except Exception:
                    # Skip values that cause errors
                    result[k] = None
            return result
        elif isinstance(data, list):
            result = []
            for item in data:
                try:
                    result.append(self._sanitize_data(item))
                except Exception:
                    # Skip items that cause errors
                    pass
            return result
        elif isinstance(data, (str, int, float, bool)) or data is None:
            return data
        else:
            # Convert other types to string
            try:
                return str(data)
            except Exception:
                return None


class UISession(BaseSession):
    """Handles UI state and theme management"""

    def __init__(self, session_id):
        super().__init__(session_id)
        self.session_id = session_id
        self.current_theme = self.load_saved_theme()
        # Send initial theme to frontend immediately after initialization
        self.send_message("theme_changed", {"theme": self.current_theme})

    def load_saved_theme(self):
        """Load theme from persistent storage"""
        try:
            with open('theme_settings.json', 'r') as f:
                settings = json.load(f)
                return settings.get('theme', 'cyber')
        except (FileNotFoundError, json.JSONDecodeError):
            return 'cyber'  # Default theme

    def save_theme(self, theme_name):
        """Save theme to persistent storage"""
        try:
            with open('theme_settings.json', 'w') as f:
                json.dump({'theme': theme_name}, f)
        except Exception as e:
            logger.error(f"Error saving theme: {e}")

    async def handle_get_theme(self, payload):
        """Handle request for current theme"""
        self.send_message("theme_changed", {"theme": self.current_theme})

    async def handle_set_theme(self, payload):
        """Handle theme change request"""
        theme_name = payload.get('theme')
        if theme_name:
            self.current_theme = theme_name
            self.save_theme(theme_name)
            self.send_message("theme_changed", {"theme": theme_name})

    async def set_theme(self, theme_name):
        """Set theme and notify frontend"""
        self.current_theme = theme_name
        self.save_theme(theme_name)
        self.send_message("theme_changed", {"theme": theme_name})
