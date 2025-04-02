from setuptools import setup, find_packages
import os

# Read the content of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="terminaltelemetry",
    version="0.1.0",
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
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "termtel": [
            "static/**/*",
            "templates/**/*",
            "termtelng/frontend/**/*",
            "icon.ico",
            "logo.svg",
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
)