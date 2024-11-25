import paramiko
import queue
import time
from typing import Dict, List, Optional, Tuple
import click
import json
from log_handler import LogThread
from tfsm_fire import TextFSMAutoEngine

# Updated field mappings to include generic templates

NORMALIZED_FIELDS = {
    'device_id': {
        'cisco_ios_cdp': 'NEIGHBOR_NAME',
        'cisco_nxos_cdp': ['CHASSIS_ID', 'NEIGHBOR_NAME'],
        'hp_procurve_cdp': 'CHASSIS_ID',
        'arista_eos_lldp': 'NEIGHBOR_NAME',
        'cisco_ios_lldp': 'NEIGHBOR_NAME',         # Changed to match template output
        'cisco_nxos_lldp': 'SYSTEM_NAME',
        'hp_procurve_lldp': 'SYSTEM_NAME',
        'show_cdp': 'NEIGHBOR_NAME',
        'show_lldp': 'NEIGHBOR_NAME'              # Changed to match template output
    },
    'ip_address': {
        'cisco_ios_cdp': 'MGMT_ADDRESS',
        'cisco_nxos_cdp': ['MGMT_ADDRESS', 'INTERFACE_IP'],
        'hp_procurve_cdp': 'MGMT_ADDRESS',
        'arista_eos_lldp': 'MGMT_ADDRESS',
        'cisco_ios_lldp': 'MGMT_ADDRESS',
        'cisco_nxos_lldp': 'MGMT_ADDRESS',
        'hp_procurve_lldp': 'MGMT_ADDRESS',
        'show_cdp': 'MGMT_ADDRESS',
        'show_lldp': 'MGMT_ADDRESS'
    },
    'local_interface': {
        'cisco_ios_cdp': 'LOCAL_INTERFACE',
        'cisco_nxos_cdp': 'LOCAL_INTERFACE',
        'hp_procurve_cdp': 'LOCAL_INTERFACE',
        'arista_eos_lldp': 'LOCAL_INTERFACE',
        'cisco_ios_lldp': 'LOCAL_INTERFACE',
        'cisco_nxos_lldp': 'LOCAL_INTERFACE',
        'hp_procurve_lldp': 'LOCAL_INTERFACE',
        'show_cdp': 'LOCAL_INTERFACE',
        'show_lldp': 'LOCAL_INTERFACE'
    },
    'remote_interface': {
        'cisco_ios_cdp': 'NEIGHBOR_INTERFACE',
        'cisco_nxos_cdp': 'NEIGHBOR_INTERFACE',
        'hp_procurve_cdp': 'NEIGHBOR_INTERFACE',
        'arista_eos_lldp': 'NEIGHBOR_INTERFACE',
        'cisco_ios_lldp': 'NEIGHBOR_PORT_ID',     # Matches template output
        'cisco_nxos_lldp': 'PORT_ID',
        'hp_procurve_lldp': 'PORT_ID',
        'show_cdp': 'NEIGHBOR_INTERFACE',
        'show_lldp': 'NEIGHBOR_PORT_ID'          # Changed to match template output
    },
    'platform': {
        'cisco_ios_cdp': 'PLATFORM',
        'cisco_nxos_cdp': 'PLATFORM',
        'hp_procurve_cdp': 'PLATFORM',
        'arista_eos_lldp': 'SYSTEM_DESC',
        'cisco_ios_lldp': 'NEIGHBOR_DESCRIPTION',  # Matches template output
        'cisco_nxos_lldp': 'SYSTEM_DESC',
        'hp_procurve_lldp': 'SYSTEM_DESC',
        'show_cdp': 'PLATFORM',
        'show_lldp': 'NEIGHBOR_DESCRIPTION'       # Changed to match template output
    }
}
class SSHConnection:
    def __init__(self, ssh_config, log_file=None, debug_output=False):
        self.debug_output = debug_output
        self.set_ssh_crypto_settings()

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_config['look_for_keys'] = False
        self.client.connect(**ssh_config)
        self.channel = self.client.invoke_shell('xterm')
        self.log_queue = queue.Queue()
        self.log_thread = None
        if log_file:
            self.log_thread = LogThread(self.log_queue, log_file)
            self.log_thread.start()

    def set_ssh_crypto_settings(self) -> None:
        """Sets SSH crypto settings for preferred KEX, ciphers, and keys."""
        if self.debug_output:
            print("Applying SSH crypto settings...")
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
        if self.debug_output:
            print("SSH crypto settings applied.")

    def send_command(self, command, timeout=30):
        """Send command and wait for output"""
        self.channel.send(command + '\n')
        time.sleep(1)  # Give device time to process

        output = ''
        start_time = time.time()

        while True:
            if self.channel.recv_ready():
                chunk = self.channel.recv(1024).decode('utf-8', errors='ignore')
                output += chunk

                # Check if we've reached the end of output (prompt)
                if '#' in chunk or '>' in chunk:
                    break

            # Check timeout
            if time.time() - start_time > timeout:
                break

            time.sleep(0.1)

        return output

    def close(self):
        if self.log_thread:
            self.log_queue.put(None)
            self.log_thread.join()
        self.channel.close()
        self.client.close()


