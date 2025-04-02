# TerminalTelemetry

![Screenshot](https://github.com/scottpeterman/terminaltelemetry/blob/c9099e0a76fb67ead274f1b49cb539883996bd4e/screenshots/slides2.gif)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

**TerminalTelemetry** is a fully themed terminal and telemetry platform inspired by retro computing aesthetics, powered by PyQt6. It fuses the real-time monitoring features of Terminal Telemetry with the session and credential management foundation of pyRetroTerm.

## Highlights

- 20+ included retro/modern themes (CRT, Doom, Borland, Cyber, etc.)
- Dynamic corner styling with SVG-based HUD corners
- Secure credential vault with Fernet encryption and keyring support
- NetBox and LogicMonitor session importers (to YAML)
- Native pyRetroTerm tab support
- Live interface/telemetry paneling in multi-session layout
- Theme editor with live preview, xterm palette editor, and border/glow control

---

## Key Features

### 🔒 Secure Credential System
- AES256 encrypted credentials
- Machine-locked secrets via `keyring`
- PBKDF2 key derivation with salt
- Import/export credential bundles
- GUI credential editor

### 🚀 Session Importers
- **NetBox Importer**:
  - Pulls device data via pynetbox
  - Groups sessions by site
  - Saves to themed YAML structure

- **LogicMonitor Importer**:
  - Uses LogicMonitor SDK
  - Site-based grouping, progress feedback
  - SSL and Zscaler cert support

### 🎨 Theme System
- JSON-defined color themes
- Corner design mapping per theme (e.g., "doom" -> "klingonTlh")
- Theme editor GUI with real-time preview
- Customize terminal palette, gridlines, scrollbars, borders
- Live reload and preview support

### 🔹 Core Telemetry
- Real-time CPU, memory, temperature, fans, and power
- Interface status table with UP/DOWN state
- LLDP/CDP neighbor discovery
- Routing table and default gateway
- Log viewer with live updates

### 🌐 Multi-Session Terminal
- Tabbed terminals with session restoration
- Per-session theme support
- SSH support for Linux/IOS/EOS/NXOS/JUNOS
- Quick Connect UI
- Device cards with credentials

### 🔧 Extensibility
- Modular drivers for platform expansion
- Plugin system for importers, UI extensions
- YAML-based session definitions

---

## Installation

```bash
pip install TerminalTelemetry
```

Or clone and run from source:

```bash
git clone https://github.com/scottpeterman/terminaltelemetry.git
cd TerminalTelemetry
python TerminalTelemetry.py
```

---

## Screenshots

> Coming soon: screenshots of the Theme Editor, Telemetry Panels, and Credential Manager

---

## License

TerminalTelemetry is licensed under the GPLv3 License. See the LICENSE file for details.

---

## Acknowledgments

- Built on the foundation of pyRetroTerm
- Doom-inspired theme engine originally from DOOM Terminal Telemetry
- Special thanks to the open-source community for tools and libraries

---

*"CLI's Don't Die, They just change their prompt!" — TerminalTelemetry*

