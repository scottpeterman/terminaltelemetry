# device_discovery.py
import json
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from PySSHPass.pysshpass import SSHClientWrapper
import sqlite3
import textfsm
import io
from tfsm_fire import TextFSMAutoEngine


@dataclass
class DeviceFingerprint:
    device_type: str
    confidence_score: float
    parsed_data: List[Dict]
    raw_output: str
    template_name: str
    processing_time: float


class DeviceDiscovery:
    def __init__(self, db_path: str, verbose: bool = False, timeout: int = 5):
        """Initialize device discovery with TextFSM database."""
        self.db_path = db_path
        self.engine = TextFSMAutoEngine(db_path, verbose=verbose)
        self.verbose = verbose

    # def process_device(
    #         self,
    #         host: str,
    #         username: str,
    #         password: str,
    #         ssh_timeout: int = 60,
    # ) -> Optional[DeviceFingerprint]:
    #     """Process a single device using show version command."""
    #     start_time = time.time()
    #     try:
    #         # Initialize SSH client with pagination disable commands
    #         command_string = (
    #             'cat /etc/*release* && hostnamectl && lscpu && free -h && df -h && echo "#\n#\n#\n"\n'
    #             "term len 0\n"
    #             "terminal length 0\n"
    #             "no page\n"
    #             "no paging\n"
    #             "set cli pager off\n"
    #             "show version\n"
    #         )
    #
    #         ssh = SSHClientWrapper(
    #             host=host,
    #             user=username,
    #             password=password,
    #             cmds=command_string,
    #             timeout=ssh_timeout,
    #             quiet=not self.verbose,
    #             invoke_shell=True,
    #             prompt_count=6  # Number of commands
    #         )
    #
    #         ssh.connect()
    #         raw_output = ssh.run_commands()
    #         ssh.close()
    #
    #         if not raw_output:
    #             if self.verbose:
    #                 print(f"No output received from {host}")
    #             return None
    #
    #         # Extract show version output
    #         cleaned_output = self._clean_output(raw_output)
    #
    #         # Try templates
    #         template_name, parsed_data, score = self.engine.find_best_template(
    #             cleaned_output,
    #             filter_string="show_version"
    #         )
    #
    #         if score > 20 and template_name and parsed_data:
    #             processing_time = time.time() - start_time
    #             return DeviceFingerprint(
    #                 device_type=self._extract_device_type(template_name),
    #                 confidence_score=score,
    #                 parsed_data=parsed_data,
    #                 raw_output=cleaned_output,
    #                 template_name=template_name,
    #                 processing_time=processing_time
    #             )
    #
    #         return None
    #
    #     except Exception as e:
    #         if self.verbose:
    #             print(f"Error processing {host}: {str(e)}")
    #         return None

    def process_device(
            self,
            host: str,
            username: str,
            password: str,
            ssh_timeout: int = 60,
    ) -> Optional[DeviceFingerprint]:
        """Process a single device, checking for Linux first, then network devices."""
        start_time = time.time()
        try:
            # Initialize SSH client with both Linux and network device commands
            command_string = (
                'cat /etc/*release* && hostnamectl && lscpu && free -h && df -h && echo "#\n#\n#\n"\n'
                "term len 0\n"
                "terminal length 0\n"
                "no page\n"
                "no paging\n"
                "set cli pager off\n"
                "show version\n"
            )

            ssh = SSHClientWrapper(
                host=host,
                user=username,
                password=password,
                cmds=command_string,
                timeout=ssh_timeout,
                quiet=not self.verbose,
                invoke_shell=True,
                prompt_count=6
            )

            ssh.connect()
            raw_output = ssh.run_commands()
            ssh.close()

            if not raw_output:
                if self.verbose:
                    print(f"No output received from {host}")
                return None

            # First, try to match against Linux template
            template_name, parsed_data, score = self.engine.find_best_template(
                raw_output,  # Use raw output for Linux
                filter_string="linux_fingerprint"
            )

            if score > 20 and template_name and parsed_data:
                processing_time = time.time() - start_time
                return DeviceFingerprint(
                    device_type="linux",
                    confidence_score=score,
                    parsed_data=parsed_data,
                    raw_output=raw_output,
                    template_name=template_name,
                    processing_time=processing_time
                )

            # If Linux check failed, try network devices
            cleaned_output = self._clean_output(raw_output)
            template_name, parsed_data, score = self.engine.find_best_template(
                cleaned_output,
                filter_string="show_version"
            )

            if score > 20 and template_name and parsed_data:
                processing_time = time.time() - start_time
                return DeviceFingerprint(
                    device_type=self._extract_device_type(template_name),
                    confidence_score=score,
                    parsed_data=parsed_data,
                    raw_output=cleaned_output,
                    template_name=template_name,
                    processing_time=processing_time
                )

            return None

        except Exception as e:
            if self.verbose:
                print(f"Error processing {host}: {str(e)}")
            return None

    def _clean_output(self, output: str) -> str:
        """Clean the SSH output to remove connection messages and prompts."""
        lines = output.split('\n')
        cleaned_lines = []
        skip_patterns = [
            "Connected to",
            "Executing command:",
            "Terminal length",
            "% Invalid input",
            "% Error",
            "term len",
            "terminal length",
            "no page",
            "no paging",
            "set cli pager",
        ]

        # Get everything after "show version"
        show_version_seen = False
        for line in lines:
            line = line.strip()
            if "show version" in line:
                show_version_seen = True
                continue
            if show_version_seen and line and not any(pattern in line for pattern in skip_patterns):
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    def _extract_device_type(self, template_name: str) -> str:
        """Extract vendor and OS from template name."""
        parts = template_name.split('_')
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
        return template_name