import threading
import queue
import logging

class LogThread(threading.Thread):
    def __init__(self, log_queue, log_file):
        super().__init__(daemon=True)
        self.log_queue = log_queue
        self.log_file = log_file
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

    def run(self):
        while True:
            log_data = self.log_queue.get()
            if log_data is None:
                # None is a signal to stop the thread
                break
            # Ensure log data is decoded if it's in bytes
            if isinstance(log_data, bytes):
                log_data = log_data.decode(errors='replace')
            logging.info(log_data)
