import time
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import serial
import queue

from key_handler import KeyHandler

class TerminalSerial(tk.Frame):
    def __init__(self, master, port, baudrate, bytesize, parity, stopbits, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.serial_conn = None
        self.read_thread = None
        self.running = False
        self.queue = queue.Queue()

        self.create_widgets()

    def create_widgets(self):
        self.text_display = scrolledtext.ScrolledText(self, state='disabled', wrap=tk.NONE)
        self.text_display.pack(expand=True, fill='both')
        self.text_display.bind("<KeyPress>", self.handle_key_press)  # Bind key press to handle_key_press


        self.connect_button = ttk.Button(self, text="Connect", command=self.connect)
        self.connect_button.pack(side=tk.BOTTOM, fill='x')

    def handle_key_press(self, event):
        # Use KeyHandler to process the key press and send it to the serial port
        KeyHandler.handle_key(event, self.serial_conn)
        return "break"  # Prevent default text widget behavior
    def connect(self):
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=0
            )
            self.running = True
            self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
            self.read_thread.start()
        except serial.SerialException as e:
            self.show_error(str(e))

    def read_from_port(self):
        while self.running:
            if self.serial_conn.in_waiting:
                data = self.serial_conn.read(self.serial_conn.in_waiting)
                self.queue.put(data)
                self.update_display()
            else:
                # Sleep briefly to prevent CPU overuse.
                time.sleep(0.01)

    def update_display(self):
        while not self.queue.empty():
            data = self.queue.get_nowait()
            # Insert data into text widget
            self.text_display.config(state='normal')
            self.text_display.insert('end', data.decode('utf-8', errors='ignore'))
            self.text_display.config(state='disabled')
            # Auto-scrolling
            self.text_display.see('end')

    def disconnect(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.running = False
            self.read_thread.join()
            self.serial_conn.close()

    def __del__(self):
        self.disconnect()

    def show_error(self, message):
        tk.messagebox.showerror("Error", message)

# You can also test the TerminalSerial class directly by uncommenting the following lines:
# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Serial Terminal")
#     terminal_frame = TerminalSerial(
#         root,
#         port='COM3',
#         baudrate=9600,
#         bytesize=serial.EIGHTBITS,
#         parity=serial.PARITY_NONE,
#         stopbits=serial.STOPBITS_ONE
#     )
#     terminal_frame.pack(expand=True, fill='both')
#     root.mainloop()
