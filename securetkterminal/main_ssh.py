import tkinter
import uuid

import sv_ttk
from tkinter import ttk, Menu
from securetkterminal.TerminalSSH import Terminal
from pprint import pprint as pp



class App(ttk.Frame):
    def __init__(self, parent, ssh_config, ui_config, log_file):
        super().__init__(parent)
        self.parent = parent
        self.ssh_config = ssh_config
        self.ui_config = ui_config
        self.log_file = log_file

        # Store the sessions (UUID -> Terminal)
        self.sessions = {}
        self.widget_to_uuid = {}
        # Create the menu bar
        self.menubar = Menu(parent)
        parent.config(menu=self.menubar)

        # Create the File menu
        # file_menu = Menu(self.menubar, tearoff=0)
        # file_menu.add_command(label="Open", command=self.open_file)  # Implement open_file function
        # file_menu.add_separator()
        # # file_menu.add_command(label="Exit", command=self.on_close)
        # self.menubar.add_cascade(label="File", menu=file_menu)

        # Create the Sessions menu
        sessions_menu = Menu(self.menubar, tearoff=0)
        sessions_menu.add_command(label="Quick Connect",
                                  command=lambda: self.quick_connect())  # Implement quick_connect function
        self.menubar.add_cascade(label="Sessions", menu=sessions_menu)
        help_menu = Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)  # Implement show_about function
        self.menubar.add_cascade(label="Help", menu=help_menu)

        # Create the Help menu
        # help_menu = Menu(self.menubar, tearoff=0)
        # help_menu.add_command(label="About", command=self.show_about)  # Implement show_about function
        # self.menubar.add_cascade(label="Help", menu=help_menu)

        # Create the tab control with a context menu
        self.tab_control = ttk.Notebook(parent)
        self.tab_control.pack(expand=1, fill="both")
        self.tab_control.bind("<Button-3>", self.show_tab_menu)  # Bind right click to show context menu

        # Create context menu for tabs
        self.tab_menu = Menu(self.tab_control, tearoff=0)
        self.tab_menu.add_command(label="Close Tab", command=self.close_active_tab)

        # Create the default SSH session tab
        # self.create_terminal_tab(ssh_config['hostname'], ssh_config['port'],
        #                          ssh_config['username'], ssh_config['password'])

        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)
        self.parent.mainloop()

    def open_file(self):
        pass  # Implement file opening logic

    def edit_session(self):
        pass  # Implement session editing logic

    def list_sessions(self):
        pass  # Implement session listing logic

    def show_about(self):
        about_window = tk.Toplevel(self.parent)
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
        ws = self.parent.winfo_screenwidth()  # Width of the screen
        hs = self.parent.winfo_screenheight()  # Height of the screen
        w = about_window.winfo_width()  # Width of the toplevel window
        h = about_window.winfo_height()  # Height of the toplevel window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        about_window.geometry('+%d+%d' % (x, y))

    def quick_connect(self):
        dialog = QuickConnectDialog(self.parent, title="Quick Connect")
        if dialog.result:
            self.create_terminal_tab(
                dialog.result['host'],
                dialog.result['port'],
                dialog.result['username'],
                dialog.result['password']
            )

    def create_terminal_tab(self, host, port, username, password):
        tab_id = uuid.uuid4()
        tab_frame = ttk.Frame(self.tab_control)
        tab_frame.uuid = tab_id  # Assign the UUID as a custom attribute

        self.tab_control.add(tab_frame, text=host, image=tab_id)

        # Create Terminal instance with ssh_config
        ssh_config = {'hostname': host, 'port': port, 'username': username, 'password': password}
        term = Terminal(tab_frame, ssh_config=ssh_config, log_file=self.log_file, **self.ui_config)
        term.uuid = tab_id
        term.pack(expand=1, fill='both')


        # Store the session
        self.sessions[str(tab_id)] = term

    def show_tab_menu(self, event):
        """Shows the context menu on right-click on a tab."""
        clicked_tab_index = self.tab_control.tk.call(self.tab_control._w, "identify", "tab", event.x, event.y)
        tab = self.tab_control.tab(clicked_tab_index)
        self.right_clicked_tab_uuid = tab['image'][0]
        if clicked_tab_index != '':
            self.right_clicked_tab = clicked_tab_index  # Save the index of the right-clicked tab
            self.tab_menu.post(event.x_root, event.y_root)

    def get_tab_frame_by_index(self, tab_index):
        """Get the frame widget for the tab at the given index."""


        """Get the frame widget for the tab at the given index."""
        try:
            # Get the tab id for the given index using the select method
            d = self.tab_control.tab(0)
            tab_id = self.tab_control.select(tab_index)

            if tab_id:
                # Get all child widgets of the Notebook
                children = self.tab_control.winfo_children()

                # Find the child widget that has the same name as the tab id
                for child in children:
                    print(dir(child))
                    if child.winfo_name() == tab_id:
                        return child  # This is the frame widget for the tab
        except tkinter.TclError:
            # This error occurs if the index is out of range
            pass
        return None
    def close_active_tab(self):
        """Closes the tab that was right-clicked."""
        if self.right_clicked_tab is not None:
            # Get the internal tab ID using the index
            tab_index = int(self.right_clicked_tab)
            tab_widget_name = self.tab_control.tabs()[
                tab_index]  # Get the tab id (internal widget name) using the index

            found_tab_with_session = None
            for child in self.tab_control.winfo_children():
                if not isinstance(child, Menu):
                    if str(child.uuid) == self.right_clicked_tab_uuid:
                        found_tab_with_session = child
                        print(f"Found it!")

                        self.close_tab(self.right_clicked_tab_uuid, tab_index)  # Close the tab using its UUID
            else:
                print(f"No tab frame found for widget name {tab_widget_name}")

            self.right_clicked_tab = None  # Reset the variable

    def on_close(self):
        """Cleans up resources and closes the application."""
        for session in self.sessions.values():
            session.destroy()  # Call the destroy method of the Terminal instance
        self.parent.destroy()

    def close_tab(self, session_id, tab_id):
        session = self.sessions.pop(session_id, None)
        if session:
            self.tab_control.forget(tab_id)  # This should remove the tab
            session.destroy()  # Call the destroy method of the Terminal instance
            print(f"Closed tab and session for {tab_id}")


