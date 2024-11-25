import threading
import tkinter
import tkinter as tk
from tkinter import ttk, Frame, Text, font, Scrollbar
import pyte
# from ttkthemes import ThemedTk

from pyte.screens import HistoryScreen
import pyte.graphics
# Placeholder for KeyHandler - You need to provide the actual implementation
from securetkterminal.ssh_handler import SSHConnection
from securetkterminal.key_handler import KeyHandler

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

class Terminal(Frame):
    def __init__(self, master=None, ssh_config=None, log_file=None, font_size=10, *args, **kwargs):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.rows = 0
        self.cols = 0
        # Configure the font
        self.custom_font = font.Font(family='Lucida Console', size=font_size)

        self.text = Text(self, font=self.custom_font, *args, **kwargs)
        self.text.grid(row=0, column=0, sticky="nsew")
        self.text.config(state='normal', cursor="xterm", insertbackground='black')

        self.text.bind("<1>", lambda event: self.text.focus_set())

        self.screen = HistoryScreen(80, 24)
        self.stream = pyte.ByteStream()
        self.stream.attach(self.screen)


        self.ssh = SSHConnection(ssh_config, log_file)
        self.after_id = None
        self.bind("<Configure>", self.on_resize)
        self.text.bind("<KeyPress>", self.on_key_press, add=True)
        self.text.tag_configure("block_cursor", background="white", foreground="black")
        self.text.focus_set()

        self.fg_color = kwargs.pop('fg', 'white')  # Fallback to white if not specified
        self.bg_color = kwargs.pop('bg', 'black')  # Fallback to white if not specified

        # Scrollback buffer and alternate screen flag
        self.scrollback_buffer = []
        self.max_scrollback_size = 1000  # Adjust as needed
        self.in_alternate_screen = False  # Flag for alternate screen
        # Add a vertical scrollbar
        self.scrollbar = Scrollbar(self, orient='vertical')
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        # Link scrollbar to the text widget
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)
        # Create a context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_to_clipboard)
        self.context_menu.add_command(label="Paste", command=self.paste_from_clipboard)
        self.context_menu.add_command(label="Dump History", command=self.dump_pyte_history)
        self.context_menu.add_command(label="Repaint Screen", command=self.custom_repaint)


        # Bind right-click to show the context menu
        self.text.bind("<Button-3>", self.show_context_menu)  # For Windows/Linux
        threading.Thread(target=self.fetch_ssh_data, daemon=True).start()

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
        self.text.config(state='normal')

        # Clear the current content of the text widget
        self.text.delete("1.0", tk.END)

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
        _, rows = self.calculate_size(self.text.winfo_width(), self.text.winfo_height())
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
        self.text.insert("1.0", full_text)

        # Apply color tags
        for y, line in enumerate(lines_to_display, 1):
            for x, char in enumerate(line):
                char_style = self.screen.buffer[y - 1][x]
                fg_color = COLOR_MAPPINGS.get(char_style.fg, self.fg_color)  # Default to white if not found
                bg_color = COLOR_MAPPINGS.get(char_style.bg, self.bg_color)  # Default to black if not found
                tag_name = f"color_{fg_color}_{bg_color}"

                # Create the tag if it doesn't exist
                if tag_name not in self.text.tag_names():
                    self.text.tag_configure(tag_name, foreground=fg_color, background=bg_color)

                self.text.tag_add(tag_name, f"{y}.{x}", f"{y}.{x + 1}")

        # Update block cursor position
        self.update_block_cursor()

        # Disable editing of the content to prevent user edits
        self.text.config(state='disabled')

        # Set the scrollbar to the bottom (most recent part of the output)
        self.text.yview_moveto(1)
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
            selected_text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            # Clear the clipboard and append the selected text
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            # No text selected or other error
            pass

    def fetch_ssh_data(self):
        def update_ui(data):
            self.stream.feed(data)  # Feed the raw byte data
            data_str = data.decode('utf-8', errors='ignore')

            self.handle_escape_sequences(
                data_str)  # Check for alternate screen escape sequences using the decoded string

            if not self.in_alternate_screen:
                # Handle scrolling only if not in alternate screen
                while len(self.screen.dirty) > 0:
                    line_index = self.screen.dirty.pop()
                    line = self.screen.buffer[line_index]
                    self.add_to_scrollback(line)

            self.redraw()
            self.update_block_cursor()


        self.ssh.read_ssh_data(lambda data: self.after(0, lambda: update_ui(data)))

    # def handle_escape_sequences(self, data_str):
    #     # Check if the data contains the escape sequences for entering or leaving alternate screen
    #     if "\x1b[?1049h" in data_str:  # Entering alternate screen
    #         self.in_alternate_screen = True
    #     elif "\x1b[?1049l" in data_str:  # Leaving alternate screen
    #         self.in_alternate_screen = False
    def handle_escape_sequences(self, data_str):
        # Entering alternate screen
        if "\x1b[?1049h" in data_str:
            self.in_alternate_screen = True
            self.screen.reset_mode(pyte.modes.LNM)

            self.redraw()
        # Leaving alternate screen
        elif "\x1b[?1049l" in data_str:
            self.in_alternate_screen = False
            self.redraw()
    def add_to_scrollback(self, line):
        if len(self.scrollback_buffer) >= self.max_scrollback_size:
            self.scrollback_buffer.pop(0)  # Remove the oldest line if we're at capacity
        self.scrollback_buffer.append(line)

    def on_key_press(self, event):
        KeyHandler.handle_key(event, self.ssh)
        return "break"

    def on_resize(self, event):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(500, lambda: self.handle_resize(event))

    def handle_resize(self, event):
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
        if self.ssh and self.ssh.channel:
            self.ssh.channel.resize_pty(width=cols, height=rows)
            self.screen.resize(rows, cols)
            self.rows = rows
            self.cols = cols
            self.redraw()

    def update_block_cursor(self):

        # Check if we're in an alternate screen mode (full screen application)
        if self.in_alternate_screen:
            cursor_line, cursor_col = self.screen.cursor.y + 1, self.screen.cursor.x
            cursor_pos = f"{cursor_line}.{cursor_col}"
            self.text.tag_remove("block_cursor", "1.0", tk.END)

            # Add a tag to the character at the cursor position
            self.text.tag_add("block_cursor", cursor_pos, f"{cursor_pos} + 1c")

            # Configure the tag to have a solid background
            self.text.tag_configure("block_cursor", background="green", foreground="black")
            self.text.mark_set("insert", f"{cursor_line}.{cursor_col}")
            self.text.see("insert")

        else:
            # Calculate the total number of lines currently in the text widget
            total_lines_in_widget = int(self.text.index('end-1c').split('.')[0])

            # Calculate the cursor's line from the bottom of the current screen view
            lines_from_bottom = self.screen.lines - self.screen.cursor.y

            # Calculate the actual line number in the text widget for the cursor
            cursor_line = total_lines_in_widget - lines_from_bottom

            # Calculate the cursor's column position
            cursor_col = self.screen.cursor.x

            # Construct the text widget index for the cursor
            cursor_pos = f"{cursor_line + 1}.{cursor_col}"

            # Remove any previous cursor positioning
            self.text.tag_remove("block_cursor", "1.0", tk.END)

            # Add a tag to the character at the cursor position
            self.text.tag_add("block_cursor", cursor_pos, f"{cursor_pos} + 1c")

            # Configure the tag to have a solid background
            self.text.tag_configure("block_cursor", background="green", foreground="black")

            # cursor_line, cursor_col = self.screen.cursor.y + 1, self.screen.cursor.x + 1
            self.text.mark_set("insert", f"{cursor_line + 1}.{cursor_col + 1}")

            self.text.see("insert")
            # Ensure the cursor is visible
            self.text.see(cursor_pos)


    def extract_history_as_text(self, screen):
        lines_as_text = []
        for line_dict in self.screen.history.top:
            processed_line = ""
            for index in sorted(line_dict.keys()):
                char = line_dict[index]
                processed_line += char.data
            lines_as_text.append(processed_line)
        return lines_as_text

    def redraw(self):
        """Redraw the terminal screen, update cursor position, and apply color."""
        self.text.config(state='normal')
        self.text.delete("1.0", tk.END)
        self.text.tag_configure("sel", background="blue", foreground="white")
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
        _, rows = self.calculate_size(self.text.winfo_width(), self.text.winfo_height())

        # Determine which lines to display based on the terminal size
        total_lines = len(combined_lines)
        start_line = max(0, total_lines - rows)
        offset = total_lines - len(self.screen.display)

        # Join the lines and insert them into the Text widget
        full_text = "\n".join(combined_lines)
        self.text.insert("1.0", full_text)
        self.text.yview_moveto(1)
        # Apply color tags
        for y, line in enumerate(self.screen.display, 1):
            for x, char in enumerate(line):
                char_style = self.screen.buffer[y - 1][x]
                fg_color = COLOR_MAPPINGS.get(char_style.fg, self.fg_color)  # Default to white if not found
                bg_color = COLOR_MAPPINGS.get(char_style.bg, self.bg_color)  # Default to black if not found
                tag_name = f"color_{fg_color}_{bg_color}"

                # Create the tag if it doesn't exist
                if tag_name not in self.text.tag_names():
                    self.text.tag_configure(tag_name, foreground=fg_color, background=bg_color)

                # Adjust line number by the offset

                adjusted_line_num = y + offset
                self.text.tag_add(tag_name, f"{adjusted_line_num}.{x}", f"{adjusted_line_num}.{x + 1}")

        # Raise the block_cursor tag to have the highest priority
        self.text.tag_raise('block_cursor')
        self.text.tag_raise('sel')
        # Update the cursor position
        cursor_line, cursor_col = self.screen.cursor.y + 1, self.screen.cursor.x + 1
        self.text.mark_set("insert", f"{cursor_line}.{cursor_col}")
        self.text.see("insert")
        self.text.focus_set()

    def destroy(self):
        self.ssh.close()
        super().destroy()

# Here you would need to define the main part of your application
if __name__ == "__main__":
    # Example usage:
    ssh_config = {
        'hostname': '10.0.0.107',
        'port': 22,
        'username': 'speterman',
        'password': 'letme1n'
    }
    log_file = "ssh_session.log"
    ui_config = {
        'wrap': "none",
        'bg': "black",
        'fg': "green",
        'font_size': 12
    }
    root = tkinter.Tk()
    term = Terminal(root, ssh_config=ssh_config, log_file=log_file, **ui_config)
    term.pack(expand=1, fill='both')

    root.mainloop()
