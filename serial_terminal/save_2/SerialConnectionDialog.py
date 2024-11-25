import tkinter as tk
from tkinter import ttk, messagebox
from serial.tools import list_ports
import serial

class SerialConnectionDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Connect to Serial Port")
        self.geometry("400x200")  # Adjust size as needed

        # Form fields
        self.port = tk.StringVar()
        self.baudrate = tk.IntVar(value=9600)
        self.databits = tk.IntVar(value=8)
        self.stopbits = tk.IntVar(value=1)
        self.parity = tk.StringVar(value='N')

        # Setup widgets
        self.create_widgets()

        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)  # Handle window close button
        self.result = None  # Initialize result

    def create_widgets(self):
        form = ttk.Frame(self)
        form.pack(padx=10, pady=10, fill='x', expand=True)

        # Port
        ttk.Label(form, text="Port").grid(row=0, column=0, sticky='w')
        port_combobox = ttk.Combobox(form, textvariable=self.port)
        port_combobox['values'] = [port.device for port in list_ports.comports()]
        port_combobox.grid(row=0, column=1, sticky='ew')

        # Baudrate
        ttk.Label(form, text="Baud Rate").grid(row=1, column=0, sticky='w')
        ttk.Entry(form, textvariable=self.baudrate).grid(row=1, column=1, sticky='ew')

        # Data Bits
        ttk.Label(form, text="Data Bits").grid(row=2, column=0, sticky='w')
        ttk.Entry(form, textvariable=self.databits).grid(row=2, column=1, sticky='ew')

        # Stop Bits
        ttk.Label(form, text="Stop Bits").grid(row=3, column=0, sticky='w')
        ttk.Entry(form, textvariable=self.stopbits).grid(row=3, column=1, sticky='ew')

        # Parity
        ttk.Label(form, text="Parity").grid(row=4, column=0, sticky='w')
        ttk.Entry(form, textvariable=self.parity).grid(row=4, column=1, sticky='ew')

        # Buttons
        buttons = ttk.Frame(self)
        buttons.pack(pady=10, fill='x', expand=True)
        ttk.Button(buttons, text="Connect", command=self.on_connect).pack(side='right', padx=5)
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side='right')

    def on_connect(self):
        try:
            # Attempt to create a serial connection
            connection = serial.Serial(
                port=self.port.get(),
                baudrate=self.baudrate.get(),
                bytesize=self.databits.get(),
                stopbits=self.stopbits.get(),
                parity=self.parity.get(),
                timeout=1
            )
            connection.close()  # Close the connection immediately for now
            print("Connected", "Successfully connected to the serial port.")
            self.result = {
                'port': self.port.get(),
                'baudrate': self.baudrate.get(),
                'bytesize': self.databits.get(),
                'parity': self.parity.get(),
                'stopbits': self.stopbits.get()
            }
            self.destroy()
        except serial.SerialException as e:
            messagebox.showerror("Connection error", str(e))
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def on_cancel(self):
        self.result = None
        self.destroy()

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")
    app = SerialConnectionDialog(root)
    root.mainloop()
