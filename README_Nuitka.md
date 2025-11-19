# TerminalTelemetry Portable Build System

Production-ready Nuitka build script for creating standalone, distributable executables of TerminalTelemetry across Windows, Linux, and macOS platforms.

---

## 🎯 Overview

This build script uses **Nuitka** to compile TerminalTelemetry into native executables with all dependencies, templates, themes, and assets bundled. The result is a portable application that runs without requiring Python installation or pip dependencies.

### Why Nuitka?

- **True compilation** to machine code (not just packaging like PyInstaller)
- **Better performance** - compiled Python runs 50-300% faster
- **Smaller footprint** - better optimization than traditional packagers
- **Professional output** - native executables with proper metadata
- **PyQt6 support** - excellent plugin system for Qt applications

---

## 📋 Prerequisites

### Python Environment
```bash
Python 3.12+ (recommended)
```

### Required System Dependencies

**Windows:**
- Visual Studio 2022 Build Tools (or full Visual Studio)
- Windows SDK
- No additional Qt libraries needed (bundled by Nuitka)

**Linux:**
- GCC compiler: `sudo apt install gcc g++ make`
- Qt6 development libraries: `sudo apt install qt6-base-dev libqt6gui6 libqt6widgets6 libqt6webenginecore6`

**macOS:**
- Xcode Command Line Tools: `xcode-select --install`
- No additional Qt libraries needed (bundled by Nuitka)

### Python Dependencies

Install from the project requirements plus Nuitka build tools:

```bash
pip install -r requirements.txt
pip install nuitka ordered-set zstandard
```

**Complete dependency list** (from pip freeze):
```
backports.tarfile==1.2.0
bcrypt==5.0.0
certifi==2025.11.12
cffi==2.0.0
charset-normalizer==3.4.4
click==8.3.1
colorama==0.4.6
cryptography==46.0.3
diff-match-patch==20241021
docutils==0.22.3
future==1.0.0
idna==3.11
importlib_metadata==8.7.0
invoke==2.2.1
Jinja2==3.1.6
junos-eznc==2.7.5
keyring==25.7.0
logicmonitor-sdk==3.0.230
lxml==6.0.2
markdown-it-py==4.0.0
MarkupSafe==3.0.3
mdurl==0.1.2
more-itertools==10.8.0
napalm==5.1.0
ncclient==0.7.0
netaddr==1.3.0
netmiko==4.6.0
netutils==1.15.0
ntc_templates==8.1.0
Nuitka==2.8.6
ordered-set==4.1.0
packaging==25.0
paramiko==4.0.0
pycparser==2.23
pyeapi==1.0.4
Pygments==2.19.2
PyNaCl==1.6.1
pynetbox==7.5.0
pyparsing==3.2.5
PyQt6==6.10.0
PyQt6-Charts==6.10.0
PyQt6-WebEngine==6.10.0
PyQt6_sip==13.10.2
pyserial==3.5
python-dateutil==2.9.0.post0
pywin32-ctypes==0.2.3
PyYAML==6.0.3
qasync==0.28.0
requests==2.32.5
requests-toolbelt==1.0.0
rfc3986==2.0.0
rich==14.2.0
ruamel.yaml==0.18.16
scp==0.15.0
setuptools==80.9.0
six==1.17.0
textfsm==2.1.0
transitions==0.9.3
ttp==0.10.0
ttp-templates==0.3.7
twine==6.2.0
typing_extensions==4.15.0
urllib3==2.5.0
yamlordereddictloader==0.4.2
zstandard==0.25.0
```

---

## 🚀 Quick Start

### Standard Build (Directory Mode - Recommended)

Creates a folder with the executable and all dependencies. **Faster startup time.**

```bash
python build_termtel_portable.py
```

**Output:**
- `dist/TerminalTelemetry.dist/` - Distributable folder
- `dist/TerminalTelemetry-v1.1.0-win32.zip` - Compressed archive
- Includes launcher scripts (`launch.sh`, `launch.bat`)

### Single-File Build (Onefile Mode)

Creates a single executable. **Easier distribution, slower startup.**

```bash
python build_termtel_portable.py --onefile
```

**Output:**
- `dist/TerminalTelemetry.exe` (Windows) or `dist/TerminalTelemetry` (Unix)
- `dist/TerminalTelemetry-v1.1.0-win32.zip` - Archive with executable

### Minimal Build (Exclude Optional Features)

Smaller build without LogicMonitor, Junos, and other optional integrations:

```bash
python build_termtel_portable.py --minimal
```

---

