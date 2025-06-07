# TerminalTelemetry

![Screenshot](https://raw.githubusercontent.com/scottpeterman/terminaltelemetry/refs/heads/main/screenshots/v2/slides1.gif)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![PyPI](https://img.shields.io/badge/pip-installable-green.svg)

**TerminalTelemetry** is a modern, cyberpunk-inspired terminal emulator and network telemetry platform built with PyQt6. It combines powerful SSH terminal capabilities with real-time network device monitoring in a sleek, themeable interface.

## 🚀 Installation

### PyPI Installation (Recommended)
```bash
pip install TerminalTelemetry
termtel-con
termtel
```

### Development Installation
```bash
git clone https://github.com/scottpeterman/terminaltelemetry.git
cd terminaltelemetry
pip install -e .
termtel
```

### Prerequisites
- Python 3.9+
- PyQt6, netmiko, textfsm (automatically installed with pip)

---

## Current Features

### 🎨 **Advanced Theme System**
- **20+ built-in themes** (Cyberpunk, Dark Mode, Retro Green, Neon Blue, etc.)
- **Dynamic JSON-based themes** with hot-reload capability
- **Live theme switching** across all components without restart
- **Per-tab theme customization** via right-click context menu
- **Individual terminal theming** - different theme for each tab
- **Theme editor** with real-time preview and custom theme creation
- **Consistent theming** across terminals, telemetry widgets, and UI components
- **Tab management** with rename functionality and clean context menus

### 🖥️ **Multi-Session Terminal Environment**
- **Tabbed SSH terminals** with xterm.js backend
- **Session management** with YAML-based configuration
- **Per-tab customization** - individual themes and renamed tab labels
- **Context menu controls** - close, rename, and theme individual tabs
- **Quick Connect** interface for rapid device access
- **Cross-platform terminal support** (Windows, macOS, Linux)

## Getting Started

### Quick Start
1. **Install via pip**: `pip install TerminalTelemetry`
2. **Launch**: `termtel`
3. **Create SSH sessions** via File → Open Sessions or use Quick Connect
4. **Open Telemetry Dashboard** via Tools → Telemetry Dashboard
5. **Connect to devices** and view real-time monitoring data
6. **Customize themes** via View → Theme menu and Theme Editor
7. **Right-click tab labels** to rename tabs or set individual themes

### Theme Customization
- **Global themes**: Use View → Theme menu to change all components
- **Individual tab themes**: Right-click any tab label → Terminal Theme → select theme
- **Custom themes**: Use View → Theme → Theme Editor to create new themes
- **Theme files**: Drop JSON theme files in the `themes/` directory for instant availability
- 
### 🖥️ **Multi-Session Terminal Environment**
- **Tabbed SSH terminals** with xterm.js backend
- **Session management** with YAML-based configuration
- **Quick Connect** interface for rapid device access
- **Cross-platform terminal support** (Windows, macOS, Linux)

### 📊 **Real-Time Network Telemetry**
- **Live device monitoring** via SSH (no SNMP required)
- **Multi-vendor support** (Cisco IOS/IOS-XE/NX-OS, Arista EOS, Linux)
- **Real-time data collection**:
  - System information (hostname, version, uptime, hardware)
  - CPU and memory utilization with progress bars
  - CDP/LLDP neighbor discovery
  - ARP table monitoring
  - Routing table with VRF support
  - Live system log streaming
- **Threaded data collection** keeps UI responsive
- **Template-based parsing** with 200+ TextFSM templates
- **CSV export** for all telemetry data tables

### 🔧 **Template System & Customization**
- **Built-in template editor** with syntax highlighting
- **200+ pre-configured TextFSM templates** for network devices
- **Live template testing** against real device output
- **Field mapping validation** with coverage reports
- **Template debugging** with detailed error reporting
- **Package resource management** - templates included in installation

### 🔒 **Enterprise Security**
- **Encrypted credential storage** with Fernet (AES-128-CBC) + HMAC
- **PBKDF2-HMAC-SHA256** key derivation (480,000 iterations)
- **Platform-specific secure storage** locations
- **Machine-specific credential binding**
- **Rate-limited authentication** prevents brute force
- **Zero plaintext storage** of sensitive data

### 🚀 **Session Import Tools**
- **NetBox Integration**:
  - Import devices directly from NetBox instances
  - Site-based organization and grouping
  - Automatic credential mapping
- **LogicMonitor Integration**:
  - SDK-based device discovery
  - Progress feedback and error handling
  - SSL certificate validation support

### 🎮 **Built-in Productivity Tools**
- **Text Editor** with syntax highlighting
- **Diff Tool** for configuration comparison
- **Space Debris Game** (Asteroids clone)
- **Doom** (WebAssembly port)
- **Serial Terminal** for console connections

---

## Architecture Highlights

### **SSH-Only Monitoring**
- **Universal compatibility** - works with any SSH-accessible device
- **No agent installation** required on target devices
- **Leverages existing access** - uses SSH credentials you already have
- **Zero infrastructure** - no monitoring servers or databases needed

### **Template-Driven Parsing**
- **200+ TextFSM templates** packaged with the application
- **Live template editing** with syntax highlighting and testing
- **Field normalization** across different vendors
- **Package resource system** - templates accessible in any environment
- **User-customizable** - fix parsing issues yourself

### **Modern Desktop Architecture**
- **Qt6-based UI** with native performance
- **Threaded data collection** prevents UI blocking
- **Signal-based communication** between components
- **Modular widget system** for easy extension
- **Package-aware resource management** for pip installations

---

## Getting Started

### Quick Start
1. **Install via pip**: `pip install TerminalTelemetry`
2. **Launch**: `termtel-con`
   - themes will bootstrap
   - run `termtel` or `termtel-con`
   - For Windows, venv\Scripts will contain .exe files you can create shortcuts to termtel.exe to feel more native.
3. **Create SSH sessions** via File → Open Sessions or use Quick Connect
4. **Open Telemetry Dashboard** via Tools → Telemetry Dashboard
5. **Connect to devices** and view real-time monitoring data
6. **Customize themes** via View → Theme menu and Theme Editor

### First Device Connection
1. Click **"Quick Connect"** in the bottom panel
2. Enter device IP, credentials, and select platform (cisco_ios, arista_eos, etc.)
3. Click **"Connect"** - terminal tab opens automatically
4. Open **Tools → Telemetry Dashboard** to see real-time monitoring
5. Use the **gear buttons** in widgets to customize TextFSM templates

### Template Customization
1. Connect to a device and open telemetry dashboard
2. Click the **⚙️ gear button** on any widget (neighbors, routes, etc.)
3. **Template editor opens** with current template and sample data
4. **Edit template** using TextFSM syntax
5. **Click "RUN TEST"** to validate against live device output
6. **Save template** - changes apply immediately

---

## Why This Approach Works

### **Superior to Commercial Tools**
- **No vendor lock-in** - works with any SSH device
- **Instant deployment** - `pip install` and run anywhere
- **Full customization** - templates, themes, everything is editable
- **Cost effective** - no licensing fees or subscription costs
- **Engineer friendly** - shows actual commands and output
- **Self-contained** - no external dependencies or servers

### **Network Engineer Workflow**
- Uses **familiar SSH access** you already have configured
- **Command-line transparency** - see exactly what commands are run
- **Template debugging** - fix parsing issues when vendors change output
- **Portable** - runs on your laptop without server infrastructure
- **Export capability** - CSV export for further analysis

---

## Supported Platforms

### **Full Support (Complete Telemetry Dashboard)**
- **Cisco IOS/IOS-XE**: System info, CDP neighbors, ARP table, routing table, CPU/memory utilization, system logs, VRF support

### **Partial Support (Basic Telemetry)**
- **Cisco NX-OS**: System info, CDP neighbors, ARP table, routing table, VRF support *(missing CPU/memory/logs)*
- **Arista EOS**: System info, LLDP neighbors, ARP table, routing table, CPU/memory, temperature, logs, VRF support *(uses LLDP instead of CDP)*

### **Basic Support (Limited Telemetry)**
- **Aruba AOS-S/CX**: System info, LLDP neighbors, ARP table, routing table *(missing CPU/memory/logs)*
- **HP ProCurve**: System info, LLDP neighbors, ARP table, routing table *(legacy switch support)*
- **Juniper JunOS**: System info, LLDP neighbors, ARP table *(minimal support)*
- **Linux**: System info, ARP table, routing table *(basic networking commands)*

### **Template Coverage**
Based on your actual TextFSM template library:
- **200+ templates total** across all vendors
- **Cisco IOS**: 100+ templates (most comprehensive)
- **Arista EOS**: 45+ templates (good coverage)
- **Cisco NX-OS**: 15+ templates (basic coverage)
- **HP ProCurve**: 7 templates (legacy support)
- **Juniper JunOS**: 3 templates (minimal)
- **Linux**: Basic networking templates
- **Aruba**: Basic switch templates

---

## Known Issues & Limitations

### **Known Platform Limitations**
- **Cisco NX-OS**: Missing CPU/memory utilization and system log templates
- **Aruba platforms**: No CPU/memory monitoring templates available  
- **HP ProCurve**: Legacy platform with limited template coverage
- **Juniper JunOS**: Minimal template support (contributions welcome)
- **Linux**: Basic networking only (no system monitoring templates)

### **Template Coverage Notes**
- **Cisco IOS/IOS-XE** has the most comprehensive template coverage
- **Arista EOS** has good coverage but uses LLDP instead of CDP for neighbors
- Other platforms have basic connectivity but may lack advanced telemetry features
- Missing templates can be created using the built-in template editor

### **Current Application Limitations**
- Single-device monitoring per telemetry tab (multi-device dashboard planned)
- No historical data storage (trending features planned)
- Template editor requires platform connection for live testing

---

## Planned Features & Roadmap

### **Near Term (v0.11-0.12)**
- **Multi-device dashboards** for network-wide monitoring
- **Historical data collection** with basic trending graphs
- **Enhanced error handling** and automatic reconnection
- **Template sharing** and import/export functionality
- **Custom command execution** with ad-hoc template creation

### **Medium Term (v0.13-0.15)**
- **Network topology discovery** and visualization
- **Configuration backup** and change detection
- **Alert system** for threshold monitoring
- **Plugin architecture** for community extensions
- **REST API** for external integrations

### **Long Term (v1.0+)**
- **Distributed monitoring** across multiple instances
- **Community template repository** with automatic updates
- **Advanced analytics** and machine learning insights
- **Mobile companion app** for alerts and basic monitoring

---

## Technical Architecture

### **Data Flow**
```
SSH Connection → Command Execution → TextFSM Parsing → Field Normalization → UI Display
     ↓                ↓                    ↓                   ↓              ↓
 netmiko         show commands      Package Templates    Platform Maps    PyQt6 Widgets
```

### **Key Components**
- **Resource Manager**: Package-aware template and config loading
- **Platform Config Manager**: JSON-driven platform definitions
- **Threaded Telemetry Controller**: Non-blocking data collection
- **Template Editor**: Live template editing and testing
- **Theme System**: JSON-based UI customization

### **Security Architecture**
- **Credential encryption** using Fernet with PBKDF2 key derivation
- **No network exposure** - purely SSH client connections
- **Local data storage** with machine-specific encryption keys
- **Memory-safe** credential handling with automatic cleanup

---

## Contributing

### **Bug Reports**
Found an issue? Please report it with:
- Device platform and software version
- Command output that failed to parse
- Steps to reproduce the issue
- Expected vs actual behavior

### **Template Contributions**
- Use the built-in template editor to create/fix templates
- Test against multiple software versions when possible
- Follow TextFSM best practices for field naming
- Submit templates for new platforms or commands

### **Development Setup**
```bash
git clone https://github.com/scottpeterman/terminaltelemetry.git
cd terminaltelemetry
pip install -e .
# Edit code, templates, themes
python -m pytest tests/  # Run tests
```

---

## Screenshots

### Main Interface with Cyberpunk Theme
*Terminal sessions alongside real-time telemetry monitoring*

### Multi-Vendor Telemetry Dashboard
*Live monitoring of Cisco devices showing neighbors, ARP, routing, and system metrics*

### Template Editor
*Real-time template customization with live preview*

---

## License

TerminalTelemetry is licensed under the GPLv3 License. See the LICENSE file for details.

---

## Acknowledgments

- Built on PyQt6 and the Python ecosystem
- Network automation powered by netmiko and TextFSM
- Terminal functionality via xterm.js
- Template system inspired by ntc-templates
- Packaging system using modern Python setuptools
- Inspired by cyberpunk aesthetics and retro computing

---

## Support & Community

- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive guides and API reference  
- **Template Library**: Community-contributed TextFSM templates

---

*"The best network monitoring tool is the one that gets out of your way and shows you what you need to know."*

## Version History

### v0.10.0 (Current)
- ✅ **Package resource system** - pip installable with embedded templates
- ✅ **Template editor integration** - live editing and testing
- ✅ **CSV export functionality** for all telemetry tables
- ✅ **Enhanced platform support** with JSON configuration
- ✅ **Threaded telemetry collection** for responsive UI
- ✅ **Improved error handling** and connection management