class NeighborDiscovery:
    def __init__(self, db_path: str, verbose: bool = False):
        self.verbose = verbose
        self.tfsm_engine = TextFSMAutoEngine(db_path, verbose=verbose)

    def _reconstruct_lldp_neighbor(self, parsed_records: List[Dict]) -> List[Dict]:
        """Reconstruct LLDP neighbor information from parsed records."""
        neighbors = []
        for record in parsed_records:
            # Skip invalid or header lines
            if not record or 'show' in record.get('SYSTEM_NAME', '').lower():
                continue

            neighbor = {}
            # Map SYSTEM_NAME to device_id if available
            if record.get('SYSTEM_NAME'):
                neighbor['device_id'] = record['SYSTEM_NAME']

            # Extract Management Address
            if record.get('MGMT_ADDRESS') and record['MGMT_ADDRESS'] != '-':
                neighbor['ip_address'] = record['MGMT_ADDRESS']

            # Map interface fields
            if record.get('LOCAL_INTERFACE'):
                neighbor['local_interface'] = record['LOCAL_INTERFACE']
            if record.get('PORT_ID'):
                neighbor['remote_interface'] = record['PORT_ID']

            # Map System Description to platform
            if record.get('SYSTEM_DESC'):
                neighbor['platform'] = record['SYSTEM_DESC']

            # Add valid neighbor
            if self._is_valid_entry(neighbor):
                neighbors.append(neighbor)
            elif self.verbose:
                click.echo(f"Skipping invalid LLDP record: {json.dumps(record, indent=2)}")

        return neighbors

    def normalize_neighbor_data(self, parsed_data: List[Dict], template_name: str) -> List[Dict]:
        """Normalize parsed neighbor data to common format"""
        normalized = []
        template_type = self._determine_template_type(template_name)

        if not template_type:
            if self.verbose:
                click.echo(f"Could not determine template type for: {template_name}")
            return []

        if self.verbose:
            click.echo(f"\nNormalizing data using template type: {template_type}")
            click.echo(f"Input data: {json.dumps(parsed_data, indent=2)}")

        for neighbor in parsed_data:
            if self.verbose:
                click.echo(f"\nProcessing neighbor record: {json.dumps(neighbor, indent=2)}")

            norm_neighbor = {}
            for norm_field, template_mappings in NORMALIZED_FIELDS.items():
                field_mapping = template_mappings.get(template_type)

                if self.verbose:
                    click.echo(f"Looking for {norm_field} using mapping {field_mapping}")

                if isinstance(field_mapping, list):
                    for field in field_mapping:
                        if neighbor.get(field):
                            norm_neighbor[norm_field] = neighbor[field]
                            if self.verbose:
                                click.echo(f"Found {norm_field}: {neighbor[field]}")
                            break
                elif field_mapping:
                    value = neighbor.get(field_mapping, '')
                    if value:
                        norm_neighbor[norm_field] = value
                        if self.verbose:
                            click.echo(f"Set {norm_field}: {value}")

            # For LLDP records, ensure we map fields correctly
            if 'lldp' in template_type.lower():
                # Map NEIGHBOR_NAME to device_id if not already set
                if 'NEIGHBOR_NAME' in neighbor and not norm_neighbor.get('device_id'):
                    norm_neighbor['device_id'] = neighbor['NEIGHBOR_NAME']

                # Map NEIGHBOR_PORT_ID to remote_interface if not already set
                if 'NEIGHBOR_PORT_ID' in neighbor and not norm_neighbor.get('remote_interface'):
                    norm_neighbor['remote_interface'] = neighbor['NEIGHBOR_PORT_ID']

                # Map NEIGHBOR_DESCRIPTION to platform if not already set
                if 'NEIGHBOR_DESCRIPTION' in neighbor and not norm_neighbor.get('platform'):
                    norm_neighbor['platform'] = neighbor['NEIGHBOR_DESCRIPTION']

            if norm_neighbor:
                normalized.append(norm_neighbor)
                if self.verbose:
                    click.echo(f"Added normalized record: {json.dumps(norm_neighbor, indent=2)}")

        return normalized

    def _validate_ip(self, ip_str: str) -> bool:
        """Validate IP address format"""
        try:
            parts = ip_str.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except (AttributeError, TypeError, ValueError):
            return False

    def _is_valid_entry(self, entry: Dict) -> bool:
        """Validate a single normalized entry."""
        # For LLDP, we need either device_id or ip_address
        has_identifier = bool(entry.get('device_id') or entry.get('ip_address'))
        has_interface = bool(entry.get('local_interface'))

        if not (has_identifier and has_interface):
            if self.verbose:
                click.echo(
                    f"Entry missing required fields. Has identifier: {has_identifier}, Has interface: {has_interface}")
            return False

        # Validate IP if present
        if entry.get('ip_address') and not self._validate_ip(entry['ip_address']):
            if self.verbose:
                click.echo(f"Invalid IP address format: {entry['ip_address']}")
            return False

    def discover_neighbors(self, ssh_conn: SSHConnection) -> Dict[str, Dict]:
        """Discover neighbors using both CDP and LLDP protocols"""
        results = {
            'cdp': {'neighbors': [], 'score': 0.0, 'template': None},
            'lldp': {'neighbors': [], 'score': 0.0, 'template': None}
        }

        # Disable pagination first
        ssh_conn.send_command('terminal length 0')

        for protocol in ['cdp', 'lldp']:
            if self.verbose:
                click.echo(f"\nTrying {protocol.upper()} discovery...")

            command = f"show {protocol} neighbors detail"
            output = ssh_conn.send_command(command)

            if "Invalid input" in output or "not enabled" in output:
                if self.verbose:
                    click.echo(f"{protocol.upper()} not supported or enabled")
                continue

            template_name, parsed_data, score = self.tfsm_engine.find_best_template(
                output,
                filter_string=f"{protocol}_neighbors_detail"
            )

            if score > 0 and parsed_data:
                if self.verbose:
                    click.echo(f"\nTemplate matched: {template_name}")
                    click.echo(f"Parse Score: {score}")
                    click.echo(f"Records found: {len(parsed_data)}")
                    click.echo("\nRaw parsed data before processing:")
                    for entry in parsed_data[:2]:
                        click.echo(json.dumps(entry, indent=2))

                # Proceed with normalization
                normalized = self.normalize_neighbor_data(parsed_data, template_name)
                if normalized:
                    results[protocol]['neighbors'] = normalized
                    results[protocol]['score'] = score
                    results[protocol]['template'] = template_name
                    if self.verbose:
                        click.echo(click.style(
                            f"\nSuccessfully found {len(normalized)} {protocol.upper()} neighbors using {template_name} "
                            f"(score: {score:.2f})",
                            fg='green'
                        ))
                elif self.verbose:
                    click.echo(f"\nNo valid {protocol.upper()} neighbors found after normalization")

        return results

    def _determine_template_type(self, template_name: str) -> Optional[str]:
        """Determine template type from template name"""
        if not template_name:
            if self.verbose:
                click.echo("No template name provided")
            return None

        template_name = template_name.lower()

        if self.verbose:
            click.echo(f"Determining template type for: {template_name}")

        # More specific matches first
        if 'cisco_ios_show_cdp_neighbors_detail' in template_name:
            return 'cisco_ios_cdp'
        elif 'cisco_ios_show_lldp_neighbors_detail' in template_name:
            return 'cisco_ios_lldp'
        elif 'cisco_nxos_show_cdp' in template_name:
            return 'cisco_nxos_cdp'
        elif 'cisco_nxos_show_lldp' in template_name:
            return 'cisco_nxos_lldp'
        elif 'arista_eos_show_lldp' in template_name:
            return 'arista_eos_lldp'
        elif 'hp_procurve_show_cdp' in template_name:
            return 'hp_procurve_cdp'

        # Generic matches last
        elif '_show_cdp_' in template_name:
            return 'show_cdp'
        elif '_show_lldp_' in template_name or 'show lldp neighbors detail' in template_name:
            return 'show_lldp'

        if self.verbose:
            click.echo(f"No matching template type found")
        return None

    def _is_valid_neighbor_data(self, parsed_data: List[Dict]) -> bool:
        """Validate that parsed data contains real neighbor information"""
        if not parsed_data:
            return False

        first_entry = parsed_data[0]
        # Check for command echo or delimiter lines
        invalid_starts = {'show', '-', 'Device', 'Interface'}

        # Check CDP fields
        if 'NEIGHBOR_NAME' in first_entry:
            value = first_entry['NEIGHBOR_NAME']
            if value and not any(value.startswith(x) for x in invalid_starts):
                return True

        # Check LLDP fields
        if 'SYSTEM_NAME' in first_entry:
            value = first_entry['SYSTEM_NAME']
            if value and not any(value.startswith(x) for x in invalid_starts):
                return True

        return False

    def save_results_to_json(self, results: Dict[str, Dict], filepath: str) -> None:
        """Save discovery results to a JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            if self.verbose:
                click.echo(f"\nResults saved to {filepath}")
        except Exception as e:
            click.echo(click.style(f"Error saving results: {str(e)}", fg='red'))


def test_neighbor_discovery():
    """Test function for neighbor discovery"""
    ssh_config = {
        'hostname': '172.16.101.1',
        'username': 'cisco',
        'password': 'cisco',
        'look_for_keys': False
    }

    try:
        # Initialize SSH connection
        ssh = SSHConnection(ssh_config, debug_output=True)

        # Initialize neighbor discovery
        discovery = NeighborDiscovery('tfsm_templates.db', verbose=True)

        # Discover neighbors
        results = discovery.discover_neighbors(ssh)

        # Print results for each protocol
        click.echo("\nDiscovery Results:")

        for protocol in ['cdp', 'lldp']:
            protocol_results = results[protocol]
            if protocol_results['neighbors']:
                click.echo(f"\n{protocol.upper()} Results:")
                click.echo(f"Template: {protocol_results['template']}")
                click.echo(f"Score: {protocol_results['score']:.2f}")
                click.echo(f"Found {len(protocol_results['neighbors'])} neighbors:")

                for neighbor in protocol_results['neighbors']:
                    click.echo(click.style("\nNeighbor Device:", fg='blue'))
                    for field, value in neighbor.items():
                        click.echo(f"{field}: {value}")
            else:
                click.echo(f"\nNo {protocol.upper()} neighbors found")

        # Save results to JSON
        output_file = 'neighbor_discovery_results.json'
        discovery.save_results_to_json(results, output_file)

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'))
    finally:
        ssh.close()


if __name__ == "__main__":
    test_neighbor_discovery()

if __name__ == "__main__":
    test_neighbor_discovery()