## 🔧 Command-Line Options

```bash
python build_termtel_portable.py [OPTIONS]

Options:
  --onefile         Build as single executable (slower startup, easier distribution)
  --minimal         Exclude optional features for smaller build size
  --no-clean        Skip cleaning previous builds (faster iteration)
  --diagnose        Show package structure and exit (diagnostic mode)
  -h, --help        Show help message
```

### Diagnostic Mode

Use `--diagnose` to troubleshoot packaging issues before building:

```bash
python build_termtel_portable.py --diagnose
```

**Shows:**
- Python version and platform
- Package structure verification
- Data directory detection
- Template/theme file counts
- Missing files or directories

---

## 📦 What Gets Bundled

### Core Application
- ✅ Python runtime (compiled)
- ✅ All Python dependencies (200+ packages)
- ✅ PyQt6 GUI framework + WebEngine
- ✅ Network automation libraries (netmiko, napalm, paramiko)

### Package Data (from MANIFEST.in)
- ✅ **200+ TextFSM templates** (`termtel/templates/`)
- ✅ **24+ themes** (`termtel/themes/`)
- ✅ **Platform configs** (`termtel/config/`)
- ✅ **Static web assets** for xterm.js (`termtel/static/`)
- ✅ **Frontend components** (`termtel/termtelng/`)
- ✅ **Widget HTML/CSS/JS** (`termtel/widgets/`)
- ✅ **Icons and logos** (`termtel/icon.ico`, `logo.svg`)

### External Package Data
- ✅ **ntc_templates** - Community TextFSM templates (auto-detected)

---

## 📊 Build Specifications

### Directory Build (Default)

**Pros:**
- Fast startup (no decompression)
- Easier debugging (files visible)
- Smaller per-launch memory footprint
- Better for development/testing

**Cons:**
- Larger file count (~2,000-3,000 files)
- Requires entire folder for distribution

**Typical Size:**
- **Windows:** 450-550 MB uncompressed
- **Linux:** 400-500 MB uncompressed
- **macOS:** 450-550 MB uncompressed

### Onefile Build

**Pros:**
- Single executable file
- Easier distribution (one file to share)
- Self-contained deployment

**Cons:**
- Slower startup (decompresses to temp dir on each launch)
- Larger executable size
- Higher memory usage during extraction

**Typical Size:**
- **Windows:** 250-300 MB (compressed in EXE)
- **Linux:** 220-280 MB (compressed)
- **macOS:** 240-300 MB (compressed)

---

## ⏱️ Build Times

Expected compilation times (varies by system):

- **Windows (Core i7/Ryzen 7):** 15-20 minutes
- **Linux (Similar specs):** 12-18 minutes
- **macOS (M1/M2):** 10-15 minutes
- **Minimal builds:** 30-40% faster

**First build is slowest** - Nuitka caches intermediate results for faster rebuilds.

---

## 📂 Output Structure

### Directory Build Output

```
dist/
├── TerminalTelemetry.dist/          # Main distribution folder
│   ├── TerminalTelemetry.exe        # Main executable (Windows)
│   ├── TerminalTelemetry            # Main executable (Unix)
│   ├── launch.bat                   # Windows launcher script
│   ├── launch.sh                    # Unix launcher script
│   ├── termtel/                     # Package data
│   │   ├── templates/               # TextFSM templates
│   │   ├── themes/                  # UI themes
│   │   ├── config/                  # Platform configs
│   │   ├── static/                  # Web assets
│   │   └── ...
│   └── [2000+ dependency files]     # Compiled modules, libraries
│
└── TerminalTelemetry-v1.1.0-win32.zip  # Compressed distribution
```

### Onefile Build Output

```
dist/
├── TerminalTelemetry.exe            # Single executable (Windows)
├── TerminalTelemetry                # Single executable (Unix)
└── TerminalTelemetry-v1.1.0-win32.zip  # Compressed archive
```

---

## 🔍 How It Works

### Build Process Flow

```
1. Entry Point Detection
   ↓
2. Clean Previous Builds (optional)
   ↓
3. Verify Nuitka Installation
   ↓
4. Build Nuitka Command
   ├── Enable PyQt6 plugin
   ├── Include package data (templates, themes, configs)
   ├── Include Python packages (netmiko, paramiko, PyQt6, etc.)
   ├── Add data directories (static assets, widgets)
   └── Add individual files (icons, logos)
   ↓
5. Execute Nuitka Compilation (15-25 min)
   ├── Python → C translation
   ├── C compilation to native code
   └── Dependency bundling
   ↓
6. Create Distribution Archive
   ├── ZIP with versioned filename
   └── Include README.md
   ↓
7. Generate Launcher Scripts (directory mode only)
   └── Platform-specific convenience scripts
```

