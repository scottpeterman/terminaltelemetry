#!/usr/bin/env python3
"""
TerminalTelemetry Production Nuitka Build Script
Handles all package data, dependencies, and creates distributable builds
"""

import subprocess
import sys
import os
import shutil
import json
from pathlib import Path
from typing import List, Dict


class TerminalTelemetryBuilder:
    """Professional build system for TerminalTelemetry"""

    def __init__(self):
        self.app_name = "TerminalTelemetry"
        self.package_name = "termtel"  # Your actual package name
        self.version = "1.1.0"
        self.company = "NetworkOps Tools"

        # Build directories
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.output_dir = self.dist_dir / "TerminalTelemetry"

        # Find entry point automatically
        self.entry_point = self.find_entry_point()

    def find_entry_point(self) -> str:
        """Find the main entry point for the application"""
        candidates = [
            "termtel/termtel.py",
            "termtel/__main__.py",
            "termtel/__init__.py",
            "terminaltelemetry/__main__.py",
            "terminaltelemetry/terminaltelemetry.py",
        ]

        for candidate in candidates:
            if Path(candidate).exists():
                print(f"✓ Found entry point: {candidate}")
                return candidate

        # If none found, ask user
        print("\n⚠️  Could not auto-detect entry point!")
        print("Please specify the main Python file to build from.")
        print("\nCommon locations:")
        for candidate in candidates:
            print(f"  - {candidate}")
        print("\nOr enter custom path:")

        while True:
            entry = input("Entry point: ").strip()
            if Path(entry).exists():
                return entry
            print(f"✗ File not found: {entry}")
            print("Try again or press Ctrl+C to exit")

    def clean(self):
        """Clean previous builds"""
        print("\n" + "=" * 70)
        print("Cleaning previous builds...")
        print("=" * 70)

        for path in [self.build_dir, self.dist_dir,
                     Path(f"{self.app_name}.dist"),
                     Path(f"{self.app_name}.build")]:
            if path.exists():
                shutil.rmtree(path)
                print(f"  ✓ Removed: {path}")

        print("  ✓ Clean complete\n")

    def check_nuitka(self):
        """Ensure Nuitka is installed"""
        try:
            import nuitka
            # Nuitka doesn't expose __version__, check via command instead
            result = subprocess.run(
                [sys.executable, "-m", "nuitka", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1] if result.stdout else "unknown"
                print(f"✓ Nuitka {version} found")
                return True
            else:
                raise ImportError("Nuitka command failed")
        except (ImportError, FileNotFoundError):
            print("✗ Nuitka not found. Installing...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "nuitka", "ordered-set", "zstandard"
            ])
            print("✓ Nuitka installed successfully")
            return True

    def get_base_command(self, onefile: bool = False) -> List[str]:
        """Build base Nuitka command"""
        cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
        ]

        if onefile:
            cmd.append("--onefile")

        cmd.extend([
            # Output configuration
            f"--output-filename={self.app_name}",
            f"--output-dir={self.dist_dir}",

            # Application metadata
            f"--company-name={self.company}",
            f"--product-name={self.app_name}",
            f"--product-version={self.version}",
            f"--file-version={self.version}",

            # PyQt6 plugin (CRITICAL!)
            "--enable-plugin=pyqt6",

            # Main package data - include EVERYTHING
            f"--include-package-data={self.package_name}",

            # Additional package data that must be included
            "--include-package-data=ntc_templates",
        ])

        return cmd

    def add_data_directories(self, cmd: List[str]) -> List[str]:
        """Add all critical data directories from MANIFEST.in"""

        # All the data directories from your MANIFEST.in
        data_includes = [
            # TextFSM templates (CRITICAL!)
            f"{self.package_name}/templates={self.package_name}/templates",

            # Platform configuration (CRITICAL!)
            f"{self.package_name}/config={self.package_name}/config",

            # Static web assets for xterm.js
            f"{self.package_name}/static={self.package_name}/static",

            # Themes
            f"{self.package_name}/themes={self.package_name}/themes",

            # Frontend assets
            f"{self.package_name}/termtelng={self.package_name}/termtelng",

            # Widgets with HTML/CSS/JS
            f"{self.package_name}/widgets={self.package_name}/widgets",
        ]

        for data_dir in data_includes:
            source = data_dir.split('=')[0]
            if Path(source).exists():
                cmd.append(f"--include-data-dir={data_dir}")
                print(f"  ✓ Including data: {source}")
            else:
                print(f"  ⚠ Skipping missing: {source}")

        return cmd

    def add_file_includes(self, cmd: List[str]) -> List[str]:
        """Add individual files that need to be included"""

        files = [
            # Icon and logo
            (f"{self.package_name}/icon.ico", f"{self.package_name}/icon.ico"),
            (f"{self.package_name}/logo.svg", f"{self.package_name}/logo.svg"),
            (f"{self.package_name}/logo.py", f"{self.package_name}/logo.py"),
        ]

        for source, dest in files:
            if Path(source).exists():
                cmd.append(f"--include-data-file={source}={dest}")
                print(f"  ✓ Including file: {source}")

        return cmd

    def add_package_includes(self, cmd: List[str]) -> List[str]:
        """Add Python packages that must be included"""

        # Critical packages for TerminalTelemetry
        packages = [
            # Network automation
            "netmiko",
            "textfsm",
            "ntc_templates",
            "napalm",
            "paramiko",
            "netaddr",

            # PyQt6 (beyond the plugin)
            "PyQt6",
            "PyQt6.QtWebEngineWidgets",
            "PyQt6.QtWebEngineCore",
            "PyQt6.QtWebChannel",

            # Cryptography
            "cryptography",
            "bcrypt",

            # Data formats
            "yaml",
            "jinja2",
            "lxml",

            # Your subpackages
            f"{self.package_name}.termtelwidgets",
            f"{self.package_name}.helpers",
            f"{self.package_name}.config",
        ]

        for package in packages:
            cmd.append(f"--include-package={package}")

        return cmd

    def add_optional_packages(self, cmd: List[str], include_all: bool = True) -> List[str]:
        """Add optional packages (can be excluded for smaller builds)"""

        if not include_all:
            return cmd

        optional = [
            "pynetbox",  # NetBox integration
            "pyserial",  # Serial console
            # Don't include these unless specifically needed:
            # "junos-eznc",  # Juniper (large, rarely used)
            # "pyeapi",      # Arista API (if not using API mode)
            # "logicmonitor-sdk",  # LogicMonitor integration
        ]

        for package in optional:
            try:
                __import__(package.replace('-', '_'))
                cmd.append(f"--include-package={package}")
                print(f"  ✓ Including optional: {package}")
            except ImportError:
                print(f"  ⚠ Skipping optional: {package} (not installed)")

        return cmd

    def add_optimizations(self, cmd: List[str]) -> List[str]:
        """Add optimization flags"""
        cmd.extend([
            "--lto=yes",  # Link-time optimization
            "--assume-yes-for-downloads",
            "--remove-output",  # Clean up intermediate files
        ])
        return cmd

    def add_platform_specific(self, cmd: List[str]) -> List[str]:
        """Add platform-specific options"""

        if sys.platform == "win32":
            cmd.extend([
                "--windows-console-mode=attach",  # For termtel-con
                f"--windows-company-name={self.company}",
                f"--windows-product-name={self.app_name}",
                f"--windows-file-version={self.version}",
                f"--windows-product-version={self.version}",
            ])

            # Add icon if exists
            icon_path = Path(f"{self.package_name}/icon.ico")
            if icon_path.exists():
                cmd.append(f"--windows-icon-from-ico={icon_path}")

        elif sys.platform == "darwin":
            cmd.extend([
                "--macos-create-app-bundle",
                f"--macos-app-name={self.app_name}",
            ])

        elif sys.platform.startswith("linux"):
            cmd.extend([
                "--linux-icon=icon.png",  # If you have one
            ])

        return cmd

    def build(self, onefile: bool = False, include_optional: bool = True):
        """Execute the build"""

        print("\n" + "=" * 70)
        print(f"Building {self.app_name} v{self.version}")
        print(f"Mode: {'Single File' if onefile else 'Directory'}")
        print("=" * 70 + "\n")

        # Build command
        cmd = self.get_base_command(onefile)
        cmd = self.add_data_directories(cmd)
        cmd = self.add_file_includes(cmd)
        cmd = self.add_package_includes(cmd)
        cmd = self.add_optional_packages(cmd, include_optional)
        cmd = self.add_optimizations(cmd)
        cmd = self.add_platform_specific(cmd)

        # Add entry point
        cmd.append(self.entry_point)

        # Print command for debugging
        print("\nBuild Command:")
        print("-" * 70)
        for i, arg in enumerate(cmd):
            if i == 0:
                print(f"{arg}", end=" \\\n  ")
            else:
                print(f"{arg}", end=" \\\n  " if i < len(cmd) - 1 else "\n")
        print("-" * 70 + "\n")

        # Execute build
        print("Starting build... (this will take 15-25 minutes)\n")
        try:
            result = subprocess.run(cmd, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Build failed with error code: {e.returncode}")
            return False

    def create_distribution(self, onefile: bool = False):
        """Create distribution package"""

        if onefile:
            # Single file - just need to zip it
            print("\nCreating distribution archive...")
            exe_name = f"{self.app_name}.exe" if sys.platform == "win32" else self.app_name
            source = self.dist_dir / exe_name

            if source.exists():
                # Create versioned archive
                import zipfile
                archive_name = f"{self.app_name}-v{self.version}-{sys.platform}"
                archive_path = self.dist_dir / f"{archive_name}.zip"

                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(source, exe_name)
                    # Add README
                    if Path("README.md").exists():
                        zf.write("README.md", "README.md")

                print(f"  ✓ Created: {archive_path}")
                print(f"  Size: {archive_path.stat().st_size / (1024 * 1024):.1f} MB")
        else:
            # Directory mode - zip the entire folder
            print("\nCreating distribution archive...")
            dist_folder = self.dist_dir / f"{self.app_name}.dist"

            if dist_folder.exists():
                import zipfile
                archive_name = f"{self.app_name}-v{self.version}-{sys.platform}"
                archive_path = self.dist_dir / f"{archive_name}.zip"

                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for file in dist_folder.rglob('*'):
                        if file.is_file():
                            arcname = file.relative_to(dist_folder.parent)
                            zf.write(file, arcname)

                    # Add README to root
                    if Path("README.md").exists():
                        zf.write("README.md", "README.md")

                print(f"  ✓ Created: {archive_path}")
                print(f"  Size: {archive_path.stat().st_size / (1024 * 1024):.1f} MB")
                print(
                    f"  Uncompressed: {sum(f.stat().st_size for f in dist_folder.rglob('*') if f.is_file()) / (1024 * 1024):.1f} MB")

    def create_launchers(self):
        """Create convenience launcher scripts"""

        dist_folder = self.dist_dir / f"{self.app_name}.dist"
        if not dist_folder.exists():
            return

        # Windows launcher
        if sys.platform == "win32":
            launcher_bat = dist_folder / "launch.bat"
            launcher_bat.write_text(f"""@echo off
REM {self.app_name} Launcher
cd /d "%~dp0"
start "" "{self.app_name}.exe"
""")
            print(f"  ✓ Created: {launcher_bat}")

        # Unix launcher
        launcher_sh = dist_folder / "launch.sh"
        launcher_sh.write_text(f"""#!/bin/bash
# {self.app_name} Launcher
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
cd "$DIR"
./{self.app_name}
""")
        launcher_sh.chmod(0o755)
        print(f"  ✓ Created: {launcher_sh}")

    def print_summary(self, onefile: bool):
        """Print build summary"""

        print("\n" + "=" * 70)
        print("Build Summary")
        print("=" * 70)

        if onefile:
            exe_name = f"{self.app_name}.exe" if sys.platform == "win32" else self.app_name
            exe_path = self.dist_dir / exe_name
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"\n✓ Single file executable created:")
                print(f"  Location: {exe_path}")
                print(f"  Size: {size_mb:.1f} MB")
                print(f"\n  To run: {exe_path}")
        else:
            dist_folder = self.dist_dir / f"{self.app_name}.dist"
            if dist_folder.exists():
                total_size = sum(f.stat().st_size for f in dist_folder.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)
                file_count = len(list(dist_folder.rglob('*')))

                exe_name = f"{self.app_name}.exe" if sys.platform == "win32" else self.app_name
                exe_path = dist_folder / exe_name

                print(f"\n✓ Directory build created:")
                print(f"  Location: {dist_folder}")
                print(f"  Size: {size_mb:.1f} MB ({file_count} files)")
                print(f"  Executable: {exe_path}")
                print(f"\n  To run: {exe_path}")
                print(f"  Or use: ./launch.sh (Unix) or launch.bat (Windows)")

        print("\n" + "=" * 70)
        print("\nNext Steps:")
        print("  1. Test the executable thoroughly")
        print("  2. Check that all themes and templates load")
        print("  3. Test SSH connections and telemetry dashboard")
        print("  4. Distribute the ZIP file from dist/ folder")
        print("=" * 70 + "\n")


