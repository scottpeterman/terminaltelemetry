import tkinter as tk
from tkinter import ttk
from TerminalSerial import TerminalSerial
from SerialConnectionDialog import SerialConnectionDialog
import serial
from pprint import pprint as pp
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
        self.serial_dialog.transient(self)
        self.serial_dialog.grab_set()
        self.wait_window(self.serial_dialog)

        # Check if the dialog was successful
        if self.serial_dialog.result:
            self.create_terminal(self.serial_dialog.result)


    def create_terminal(self, connection_details):
        # Create and pack the TerminalSerial frame
        # Map the input values to pySerial constants
        # Map bytesize
        bytesize_map = {
            5: serial.FIVEBITS,
            6: serial.SIXBITS,
            7: serial.SEVENBITS,
            8: serial.EIGHTBITS,
        }
        pp(connection_details)
        pp(bytesize_map)
        bytesize = bytesize_map.get(int(connection_details['bytesize']))

        # Map parity
        parity_map = {
            'N': serial.PARITY_NONE,
            'E': serial.PARITY_EVEN,
            'O': serial.PARITY_ODD,
            'M': serial.PARITY_MARK,
            'S': serial.PARITY_SPACE,
        }
        parity = parity_map.get(connection_details['parity'].upper())

        # Map stopbits
        stopbits_map = {
            1: serial.STOPBITS_ONE,
            1.5: serial.STOPBITS_ONE_POINT_FIVE,
            2: serial.STOPBITS_TWO,
        }
        stopbits = stopbits_map.get(connection_details['stopbits'])

        if None in (bytesize, parity, stopbits):
            raise ValueError("Invalid serial port parameters.")

        self.terminal_frame = TerminalSerial(
            self,
            port=connection_details['port'],
            baudrate=connection_details['baudrate'],
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits
        )
        self.terminal_frame.pack(expand=True, fill='both')
        self.terminal_frame.connect()
        print("Terminal should be packed now.")



if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()