### Critical Nuitka Flags Used

```python
--standalone              # Bundle all dependencies
--enable-plugin=pyqt6     # CRITICAL - Handle Qt resources
--include-package-data    # Auto-include MANIFEST.in data
--include-data-dir        # Explicit data directory includes
--include-package         # Explicit package includes
--output-filename         # Custom executable name
--company-name            # Windows PE metadata
--product-version         # Version info in executable
```

---

## 🛠️ Customization

### Modify Build Configuration

Edit `build_termtel_portable.py` to customize:

**1. Version and Metadata** (lines 20-23):
```python
self.app_name = "TerminalTelemetry"
self.package_name = "termtel"
self.version = "1.1.0"              # <-- Change version
self.company = "NetworkOps Tools"   # <-- Change company
```

**2. Entry Point** (lines 35-41):
```python
candidates = [
    "termtel/termtel.py",           # <-- Add your entry points
    "termtel/__main__.py",
    # ...
]
```

**3. Data Directories** (lines 140-158):
```python
data_includes = [
    f"{self.package_name}/templates={self.package_name}/templates",
    # Add more data directories here
]
```

**4. Package Includes** (lines 191-219):
```python
packages = [
    "netmiko",
    "textfsm",
    # Add more required packages
]
```

### Add Platform-Specific Options

**Windows Icon:**
```python
cmd.append("--windows-icon-from-ico=termtel/icon.ico")
```

**Console vs GUI Mode (Windows):**
```python
cmd.append("--disable-console")  # No console window (GUI only)
# OR
cmd.append("--enable-console")   # Show console (debugging)
```

**macOS App Bundle:**
```python
cmd.append("--macos-create-app-bundle")
cmd.append("--macos-app-icon=termtel/icon.icns")
```

---

## 🧪 Testing Builds

### Post-Build Checklist

After building, **always test thoroughly:**

1. **Launch the executable**
   - Directory mode: Run `TerminalTelemetry.exe` or `./TerminalTelemetry`
   - Onefile mode: Run the single executable

2. **Verify themes load**
   - View → Theme menu
   - Check all 24+ themes switch correctly

3. **Verify templates load**
   - Tools → Telemetry Dashboard
   - Click gear icons on widgets
   - Template editor should show templates

4. **Test SSH connections**
   - Quick Connect to a device
   - Verify terminal opens and connects
   - Run network commands

5. **Test telemetry collection**
   - Open telemetry dashboard after SSH connection
   - Verify all widgets populate with data
   - Check neighbors, ARP, routing tables, etc.

6. **Export functionality**
   - Test CSV export from telemetry tables
   - Verify file saves correctly

7. **Session management**
   - Save sessions (File → Sessions)
   - Reload and verify sessions persist

### Known Issues to Watch For

**Templates not loading:**
- Verify `termtel/templates/` directory is in build output
- Check `ntc_templates` package data is included
- Use `--diagnose` to verify template counts

**Themes not applying:**
- Confirm `termtel/themes/` directory exists
- Check JSON theme files are valid
- Verify PyQt6 resources loaded correctly

**WebEngine not loading (terminal blank):**
- Ensure `--enable-plugin=pyqt6` is present
- Verify `termtel/static/` directory included
- Check PyQt6-WebEngine installed in build environment

**SSH connections failing:**
- Paramiko/cryptography libraries must be fully included
- Check `~/.ssh_manager/` directory permissions
- Verify credential encryption working

---

## 🐛 Troubleshooting

### Build Fails

**"Module not found" errors:**
```bash
# Add missing package explicitly
--include-package=missing_package_name
```

**PyQt6 plugin errors:**
```bash
# Ensure plugin is enabled (should be automatic)
--enable-plugin=pyqt6
```

**Out of memory during build:**
```bash
# Use minimal build
python build_termtel_portable.py --minimal

# Or increase system swap/pagefile
```

### Runtime Issues

**"Failed to load platform plugin" (Linux):**
```bash
# Install Qt6 platform plugins
sudo apt install qt6-qpa-plugins libqt6gui6
```

**Missing templates at runtime:**
```bash
# Verify template directory in output
ls dist/TerminalTelemetry.dist/termtel/templates/

# Use diagnostic mode before building
python build_termtel_portable.py --diagnose
```

