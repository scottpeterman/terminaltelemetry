import tkinter as tk
from tkinter import ttk
from TerminalSerial import TerminalSerial
from SerialConnectionDialog import SerialConnectionDialog
import serial

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Serial Terminal")
        self.geometry("800x600")  # Adjust size as needed

        # Start the process of creating the serial connection dialog
        self.create_serial_dialog()

    def create_serial_dialog(self):
        self.serial_dialog = SerialConnectionDialog(self)

        # Make the dialog modal and wait for it to close before continuing
        self.serial_dialog.transient(self)  # Set the dialog to be a transient window of the main window
        self.serial_dialog.grab_set()  # Redirect all events to this dialog
        self.wait_window(self.serial_dialog)  # Wait for the dialog to close


def create_terminal(self, connection_details):
        # Create and pack the TerminalSerial frame
        self.terminal_frame = TerminalSerial(
            self,
            port=connection_details['port'],
            baudrate=connection_details['baudrate'],
            bytesize=serial.EIGHTBITS,  # Modify as needed
            parity=serial.PARITY_NONE,  # Modify as needed
            stopbits=serial.STOPBITS_ONE  # Modify as needed
        )
        self.terminal_frame.pack(expand=True, fill='both')

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

