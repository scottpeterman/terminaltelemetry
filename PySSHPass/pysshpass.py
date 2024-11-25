import socket
import sys
import paramiko
import os
import time
import click
import select


class SSHClientWrapper:
    def __init__(self, host, user, password, cmds='', invoke_shell=False, prompt='', prompt_count=1, timeout=360,
                 disable_auto_add_policy=False, look_for_keys=False, delay=0.5, quiet=False):
        self.quiet = quiet
        self.host = host
        self.user = user
        self.password = password or os.getenv('PYSSH_PASS')
        if not self.password:
            raise ValueError("No password provided. Use either --password or set the PYSSH_PASS environment variable.")
        self.cmds = cmds
        self.delay = delay
        self.invoke_shell = invoke_shell
        self.prompt = prompt
        self.prompt_count = prompt_count
        self.timeout = timeout
        self.disable_auto_add_policy = disable_auto_add_policy
        self.look_for_keys = look_for_keys
        self.client = None
        self.log_file = None
        self.shell_channel = None  # Keeps the shell channel open between runs
        self.exit_reason = "Not running..."
        self.connected = False
        # Parse host and port
        if ':' in host:
            self.hostname, port = host.split(':')
            try:
                self.port = int(port)
            except ValueError:
                raise ValueError(f"Invalid port number: {port}")
        else:
            self.hostname = host
            self.port = 22  # Default SSH port

    def logging_setup(self, log_dir="pyssh_log"):
        log_file = os.path.join(log_dir, f'{self.host}.log')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.log_file = log_file

    def connect(self):
        self.logging_setup()


        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect((self.hostname, self.port))
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to {self.hostname}:{self.port} - {str(e)}")
        finally:
            sock.close()

        # Initialize SSH client
        self.client = paramiko.SSHClient()
        if self.disable_auto_add_policy:
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                look_for_keys=self.look_for_keys,
                timeout=self.timeout,
                allow_agent=False
            )
            connect_msg = f"Connected to {self.host} using the specified algorithms.\n"
            self.log(connect_msg)
            self.connected = True
        except paramiko.AuthenticationException:
            self.log("Authentication failed, please verify your credentials.\n", error=True)
        except paramiko.SSHException as e:
            self.log(f"Could not establish SSH connection: {str(e)}\n", error=True)
            # sys.exit(1)
        except Exception as e:
            self.log(f"PySSHPass Base exception: {str(e)}\n", error=True)
            # sys.exit(1)

    def open_shell(self):
        """Open the shell channel only once and reuse it."""
        if self.shell_channel is None:
            self.shell_channel = self.client.invoke_shell()

    def log(self, message, error=False):
        """Logs messages to both file and optionally to stdout based on quiet mode."""
        if not self.quiet or error:
            print(message, end='')
        with open(self.log_file, 'a') as f:
            f.write(message)
            f.flush()

    def run_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        start_time = time.time()
        output = ""
        with open(self.log_file, 'a') as f:
            while True:
                if stdout.channel.recv_ready():
                    output_chunk = stdout.channel.recv(4096).decode('utf-8')
                    f.write(output_chunk)
                    f.flush()
                    output += output_chunk
                    start_time = time.time()  # Reset the timeout counter on data reception
                if time.time() - start_time > self.timeout:
                    timeout_msg = "\nCommand timed out.\n"
                    self.log(timeout_msg, error=True)
                    break
        return output

    def get_command_list(self):
        # Split commands by comma and remove unnecessary spaces
        command_list = []
        for cmd in self.cmds.split(','):
            if cmd == '':
                cmd = '[\n]'
            stripped_cmd = cmd.strip()
            if stripped_cmd:  # Add only non-empty commands
                command_list.append(stripped_cmd)
        return command_list

    def run_commands(self):
        self.exit_reason = "running commands..."
        command_list = self.get_command_list()
        aggregate_output = ""

        if not self.invoke_shell and len(command_list) > 1:
            raise ValueError(
                "Multiple commands are not allowed in non-shell mode. Please use '--invoke-shell' for running multiple commands."
            )

        if self.invoke_shell:
            if self.shell_channel is None:
                self.open_shell()

            for cmd in command_list:
                self.run_command_in_shell(self.shell_channel, cmd)
                time.sleep(self.delay)

            aggregate_output = self.read_shell_output()
        else:
            for cmd in command_list:
                aggregate_output += self.run_command(cmd)

        return aggregate_output

    def read_shell_output(self):
        """Read the output from the shell without using threading."""
        output = ""
        buffer_size = 4096
        counter = 0
        end_time = time.time() + self.timeout  # Calculate the absolute end time

        try:
            with open(self.log_file, 'a') as f:
                while time.time() < end_time:
                    rlist, _, _ = select.select([self.shell_channel], [], [], self.timeout)
                    if rlist:
                        output_chunk = self.shell_channel.recv(buffer_size).decode('utf-8').replace('\r', '')
                        f.write(output_chunk)
                        f.flush()
                        output += output_chunk

                        # Check for prompt
                        lines = output_chunk.split("\n")
                        for line in lines:
                            if self.prompt in line:
                                counter += 1
                                if counter >= self.prompt_count:
                                    # Successful prompt detection
                                    final_msg = f"\nSuccessfully detected prompt ({self.prompt}) {counter} times.\n"
                                    self.log(final_msg)
                                    if not self.quiet:
                                        print(final_msg)
                                    return output
                    elif self.shell_channel.closed:
                        # If the shell channel is closed, stop reading
                        break

        except Exception as e:
            self.log(f"SSH exception during shell read: {str(e)}\n", error=True)
            self.exit_reason = f"SSH exception: {str(e)}"
            return output  # Return collected output before the error

        # If we exit the loop without detecting the prompt the required number of times (timeout)
        timeout_msg = (f"\nRead timeout after {self.timeout} seconds.\n"
                       f"Expected prompt count: {self.prompt_count}, Actual count: {counter}\n")
        self.exit_reason = timeout_msg

        self.log(timeout_msg, error=True)

        # Always print feedback to the user if not in quiet mode
        if not self.quiet:
            print(timeout_msg)

        return output  # Return collected output even after timeout

    def run_command_in_shell(self, channel, command):
        """
        Send command to the shell.
        """
        command = command.replace('"', '')
        if command == '[\n]':
            cmd_msg = f"Executing command: [NEWLINE]\n"
            channel.send('\n')
        else:
            cmd_msg = f"Executing command: {command}\n"
            channel.send(command + '\n')
        self.log(cmd_msg)

    def find_prompt(self, timeout=10, ends_with=None):
        """
        Dynamically find the prompt by reading the shell output until a line ends with a typical prompt character
        or a user-specified string.
        Returns the detected prompt.
        """
        if not self.connected:
            return None
        if ends_with is None:
            # Default prompt characters if not provided
            ends_with = ('>', '#', '$')

        self.open_shell()  # Ensure the shell is open
        self.shell_channel.settimeout(timeout)
        buffer_size = 4096
        output = ""

        try:
            if isinstance(timeout,str):
                timeout = 5
            end_time = time.time() + timeout  # Calculate the absolute end time
            self.run_command_in_shell(self.shell_channel, command="\n")
            while time.time() < end_time:
                if self.shell_channel.recv_ready():
                    output_chunk = self.shell_channel.recv(buffer_size).decode('utf-8')
                    output += output_chunk

                    # Split the output into lines and check if any ends with a character or string in ends_with
                    lines = output.split("\n")
                    for line in lines:
                        # Check if the line ends with any of the characters/strings in ends_with
                        if line.strip().endswith(ends_with):
                            self.prompt = line.strip()  # Set the detected prompt
                            return self.prompt

                time.sleep(0.1)

        except Exception as e:
            self.log(f"Error while detecting prompt: {str(e)}", error=True)

        # If the loop completes without finding a prompt, return an empty string
        return ""


    def close(self):
        self.log(self.exit_reason)
        if self.client:
            if self.shell_channel:
                self.shell_channel.close()  # Close the shell when done with all commands
            self.client.close()


