# SSH Terminal Telemetry

A unified terminal emulator with integrated device discovery, fingerprinting, and network visualization.

## ⚠️ Proof of Concept

**IMPORTANT**: This project is currently a Proof of Concept (POC) to demonstrate the feasibility and potential of combining terminal emulation, device discovery, and network visualization in a single interface. While functional, it should not be considered production-ready software. Features may be incomplete, and significant changes could occur during development.

This POC aims to spark discussion about improving network operations tooling and demonstrate possible approaches to reducing tool sprawl in network management.

## Overview

SSH Terminal Telemetry combines interactive terminal access, automatic device fingerprinting, and network visualization into a single, integrated interface. It eliminates the need to juggle multiple tools by providing:

![SSH Terminal Telemetry Demo](https://raw.githubusercontent.com/scottpeterman/terminaltelemetry/main/screenshots/slideshow.gif)
## Key Features

- **Unified Interface**: Terminal, device information, and network visualization in a single window
- **Automatic Device Fingerprinting**: Identifies device types and capabilities without manual intervention
- **Real-time Telemetry**: Displays parsed device information as you work
- **Network Mapping**: Automatically generates network topology diagrams
- **Cross-Platform**: Supports network devices (Cisco, etc.) and Linux systems
- **Extensible**: Template-based fingerprinting system allows easy addition of new device types

## Technical Design

### Architecture

The application is built on three main components:

1. **Terminal Interface**: 
   - Built using Tkinter/ttk for cross-platform compatibility
   - Split-pane design with terminal on left, discovery/telemetry on right
   - Supports multiple concurrent sessions via tabs

2. **Device Discovery Engine**:
   - Uses TextFSM templates for pattern matching
   - SQLite database stores device templates and fingerprints
   - Scoring engine ranks template matches for accurate device identification

3. **Network Visualization**:
   - Generates network topology maps based on discovered connections
   - Interactive visualization with zoom and pan capabilities
   - Supports different layout algorithms

### Device Fingerprinting Process

1. **Initial Connection**:
   - Establishes SSH session
   - Sends platform-agnostic commands first (Linux)
   - Falls back to network device commands

2. **Template Matching**:
   - Processes command output through TextFSM templates
   - Each template generates a confidence score
   - Best matching template determines device type

3. **Data Extraction**:
   - Parses device-specific information using matched template
   - Extracts key data points (OS, version, hardware, etc.)
   - Updates real-time display

### TextFSM Template Database

- Organized by command patterns (show version, system info, etc.)
- Each template includes:
  - Command patterns
  - Expected output format
  - Field definitions
  - Parsing rules
- Confidence scoring based on successful field matches

## Use Cases

### Network Engineers
- Rapid device identification and documentation
- Interactive troubleshooting with real-time data parsing
- Automatic network topology mapping

### System Administrators
- Unified interface for both network and Linux systems
- Automatic system information collection
- Consistent interface across different platforms

### DevOps Teams
- Integration with existing automation tools
- Template-based extensibility
- Cross-platform compatibility

## Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

### Basic Usage
```python
python main.py
```

### Adding New Device Templates
1. Create TextFSM template file
2. Add template to database:
```python
python add_template.py <template_file> <command_type>
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- TextFSM for template-based text parsing
- PySSHPass for SSH connectivity
- NetworkX for topology mapping

## Roadmap

- [ ] Additional platform support
- [ ] Enhanced telemetry collection
- [ ] API for external integration
- [ ] Configuration management features
- [ ] Custom template editor

## Why Another Terminal?

Existing solutions typically focus on either terminal access, network monitoring, or automation - but rarely combine these effectively. This project aims to provide:

1. **Reduced Tool Sprawl**: One interface for terminal access, device discovery, and visualization
2. **Automatic Documentation**: Device information and network topology captured automatically
3. **Real-Time Intelligence**: Immediate access to parsed device information while working
4. **Extensible Platform**: Template-based system allows easy addition of new device types
5. **Cross-Platform Support**: Same interface works for network devices and Linux systems

The goal is to streamline network operations by combining the most frequently used tools into a single, efficient interface.