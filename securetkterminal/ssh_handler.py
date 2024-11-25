import paramiko
from securetkterminal.log_handler_ssh import LogThread
import queue

class SSHConnection:
    def __init__(self, ssh_config, log_file=None):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(**ssh_config)
        self.channel = self.client.invoke_shell('xterm')

        self.log_queue = queue.Queue()
        self.log_thread = None
        if log_file:
            self.log_thread = LogThread(self.log_queue, log_file)
            self.log_thread.start()

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