# CLI configuration using click
@click.command()
@click.option('--host', '-h', required=True, help='SSH Host (ip:port)')
@click.option('--user', '-u', required=True, help='SSH Username')
@click.option('--password', '-p', required=False, help='SSH Password')
@click.option('--cmds', '-c', default='', help='Commands to run, separated by comma')
@click.option('--invoke-shell/--no-invoke-shell', default=True,
              help='Invoke shell before running the command [default=True]')
@click.option('--prompt', default='', help='Prompt to look for before breaking the shell')
@click.option('--prompt-count', default=1, help='Number of prompts to look for before breaking the shell')
@click.option('--timeout', '-t', default=360, help='Command timeout duration in seconds')
@click.option('--disable-auto-add-policy', is_flag=True, default=False,
              help='Disable automatically adding the host key [default=False]')
@click.option('--look-for-keys', is_flag=True, default=False, help='Look for local SSH key [default=False]')
@click.option('--delay', '-d', default=0.5, help='Delay between sending commands in seconds [default is 0.5 seconds]')
@click.option('--quiet', is_flag=True, default=False, help='Suppress output when running as a library')
def ssh_client(host, user, password, cmds, invoke_shell, prompt, prompt_count, timeout, disable_auto_add_policy,
               look_for_keys, delay, quiet):
    """
    CLI wrapper for SSHClientWrapper class
    """
    ssh_client = SSHClientWrapper(host, user, password, cmds, invoke_shell, prompt, prompt_count, timeout,
                                  disable_auto_add_policy, look_for_keys, delay, quiet)
    ssh_client.connect()
    output = ssh_client.run_commands()  # Runs the commands and returns the output
    if not quiet:
        print(output)
    ssh_client.close()


if __name__ == '__main__':
    ssh_client()