**WebEngine crashes:**
```bash
# Ensure all WebEngine dependencies included
--include-package=PyQt6.QtWebEngineCore
--include-package=PyQt6.QtWebEngineWidgets
```

### Performance Issues

**Slow startup (onefile mode):**
- This is normal - onefile decompresses on launch
- Use directory mode for faster startup
- First launch is always slowest (creates cache)

**Large executable size:**
- Use `--minimal` to exclude optional features
- Remove unused vendor templates if not needed
- Consider directory mode instead of onefile

---

## 📤 Distribution

### Recommended Distribution Method

**Directory builds:**
```bash
# Created automatically by build script
dist/TerminalTelemetry-v1.1.0-win32.zip
```

**Contents:**
- Main executable
- All dependencies
- README.md
- Launcher scripts

### Distribution Checklist

- [ ] Test on clean system without Python installed
- [ ] Verify all features work (SSH, telemetry, themes)
- [ ] Include README with system requirements
- [ ] Document known limitations (if any)
- [ ] Provide SHA256 hash of distribution file
- [ ] Tag release in version control

### Platform-Specific Notes

**Windows:**
- Users may need Visual C++ Redistributable (usually included)
- First launch may trigger Windows Defender scan (normal)
- Consider code signing for professional distribution

**Linux:**
- Provide system dependency list (Qt6 libraries)
- Test on multiple distributions (Ubuntu, Fedora, etc.)
- May need to mark as executable: `chmod +x TerminalTelemetry`

**macOS:**
- May need to allow unsigned apps: System Preferences → Security
- Consider notarization for App Store or public distribution
- Test on both Intel and Apple Silicon

---

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Build TerminalTelemetry

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install nuitka ordered-set zstandard
      
      - name: Build with Nuitka
        run: python build_termtel_portable.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: TerminalTelemetry-${{ matrix.os }}
          path: dist/*.zip
```

---

## 📈 Performance Comparison

### Nuitka vs Other Packagers

| Feature | Nuitka | PyInstaller | cx_Freeze |
|---------|--------|-------------|-----------|
| **Compilation** | ✅ True C compilation | ❌ Bytecode packaging | ❌ Bytecode packaging |
| **Performance** | 🚀 50-300% faster | 📊 Same as Python | 📊 Same as Python |
| **Size** | 📦 Optimized | 📦 Larger | 📦 Larger |
| **PyQt6 Support** | ✅ Excellent plugin | ⚠️ Manual work | ⚠️ Manual work |
| **Package Data** | ✅ Auto-detection | ⚠️ Manual specs | ⚠️ Manual specs |
| **Build Time** | ⏱️ Slower (15-25 min) | ⏱️ Fast (2-5 min) | ⏱️ Fast (2-5 min) |

**Why Nuitka for TerminalTelemetry:**
- PyQt6 WebEngine requires proper resource handling (Nuitka plugin)
- 200+ TextFSM templates need reliable package data inclusion
- Network operations benefit from compiled performance
- Professional executable output with proper metadata

---

## 🎯 Best Practices

### Development Workflow

1. **Develop and test with pip install -e .**
2. **Use `--diagnose` before building** to verify package structure
3. **Build in clean virtual environment** to avoid dependency pollution
4. **Test directory build first** (faster iteration)
5. **Test onefile build for distribution** (final verification)
6. **Keep build script in version control** alongside code

### Version Management

Update version in **three places** for consistency:
1. `build_termtel_portable.py` (line 22): `self.version = "1.1.0"`
2. `setup.py`: `version="1.1.0"`
3. `termtel/__init__.py`: `__version__ = "1.1.0"`

### Build Hygiene

```bash
# Always clean before release builds
python build_termtel_portable.py --no-clean  # Development iteration
python build_termtel_portable.py             # Clean production build
```

---

## 📝 License

This build script is part of TerminalTelemetry, licensed under GPLv3.

Nuitka itself is Apache 2.0 licensed (commercial licensing available for proprietary use).

---

## 🙏 Credits

- **Nuitka** - Kay Hayen and contributors
- **TerminalTelemetry** - Scott Peterman
- **Community** - TextFSM templates, theme contributions, testing

---

## 📞 Support

**Issues with builds?**
- Check the troubleshooting section above
- Run with `--diagnose` to identify missing files
- Open GitHub issue with diagnostic output

**Need help with Nuitka?**
- [Nuitka Documentation](https://nuitka.net/doc/user-manual.html)
- [Nuitka GitHub](https://github.com/Nuitka/Nuitka)

---

*Last Updated: November 2024 | Build Script Version: 1.0*