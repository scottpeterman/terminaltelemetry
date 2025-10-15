# ssh_key_config.py
import json
import os
from pathlib import Path


class SSHKeyConfig:
    """Manages SSH key configuration from JSON file"""

    def __init__(self, config_path=None):
        if config_path is None:
            # Default to user's home directory
            self.config_path = Path.home() / ".ssh_manager" / "keys.json"
        else:
            self.config_path = Path(config_path)

        self.ensure_config_exists()

    def ensure_config_exists(self):
        """Create config directory and default file if they don't exist"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.config_path.exists():
            # Create default config with common key locations
            default_config = {
                "default_key": str(Path.home() / ".ssh" / "id_rsa"),
                "keys": {
                    "default": str(Path.home() / ".ssh" / "id_rsa"),
                    "id_rsa": str(Path.home() / ".ssh" / "id_rsa"),
                    "id_ed25519": str(Path.home() / ".ssh" / "id_ed25519"),
                    "id_ecdsa": str(Path.home() / ".ssh" / "id_ecdsa")
                },
                "host_keys": {
                    # Example: "10.0.0.1": "/path/to/specific/key"
                }
            }
            self.save_config(default_config)

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading SSH key config: {e}")
            return {"default_key": str(Path.home() / ".ssh" / "id_rsa"), "keys": {}, "host_keys": {}}

    def save_config(self, config):
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving SSH key config: {e}")

    def get_key_path(self, host=None, username=None):
        """
        Get SSH key path for authentication.
        Priority: host-specific key > username-specific key > default key

        Args:
            host: Target hostname/IP (optional)
            username: SSH username (optional)

        Returns:
            str: Path to SSH private key file, or None if not found
        """
        config = self.load_config()

        # 1. Check for host-specific key
        if host and host in config.get("host_keys", {}):
            key_path = config["host_keys"][host]
            if os.path.exists(key_path):
                print(f"Using host-specific key for {host}: {key_path}")
                return key_path

        # 2. Check for username-specific key
        if username and username in config.get("keys", {}):
            key_path = config["keys"][username]
            if os.path.exists(key_path):
                print(f"Using username-specific key for {username}: {key_path}")
                return key_path

        # 3. Check for default key
        default_key = config.get("default_key")
        if default_key and os.path.exists(default_key):
            print(f"Using default key: {default_key}")
            return default_key

        # 4. Try common key locations
        common_keys = [
            Path.home() / ".ssh" / "id_rsa",
            Path.home() / ".ssh" / "id_ed25519",
            Path.home() / ".ssh" / "id_ecdsa"
        ]

        for key_path in common_keys:
            if key_path.exists():
                print(f"Using discovered key: {key_path}")
                return str(key_path)

        print("No SSH key found")
        return None

    def add_host_key(self, host, key_path):
        """Add or update a host-specific key"""
        config = self.load_config()
        if "host_keys" not in config:
            config["host_keys"] = {}
        config["host_keys"][host] = key_path
        self.save_config(config)
        print(f"Added key for host {host}: {key_path}")

    def add_user_key(self, username, key_path):
        """Add or update a username-specific key"""
        config = self.load_config()
        if "keys" not in config:
            config["keys"] = {}
        config["keys"][username] = key_path
        self.save_config(config)
        print(f"Added key for user {username}: {key_path}")

    def set_default_key(self, key_path):
        """Set the default SSH key"""
        config = self.load_config()
        config["default_key"] = key_path
        self.save_config(config)
        print(f"Set default key: {key_path}")


# Example JSON structure that will be created:
"""
{
  "default_key": "/home/user/.ssh/id_rsa",
  "keys": {
    "default": "/home/user/.ssh/id_rsa",
    "id_rsa": "/home/user/.ssh/id_rsa",
    "id_ed25519": "/home/user/.ssh/id_ed25519",
    "id_ecdsa": "/home/user/.ssh/id_ecdsa",
    "admin": "/home/user/.ssh/admin_key",
    "root": "/home/user/.ssh/root_key"
  },
  "host_keys": {
    "10.0.0.104": "/home/user/.ssh/production_key",
    "192.168.1.100": "/home/user/.ssh/lab_key"
  }
}
"""