import tkinter as tk
import webbrowser


def show_about(self):
    about_window = tk.Toplevel(self.parent)
    about_window.title("About")

    # Add your application information
    info_text = tk.Label(about_window, text="SecureTkTerminal\nA comprehensive mult-tabbed terminal emulation application built with Python and Tkinter", justify=tk.LEFT)
    info_text.pack(pady=(10, 0), padx=10)

    # Add GitHub link
    link_text = tk.Label(about_window, text="GitHub Repository", fg="blue", cursor="hand2")
    link_text.pack(pady=(0, 10), padx=10)
    link_text.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/scottpeterman/securetkterminal"))

    # Add a close button
    close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
    close_button.pack(pady=(0, 10))


class QuickConnectDialog(tkinter.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.grab_set()
        bg_color = "#333333"

        self.configure(background=bg_color)  # Set the background color of the Toplevel

        self.transient(parent)  # Dialog window is related to the main window
        self.title("Quick Connect")  # Set the title here
        self.update_idletasks()  # Update "requested size" from geometry manager

        ws = self.winfo_screenwidth()  # Width of the screen
        hs = self.winfo_screenheight()  # Height of the screen

        w = self.winfo_reqwidth()  # Width for the Toplevel
        h = self.winfo_reqheight()  # Height for the Toplevel

        # Calculate x, y coordinates
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.parent = parent
        self.result = None

        body = ttk.Frame(self)
        body.configure(style="TFrame")  # Apply ttk style if you have set one for TFrame
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5, fill="both", expand=True)
        # body.configure(bg=bg_color)  # Set the background color of the Frame

        self.buttonbox()

        self.grab_set()  # Modal: input is grabbed to this window

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self, master):
        # create dialog body. Return widget that should have initial focus.
        ttk.Label(master, text="Host:").grid(row=0, column=0)
        ttk.Label(master, text="Port:").grid(row=1, column=0)
        ttk.Label(master, text="Username:").grid(row=2, column=0)
        ttk.Label(master, text="Password:").grid(row=3, column=0)

        self.e1 = ttk.Entry(master)
        self.e2 = ttk.Entry(master)
        self.e3 = ttk.Entry(master)
        self.e4 = ttk.Entry(master, show="*")

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)

        self.e2.insert(tkinter.END, '22')  # Default value for port

        return self.e1  # initial focus on the Host field

    def buttonbox(self):
        # Add standard button box.
        box = ttk.Frame(self)

        ok_button = ttk.Button(box, text="Ok", width=10, command=self.on_ok, default=tkinter.ACTIVE)
        ok_button.pack(side=tkinter.LEFT, padx=5, pady=5)
        cancel_button = ttk.Button(box, text="Cancel", width=10, command=self.on_cancel)
        cancel_button.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.on_ok)
        self.bind("<Escape>", self.on_cancel)

        box.pack()

    def on_ok(self, event=None):
        # process the data
        self.result = {
            'host': self.e1.get(),
            'port': int(self.e2.get()),
            'username': self.e3.get(),
            'password': self.e4.get()
        }
        self.withdraw()
        self.update_idletasks()
        self.parent.focus_set()  # Put focus back to the parent window
        self.destroy()

    def on_cancel(self, event=None):
        # put focus back to the parent window
        self.result = None
        self.parent.focus_set()
        self.destroy()



# SSH Configuration
ssh_config = {
    'hostname': '',
    'port': 22,
    'username': '',
    'password': ''
}

# Terminal UI Configuration
ui_config = {
    'wrap': "none",
    'bg': "black",
    'fg': "white",
    'font_size': 12
}

# Log File Configuration
log_file = "ssh_session.log"

def run():
    root = tkinter.Tk()
    sv_ttk.set_theme("dark")

    # Calculate x and y coordinates for the Tk root window
    ws = root.winfo_screenwidth()  # Width of the screen
    hs = root.winfo_screenheight()  # Height of the screen

    w = 900  # Width for the window
    h = 600  # Height for the window

    # Calculate x, y coordinates
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)

    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    # root = ThemedTk(theme="adapta")
    root.title("SSH Terminal Emulator")

    app = App(root, ssh_config, ui_config, log_file)
    app.pack(expand=True, fill="both")

    root.mainloop()


# Create and run the application
if __name__ == "__main__":
    # root = ThemedTk(theme="itft1")
    # root = ThemedTk(theme="equilux")
    run()

