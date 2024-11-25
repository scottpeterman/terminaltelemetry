# device_discovery_gui2.py
import os
import re
import tkinter as tk
from tkinter import ttk
import threading
from typing import Optional, Dict, Any, List

from PIL import ImageTk, Image

from device_discovery import DeviceDiscovery
from test_discovery2 import NetworkMapper


class MapViewer(tk.Toplevel):
    """Large map viewer window with zoom capabilities"""

    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.title("Network Map Viewer")

        # Make window fullscreen
        self.state('zoomed')

        # Main container frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure the main frame grid
        main_frame.grid_rowconfigure(0, weight=1)  # Canvas row expands
        main_frame.grid_columnconfigure(0, weight=1)  # Canvas column expands

        # Create canvas with scrollbars
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(canvas_frame, bg='#1A1A1A', highlightthickness=0)
        h_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)

        # Configure canvas scrolling
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        # Grid layout for canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")

        # Configure canvas frame grid
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Add control frame at the bottom
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        # Center the buttons in the control frame
        control_frame.grid_columnconfigure(0, weight=1)  # Left padding
        control_frame.grid_columnconfigure(5, weight=1)  # Right padding

        # Style for larger buttons
        style = ttk.Style()
        style.configure('Map.TButton', padding=(10, 5))

        # Add buttons with more padding and centered
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=0, column=1, columnspan=3)

        ttk.Button(btn_frame, text="Zoom In", style='Map.TButton',
                   command=self.zoom_in).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Zoom Out", style='Map.TButton',
                   command=self.zoom_out).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Reset", style='Map.TButton',
                   command=self.reset_zoom).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Exit Fullscreen", style='Map.TButton',
                   command=self.toggle_fullscreen).pack(side=tk.LEFT, padx=10)

        # Load and display image
        self.original_image = Image.open(image_path)
        self.setup_initial_image()

        # Bind mouse wheel to zoom
        self.canvas.bind('<Control-MouseWheel>', self.mouse_wheel_zoom)

        # Bind escape key to exit fullscreen
        self.bind('<Escape>', lambda e: self.toggle_fullscreen())
        # self.reset_zoom()


        self.is_fullscreen = True

    def setup_initial_image(self):
        """Set up the initial image with proper sizing"""
        # Get the available canvas space
        screen_width = self.winfo_screenwidth() * 0.85
        screen_height = (self.winfo_screenheight() - 150) * 0.85  # Reduced height for controls

        # Calculate the aspect ratio of the original image
        image_aspect = self.original_image.width / self.original_image.height

        # Calculate maximum dimensions that maintain aspect ratio
        if (screen_width / screen_height) > image_aspect:
            # Screen is wider than image aspect - fit to height
            target_height = screen_height
            target_width = screen_height * image_aspect
        else:
            # Screen is taller than image aspect - fit to width
            target_width = screen_width
            target_height = screen_width / image_aspect

        # Apply scaling factor but maintain aspect ratio
        scale_factor = 3 # Reduced from 2.5 for better initial view
        new_width = int(target_width * scale_factor)
        new_height = int(target_height * scale_factor)

        # Resize image
        resized_image = self.original_image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )
        self.photo = ImageTk.PhotoImage(resized_image)

        # Calculate center position
        canvas_width = self.winfo_screenwidth()
        canvas_height = self.winfo_screenheight() - 150
        x_pos = max(0, (canvas_width - new_width) // 2)
        y_pos = max(0, (canvas_height - new_height) // 2)

        # Create image on canvas
        self.image_item = self.canvas.create_image(
            x_pos, y_pos,
            anchor="nw",
            image=self.photo
        )

        # Set the scroll region with padding
        padding = 100  # Reduced padding
        self.canvas.configure(scrollregion=(
            -padding + x_pos,
            -padding + y_pos,
            new_width + padding + x_pos,
            new_height + padding + y_pos
        ))

        # Center the view
        self.canvas.xview_moveto(0.5)
        self.canvas.yview_moveto(0.5)

    def mouse_wheel_zoom(self, event):
        """Handle mouse wheel zooming with Control key"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def update_zoom(self):
        """Update the image with the current zoom level"""
        # Get the available canvas space
        screen_width = self.winfo_screenwidth() * 0.85
        screen_height = (self.winfo_screenheight() - 150) * 0.85

        # Calculate the aspect ratio of the original image
        image_aspect = self.original_image.width / self.original_image.height

        # Calculate maximum dimensions that maintain aspect ratio
        if (screen_width / screen_height) > image_aspect:
            target_height = screen_height * 1.3
            target_width = screen_height * image_aspect * 1.3
        else:
            target_width = screen_width
            target_height = screen_width / image_aspect

        # Apply scaling factor and zoom level
        scale_factor = 1.5  # Match initial scale factor
        new_width = int(target_width * scale_factor * self.zoom_level)
        new_height = int(target_height * scale_factor * self.zoom_level)

        # Get current view center
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Resize image
        resized_image = self.original_image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )
        self.photo = ImageTk.PhotoImage(resized_image)

        # Update canvas
        self.canvas.delete(self.image_item)

        x_pos = (canvas_width - new_width) // 2
        y_pos = (canvas_height - new_height) // 2

        self.image_item = self.canvas.create_image(
            x_pos, y_pos,
            anchor="nw",
            image=self.photo
        )

        # Update scroll region with padding
        padding = 100
        self.canvas.configure(scrollregion=(
            -padding + x_pos,
            -padding + y_pos,
            new_width + padding + x_pos,
            new_height + padding + y_pos
        ))

    def toggle_fullscreen(self):
        """Toggle fullscreen state"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.state('zoomed')
        else:
            self.state('normal')
            self.geometry('800x600')

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.update_zoom()

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.update_zoom()

    def reset_zoom(self):
        self.zoom_level = 1.0
        self.update_zoom()

class DiscoveryOutput(ttk.Frame):
    """Right panel showing discovery results with enhanced styling"""

    def __init__(self, parent):
        super().__init__(parent)

        # Header with discover button
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=5, pady=2)

        self.discover_btn = ttk.Button(
            header_frame,
            text="🔍 Discover",
            width=15
        )
        self.discover_btn.pack(side='left')

        self.status_label = ttk.Label(header_frame, text="")
        self.status_label.pack(side='left', padx=5)

        # Results text area with enhanced styling
        self.text_area = tk.Text(
            self,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            font=('Consolas', 10),
            bg='#1e1e1e',  # Dark background
            fg='#d4d4d4',  # Light text
            insertbackground='white',
            width=40
        )
        self.text_area.pack(expand=True, fill='both', padx=5, pady=5)

        # Configure text tags for colored output
        self.text_area.tag_configure('header',
                                     font=('Consolas', 11, 'bold'),
                                     foreground='#569CD6'  # Bright blue
                                     )
        self.text_area.tag_configure('value',
                                     foreground='#4EC9B0'  # Bright teal
                                     )
        self.text_area.tag_configure('field',
                                     foreground='#9CDCFE'  # Light blue
                                     )
        self.text_area.tag_configure('section',
                                     font=('Consolas', 10, 'bold'),
                                     foreground='#CE9178'  # Orange
                                     )
        self.text_area.tag_configure('success',
                                     foreground='#4EC9B0'  # Bright teal
                                     )
        self.text_area.tag_configure('error',
                                     foreground='#F14C4C'  # Bright red
                                     )

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_area.yview)

    def insert_field(self, name: str, value: str):
        """Insert a field-value pair with proper styling"""
        self.text_area.insert('end', f"{name}: ", 'field')
        self.text_area.insert('end', f"{value}\n", 'value')

    def update_content(self, content: Dict):
        """Updates the text area with styled content"""
        self.text_area.delete(1.0, tk.END)

        # Device info header
        self.text_area.insert('end', "Device Information\n", 'header')
        self.text_area.insert('end', "─" * 40 + "\n", 'field')
        self.insert_field("Device Type", content['device_type'])
        self.insert_field("Confidence", f"{content['confidence_score']:.1f}%")
        self.insert_field("Template", content['template'])
        self.insert_field("Processing Time", f"{content['processing_time']:.2f}s")

        # Parsed data section
        self.text_area.insert('end', "\nParsed Data\n", 'section')
        self.text_area.insert('end', "─" * 40 + "\n", 'field')

        for key, value in content['parsed_data'].items():
            if value:  # Only show non-empty values
                self.insert_field(f"  {key}", value)

    def update_status(self, status: str, success: bool = True):
        """Updates the status label with colored status"""
        tag = 'success' if success else 'error'
        self.status_label.configure(
            text=status,
            foreground='#4EC9B0' if success else '#F14C4C'
        )

    def show_error(self, error_msg: str):
        """Display error message with styling"""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert('end', "Error During Discovery\n", 'header')
        self.text_area.insert('end', "─" * 40 + "\n", 'field')
        self.text_area.insert('end', f"\n{error_msg}\n", 'error')


