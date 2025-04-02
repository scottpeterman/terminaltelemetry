import json
import traceback
from typing import Dict, Any, List, Optional
import re
from netmiko import ConnectHandler
from netmiko.linux.linux_ssh import LinuxSSH
import logging
import os
logger = logging.getLogger(__name__)


class LinuxDriver:
    """Linux driver that mimics NAPALM's interface using Netmiko's Linux driver"""

    def __init__(self, hostname: str, username: str, password: str, optional_args: Optional[Dict] = None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.optional_args = optional_args or {}
        self.device = None
        self._device_info = {}
        self.platform = 'linux'
        self.prompt = "$"
        self._sudo_authenticated = False

    def open(self) -> None:
        """Open connection to the Linux device"""
        try:
            # Configure device parameters for Netmiko
            device_params = {
                'device_type': 'linux',
                'host': self.hostname,
                'username': self.username,
                'password': self.password,
                'timeout': self.optional_args.get('timeout', 60),
                'auth_timeout': self.optional_args.get('auth_timeout', 20),
                'banner_timeout': self.optional_args.get('banner_timeout', 20),
                'session_timeout': self.optional_args.get('session_timeout', 60),
                'fast_cli': False,
                'global_delay_factor': 3,
            }

            # Add any additional SSH options from optional_args
            if 'ssh_config_file' in self.optional_args:
                device_params['ssh_config_file'] = self.optional_args['ssh_config_file']

            # Establish connection using Netmiko
            logger.debug(f"Attempting connection to {self.hostname}")
            self.device = ConnectHandler(**device_params)

            self.prompt = self.device.find_prompt()
            print(f"found prompt: {self.prompt}")
            logger.info(f"Successfully connected to {self.hostname}")

        except Exception as e:
            error_msg = f"Failed to connect to Linux device: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)

    def close(self) -> None:
        """Safely close connection to the device"""
        if self.device:
            try:
                self.device.disconnect()
                logger.info(f"Closed connection to {self.hostname}")
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")
            finally:
                self.device = None

    import json
    import traceback
    from typing import Dict, Any, List, Optional
    import logging

    # Configure logging to show debug messages
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    def _ensure_sudo(self):
        """Ensure sudo access is available with enhanced debugging"""
        logger.debug("Starting sudo authentication check")
        try:
            logger.info("Sending sudo hostname command")
            output = self.device.send_command_timing("sudo hostname", cmd_verify=False)
            logger.debug(f"Initial sudo response: {output}")

            if "[sudo]" in output or "password" in output.lower():
                logger.info("Sudo password prompt detected, sending password")
                output_pwresp = self.device.send_command_timing(f"{self.password}\n")
                logger.debug(f"Password response: {output_pwresp}")

                # Verify if sudo was successful
                if "incorrect" in output_pwresp.lower():
                    logger.error("Incorrect sudo password provided")
                    return False
                logger.info("Sudo authentication completed")
                self._sudo_authenticated = True
            else:
                logger.debug("No sudo password prompt detected, assuming sudo works")
                self._sudo_authenticated = True

            return self._sudo_authenticated
        except Exception as e:
            logger.error(f"Sudo authentication failed: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def _send_command_sudo(self, command: str) -> str:
        """Send command with sudo after ensuring sudo access"""
        logger.debug(f"Attempting to run sudo command: {command}")
        try:
            if not self._sudo_authenticated:

                if not self._ensure_sudo():
                    logger.error("Sudo authentication failed. Cannot execute command.")
                    return ""

            result = self.device.send_command_timing(f"sudo {command}", cmd_verify=False)
            logger.debug(f"Command result: {result}")
            return result
        except Exception as e:
            logger.error(f"Sudo command failed: {str(e)}")
            logger.error(traceback.format_exc())
            return ""

    def get_facts(self) -> Dict[str, Any]:
        """Get device facts using uname commands"""
        try:
            # Get hostname - both hostname command and uname -n should work
            hostname = self.device.send_command('hostname').strip()

            # Get detailed system information using uname
            # -a: all information
            # -s: kernel name
            # -r: kernel release
            # -v: kernel version
            # -m: machine hardware name
            # -p: processor type
            # -i: hardware platform
            # -o: operating system
            uname_full = self.device.send_command('uname -a').strip()
            kernel_name = self.device.send_command('uname -s').strip()
            kernel_release = self.device.send_command('uname -r').strip()
            machine_hw = self.device.send_command('uname -m').strip()
            os_name = self.device.send_command('uname -o').strip()

            # Combine kernel info for model
            model = f"{kernel_name} {machine_hw}"

            # Use kernel release as serial number - it's unique per system
            serial = kernel_release

            # Get OS version from /etc/os-release if available, fallback to uname info
            try:
                os_info = self.device.send_command('cat /etc/os-release')
                os_version = re.search(r'VERSION="(.*)"', os_info)
                os_version = os_version.group(1) if os_version else f"{os_name} {kernel_release}"
            except:
                os_version = f"{os_name} {kernel_release}"

            # Get uptime
            uptime_str = self.device.send_command('cat /proc/uptime')
            uptime_seconds = float(uptime_str.split()[0])

            return {
                'hostname': hostname,
                'model': model,
                'serial_number': serial,
                'os_version': os_version,
                'uptime': int(uptime_seconds),
                'vendor': 'Linux',
                'interface_list': []
            }

        except Exception as e:
            error_msg = f"Error getting facts: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)



    def get_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """Get interface information"""
        interfaces = {}

        try:
            ip_link = self.device.send_command('ip link show')

            for line in ip_link.split('\n'):
                if ':' in line and '@' not in line:
                    name = line.split(':')[1].strip().split('@')[0]
                    state = 'UP' in line

                    interfaces[name] = {
                        'is_up': state,
                        'is_enabled': True,
                        'description': '',
                        'speed': 0,
                        'mtu': 0,
                        'mac_address': '',
                        'last_flapped': -1.0
                    }

                    # Try to get additional interface details
                    try:

                        ethtool_output = self.device.send_command(f'ethtool {name}')
                        speed_match = re.search(r'Speed: (\d+)Mb/s', ethtool_output)
                        if speed_match:
                            interfaces[name]['speed'] = int(speed_match.group(1))
                    except:
                        pass

            return interfaces

        except Exception as e:
            error_msg = f"Error getting interfaces: {str(e)}"
            logger.error(error_msg)



    def _write_debug(self, filename: str, content: str):
        os.makedirs('./output_debug', exist_ok=True)
        """Helper to write debug output to local file"""
        try:
            with open(f'./output_debug/{filename}.txt', 'w') as f:
                f.write(f"Command output for {filename}:\n")
                f.write(content)
        except Exception as e:
            print(f"Error writing debug file {filename}: {str(e)}")

    import re
    import traceback

    def get_environment(self):
        """Get environmental information matching TelemetryCollector's expected schema"""
        environment = {
            'cpu': {'CPU0': {'%usage': 0.0}},
            'memory': {'available_ram': 0, 'used_ram': 0},
            'temperature': {},
            'power': {},
            'fans': {}
        }

        try:
            # **Detect VMware**
            vmware_detected = False
            try:
                product_name = self.device.send_command("cat /sys/class/dmi/id/product_name 2>/dev/null")
                if product_name and "VMware" in product_name:
                    vmware_detected = True
            except Exception:
                pass  # Ignore failures

            if not vmware_detected:
                try:
                    scsi_info = self.device.send_command("cat /proc/scsi/scsi 2>/dev/null")
                    if scsi_info and "VMware" in scsi_info:
                        vmware_detected = True
                except Exception:
                    pass

            # If VMware is detected, return "N/A" for Temp, Power, and Fans
            if vmware_detected:
                environment['temperature'] = {"status": "N/A (VMware detected)"}
                environment['power'] = {"status": "N/A (VMware detected)"}
                environment['fans'] = {"status": "N/A (VMware detected)"}
                print("VMware detected. Skipping Temp, Power, and Fan collection.")
                return environment

            # **CPU Information**
            try:
                cpu_count = None
                nproc_output = self.device.send_command("nproc 2>/dev/null")
                if nproc_output and nproc_output.strip().isdigit():
                    cpu_count = int(nproc_output.strip())

                if cpu_count is None:
                    cpu_info = self.device.send_command("grep -c processor /proc/cpuinfo 2>/dev/null")
                    if cpu_info and cpu_info.strip().isdigit():
                        cpu_count = int(cpu_info.strip())

                if cpu_count is None:
                    cpu_entries = self.device.send_command(
                        "grep 'physical id' /proc/cpuinfo 2>/dev/null | sort -u | wc -l")
                    if cpu_entries and cpu_entries.strip().isdigit():
                        cpu_count = int(cpu_entries.strip())

                if cpu_count is None:
                    print("Could not determine CPU count, defaulting to 1")
                    cpu_count = 1

                print(f"Detected {cpu_count} CPU(s)")

                cpu_stats = self.device.send_command("grep 'cpu ' /proc/stat")
                if cpu_stats and cpu_stats.strip():
                    try:
                        stats = list(map(int, cpu_stats.split()[1:]))
                        idle = stats[3]
                        total = sum(stats)
                        usage = round(100.0 * (1.0 - idle / total), 1) if total > 0 else 0.0

                        environment['cpu'] = {f'CPU{i}': {'%usage': usage} for i in range(cpu_count)}

                    except Exception as e:
                        print(f"Error calculating CPU usage: {str(e)}")
                        traceback.print_exc()

            except Exception as e:
                print(f"Error getting CPU info: {str(e)}")
                traceback.print_exc()

            # **Memory Information**
            try:
                mem_output = self.device.send_command('cat /proc/meminfo')
                if mem_output:
                    total = int(re.search(r'MemTotal:\s+(\d+)', mem_output).group(1)) * 1024
                    free = int(re.search(r'MemFree:\s+(\d+)', mem_output).group(1)) * 1024
                    buffers = int(re.search(r'Buffers:\s+(\d+)', mem_output).group(1)) * 1024
                    cached = int(re.search(r'Cached:\s+(\d+)', mem_output).group(1)) * 1024

                    available = total
                    used = total - free - buffers - cached

                    environment['memory'].update({
                        'available_ram': available,
                        'used_ram': used
                    })
            except Exception as e:
                print(f"Error getting memory info: {str(e)}")
                traceback.print_exc()

            # **Temperature Information**
            try:
                temp_paths = self.device.send_command("find /sys/class/hwmon -type f -name 'temp*_input' 2>/dev/null")
                if temp_paths and temp_paths.strip():
                    for temp_file in temp_paths.splitlines():
                        temp_output = self._send_command_sudo(f"cat {temp_file} 2>/dev/null")
                        if temp_output and temp_output.strip().isdigit():
                            temp_c = round(int(temp_output.strip()) / 1000.0, 1)

                            # Get sensor label (if available)
                            label_file = temp_file.replace("_input", "_label")
                            label_output = self._send_command_sudo(f"cat {label_file} 2>/dev/null")
                            sensor_label = label_output.strip() if label_output else temp_file.split("/")[-1]
                            try:
                                environment['temperature'][sensor_label] = {"temperature": temp_c}
                            except:
                                pass
            except Exception as e:
                print(f"Error getting temperature info: {str(e)}")
                traceback.print_exc()

            # **Power Information**
            try:
                power_paths = self.device.send_command(
                    "find /sys/class/power_supply -type f -name 'uevent' 2>/dev/null")
                if power_paths and power_paths.strip():
                    for power_file in power_paths.splitlines():
                        power_output = self._send_command_sudo(f"cat {power_file} 2>/dev/null")
                        if power_output:
                            power_data = {}
                            for line in power_output.splitlines():
                                if "=" in line:
                                    try:
                                        key, value = line.split("=", 1)
                                        power_data[key.lower()] = value
                                    except:
                                        pass

                            environment['power'][power_file] = power_data
            except Exception as e:
                print(f"Error getting power info: {str(e)}")
                traceback.print_exc()

            # **Fan Information**
            try:
                fan_paths = self.device.send_command("find /sys/class/hwmon -type f -name 'fan*_input' 2>/dev/null")
                if fan_paths and fan_paths.strip():
                    for fan_file in fan_paths.splitlines():
                        fan_output = self._send_command_sudo(f"cat {fan_file} 2>/dev/null")
                        if fan_output and fan_output.strip().isdigit():
                            fan_speed = int(fan_output.strip())

                            # Get fan label (if available)
                            label_file = fan_file.replace("_input", "_label")
                            label_output = self._send_command_sudo(f"cat {label_file} 2>/dev/null")
                            fan_label = label_output.strip() if label_output else fan_file.split("/")[-1]
                            try:
                                environment['fans'][fan_label] = {"rpm": fan_speed}
                            except:
                                pass
            except Exception as e:
                print(f"Error getting fan info: {str(e)}")
                traceback.print_exc()

        except Exception as e:
            print(f"Error in get_environment: {str(e)}")
            traceback.print_exc()

        return environment

    # def get_environment(self):
    #     """Get environmental information matching TelemetryCollector's expected schema"""
    #     environment = {
    #         'cpu': {
    #             'CPU0': {
    #                 '%usage': 0.0
    #             }
    #         },
    #         'memory': {
    #             'available_ram': 0,
    #             'used_ram': 0
    #         },
    #         'temperature': {},
    #         'power': {},
    #         'fans': {}
    #     }
    #
    #     try:
    #         # CPU Information
    #         try:
    #             # Try multiple methods to get CPU count
    #             cpu_count = None
    #
    #             # Try nproc first
    #             nproc_output = self.device.send_command("nproc 2>/dev/null")
    #             if nproc_output and nproc_output.strip():
    #                 try:
    #                     cpu_count = int(nproc_output.strip())
    #                 except ValueError:
    #                     pass
    #
    #             # If nproc fails, try counting processor entries in cpuinfo
    #             if cpu_count is None:
    #                 cpu_info = self.device.send_command("grep -c processor /proc/cpuinfo 2>/dev/null")
    #                 if cpu_info and cpu_info.strip():
    #                     try:
    #                         cpu_count = int(cpu_info.strip())
    #                     except ValueError:
    #                         pass
    #
    #             # If both fail, try counting unique CPU entries in cpuinfo
    #             if cpu_count is None:
    #                 cpu_entries = self.device.send_command(
    #                     "grep 'physical id' /proc/cpuinfo 2>/dev/null | sort -u | wc -l")
    #                 if cpu_entries and cpu_entries.strip():
    #                     try:
    #                         cpu_count = int(cpu_entries.strip())
    #                     except ValueError:
    #                         pass
    #
    #             # If all else fails, default to 1
    #             if cpu_count is None:
    #                 print("Could not determine CPU count, defaulting to 1")
    #                 cpu_count = 1
    #
    #             print(f"Detected {cpu_count} CPU(s)")
    #
    #             # Get CPU usage
    #             cpu_stats_cmd = "grep 'cpu ' /proc/stat"
    #             cpu_stats = self.device.send_command(cpu_stats_cmd)
    #             print(f"CPU stats output: {cpu_stats}")
    #
    #             if cpu_stats and cpu_stats.strip():
    #                 try:
    #                     stats = list(map(int, cpu_stats.split()[1:]))
    #                     idle = stats[3]
    #                     total = sum(stats)
    #                     if total > 0:
    #                         usage = round(100.0 * (1.0 - idle / total), 1)
    #                         print(f"Calculated CPU usage: {usage}%")
    #
    #                         environment['cpu'] = {}
    #                         for i in range(cpu_count):
    #                             environment['cpu'][f'CPU{i}'] = {
    #                                 '%usage': usage
    #                             }
    #                 except Exception as e:
    #                     print(f"Error calculating CPU usage: {str(e)}")
    #                     traceback.print_exc()
    #
    #         except Exception as e:
    #             print(f"Error getting CPU info: {str(e)}")
    #             traceback.print_exc()
    #
    #         # Memory Information
    #         try:
    #             mem_output = self.device.send_command('cat /proc/meminfo')
    #             if mem_output:
    #                 total = int(re.search(r'MemTotal:\s+(\d+)', mem_output).group(1)) * 1024
    #                 free = int(re.search(r'MemFree:\s+(\d+)', mem_output).group(1)) * 1024
    #                 buffers = int(re.search(r'Buffers:\s+(\d+)', mem_output).group(1)) * 1024
    #                 cached = int(re.search(r'Cached:\s+(\d+)', mem_output).group(1)) * 1024
    #
    #                 available = total
    #                 used = total - free - buffers - cached
    #
    #                 environment['memory'].update({
    #                     'available_ram': available,
    #                     'used_ram': used
    #                 })
    #         except Exception as e:
    #             print(f"Error getting memory info: {str(e)}")
    #             traceback.print_exc()
    #
    #         # Temperature Information - Dynamic Discovery
    #         try:
    #             # First find all coretemp devices
    #             ls_cmd = "ls -d /sys/devices/platform/coretemp.* 2>/dev/null || true"
    #             coretemp_list = self._send_command_sudo(ls_cmd)
    #             print(coretemp_list)
    #             if coretemp_list and coretemp_list.strip():
    #                 for coretemp_path in coretemp_list.splitlines():
    #                     try:
    #                         # Find the hwmon directory
    #                         hwmon_cmd = f"ls {coretemp_path}/hwmon/hwmon* 2>/dev/null || true"
    #                         print(hwmon_cmd)
    #                         hwmon_path = self._send_command_sudo(hwmon_cmd)
    #                         print(hwmon_path)
    #
    #                         if not hwmon_path:
    #                             continue
    #
    #                         # List all temperature inputs
    #                         temp_cmd = f"ls {hwmon_path}/temp*_input 2>/dev/null || true"
    #                         print(temp_cmd)
    #                         temp_files = self._send_command_sudo(temp_cmd)
    #                         print(temp_files)
    #                         if temp_files and temp_files.strip():
    #                             for temp_file in temp_files.splitlines():
    #                                 try:
    #                                     # Extract temperature number
    #                                     temp_num = re.search(r'temp(\d+)_input', temp_file)
    #                                     print(temp_num)
    #                                     if not temp_num:
    #                                         continue
    #                                     temp_num = temp_num.group(1)
    #
    #                                     # Get label if available
    #                                     label_file = temp_file.replace('_input', '_label')
    #                                     label_output = self._send_command_sudo(f"cat {label_file} 2>/dev/null || true")
    #                                     sensor_label = label_output.strip() if label_output and 'No such file' not in label_output else f"Core {int(temp_num) - 1}"
    #
    #                                     # Get temperature value
    #                                     temp_output = self._send_command_sudo(f"cat {temp_file} 2>/dev/null || true")
    #                                     if temp_output and 'No such file' not in temp_output:
    #                                         temp = float(temp_output.strip()) / 1000.0
    #
    #                                         # Get threshold values if available
    #                                         max_file = temp_file.replace('_input', '_max')
    #                                         crit_file = temp_file.replace('_input', '_crit')
    #                                         alarm_file = temp_file.replace('_input', '_crit_alarm')
    #
    #                                         max_output = self._send_command_sudo(f"cat {max_file} 2>/dev/null || true")
    #                                         crit_output = self._send_command_sudo(
    #                                             f"cat {crit_file} 2>/dev/null || true")
    #                                         alarm_output = self._send_command_sudo(
    #                                             f"cat {alarm_file} 2>/dev/null || true")
    #
    #                                         # Determine alert and critical status
    #                                         is_alert = False
    #                                         is_critical = False
    #
    #                                         if max_output and 'No such file' not in max_output:
    #                                             max_temp = float(max_output.strip()) / 1000.0
    #                                             is_alert = temp >= max_temp
    #
    #                                         if crit_output and 'No such file' not in crit_output:
    #                                             crit_temp = float(crit_output.strip()) / 1000.0
    #                                             is_critical = temp >= crit_temp
    #
    #                                         if alarm_output and 'No such file' not in alarm_output:
    #                                             if int(alarm_output.strip()) == 1:
    #                                                 is_alert = True
    #                                                 is_critical = True
    #
    #                                         # Extract CPU number from path
    #                                         cpu_num = re.search(r'coretemp\.(\d+)', coretemp_path)
    #                                         cpu_id = cpu_num.group(1) if cpu_num else '0'
    #
    #                                         sensor_name = f"CPU{cpu_id} {sensor_label}"
    #                                         environment['temperature'][sensor_name] = {
    #                                             'temperature': round(temp, 1),
    #                                             'is_alert': is_alert,
    #                                             'is_critical': is_critical
    #                                         }
    #
    #                                 except Exception as e:
    #                                     print(f"Error processing temperature file {temp_file}: {str(e)}")
    #                                     traceback.print_exc()
    #                                     continue
    #
    #                     except Exception as e:
    #                         print(f"Error processing coretemp device {coretemp_path}: {str(e)}")
    #                         traceback.print_exc()
    #                         continue
    #
    #         except Exception as e:
    #             print(f"Error getting temperature info: {str(e)}")
    #             traceback.print_exc()
    #
    #     except Exception as e:
    #         print(f"Error in get_environment: {str(e)}")
    #         traceback.print_exc()
    #
    #     return environment

    def get_lldp_neighbors_detail(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get LLDP neighbor information"""
        neighbors = {}

        try:
            lldp_output = self.device.send_command('lldpctl -f keyvalue')

            current_port = None
            neighbor_data = {}

            for line in lldp_output.split('\n'):
                if not line:
                    continue

                parts = line.split('=', 1)
                if len(parts) != 2:
                    continue

                key, value = parts
                key_parts = key.split('.')

                if 'lldp' in key_parts and 'port' in key_parts and 'local' in key_parts:
                    current_port = value
                    if current_port not in neighbors:
                        neighbors[current_port] = []
                    neighbor_data = {}

                elif current_port and 'chassis' in key_parts and 'name' in key_parts:
                    neighbor_data['remote_system_name'] = value
                elif current_port and 'port' in key_parts and 'descr' in key_parts:
                    neighbor_data['remote_port'] = value

                if neighbor_data and 'remote_system_name' in neighbor_data and 'remote_port' in neighbor_data:
                    neighbors[current_port].append(neighbor_data)
                    neighbor_data = {}

            return neighbors

        except Exception as e:
            logger.warning(f"Error getting LLDP neighbors (this is normal if LLDP is not installed): {str(e)}")
            return {}

    def get_route_to(self, destination: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get routing information"""
        routes = {'0.0.0.0/0': []}

        try:
            route_output = self.device.send_command('ip route show')

            for line in route_output.split('\n'):
                if 'default' in line:
                    parts = line.split()
                    next_hop = parts[2] if len(parts) > 2 else ''
                    routes['0.0.0.0/0'].append({
                        'protocol': 'static',
                        'current_active': True,
                        'last_active': True,
                        'age': -1,
                        'next_hop': next_hop,
                        'outgoing_interface': parts[4] if len(parts) > 4 else '',
                        'selected_next_hop': True,
                        'preference': -1,
                        'inactive_reason': '',
                        'routing_table': 'default',
                        'protocol_attributes': {}
                    })

            return routes

        except Exception as e:
            error_msg = f"Error getting route information: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)