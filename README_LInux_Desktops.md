# 📘 Linux Installation & Troubleshooting Appendix

This appendix provides comprehensive guidance for installing and running TerminalTelemetry on Linux systems, including native installations, WSL2, and troubleshooting common issues.

---

## Table of Contents
- [System Requirements](#system-requirements)
- [Native Linux Installation](#native-linux-installation)
- [WSL2 Installation (Windows)](#wsl2-installation-windows)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Remote Display Configuration](#remote-display-configuration)

---

## System Requirements

### Desktop Environment Required

**TerminalTelemetry is a desktop application** built with PyQt6 and requires a graphical desktop environment. It will **NOT** work on:
- Headless servers (no display attached)
- SSH-only terminal sessions without X11 forwarding
- Container environments without display capabilities
- Systems without X11 or Wayland display servers

### Minimum Requirements

- **Linux Distribution:** Ubuntu 20.04+, Debian 11+, RHEL/Rocky 8+, Fedora 35+, or equivalent
- **Python:** 3.12 or higher
- **Desktop Environment:** Any (GNOME, KDE, XFCE, etc.)
- **Display Server:** X11 or Wayland
- **Memory:** 512MB RAM minimum (2GB+ recommended for multiple device sessions)
- **Disk Space:** 200MB for application and dependencies

---

## Native Linux Installation

### Step 1: Install System Dependencies

TerminalTelemetry requires Qt6 libraries and graphics components that are not included with Python packages. These must be installed at the system level before installing the application.

#### **Ubuntu / Debian**

```bash
# Update package lists
sudo apt update

# Install Qt6 and required graphics libraries
sudo apt install -y \
    libqt6gui6t64 libqt6widgets6t64 libqt6core6t64 \
    qt6-base-dev \
    libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0 \
    libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-xfixes0 \
    libx11-xcb1 libgl1 libglib2.0-0t64
```

**Note:** Package names may vary slightly between Ubuntu versions. If you encounter "package not found" errors, try:
```bash
# For systems without t64 packages (older Ubuntu/Debian)
sudo apt install -y \
    libqt6gui6 libqt6widgets6 libqt6core6 \
    qt6-base-dev \
    libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0 \
    libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-xfixes0 \
    libx11-xcb1 libgl1 libglib2.0-0
```

#### **RHEL / Rocky Linux / CentOS Stream**

```bash
# Enable EPEL repository (if not already enabled)
sudo dnf install -y epel-release

# Install Qt6 and dependencies
sudo dnf install -y \
    qt6-qtbase qt6-qtbase-gui \
    libxcb xcb-util-cursor xcb-util-image xcb-util-keysyms \
    xcb-util-renderutil xcb-util-wm libxkbcommon-x11 \
    mesa-libGL mesa-libEGL
```

#### **Fedora**

```bash
# Install Qt6 and dependencies
sudo dnf install -y \
    qt6-qtbase qt6-qtbase-gui \
    libxcb xcb-util-cursor xcb-util-image xcb-util-keysyms \
    xcb-util-renderutil xcb-util-wm libxkbcommon-x11 \
    mesa-libGL mesa-libEGL
```

#### **Arch Linux / Manjaro**

```bash
# Install Qt6 and dependencies
sudo pacman -S \
    qt6-base \
    libxcb xcb-util-cursor xcb-util-image xcb-util-keysyms \
    xcb-util-renderutil xcb-util-wm libxkbcommon-x11 \
    mesa
```

### Step 2: Verify Qt6 Installation

Test that Qt6 is properly installed before proceeding:

```bash
# Simple Qt6 test - should open a small window with "Qt6 Works!" text
python3 -c "from PyQt6.QtWidgets import QApplication, QLabel; import sys; app = QApplication(sys.argv); label = QLabel('Qt6 Works!'); label.show(); sys.exit(app.exec())"
```

If this test fails with "ModuleNotFoundError: No module named 'PyQt6'", that's expected at this stage. If it fails with Qt platform plugin errors, the system dependencies are not properly installed.

### Step 3: Install TerminalTelemetry

```bash
# Install from PyPI
pip install TerminalTelemetry

# Bootstrap themes on first run
termtel-con

# Launch the application
termtel
```

### Step 4: Create Desktop Launcher (Optional)

Create a `.desktop` file for easy launching from your application menu:

```bash
# Create desktop entry
cat > ~/.local/share/applications/terminaltelemetry.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=TerminalTelemetry
Comment=Cyberpunk-Inspired Terminal Emulator & Network Telemetry Platform
Exec=termtel
Terminal=false
Categories=Network;System;
Keywords=ssh;terminal;telemetry;network;
EOF

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

---

## WSL2 Installation (Windows)

Windows Subsystem for Linux 2 (WSL2) allows you to run TerminalTelemetry on Windows using a Linux environment with native GUI support.

### Prerequisites

- **Windows 11** (any build) **OR** **Windows 10** Build 19044 or higher
  - Check your version: Press `Win+R`, type `winver`, press Enter
- **WSL2** installed and updated
- A Linux distribution installed (Ubuntu 22.04 or 24.04 recommended)

### Step 1: Install/Update WSL2

Open **PowerShell as Administrator** and run:

```powershell
# Install WSL2 (if not already installed)
wsl --install

# Update to latest version with WSLg support
wsl --update

# Restart WSL
wsl --shutdown
```

**WSLg (Windows Subsystem for Linux GUI)** is included automatically in modern WSL2 and provides:
- Native Linux GUI application support
- Wayland and X11 display servers
- Audio support
- GPU acceleration
- Seamless window integration with Windows desktop

**No separate X server installation is required!**

### Step 2: Install Linux Distribution (if needed)

```powershell
# List available distributions
wsl --list --online

# Install Ubuntu (recommended)
wsl --install -d Ubuntu-24.04
```

### Step 3: Install System Dependencies in WSL2

Open your WSL2 Linux distribution (Ubuntu) and run:

```bash
# Update package lists
sudo apt update

# Install Qt6 and required graphics libraries
sudo apt install -y \
    libqt6gui6t64 libqt6widgets6t64 libqt6core6t64 \
    qt6-base-dev \
    libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0 \
    libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-xfixes0 \
    libx11-xcb1 libgl1 libglib2.0-0t64
```

### Step 4: Verify WSLg is Working

```bash
# Check that display variables are set
echo $WAYLAND_DISPLAY  # Should show: wayland-0
echo $DISPLAY          # Should show: :0

# Test with a simple GUI app
sudo apt install -y x11-apps
xeyes  # Should open a window with animated eyes
```

### Step 5: Install TerminalTelemetry

```bash
# Install from PyPI
pip install TerminalTelemetry

# Bootstrap themes
termtel-con

# Launch application
termtel
```

The application window will appear on your Windows desktop, integrated with your other Windows applications!

### WSL2 Troubleshooting

#### Problem: No display variables set

```bash
# Check WSLg status
echo $WAYLAND_DISPLAY
echo $DISPLAY
```

**Solution:**
```powershell
# In PowerShell as Administrator
wsl --shutdown
# Restart your Linux distribution
```

#### Problem: "Could not connect to display"

**Check WSL version:**
```powershell
# In PowerShell
wsl --version
# Should show WSL version 2.0.0 or higher
```

**Solution:** Update WSL
```powershell
wsl --update
wsl --shutdown
```

#### Problem: Graphics/rendering issues

**Solution:** Update your Windows GPU drivers
- NVIDIA: Download from [nvidia.com](https://www.nvidia.com/download/index.aspx)
- AMD: Download from [amd.com](https://www.amd.com/en/support)
- Intel: Download from [intel.com](https://www.intel.com/content/www/us/en/download-center/home.html)

### Legacy Windows 10 (Pre-Build 19044)

If you cannot upgrade to a WSLg-compatible Windows version, you'll need a manual X server:

1. **Install an X Server on Windows:**
   - [VcXsrv](https://sourceforge.net/projects/vcxsrv/) (free, open source)
   - [X410](https://x410.dev/) (paid, from Microsoft Store)

2. **Configure X Server:**
   - Launch VcXsrv with "Disable access control" checked
   - Use "Multiple windows" mode

3. **Set Display in WSL2:**
   ```bash
   # Add to ~/.bashrc
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   export LIBGL_ALWAYS_INDIRECT=1
   ```

4. **Allow WSL2 through Windows Firewall** for the X server port (6000)

**Recommendation:** Upgrade to Windows 11 or Windows 10 Build 19044+ for the best experience.

---

## Troubleshooting Guide

### Common Error Messages and Solutions

#### Error: "Could not load the Qt platform plugin 'xcb'"

**Full error message:**
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized.
```

**Cause:** Missing Qt6 system libraries

**Solution:**
```bash
# Install missing XCB libraries (Ubuntu/Debian)
sudo apt install -y \
    libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0 \
    libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-xfixes0
```

#### Error: "From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed"

**Cause:** Missing the `libxcb-cursor0` library specifically

**Solution:**
```bash
sudo apt install -y libxcb-cursor0
```

#### Error: "No Qt platform plugin could be initialized"

**Full error message:**
```
This application failed to start because no Qt platform plugin could be initialized.
Available platform plugins are: wayland, xcb, eglfs, offscreen, vnc, linuxfb.
```

**Cause:** Missing Qt6 base libraries

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install -y qt6-base-dev libqt6gui6t64 libqt6widgets6t64

# RHEL/Fedora
sudo dnf install -y qt6-qtbase qt6-qtbase-gui
```

#### Error: "cannot connect to X server"

**Cause:** No display server is available or `$DISPLAY` variable is not set

**Solution:**

1. **Verify you're on a desktop system:**
   ```bash
   echo $DISPLAY  # Should show :0 or similar
   ps aux | grep -E 'X|wayland'  # Should show display server process
   ```

2. **If on a desktop system but still failing:**
   ```bash
   export DISPLAY=:0
   # Or for Wayland:
   export WAYLAND_DISPLAY=wayland-0
   ```

3. **If accessing remotely via SSH:**
   ```bash
   # Connect with X11 forwarding
   ssh -X user@remote-host
   ```

#### Error: "ModuleNotFoundError: No module named 'PyQt6'"

**Cause:** PyQt6 Python package not installed

**Solution:**
```bash
pip install PyQt6
# Or reinstall TerminalTelemetry
pip install --force-reinstall TerminalTelemetry
```

### Performance Issues

#### Problem: Slow rendering or laggy interface

**Solutions:**

1. **Check GPU acceleration:**
   ```bash
   glxinfo | grep "direct rendering"  # Should say "yes"
   ```

2. **Force software rendering (if GPU issues):**
   ```bash
   export QT_XCB_GL_INTEGRATION=none
   termtel
   ```

3. **Disable compositor effects (KDE/GNOME):**
   - KDE: System Settings → Display → Compositor → Disable
   - GNOME: May require extension or tweaks

#### Problem: High CPU usage

**Solutions:**

1. **Reduce theme complexity** - Use simpler themes (Dark, Light) instead of Cyberpunk
2. **Close unused telemetry tabs** - Each telemetry session polls devices
3. **Increase polling intervals** in telemetry settings

### Display Server Issues

#### Wayland vs X11

TerminalTelemetry works with both Wayland and X11, but some features may work better on X11.

**Check your current display server:**
```bash
echo $XDG_SESSION_TYPE  # Shows: wayland or x11
```

**Force X11 session (if using Wayland with issues):**
- At login screen, select "GNOME on Xorg" or similar X11 option
- Or set in `~/.xinitrc` or session configuration

**Force specific Qt platform:**
```bash
# Force X11
export QT_QPA_PLATFORM=xcb
termtel

# Force Wayland
export QT_QPA_PLATFORM=wayland
termtel
```

### Debug Mode

Enable Qt debug output to diagnose issues:

```bash
# Show detailed Qt plugin information
export QT_DEBUG_PLUGINS=1
termtel

# Show Qt platform abstraction debug info
export QT_LOGGING_RULES="qt.qpa.*=true"
termtel
```

### Permission Issues

#### Problem: Permission denied errors

**Solution:**
```bash
# Ensure user is in necessary groups
sudo usermod -aG dialout $USER  # For serial terminal access
sudo usermod -aG video $USER    # For GPU access

# Re-login for group changes to take effect
```

---

## Remote Display Configuration

### SSH X11 Forwarding

Run TerminalTelemetry on a remote Linux desktop and display it locally:

**From your local machine:**
```bash
# Enable X11 forwarding with compression
ssh -XC user@remote-desktop

# Verify display is set
echo $DISPLAY  # Should show: localhost:10.0 or similar

# Launch application
termtel
```

**For better performance:**
```bash
# Use X11 forwarding with compression and trusted forwarding
ssh -YC user@remote-desktop
```

**Server-side configuration** (on remote host):
```bash
# Edit /etc/ssh/sshd_config
sudo nano /etc/ssh/sshd_config

# Ensure these are set:
X11Forwarding yes
X11DisplayOffset 10
X11UseLocalhost yes

# Restart SSH service
sudo systemctl restart sshd
```

### VNC (Alternative for slow connections)

For better performance over slow networks, use VNC instead of X11 forwarding:

**On remote Linux desktop:**
```bash
# Install VNC server
sudo apt install -y tigervnc-standalone-server

# Start VNC server
vncserver :1 -geometry 1920x1080 -depth 24

# Set VNC password (first time only)
vncpasswd
```

**On local machine:**
```bash
# Install VNC viewer
sudo apt install -y tigervnc-viewer

# Connect through SSH tunnel
ssh -L 5901:localhost:5901 user@remote-host

# In another terminal, connect to VNC
vncviewer localhost:5901
```

### XPRA (Alternative for better performance)

XPRA provides better performance than X11 forwarding:

```bash
# Install on both local and remote machines
sudo apt install -y xpra

# On remote host:
xpra start :100 --start=termtel --bind-tcp=0.0.0.0:10000

# On local machine:
xpra attach ssh://user@remote-host:100
```

---

## Additional Resources

- **Official WSL GUI Documentation:** [https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)
- **Qt for Linux Documentation:** [https://doc.qt.io/qt-6/linux.html](https://doc.qt.io/qt-6/linux.html)
- **PyQt6 Documentation:** [https://www.riverbankcomputing.com/static/Docs/PyQt6/](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- **TerminalTelemetry GitHub Issues:** [https://github.com/scottpeterman/terminaltelemetry/issues](https://github.com/scottpeterman/terminaltelemetry/issues)

---

## Quick Reference Commands

### Installation Quick Start
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y libqt6gui6t64 libqt6widgets6t64 libqt6core6t64 qt6-base-dev libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0 libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-xfixes0 libx11-xcb1 libgl1 libglib2.0-0t64
pip install TerminalTelemetry
termtel-con
termtel
```

### Diagnostic Commands
```bash
# Check display server
echo $DISPLAY
echo $WAYLAND_DISPLAY
ps aux | grep -E 'X|wayland'

# Test Qt6
python3 -c "from PyQt6.QtWidgets import QApplication, QLabel; import sys; app = QApplication(sys.argv); label = QLabel('Test'); label.show(); sys.exit(app.exec())"

# Check OpenGL
glxinfo | grep "direct rendering"

# Debug Qt plugins
QT_DEBUG_PLUGINS=1 termtel
```

---

*Last Updated: October 2025 - TerminalTelemetry v0.10.0*