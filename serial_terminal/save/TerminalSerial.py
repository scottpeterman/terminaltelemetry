import time
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import serial
import queue

from serial_terminal.KeyHandler import KeyHandler

class TerminalSerial(tk.Frame):
    def __init__(self, master, port, baudrate, bytesize, parity, stopbits, *args, **kwargs):
        print(f"Initializing TerminalSerial with: port={port}, baudrate={baudrate}, ...")
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
        self.text_display.tag_configure("block_cursor", background="black", foreground="white")
        self.toggle_cursor()
        self.text_display.bind("<KeyPress>", self.handle_key_press)  # Bind key press to handle_key_press



    def handle_key_press(self, event):
        # Use KeyHandler to process the key press and send it to the serial port
        KeyHandler.handle_key(event, self.serial_conn)
        return "break"  # Prevent default text widget behavior



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

    def connect(self):
        try:
            print("Attempting to connect...")
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=0
            )
            if self.serial_conn.is_open:
                print("Connected successfully.")
                # Set the cursor color
                self.text_display.config(insertbackground='white')

                # Create a tag to change the background color where the cursor is
                self.text_display.tag_configure('block_cursor', background='black')

                # Update the tag to be applied to the character at the cursor position
                cursor_index = self.text_display.index(tk.INSERT)
                self.text_display.tag_add('block_cursor', cursor_index, f"{cursor_index} + 1c")

                # Ensure to remove and reapply the tag each time the cursor moves

                self.running = True
                self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
                self.read_thread.start()
            else:
                print("Failed to open the port.")
                self.show_error("Failed to open the port.")
        except serial.SerialException as e:
            print(f"SerialException: {e}")
            self.show_error(str(e))

    def update_block_cursor(self):
        # First, remove the tag from the entire text
        self.text_display.tag_remove("block_cursor", "1.0", tk.END)

        # Insert the tag at the current cursor position (insertion point)
        self.text_display.tag_add("block_cursor", "insert", "insert+1c")

        # Ensure the tag is only applied to the cursor position
        self.text_display.tag_configure("block_cursor", background="black", foreground="white")

        # Make sure the cursor is visible
        self.text_display.see("insert")

        # Continue to toggle the cursor
        self.after(500, self.toggle_cursor)

    def toggle_cursor(self):
        # If the tag is set (cursor is visible), remove it to hide the cursor
        if self.text_display.tag_ranges("block_cursor"):
            self.text_display.tag_remove("block_cursor", "insert", "insert+1c")
        else:
            # If the tag is not set (cursor is hidden), add it to show the cursor
            self.text_display.tag_add("block_cursor", "insert", "insert+1c")
        # Schedule the next toggle
        self.after(500, self.toggle_cursor)



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