class DiscoveryFrame(ttk.Frame):
    """Frame containing the split terminal, discovery view, and map display"""

    def __init__(self, parent, ssh_config, terminal_class, **kwargs):
        super().__init__(parent)
        self.ssh_config = ssh_config
        self.output_dir = "network_maps"
        self.mapper = NetworkMapper(ssh_config=self.ssh_config, output_dir=self.output_dir, verbose=True)

        # Create horizontal paned window
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(expand=True, fill='both')

        # Left side: Terminal container frame
        terminal_frame = ttk.Frame(self.paned)

        # Right side: Vertical panel for discovery results and map
        right_panel = ttk.Frame(self.paned)
        right_panel.columnconfigure(0, weight=1)
        # Equal weights for both sections
        right_panel.rowconfigure(0, weight=1)  # Discovery output
        right_panel.rowconfigure(1, weight=1)  # Map section

        # Discovery results (top-right)
        self.discovery_output = DiscoveryOutput(right_panel)
        self.discovery_output.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Map display with scrollbars (bottom-right)
        self.map_frame = ttk.Frame(right_panel)
        self.map_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Create canvas and scrollbars for map
        self.map_canvas = tk.Canvas(self.map_frame, bg='#1A1A1A', highlightthickness=0)
        h_scrollbar = ttk.Scrollbar(self.map_frame, orient="horizontal", command=self.map_canvas.xview)
        v_scrollbar = ttk.Scrollbar(self.map_frame, orient="vertical", command=self.map_canvas.yview)

        # Configure canvas scrolling
        self.map_canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # Grid layout for scrollable view
        self.map_canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure map frame grid weights
        self.map_frame.grid_rowconfigure(0, weight=1)
        self.map_frame.grid_columnconfigure(0, weight=1)

        # Create label inside canvas for the map
        self.image_label = ttk.Label(self.map_canvas, text="Map will be displayed here after discovery.")
        self.map_canvas.create_window((0, 0), window=self.image_label, anchor="nw")

        # Add the main panels to the paned window
        self.paned.add(terminal_frame, weight=3)
        self.paned.add(right_panel, weight=2)

        # Create terminal in its container
        self.terminal = terminal_class(terminal_frame, ssh_config=ssh_config, **kwargs)
        self.terminal.pack(expand=True, fill='both')

        # Connect discover button to action
        self.discovery_output.discover_btn.configure(command=self.start_discovery)

        # Configure initial sash position
        self.after(100, self._set_initial_sash_position)
    def _set_initial_sash_position(self):
        """Set the initial position of the sash to give the terminal more width"""
        total_width = self.winfo_width()
        if total_width > 1:
            sash_position = int(total_width * 0.6)
            try:
                self.paned.sashpos(0, sash_position)
            except:
                pass


    def start_discovery(self):
        """Start discovery process using current session credentials"""
        self.discovery_output.discover_btn.configure(state='disabled')
        self.discovery_output.update_status("Discovery in progress...")

        # Start discovery in a thread
        discovery_thread = threading.Thread(
            target=self.run_discovery,
            daemon=True
        )
        discovery_thread.start()

    def run_discovery(self):
        """Runs the discovery and mapping process for this tab."""
        try:
            # Perform device discovery
            discovery = DeviceDiscovery('tfsm_templates.db', verbose=True)

            fingerprint = discovery.process_device(
                host=self.ssh_config['hostname'],
                username=self.ssh_config['username'],
                password=self.ssh_config['password'],
                ssh_timeout=60
            )
            # In run_discovery() after getting the fingerprint:
            if fingerprint:
                # Update discovery results
                self.after(100, self.update_results, fingerprint)

                # Only generate map if it's not a Linux system
                if fingerprint.device_type.lower() != 'linux':
                    map_image_path = self.mapper.create_network_map(max_hops=2)
                    self.after(100, self.update_map)
                else:
                    # Update the map area with a message for Linux systems
                    self.after(100, lambda: self.image_label.configure(
                        text="Network mapping not available for Linux systems"
                    ))
        except Exception as e:
            self.after(100, self.update_error, str(e))
        finally:
            self.after(100, lambda: self.discovery_output.discover_btn.configure(state='normal'))

    def update_results(self, fingerprint):
        """Updates discovery output with fingerprint data"""
        if fingerprint:
            content = {
                'device_type': fingerprint.device_type,
                'confidence_score': fingerprint.confidence_score,
                'template': fingerprint.template_name,
                'processing_time': fingerprint.processing_time,
                'parsed_data': fingerprint.parsed_data[0] if fingerprint.parsed_data else {}
            }
            self.discovery_output.update_content(content)
            self.discovery_output.update_status(
                f"✓ {fingerprint.device_type} ({fingerprint.confidence_score:.0f}% match)",
                True
            )
        else:
            self.discovery_output.show_error("No device match found")
            self.discovery_output.update_status("✗ No match found", False)

    def update_map(self):
        """Load and display the generated map image."""
        try:
            from focused_network_map import create_standard_filename

            hostname = self.ssh_config.get('resolved_hostname', self.ssh_config['hostname'])
            self.map_image_path = os.path.join(  # Store path as instance variable
                self.output_dir,
                create_standard_filename(
                    map_name='network_topology',
                    start_node=hostname,
                    max_hops=2,
                    layout_type='circular'
                )
            )

            if not os.path.exists(self.map_image_path):
                raise FileNotFoundError(f"Map file not found: {self.map_image_path}")

            # Load and resize the image
            image = Image.open(self.map_image_path)
            # Set a larger display size
            display_width = 200
            aspect_ratio = image.size[1] / image.size[0]
            display_height = int(display_width * aspect_ratio)

            image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)
            self.map_image = ImageTk.PhotoImage(image)

            # Update image and configure scrollregion
            self.image_label.configure(image=self.map_image, text="")
            self.map_canvas.configure(scrollregion=self.map_canvas.bbox("all"))

            # Bind click event to the label
            self.image_label.bind('<Button-1>', self.open_map_viewer)

            # Add a visual hint that the map is clickable
            self.image_label.configure(cursor="hand2")

            # Center the image in the canvas
            canvas_width = self.map_canvas.winfo_width()
            canvas_height = self.map_canvas.winfo_height()
            x = max(0, (canvas_width - display_width) // 2)
            y = max(0, (canvas_height - display_height) // 2)
            self.map_canvas.coords(self.map_canvas.find_all()[0], x, y)

        except Exception as e:
            print(f"Error loading map image: {e}")
            self.image_label.configure(text="Error: Map image could not be loaded.")

    def open_map_viewer(self, event=None):
        """Open the large map viewer window"""
        if hasattr(self, 'map_image_path'):
            viewer = MapViewer(self, self.map_image_path)
            viewer.focus()  # Bring the viewer window to front
    def update_error(self, error_msg: str):
        """Updates discovery output with error message"""
        self.discovery_output.show_error(error_msg)
        self.discovery_output.update_status("✗ Discovery failed", False)
