import time
import tkinter as tk
from tkinter import ttk, Frame, Text, font, Scrollbar, scrolledtext
import threading
import serial
import pyte
from KeyHandler import KeyHandler

COLOR_MAPPINGS = {
    "black": "black",
    "red": "#ff0000",
    "green": "#00ff00",
    "yellow": "#ffff00",
    "blue": "#0000ff",
    "magenta": "#ff00ff",
    "cyan": "#00ffff",
    "white": "white",
    # Add more mappings for bright colors or other color names used by Pyte
}

class TerminalSerial(tk.Frame):
    # REDRAW_INTERVAL = 0.01  # Time (in seconds) between redraw calls


    def __init__(self, master, port, baudrate, bytesize, parity, stopbits, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.custom_font = None
        self.master = master
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.serial_conn = None
        self.read_thread = None
        self.running = False
        self.in_alternate_screen = False
        self.create_widgets()
        self.fg_color = kwargs.pop('fg', 'white')  # Fallback to white if not specified
        self.bg_color = kwargs.pop('bg', 'black')  # Fallback to white if not specified
        # Initialize pyte screen and stream
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.Stream()
        self.stream.attach(self.screen)
        self.last_redraw_time = time.time()





    def on_resize(self, event):
        cols, rows = self.calculate_size(event.width, event.height)
        self.resize_pty(cols, rows)

    def calculate_size(self, width, height):
        char_width = self.custom_font.measure('M')
        char_height = self.custom_font.metrics('linespace')
        cols = width // char_width
        rows = height // char_height
        self.rows = rows
        self.cols = cols
        return cols, rows

    def resize_pty(self, cols, rows):

        self.screen.resize(rows, cols)
        self.rows = rows
        self.cols = cols

        self.redraw()
        self.update_block_cursor()

    def create_widgets(self):
        self.text_display = scrolledtext.ScrolledText(self, font=font.Font(family='Lucida Console', size=10), state='disabled', wrap=tk.NONE)
        self.text_display.pack(expand=True, fill='both')
        self.text_display.bind("<KeyPress>", self.handle_key_press)
        self.text_display.tag_configure("block_cursor", background="white", foreground="black")
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_to_clipboard)
        self.context_menu.add_command(label="Paste", command=self.paste_from_clipboard)
        self.context_menu.add_command(label="Dump History", command=self.dump_pyte_history)
        self.context_menu.add_command(label="Repaint Screen", command=self.custom_repaint)
        self.text_display.bind("<Button-3>", self.show_context_menu)  # For Windows/Linux



    def handle_key_press(self, event):
        if self.serial_conn:
            KeyHandler.handle_key(event, self.serial_conn)
        return "break"

    def read_from_port(self):
        while self.running:
            if self.serial_conn.in_waiting:
                data = self.serial_conn.read(self.serial_conn.in_waiting)
                self.master.after(0, lambda: self.update_ui(data))
            else:
                time.sleep(0.01)

    def update_ui(self, data):
        self.handle_escape_sequences()
        self.stream.feed(data.decode('utf-8', errors='ignore'))
        self.redraw()
        self.update_block_cursor()

    def redraw(self):
        """Redraw the terminal screen, update cursor position, and apply color."""
        self.text_display.config(state='normal')
        self.text_display.delete("1.0", tk.END)
        self.text_display.tag_configure("sel", background="blue", foreground="white")
        # Extract history as text lines
        history_lines = self.extract_history_as_text(self.screen)

        # Combine history and current screen content, if not in full screen app
        if self.in_alternate_screen:
            combined_lines = []
        else:
            combined_lines = history_lines
        for line in self.screen.display:
            if isinstance(line, str):
                combined_lines.append(line)
            else:
                # If the line is not a string, concatenate characters to form the line string
                line_str = ""
                for char in line:
                    if hasattr(char, 'data'):
                        line_str += char.data
                    else:
                        line_str += char  # Assuming char is a character
                combined_lines.append(line_str)

        # Calculate the terminal screen height in rows
        _, rows = self.calculate_size(self.text_display.winfo_width(), self.text_display.winfo_height())

        # Determine which lines to display based on the terminal size
        total_lines = len(combined_lines)
        start_line = max(0, total_lines - rows)
        offset = total_lines - len(self.screen.display)

        # Join the lines and insert them into the Text widget
        full_text = "\n".join(combined_lines)
        self.text_display.insert("1.0", full_text)
        self.text_display.yview_moveto(1)
        # Apply color tags
        for y, line in enumerate(self.screen.display, 1):
            for x, char in enumerate(line):
                char_style = self.screen.buffer[y - 1][x]
                fg_color = COLOR_MAPPINGS.get(char_style.fg, self.fg_color)  # Default to white if not found
                bg_color = COLOR_MAPPINGS.get(char_style.bg, self.bg_color)  # Default to black if not found
                tag_name = f"color_{fg_color}_{bg_color}"

                # Create the tag if it doesn't exist
                if tag_name not in self.text_display.tag_names():
                    self.text_display.tag_configure(tag_name, foreground=fg_color, background=bg_color)

                # Adjust line number by the offset

                adjusted_line_num = y + offset
                self.text_display.tag_add(tag_name, f"{adjusted_line_num}.{x}", f"{adjusted_line_num}.{x + 1}")

        # Raise the block_cursor tag to have the highest priority
        self.text_display.tag_raise('block_cursor')
        self.text_display.tag_raise('sel')
        # Update the cursor position
        cursor_line, cursor_col = self.screen.cursor.y + 1, self.screen.cursor.x + 1
        self.text_display.mark_set("insert", f"{cursor_line}.{cursor_col}")
        self.text_display.see("insert")
        self.text_display.focus_set()
    def extract_history_as_text(self, screen):
        # Extract history lines from pyte screen
        # ...
        return []

    def handle_escape_sequences(self):
        return
    def update_block_cursor(self):
        # Move cursor to the position indicated by pyte screen
        cursor_pos = f"{self.screen.cursor.y + 1}.{self.screen.cursor.x}"
        self.text_display.mark_set("insert", cursor_pos)
        self.text_display.see(cursor_pos)

        # Update block cursor tag
        self.text_display.tag_add("block_cursor", "insert", "insert+1c")
        self.text_display.tag_configure("block_cursor", background="white", foreground="white")

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
            if self.serial_conn.is_open:
                self.running = True
                self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
                self.read_thread.start()
                # cols, rows = self.calculate_size(event.width, event.height)
                self.screen.resize(45,95)
                self.update_ui(b"connected...\n")
            else:
                self.show_error("Failed to open the port.")
        except serial.SerialException as e:
            self.show_error(str(e))

    def disconnect(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.running = False
            self.read_thread.join()
            self.serial_conn.close()

    def show_error(self, message):
        tk.messagebox.showerror("Error", message)

    def __del__(self):
        self.disconnect()

    def paste_from_clipboard(self):
        try:
            clipboard_text = self.master.clipboard_get(type="STRING")  # Change 'master' to whatever your root Tkinter object is
            KeyHandler.send(clipboard_text, self.ssh)
            # self.text.insert(tk.INSERT, clipboard_text)
        except tk.TclError:  # If there is no data on clipboard
            pass

    def custom_repaint(self):
        """Redraw the terminal screen, update cursor position, and apply color."""
        # Enable text widget editing to update the content
        self.text_display.config(state='normal')

        # Clear the current content of the text widget
        self.text_display.delete("1.0", tk.END)

        # Extract history as text lines
        history_lines = []
        for line_dict in self.screen.history.top:
            processed_line = ""
            for index in sorted(line_dict.keys()):
                char = line_dict[index]
                processed_line += char.data
            history_lines.append(processed_line)

        # Combine history and current screen content
        combined_lines = history_lines
        for line in self.screen.display:
            print(line)
        for line in self.screen.display:
            # If the line is a string, append it directly
            if isinstance(line, str):
                combined_lines.append(line)
            else:
                # If the line is not a string, it might be a list or another collection of characters
                line_str = ""
                for char in line:
                    # Check if char has a 'data' attribute
                    if hasattr(char, 'data'):
                        line_str += char.data
                    else:
                        line_str += char  # Assuming char is a character
                combined_lines.append(line_str)

        # Calculate the terminal screen height in rows
        _, rows = self.calculate_size(self.text_display.winfo_width(), self.text_display.winfo_height())
        for line in combined_lines:
            print("combined lines ---------------------------------------")
            print(line)
        print("----------------------------------------")
        # Determine which lines to display based on the terminal size
        total_lines = len(combined_lines)
        start_line = max(0, total_lines - rows)
        lines_to_display = combined_lines[start_line:]

        # Join the lines and insert them into the Text widget
        full_text = "\n".join(combined_lines)
        self.text_display.insert("1.0", full_text)

        # Apply color tags
        for y, line in enumerate(lines_to_display, 1):
            for x, char in enumerate(line):
                char_style = self.screen.buffer[y - 1][x]
                fg_color = COLOR_MAPPINGS.get(char_style.fg, self.fg_color)  # Default to white if not found
                bg_color = COLOR_MAPPINGS.get(char_style.bg, self.bg_color)  # Default to black if not found
                tag_name = f"color_{fg_color}_{bg_color}"

                # Create the tag if it doesn't exist
                if tag_name not in self.text_display.tag_names():
                    self.text_display.tag_configure(tag_name, foreground=fg_color, background=bg_color)

                self.text_display.tag_add(tag_name, f"{y}.{x}", f"{y}.{x + 1}")

        # Update block cursor position
        self.update_block_cursor()

        # Disable editing of the content to prevent user edits
        self.text_display.config(state='disabled')

        # Set the scrollbar to the bottom (most recent part of the output)
        self.text_display.yview_moveto(1)
    def dump_pyte_history(self):
        lines_as_text = []
        for line_dict in self.screen.history.top:
            processed_line = ""
            for index in sorted(line_dict.keys()):
                char = line_dict[index]
                processed_line += char.data
            lines_as_text.append(processed_line)

        # Now print or add to the text widget
        final_output = "\n".join(lines_as_text)
        print(final_output)  # or display in your text widget
        return final_output

    def show_context_menu(self, event):
        try:
            # Display the context menu
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Make sure the menu is closed after selection
            self.context_menu.grab_release()

    def copy_to_clipboard(self):
        try:
            # Get the selected text
            selected_text = self.text_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            # Clear the clipboard and append the selected text
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            # No text selected or other error
            pass


# For direct testing of TerminalSerial
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Serial Terminal")
    terminal_frame = TerminalSerial(
        root,
        port='COM7',
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE
    )
    terminal_frame.pack(expand=True, fill='both')
    terminal_frame.connect()
    root.mainloop()
