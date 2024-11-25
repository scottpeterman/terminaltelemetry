import json
import os
import re
from typing import Dict, List, Optional
from discovery_util import SSHConnection, NeighborDiscovery
from focused_network_map import create_focused_network_diagram


class NetworkMapper:
    def __init__(self, ssh_config: Dict, output_dir: str, verbose: bool = False):
        self.ssh_config = ssh_config
        self.output_dir = output_dir
        self.verbose = verbose
        os.makedirs(output_dir, exist_ok=True)

    def clean_hostname(self, hostname: str) -> str:
        """Clean up hostname by removing domain and special characters"""
        # Remove domain name (everything after first dot)
        hostname = hostname.split('.')[0]

        # Remove any special characters commonly found in device names
        hostname = re.sub(r'[(){}\[\]\'"`]', '', hostname)

        # Convert to lowercase and strip whitespace
        hostname = hostname.lower().strip()

        return hostname

    def get_hostname_from_prompt(self, ssh_conn: SSHConnection) -> str:
        """Extract hostname from device prompt"""
        # Send newline to get prompt
        output = ssh_conn.send_command('\n')
        # Look for hostname in prompt (assumes format like "hostname#" or "hostname>")
        prompt_line = output.strip().split('\n')[-1]
        hostname = prompt_line.split('#')[0].split('>')[0].strip()
        return self.clean_hostname(hostname)

    def transform_neighbors_to_map_format(self, hostname: str, neighbors_data: Dict) -> Dict:
        """Transform neighbor discovery data to mapping format"""
        network_map = {hostname: {"peers": {}}}

        # Process both CDP and LLDP neighbors
        for protocol in ['cdp', 'lldp']:
            for neighbor in neighbors_data[protocol]['neighbors']:
                # Clean up peer_id by removing domain name and special characters
                peer_id = self.clean_hostname(neighbor.get('device_id', ''))
                if not peer_id:
                    continue

                # Initialize peer entry if not exists
                if peer_id not in network_map[hostname]['peers']:
                    network_map[hostname]['peers'][peer_id] = {
                        "connections": []
                    }

                # Clean up interface names
                local_port = self.clean_interface_name(neighbor.get('local_interface', ''))
                remote_port = self.clean_interface_name(neighbor.get('remote_interface', ''))
                connection = [local_port, remote_port]

                # Avoid duplicate connections
                if connection not in network_map[hostname]['peers'][peer_id]['connections']:
                    network_map[hostname]['peers'][peer_id]['connections'].append(connection)

                # Add peer as a node with reverse connection
                if peer_id not in network_map:
                    network_map[peer_id] = {"peers": {
                        hostname: {
                            "connections": [[remote_port, local_port]]
                        }
                    }}

        return network_map

    def clean_interface_name(self, interface: str) -> str:
        """Normalize interface names for consistency"""
        # Common interface abbreviations
        interface_map = {
            'Gi': 'GigabitEthernet',
            'Te': 'TenGigabitEthernet',
            'Fa': 'FastEthernet',
            'Eth': 'Ethernet',
            'Po': 'Port-channel',
            'Lo': 'Loopback',
            'Vl': 'Vlan'
        }

        # Clean up the interface name
        interface = interface.strip()

        # Expand common abbreviated interface names
        for abbrev, full in interface_map.items():
            if interface.startswith(abbrev):
                interface = interface.replace(abbrev, full)
                break

        return interface

    def create_network_map(self, max_hops: int = 2) -> str:
        """Create network map starting from discovered device."""
        try:
            ssh_conn = SSHConnection(self.ssh_config, debug_output=self.verbose)

            # Get and clean the resolved hostname
            hostname = self.get_hostname_from_prompt(ssh_conn)
            hostname = self.clean_hostname(hostname)
            self.ssh_config['resolved_hostname'] = hostname

            if self.verbose:
                print(f"Resolved hostname: {hostname}")

            # Discover neighbors
            discovery = NeighborDiscovery('tfsm_templates.db', verbose=self.verbose)
            neighbors_data = discovery.discover_neighbors(ssh_conn)

            # Transform data to mapping format
            network_map = self.transform_neighbors_to_map_format(hostname, neighbors_data)

            # Save intermediate JSON for debugging
            json_path = os.path.join(self.output_dir, 'network_map.json')
            with open(json_path, 'w') as f:
                json.dump(network_map, f, indent=2)

            # Use create_focused_network_diagram with circular layout
            output_file = create_focused_network_diagram(
                json_file=json_path,
                output_dir=self.output_dir,
                map_name='network_topology',
                start_node=hostname,
                max_hops=max_hops,
                layout_algo='circular'
            )

            # Verify the file exists
            if output_file and os.path.exists(output_file):
                if self.verbose:
                    print(f"Network map created successfully: {output_file}")
                return output_file
            else:
                if self.verbose:
                    print(f"Map file was not created: {output_file}")
                return None

        except Exception as e:
            print(f"Error creating network map: {str(e)}")
            return None
        finally:
            if 'ssh_conn' in locals():
                ssh_conn.close()

def main():
    # Example usage
    ssh_config = {
        'hostname': '172.16.101.1',
        'username': 'cisco',
        'password': 'cisco',
        'look_for_keys': False
    }

    mapper = NetworkMapper(
        ssh_config=ssh_config,
        output_dir='network_maps',
        verbose=True
    )
    mapper.create_network_map(max_hops=2)


if __name__ == "__main__":
    main()