import tkinter as tk
import webbrowser
from tkinter import ttk, font
from securetkterminal.TerminalSerial import  TerminalSerial
from securetkterminal.SerialConnectionDialog import SerialConnectionDialog
import serial
from pprint import pprint as pp
import sv_ttk


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        sv_ttk.set_theme("dark")

        self.title("Serial Terminal")
        # Calculate window geometry for centering
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)  # Implement show_about function
        self.menubar.add_cascade(label="Help", menu=help_menu)

        # Set the geometry and center the window
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Start the process of creating the serial connection dialog
        self.create_serial_dialog()

        self.custom_font = font.Font(family='Lucida Console', size=12)

    def create_serial_dialog(self):
        self.serial_dialog = SerialConnectionDialog(self)
        # self.serial_dialog.geometry("400x250")
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()

        # Dialog size
        dialog_width = 400
        dialog_height = 400

        # Calculate position relative to the parent window
        position_right = int(parent_x + (parent_width / 2) - (dialog_width / 2)) + 600
        position_down = int(parent_y + (parent_height / 2) - (dialog_height / 2)) + 300

        # Set the geometry of dialog
        self.serial_dialog.geometry(f"{dialog_width}x{dialog_height}+{position_right}+{position_down}")
        # Make the dialog modal and wait for it to close before continuing
        self.serial_dialog.transient(self)
        self.serial_dialog.grab_set()
        self.wait_window(self.serial_dialog)

        # Check if the dialog was successful
        if self.serial_dialog.result:
            self.create_terminal(self.serial_dialog.result)



    def create_terminal(self, connection_details):
        # Map the input values to pySerial constants

        # Mapping for bytesize
        bytesize_map = {
            5: serial.FIVEBITS,
            6: serial.SIXBITS,
            7: serial.SEVENBITS,
            8: serial.EIGHTBITS,
        }
        bytesize = bytesize_map.get(int(connection_details['bytesize']), serial.EIGHTBITS)

        # Mapping for parity
        parity_map = {
            'N': serial.PARITY_NONE,
            'E': serial.PARITY_EVEN,
            'O': serial.PARITY_ODD,
            'M': serial.PARITY_MARK,
            'S': serial.PARITY_SPACE,
        }
        parity = parity_map.get(connection_details['parity'].upper(), serial.PARITY_NONE)

        # Mapping for stopbits
        stopbits_map = {
            1: serial.STOPBITS_ONE,
            1.5: serial.STOPBITS_ONE_POINT_FIVE,
            2: serial.STOPBITS_TWO,
        }
        stopbits = stopbits_map.get(connection_details['stopbits'], serial.STOPBITS_ONE)

        # Create and pack the TerminalSerial frame
        self.terminal_frame = TerminalSerial(
            self,
            port=connection_details['port'],
            baudrate=connection_details['baudrate'],
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits
        )
        self.terminal_frame.custom_font = font.Font(family='Lucida Console', size=12)
        self.terminal_frame.pack(expand=True, fill='both')
        self.terminal_frame.connect()

    def show_about(self):
        about_window = tk.Toplevel(self)
        about_window.title("About")

        # Add your application information
        info_text = tk.Label(about_window, text="SecureTkTerminal\n\nA comprehensive terminal emulation application built with Python, Tkinter and sv-ttk", justify=tk.LEFT)
        info_text.pack(pady=(10, 0), padx=10)

        # Add GitHub link
        link_text = tk.Label(about_window, text="GitHub Repository", fg="green", cursor="hand2")
        link_text.pack(pady=(0, 10), padx=10)
        link_text.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/scottpeterman/securetkterminal"))

        # Add a close button
        close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
        close_button.pack(pady=(0, 10))
        # Wait for the window to update to get its width and height
        about_window.update_idletasks()

        # Calculate position x, y
        ws = self.winfo_screenwidth()  # Width of the screen
        hs = self.winfo_screenheight()  # Height of the screen
        w = about_window.winfo_width()  # Width of the toplevel window
        h = about_window.winfo_height()  # Height of the toplevel window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        about_window.geometry('+%d+%d' % (x, y))


def run():
    app = MainApplication()
    app.mainloop()

if __name__ == "__main__":
    run()