def main():
    """Main build process"""
    import argparse

    parser = argparse.ArgumentParser(description="Build TerminalTelemetry with Nuitka")
    parser.add_argument("--onefile", action="store_true",
                        help="Build as single file (slower startup, easier distribution)")
    parser.add_argument("--minimal", action="store_true",
                        help="Exclude optional features (smaller build)")
    parser.add_argument("--no-clean", action="store_true",
                        help="Don't clean previous builds")
    parser.add_argument("--diagnose", action="store_true",
                        help="Show package structure and exit (diagnostic mode)")

    args = parser.parse_args()

    # Diagnostic mode
    if args.diagnose:
        print("\n" + "=" * 70)
        print("TerminalTelemetry Package Diagnostic")
        print("=" * 70 + "\n")

        # Check Python environment
        print(f"Python: {sys.version}")
        print(f"Platform: {sys.platform}")
        print(f"Working directory: {Path.cwd()}\n")

        # Check for package directories
        print("Package structure:")
        for pkg in ["termtel", "terminaltelemetry"]:
            pkg_path = Path(pkg)
            if pkg_path.exists():
                print(f"✓ Found package: {pkg}/")
                # Show key files
                for file in ["__init__.py", "__main__.py", "termtel.py"]:
                    if (pkg_path / file).exists():
                        print(f"  ✓ {file}")
                    else:
                        print(f"  ✗ {file}")
            else:
                print(f"✗ Missing package: {pkg}/")

        print("\nData directories:")
        for pkg in ["termtel", "terminaltelemetry"]:
            for subdir in ["templates", "themes", "static", "config"]:
                path = Path(pkg) / subdir
                if path.exists():
                    count = len(list(path.rglob("*")))
                    print(f"✓ {pkg}/{subdir}/ ({count} files)")
                else:
                    print(f"✗ {pkg}/{subdir}/")

        print("\nKey files:")
        for file in ["setup.py", "requirements.txt", "README.md", "MANIFEST.in"]:
            if Path(file).exists():
                print(f"✓ {file}")
            else:
                print(f"✗ {file}")

        print("\n" + "=" * 70)
        return 0

    builder = TerminalTelemetryBuilder()

    # Check Nuitka
    if not builder.check_nuitka():
        return 1

    # Clean
    if not args.no_clean:
        builder.clean()

    # Build
    success = builder.build(
        onefile=args.onefile,
        include_optional=not args.minimal
    )

    if not success:
        print("\n✗ Build failed!")
        return 1

    # Create distribution package
    builder.create_distribution(onefile=args.onefile)

    # Create launchers (onedir only)
    if not args.onefile:
        builder.create_launchers()

    # Summary
    builder.print_summary(onefile=args.onefile)

    return 0


if __name__ == "__main__":
    sys.exit(main())