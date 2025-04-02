# DarkPTY Developer Guide

This guide is intended for developers extending or integrating with **DarkPTY**, especially around its Telemetry and Theme systems.

---

## Telemetry Architecture

DarkPTY supports device telemetry via a **NAPALM-inspired interface**, but is not bound to the NAPALM library. Drivers are modular and can be extended or swapped easily.

### Driver Structure
Drivers follow this base contract:

```python
class CustomDriver:
    def open(self): ...
    def close(self): ...
    def get_facts(self): ...
    def get_interfaces(self): ...
    def get_environment(self): ...
    def get_lldp_neighbors_detail(self): ...
    def get_route_to(self, destination): ...
```

All methods are expected to return dictionaries that follow the existing Terminal Telemetry schema.

### Built-in Drivers

| Driver Name | Platform     | Backing Library | Notes                      |
|-------------|--------------|------------------|----------------------------|
| `ios`       | Cisco IOS    | Netmiko/NAPALM   | SSH required               |
| `eos`       | Arista EOS   | Netmiko/NAPALM   |                            |
| `nxos_ssh`  | Cisco NXOS   | Netmiko/NAPALM   | SSH-based NXOS variant     |
| `junos`     | Juniper      | NAPALM           | Requires SSH + RPC support |
| `linux`     | Linux        | Netmiko          | Custom driver (non-NAPALM) |

---

## LinuxDriver - Example Custom Driver

The included `LinuxDriver` showcases extensibility:

- Fully functional SSH-based Linux telemetry
- Uses Netmiko's `linux_ssh` platform
- Includes custom sudo handling
- Auto-detects VMware for telemetry suppression
- Compatible with TelemetryCollector schemas

#### Highlights

- CPU usage computed from `/proc/stat`
- Memory computed from `/proc/meminfo`
- Temperature, Fan, and Power data from `/sys/class/hwmon`
- LLDP via `lldpctl -f keyvalue`
- Routes via `ip route show`

#### Advanced Features

- Graceful fallback when sensors or files are missing
- Debug logging and output capture
- File-based debug output via `_write_debug()`

---

## Session Files

DarkPTY uses generic, highly portable YAML files to define sessions. These session definitions are intentionally open and easy to manipulate. They decouple secure credentials from session definitions and make sharing across environments straightforward.

### Format
Each YAML file contains a list of folders and sessions:

```yaml
- folder_name: Lab
  sessions:
    - display_name: Router01
      host: 192.168.1.1
      port: 22
      DeviceType: ios
      Vendor: cisco
      Model: ISR4431
      SoftwareVersion: 16.9.3
      SerialNumber: FGL1234567Y
      credsid: 1
```

### Benefits
- Portable and human-readable
- Version-control and diff-friendly
- Secure credentials stored separately (referenced by `credsid`)
- Supported by LogicMonitor and NetBox importers
- Easy to manipulate for batch operations or automation

### Why YAML?
DarkPTY avoids opaque binary formats or tightly bound config folders (like SecureCRT's `.ini` mess). YAML provides clarity, portability, and diffable structure. This design came from real-world frustrations with shared SecureCRT folders.

### Importers
- LogicMonitor and NetBox integration scripts generate these YAML files
- YAML output can be imported directly into DarkPTY's session tree
- Folder structure and metadata are preserved automatically

---

## Theme System

DarkPTY uses a flexible JSON-based theme system compatible with both UI panels and terminal rendering.

### Theme Structure

```json
{
  "name": "gruvbox",
  "colors": {
    "primary": "#282828",
    "text": "#ebdbb2",
    "border": "#b8bb26",
    "success": "#b8bb26",
    "error": "#cc241d",
    "grid": "rgba(184,187,38,0.1)"
  },
  "terminal": {
    "foreground": "#ebdbb2",
    "background": "#282828",
    "cursor": "#ebdbb2",
    "black": "#282828",
    "red": "#cc241d",
    "green": "#98971a",
    ...
  }
}
```

### Theme Editor

DarkPTY includes a theme editor supporting:

- Live preview
- xterm color palette editing
- Corner design selection
- Scrollbar, grid, and border style customization

---

## Adding a New Driver

1. Subclass a new driver following the base interface.
2. Implement SSH connection via Netmiko or other methods.
3. Return telemetry fields matching the collector schema.
4. Register your driver type in the session form.

---

## Questions or Contributions?
PRs and feedback welcome on [GitHub](https://github.com/scottpeterman/darkpty).

---

*Built with extensibility in mind. The more drivers, the darker the pty.*

