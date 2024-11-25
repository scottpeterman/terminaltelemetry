import paramiko
from log_handler import LogThread
import queue

import paramiko
import queue


class SSHConnection:
    def __init__(self, ssh_config, log_file=None, debug_output=False):
        self.debug_output = debug_output

        # Set crypto settings before creating the client
        self.set_ssh_crypto_settings()

        self.client = paramiko.SSHClient()

        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # print(ssh_config)
        # self.client.connect(**ssh_config)
        self.client.connect(look_for_keys=False, **ssh_config)

        self.channel = self.client.invoke_shell('xterm')

        self.log_queue = queue.Queue()
        self.log_thread = None
        if log_file:
            self.log_thread = LogThread(self.log_queue, log_file)
            self.log_thread.start()

    def set_ssh_crypto_settings(self) -> None:
        """Sets SSH crypto settings for preferred KEX, ciphers, and keys."""
        if self.debug_output:
            print("Applying SSH crypto settings...")

        paramiko.Transport._preferred_kex = (
            "diffie-hellman-group14-sha1",
            "diffie-hellman-group-exchange-sha1",
            "diffie-hellman-group-exchange-sha256",
            "diffie-hellman-group1-sha1",
            "ecdh-sha2-nistp256",
            "ecdh-sha2-nistp384",
            "ecdh-sha2-nistp521",
            "curve25519-sha256",
            "curve25519-sha256@libssh.org",
            "diffie-hellman-group16-sha512",
            "diffie-hellman-group18-sha512"
        )
        paramiko.Transport._preferred_ciphers = (
            "aes128-cbc",
            "aes128-ctr",
            "aes192-ctr",
            "aes256-ctr",
            "aes256-cbc",
            "3des-cbc",
            "aes192-cbc",
            "aes256-gcm@openssh.com",
            "aes128-gcm@openssh.com",
            "chacha20-poly1305@openssh.com",
            "aes256-gcm",
            "aes128-gcm"
        )
        paramiko.Transport._preferred_keys = (
            "ssh-rsa",
            "ssh-dss",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
            "ssh-ed25519",
            "rsa-sha2-256",
            "rsa-sha2-512"
        )
        if self.debug_output:
            print("SSH crypto settings applied.")

    def send_command(self, command):
        self.channel.send(command)

    def read_ssh_data(self, data_callback):
        while True:
            data = self.channel.recv(1024)
            if not data:
                break
            if self.log_thread:
                self.log_queue.put(data)
            data_callback(data)

    def close(self):
        if self.log_thread:
            self.log_queue.put(None)  # Signal the logging thread to stop
            self.log_thread.join()
        self.channel.close()
        self.client.close()