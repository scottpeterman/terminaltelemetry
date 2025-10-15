# SSH Key-Based Authentication Implementation

## Overview

This implementation adds robust SSH key-based authentication with comprehensive cipher/KEX compatibility for connecting to network devices (Cisco, Juniper, Arista, Palo Alto, etc.) and legacy servers.

## 🎯 Key Features

1. **Automatic Key Authentication** - When password is blank (`""`), automatically uses SSH key from config
2. **JSON Key Configuration** - Flexible key management with host-specific, user-specific, and default keys
3. **Multi-Key Type Support** - Automatically detects and uses RSA, ED25519, ECDSA, and DSS keys
4. **Legacy Device Compatibility** - Comprehensive cipher/KEX algorithm support for older network equipment
5. **Algorithm Detection** - Proactively detects and validates server-supported algorithms
6. **Detailed Debug Output** - Clear logging of connection process and negotiated algorithms

---

## 🔧 The Problem We Solved

### Issue #1: Unknown Cipher Errors
**Problem:** Paramiko's `ValueError: unknown cipher` when connecting to devices.

**Root Cause:** We were setting cipher/KEX/key algorithms in `Transport._preferred_*` lists that weren't compiled into the Paramiko installation.

**Solution:** 
```python
# Detect what's actually available in Paramiko
available_ciphers = list(transport_module.Transport._cipher_info.keys())
available_kex = list(transport_module.Transport._kex_info.keys())
available_keys = list(transport_module.Transport._key_info.keys())

# Filter our preferences to only include available algorithms
self.cipher_settings = tuple([c for c in self.cipher_settings if c in available_ciphers])
```

This ensures we only use algorithms that Paramiko actually supports, preventing the "unknown cipher" error.

### Issue #2: Key Authentication Not Working
**Problem:** Key authentication would hang or fail silently.

**Root Cause:** 
1. Algorithm detection was trying to connect to `localhost:22` which would hang if SSH wasn't running
2. Key type detection wasn't comprehensive enough
3. No clear error messages when things went wrong

**Solution:**
- Removed localhost detection (not needed - Paramiko negotiates automatically)
- Added timeout-based server algorithm detection (optional, for debugging)
- Enhanced key loading to try all key types (RSA, ED25519, ECDSA, DSS)
- Added comprehensive debug logging at every step

---

## 📋 How It Works

### Authentication Flow

```
1. User provides blank password ("")
   ↓
2. SSHKeyConfig looks up key path:
   - Check for host-specific key (e.g., "10.0.0.104")
   - Check for username-specific key (e.g., "admin")
   - Check for default key
   - Check common locations (~/.ssh/id_rsa, etc.)
   ↓
3. Detect available algorithms in Paramiko
   - Read Transport._cipher_info, _kex_info, _key_info
   - Filter preferences to only available algorithms
   ↓
4. Optional: Detect server algorithms (with 3s timeout)
   - Shows what server proposes
   - Validates compatibility
   ↓
5. Load SSH key
   - Try RSA, ED25519, ECDSA, DSS formats
   - Detect key type
   ↓
6. Connect with key
   - client.connect(pkey=private_key)
   - Paramiko negotiates using our filtered algorithm list
   ↓
7. Setup shell
   - Invoke shell or create PTY
   - Start ShellReaderThread
   ↓
8. Success! Terminal is ready
```

### Key Configuration Priority

```
Host-specific key (highest priority)
  ↓
Username-specific key
  ↓
Default key
  ↓
Auto-discovery (~/.ssh/id_rsa, etc.)
```

---

## 🔑 Configuration

### JSON Configuration File

**Location:** `~/.ssh_manager/keys.json`

**Structure:**
```json
{
  "default_key": "/home/user/.ssh/id_rsa",
  "keys": {
    "admin": "/home/user/.ssh/admin_key",
    "root": "/home/user/.ssh/root_key",
    "netadmin": "/home/user/.ssh/network_key"
  },
  "host_keys": {
    "10.0.0.104": "/home/user/.ssh/production_key",
    "192.168.1.1": "/home/user/.ssh/lab_key",
    "switch01.example.com": "/home/user/.ssh/switch_key"
  }
}
```

### Managing Keys

Use the included `manage_keys_script.py`:

```bash
python manage_keys_script.py

Options:
1. View current configuration
2. Set default key
3. Add host-specific key
4. Add user-specific key
5. Test key lookup
6. Exit
```

Or programmatically:

```python
from ssh_key_config import SSHKeyConfig

config = SSHKeyConfig()

# Set default key
config.set_default_key("/home/user/.ssh/id_rsa")

# Add host-specific key
config.add_host_key("10.0.0.104", "/home/user/.ssh/prod_key")

# Add user-specific key
config.add_user_key("admin", "/home/user/.ssh/admin_key")

# Lookup key
key_path = config.get_key_path(host="10.0.0.104", username="admin")
```

---

## 🛠️ Algorithm Support

### Ciphers (in preference order)
Modern (preferred):
- `aes128-ctr`, `aes192-ctr`, `aes256-ctr`
- `aes128-gcm@openssh.com`, `aes256-gcm@openssh.com`
- `chacha20-poly1305@openssh.com`

Legacy (for older devices):
- `aes128-cbc`, `aes192-cbc`, `aes256-cbc`
- `3des-cbc`

### KEX Algorithms
Modern:
- `diffie-hellman-group14-sha256`
- `diffie-hellman-group-exchange-sha256`
- `ecdh-sha2-nistp256/384/521`
- `curve25519-sha256`

Legacy (for network devices):
- `diffie-hellman-group14-sha1`
- `diffie-hellman-group-exchange-sha1`
- `diffie-hellman-group1-sha1`

