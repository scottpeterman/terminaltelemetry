from setuptools import setup, find_packages
import os

# Read the content of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="TerminalTelemetry",
    version="1.1.0",
    author="Scott Peterman",
    author_email="scottpeterman@gmail.com",
    description="A PyQt6 terminal emulator with SSH and telemetry capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scottpeterman/terminaltelemetry",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: System Shells",
        "Topic :: Terminals :: Terminal Emulators/X Terminals",
    ],
    python_requires=">=3.12",
    install_requires=requirements,

    include_package_data=True,
    zip_safe=False,  # Important for accessing package data files

    # Updated package_data to include all necessary resources
    package_data={
        "termtel": [
            # Static web assets
            "static/**/*",
            "static/css/*.css",
            "static/js/*.js",
            "static/images/*",
            "static/*.html",
            "static/*.wasm",
            "static/*.sav",

            # TextFSM templates
            "templates/textfsm/*.textfsm",
            "templates/**/*",

            # Widgets with web content
            "widgets/**/*.html",
            "widgets/**/*.css",
            "widgets/**/*.js",
            "widgets/**/*.json",

            # Platform configuration
            "config/*.json",
            "config/platforms/*.json",
            "config/platforms/platforms.json",

            # Frontend assets
            "termtelng/frontend/**/*",

            # Icons and logos
            "icon.ico",
            "logo.svg",
            "logo.py",

            # Database files
            "*.db",

            # Any additional resource files
            "*.html",
            "themes/*.json",
        ],
        "termtel.termtelwidgets": [
            "*.py",
        ],
        # Include helper modules
        "termtel.helpers": [
            "*.py",
        ],
        # Include config as a separate package to ensure it's found
        "termtel.config": [
            "*.json",
            "platforms/*.json",
        ],
    },

    entry_points={
        "console_scripts": [
            "termtel-con=termtel.termtel:main",
        ],
        "gui_scripts": [
            "termtel=termtel.termtel:main",
        ],
    },

    # Additional metadata for better discoverability
    keywords="terminal ssh telemetry network monitoring pyqt6 netmiko textfsm",
    project_urls={
        "Source": "https://github.com/scottpeterman/terminaltelemetry",
    },
)