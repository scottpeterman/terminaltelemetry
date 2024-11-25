import tkinter as tk
from tkinter import ttk
import textfsm


class TextFSMTester(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("TextFSM Template Tester")
        self.configure(bg='#2b2b2b')

        # Make window open maximized
        self.state('zoomed')

        # Main container to hold everything
        main_container = tk.Frame(self, bg='#2b2b2b')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Create main layout frames
        top_frame = tk.Frame(main_container, bg='#2b2b2b')
        top_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        button_frame = tk.Frame(main_container, bg='#2b2b2b', height=50)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        # Prevent button_frame from being compressed
        button_frame.pack_propagate(False)

        # Create and configure the text widgets
        # Source Text (top left)
        source_label = tk.Label(top_frame, text="Source", bg='#2b2b2b', fg='white')
        source_label.grid(row=0, column=0, sticky='w', padx=5)

        self.source_text = tk.Text(top_frame, height=15, width=50, bg='#1e1e1e', fg='white',
                                   insertbackground='white')
        self.source_text.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        # Template Text (bottom left)
        template_label = tk.Label(top_frame, text="Template", bg='#2b2b2b', fg='white')
        template_label.grid(row=2, column=0, sticky='w', padx=5)

        self.template_text = tk.Text(top_frame, height=15, width=50, bg='#1e1e1e', fg='white',
                                     insertbackground='white')
        self.template_text.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        # Result Text (right side)
        result_label = tk.Label(top_frame, text="Result", bg='#2b2b2b', fg='white')
        result_label.grid(row=0, column=1, sticky='w', padx=5)

        self.result_text = tk.Text(top_frame, height=31, width=50, bg='#1e1e1e', fg='white',
                                   insertbackground='white')
        self.result_text.grid(row=1, column=1, rowspan=3, padx=5, pady=5, sticky='nsew')

        # Configure grid weights for top_frame
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_rowconfigure(1, weight=1)
        top_frame.grid_rowconfigure(3, weight=1)

        # Create buttons
        render_btn = ttk.Button(button_frame, text="Render", command=self.render_template)
        render_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)

        example_btn = ttk.Button(button_frame, text="Example", command=self.load_example)
        example_btn.pack(side=tk.LEFT, padx=5)

    def render_template(self):
        try:
            # Get the template and source text
            template_text = self.template_text.get("1.0", tk.END)
            source_text = self.source_text.get("1.0", tk.END)

            # Create a temporary file for the template
            with open("temp_template.textfsm", "w") as f:
                f.write(template_text)

            # Parse with TextFSM
            with open("temp_template.textfsm") as f:
                template = textfsm.TextFSM(f)
                result = template.ParseText(source_text)

            # Format and display results
            self.result_text.delete("1.0", tk.END)
            header = template.header
            self.result_text.insert(tk.END, f"Header: {header}\n\nResults:\n")

            for row in result:
                self.result_text.insert(tk.END, f"{row}\n")

        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Error: {str(e)}")

    def clear_all(self):
        self.source_text.delete("1.0", tk.END)
        self.template_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)

    def load_example(self):
        example_source = """Interface                  IP-Address      OK? Method Status                Protocol
FastEthernet0/0            192.168.1.1    YES NVRAM  up                    up      
FastEthernet0/1            unassigned     YES NVRAM  administratively down down    
Loopback0                  1.1.1.1        YES NVRAM  up                    up"""

        example_template = """Value Interface (\S+)
Value IP_Address (\S+)
Value OK (\S+)
Value Method (\S+)
Value Status (.+?)
Value Protocol (\S+)

Start
  ^${Interface}\s+${IP_Address}\s+${OK}\s+${Method}\s+${Status}\s+${Protocol}\s*$$ -> Record"""

        self.source_text.delete("1.0", tk.END)
        self.template_text.delete("1.0", tk.END)

        self.source_text.insert("1.0", example_source)
        self.template_text.insert("1.0", example_template)


if __name__ == "__main__":
    app = TextFSMTester()
    app.mainloop()