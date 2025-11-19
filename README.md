# TerminalTelemetry

![Screenshot](https://raw.githubusercontent.com/scottpeterman/terminaltelemetry/refs/heads/main/screenshots/v2/slides3.gif)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![PyPI](https://img.shields.io/badge/pip-installable-green.svg)

**TerminalTelemetry** is a modern, cyberpunk-inspired terminal emulator and network telemetry platform built with PyQt6. It combines powerful SSH terminal capabilities with real-time network device monitoring in a sleek, themeable interface.

---

## 🖥️ Platform Requirements

**TerminalTelemetry is a native desktop application** - requires a graphical desktop environment (not for headless servers or web browsers).

### Quick Installation

#### Application Entry Points
TerminalTelemetry provides two launcher commands:
- **`termtel`** - Standard GUI launch (Windows: `termtel.exe`)
- **`termtel-con`** - Launch with console output (for debugging and troubleshooting)

---

## 📦 Portable Windows Build (No Python Required!)

**Don't want to install Python?** We've got you covered with a standalone Windows build.

### 🚀 Quick Start - Portable Version

**Download pre-built Windows package:**
- 📥 [**TerminalTelemetry Portable Builds**](https://drive.google.com/drive/folders/1ST4DUCxRH13yUB6GZjcNoiIF1ekSaCZu) (Google Drive)
- 💾 **Size:** ~522 MB (ZIP) / ~547 MB (extracted)
- ✅ **No Python installation required**
- ✅ **No pip, no virtual environments, no hassle**
- ✅ **All dependencies bundled** - just extract and run

### Installation Steps

1. **Download** the latest `TerminalTelemetry-v1.x.x-win32.zip` from Google Drive
2. **Extract** the ZIP file to your preferred location (e.g., `C:\Apps\TerminalTelemetry\`)
3. **Run** `TerminalTelemetry.exe` from the extracted folder
4. **First launch** - App will download latest themes automatically (one-time setup)
5. **Optional:** Create a desktop shortcut to `TerminalTelemetry.exe` for easy access

**That's it!** No Python, no pip, no dependencies to install.

### What's Included in the Portable Build?

✅ **Native executable** - `TerminalTelemetry.exe` (125 MB)  
✅ **Complete Python runtime** - Compiled into native code  
✅ **200+ TextFSM templates** - All network device parsers (`termtel/templates/`)  
✅ **All Python dependencies** - netmiko, paramiko, PyQt6, cryptography bundled  
✅ **PyQt6 WebEngine** - Complete browser engine for xterm.js terminal  
✅ **Platform configurations** - Cisco, Arista, Juniper support (`termtel/config/`)  
✅ **Static web assets** - xterm.js terminal interface  
✅ **316 files total** - Everything needed to run standalone

### Build Structure

```
TerminalTelemetry.dist/
├── TerminalTelemetry.exe        # Main executable (125 MB)
├── termtel/                     # Application package data
│   ├── templates/               # 200+ TextFSM templates
│   ├── config/                  # Platform configurations
│   ├── static/                  # xterm.js assets
│   └── ...
├── themes/                      # Included themes (auto-updates on first run)
├── PyQt6/                       # Qt framework
├── qt6*.dll                     # Qt6 libraries (~60 DLLs)
├── python312.dll                # Python runtime
├── ntc_templates/               # Community templates
├── [cryptography, bcrypt, etc.] # Security libraries
└── [200+ other dependencies]    # All bundled libraries
```

### System Requirements

**Windows:**
- Windows 10 or 11 (64-bit)
- 4 GB RAM minimum (8 GB recommended for large configs)
- 600 MB free disk space (for extraction)
- No additional software required

**Note:** First launch may take a few seconds as Windows Defender scans the executable (normal for unsigned applications).

### Portable vs pip Install

| Feature | Portable Build | pip Install |
|---------|---------------|-------------|
| **Python Required** | ❌ No | ✅ Yes (3.12+) |
| **Installation Time** | 🚀 2 minutes (download + extract) | ⏱️ 5-10 minutes (pip + dependencies) |
| **Disk Space** | 📦 547 MB | 📦 ~300 MB |
| **File Count** | 316 files in folder | Varies by environment |
| **Updates** | 🔄 Manual (download new version) | 🔄 `pip install --upgrade` |
| **Startup Time** | ⚡ Instant (no decompression) | ⚡ Instant |
| **Theme Updates** | 🔄 Auto-download on first launch | 🔄 Included in package |
| **Best For** | Windows users, quick deployment, no Python | Developers, Linux/macOS, latest updates |

### Building Your Own Portable Version

Want to create your own portable builds or build for Linux/macOS? See the [**Build Documentation**](BUILD_README.md) for detailed instructions on using our Nuitka-based build system.

---

**Windows & macOS (pip install):**
```bash
pip install TerminalTelemetry
termtel
```

**Linux & WSL2:**

⚠️ **Linux requires Qt6 system libraries first.** Quick install for Ubuntu/Debian:
```bash
sudo apt install -y libqt6gui6t64 libqt6widgets6t64 libqt6core6t64 qt6-base-dev \
    libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
    libxcb-render-util0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0 \
    libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-xfixes0 libx11-xcb1 libgl1 libglib2.0-0t64

pip install TerminalTelemetry
termtel
```

**📘 For other Linux distributions, WSL2 setup, and troubleshooting:** [Linux Installation Guide](README_Linux_Desktops.md)

> **Looking for a web-based tool?** See [Velociterm](https://github.com/scottpeterman/velociterm) instead.

---

## 🚀 Current Features

### 🎨 **Advanced Theme System**
- **24+ built-in themes** (Cyberpunk, Nord, Gruvbox, Doom, Borland, Amiga, CRT-Green/Amber, and more)
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
- 
- **SSH key authentication** 🆕
  - Automatic private key detection from `~/.ssh/`
  - Support for RSA, ED25519, ECDSA, DSS key types
  - Config-based key management (`~/.ssh_manager/keys.json`)
  - Per-session key preferences with persistent settings
- **Platform-specific secure storage** locations
- **Machine-specific credential binding**
- **Rate-limited authentication** prevents brute force
- **Zero plaintext storage** of sensitive data

![Screenshot](https://raw.githubusercontent.com/scottpeterman/terminaltelemetry/refs/heads/main/screenshots/v2/key_auth_sessions.png)
### 🚀 **Session Import Tools**
- **NetBox Integration**:
  - Import devices directly from NetBox instances
  - Site-based organization and grouping
  - Automatic credential mapping
- **LogicMonitor Integration**:
  - SDK-based device discovery
  - Progress feedback and error handling
  - SSL certificate validation support

### 🧰 **Built-in Tools**
- **Text Editor** with syntax highlighting
- **Diff Tool** for configuration comparison
- **Serial Terminal** for console connections
- **Space Debris & Doom** - Demonstrates the framework's capability as a general-purpose tool delivery platform. The terminal application's architecture is designed to host any PyQt6 or web-based component, making it easy to extend with custom tools and utilities.

---

## 🗃️ Architecture Highlights

### **SSH-Only Monitoring**
- Works with any SSH-accessible device
- No agent installation required on target devices
- Leverages existing SSH credentials
- Zero infrastructure - no monitoring servers or databases needed

### **Template-Driven Parsing**
- 200+ TextFSM templates packaged with the application
- Live template editing with syntax highlighting and testing
- Field normalization across different vendors
- Package resource system - templates accessible in any environment
- User-customizable - fix parsing issues yourself

### **Extensible Desktop Platform**
- Qt6-based UI with native performance
- Threaded data collection prevents UI blocking
- Signal-based communication between components
- Modular widget system - easily add new tools and features
- Package-aware resource management for pip installations
- Tab-based interface can host any PyQt6 widget or web content

---

## 🎯 Getting Started

### Quick Start (Portable Build)
1. **Download**: Get the portable ZIP from [Google Drive](https://drive.google.com/drive/folders/1ST4DUCxRH13yUB6GZjcNoiIF1ekSaCZu)
2. **Extract**: Unzip to any folder
3. **Launch**: Run `TerminalTelemetry.exe`
4. **Create SSH sessions** via File → Open Sessions or use Quick Connect
5. **Open Telemetry Dashboard** via Tools → Telemetry Dashboard
6. **Connect to devices** and view real-time monitoring data
7. **Customize themes** via View → Theme menu and Theme Editor

### Quick Start (pip Install)
1. **Install via pip**: `pip install TerminalTelemetry`
2. **Launch**: `termtel`
3. **Create SSH sessions** via File → Open Sessions or use Quick Connect
4. **Open Telemetry Dashboard** via Tools → Telemetry Dashboard
5. **Connect to devices** and view real-time monitoring data
6. **Customize themes** via View → Theme menu and Theme Editor

**Note for Windows pip users:** After installation, you can create a desktop shortcut to `venv\Scripts\termtel.exe` for easier access.

### First Device Connection
1. Click **"Quick Connect"** in the bottom panel
2. Enter device IP, credentials, and select platform (cisco_ios, arista_eos, etc.)
3. Click **"Connect"** - terminal tab opens automatically
4. Open **Tools → Telemetry Dashboard** to see real-time monitoring
5. Use the **gear buttons** in widgets to customize TextFSM templates

### Theme Customization
- **Global themes**: Use View → Theme menu to change all components
- **Individual tab themes**: Right-click any tab label → Terminal Theme → select theme
- **Custom themes**: Use View → Theme → Theme Editor to create new themes
- **Theme files**: Drop JSON theme files in the `~/.termtel/themes/` directory for instant availability

### Template Customization
1. Connect to a device and open telemetry dashboard
2. Click the **⚙️ gear button** on any widget (neighbors, routes, etc.)
3. **Template editor opens** with current template and sample data
4. **Edit template** using TextFSM syntax
5. **Click "RUN TEST"** to validate against live device output
6. **Save template** - changes apply immediately

---

## 📡 Supported Platforms

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

## ⚠️ Known Issues & Limitations

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

## 🗺️ Planned Features & Roadmap

### **Near Term (v0.16-0.17)**
- Multi-device dashboards for network-wide monitoring
- Historical data collection with basic trending graphs
- Enhanced error handling and automatic reconnection
- Template sharing and import/export functionality
- Custom command execution with ad-hoc template creation

### **Medium Term (v0.18-0.20)**
- Network topology discovery and visualization
- Configuration backup and change detection
- Alert system for threshold monitoring
- Plugin architecture for community extensions
- REST API for external integrations

### **Long Term (v1.0+)**
- Distributed monitoring across multiple instances
- Community template repository with automatic updates
- Advanced analytics and machine learning insights
- Mobile companion app for alerts and basic monitoring

---

## 🔧 Technical Architecture

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
- **Modular Tab System**: Extensible framework for hosting custom tools and widgets

### **Security Architecture**
- **Credential encryption** using Fernet with PBKDF2 key derivation
- **SSH key authentication** with automatic key detection
- **No network exposure** - purely SSH client connections
- **Local data storage** with machine-specific encryption keys
- **Memory-safe** credential handling with automatic cleanup

---

## 🤝 Contributing

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

## 📸 Screenshots

### Main Interface with Cyberpunk Theme
*Terminal sessions alongside real-time telemetry monitoring*

### Multi-Vendor Telemetry Dashboard
*Live monitoring of Cisco devices showing neighbors, ARP, routing, and system metrics*

### Template Editor
*Real-time template customization with live preview*

---

## 📄 License

TerminalTelemetry is licensed under the GPLv3 License. See the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built on PyQt6 and the Python ecosystem
- Network automation powered by netmiko and TextFSM
- Terminal functionality via xterm.js
- Template system inspired by ntc-templates
- Packaging system using modern Python setuptools
- Inspired by cyberpunk aesthetics and retro computing

---

## 📚 Support & Community

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Repository**: https://github.com/scottpeterman/terminaltelemetry
- **Documentation**: Comprehensive guides and API reference  
- **Template Library**: Community-contributed TextFSM templates
- **Portable Builds**: [Windows executables on Google Drive](https://drive.google.com/uc?export=download&id=1ao4y1Lt_9HGJRk291MbYLqHHglfNouT7)

---

## 📋 Version History

### v0.15.0 (Current - October 2025)
- ✅ **SSH key authentication** - Passwordless authentication with auto-detection
- ✅ **24+ themes** - Expanded theme library with vintage and retro options
- ✅ **Package resource system** - pip installable with embedded templates
- ✅ **Template editor integration** - live editing and testing
- ✅ **CSV export functionality** for all telemetry tables
- ✅ **Enhanced platform support** with JSON configuration
- ✅ **Threaded telemetry collection** for responsive UI
- ✅ **Improved error handling** and connection management
- ✅ **Portable Windows builds** - No Python installation required

---

*"The best network monitoring tool is the one that gets out of your way and shows you what you need to know."*