### Host Key Types
- `rsa-sha2-512`, `rsa-sha2-256` (modern)
- `ssh-rsa` (legacy, widely supported)
- `ecdsa-sha2-nistp256/384/521`
- `ssh-ed25519`
- `ssh-dss` (very old devices)

---

## 📊 Debug Output

### Successful Connection Example

```
Applied transport settings:
  Ciphers: aes128-ctr, aes192-ctr, aes256-ctr... (9 total)
  KEX: diffie-hellman-group14-sha256, ecdh-sha2-nistp256... (10 total)
  Keys: rsa-sha2-512, rsa-sha2-256, ssh-rsa... (7 total)

Password is blank, attempting key-based authentication
Using default key: /Users/user/.ssh/id_rsa
Found key in config: /Users/user/.ssh/id_rsa

=== Detecting server algorithms for host:22 ===
SERVER PROPOSES:
  Ciphers (c->s): aes256-ctr, aes192-ctr, aes128-ctr
  KEX algorithms: ecdh-sha2-nistp521, ecdh-sha2-nistp256
  Host key types: rsa-sha2-512, rsa-sha2-256, ssh-rsa

COMPATIBILITY CHECK:
  ✓ Common ciphers: aes128-ctr, aes192-ctr, aes256-ctr
  ✓ Common KEX: ecdh-sha2-nistp256, ecdh-sha2-nistp521
  ✓ Common keys: rsa-sha2-512, rsa-sha2-256, ssh-rsa
============================================================

Loading SSH key...
✓ Loaded RSA key successfully
Connecting to host:22 with RSA key...
✓ Connection established!
✓ Successfully authenticated with RSA key

✓ Transport acquired
  Negotiated cipher: aes128-ctr
  Negotiated MAC: hmac-sha2-256
  Negotiated KEX: ecdh-sha2-nistp256

Setting up shell...
  → Invoking shell...
  ✓ Shell invoked successfully!
  → Starting ShellReaderThread...
  ✓ ShellReaderThread started
✓ Backend initialization complete!
```

---

## 🚨 Troubleshooting

### "No SSH key found in config"
**Cause:** No key configured and none found in standard locations.

**Fix:** 
```bash
python manage_keys_script.py
# Select option 2 to set default key
```

### "Key is encrypted and requires a passphrase"
**Cause:** Your SSH key has a passphrase.

**Fix:** Either:
1. Use a key without passphrase for automation
2. Implement passphrase handling (future enhancement)

### "No common ciphers/KEX/keys"
**Cause:** Server requires algorithms not available in your Paramiko.

**Fix:**
1. Upgrade Paramiko: `pip install --upgrade paramiko`
2. Check server's algorithm list in debug output
3. Install cryptography with more algorithms: `pip install cryptography`

### Connection hangs
**Cause:** Network issue or firewall blocking SSH port.

**Fix:**
1. Verify connectivity: `telnet host 22`
2. Check firewall rules
3. Increase timeout in `_detect_server_algorithms(timeout=10)`

---

## 📁 Files

- **`sshshell.py`** - Main SSH backend with key auth logic
- **`ssh_key_config.py`** - JSON-based key configuration manager
- **`manage_keys_script.py`** - Interactive key configuration tool
- **`sshshellreader.py`** - Thread for reading SSH channel output
- **`~/.ssh_manager/keys.json`** - User's key configuration (auto-created)

---

## 🎯 Usage Examples

### Connect with blank password (uses key auth)
```python
backend = Backend(
    host="switch01.example.com",
    username="admin",
    password="",  # Blank triggers key auth
    port="22"
)
```

### Connect with explicit key path
```python
backend = Backend(
    host="router.example.com",
    username="netadmin",
    key_path="/path/to/specific/key",
    port="22"
)
```

### Connect with password
```python
backend = Backend(
    host="server.example.com",
    username="user",
    password="actual_password",
    port="22"
)
```

---

## 🔮 Future Enhancements

- [ ] SSH key passphrase support
- [ ] SSH agent integration
- [ ] Certificate-based authentication
- [ ] Connection pooling/reuse
- [ ] Automatic algorithm fallback on connection failure
- [ ] Key generation utility

---

## 📝 Technical Notes

### Why Algorithm Filtering Works

Paramiko internally maintains dictionaries of supported algorithms:
- `Transport._cipher_info` - Available cipher implementations
- `Transport._kex_info` - Available KEX algorithms
- `Transport._key_info` - Available host key types

When `client.connect()` is called, it checks if requested algorithms exist in these dictionaries. By reading these dictionaries first and filtering our preferences, we ensure we only request algorithms that Paramiko can actually handle.

### Why We Set Global Transport Preferences

```python
paramiko.Transport._preferred_ciphers = self.cipher_settings
```

This sets the preference order for ALL Transport instances. When the client creates a transport during `connect()`, it inherits these preferences and uses them during KEX negotiation with the server.

### Server Algorithm Detection

The optional server algorithm detection hooks into Paramiko's `_parse_kex_init` method to capture the server's KEX_INIT message before negotiation completes. This gives us visibility into what the server offers, which is invaluable for debugging compatibility issues.

---

## ✅ Success Criteria

You know everything is working when you see:

1. ✓ Applied transport settings (filtered to available algorithms)
2. ✓ Found key in config
3. ✓ Loaded [KEY_TYPE] key successfully
4. ✓ Connection established
5. ✓ Successfully authenticated
6. ✓ Transport acquired with negotiated algorithms
7. ✓ Shell invoked successfully
8. ✓ ShellReaderThread started
9. ✓ Backend initialization complete

---

## 📜 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

## 🙏 Acknowledgments

- Paramiko library for SSH implementation
- PyQt6 for GUI framework
- PyQt6 for GUI framework