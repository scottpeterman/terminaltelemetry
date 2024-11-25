import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
import os

class GifMakerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PNG to Animated GIF Converter")
        self.geometry("600x400")
        self.image_list = []
        self.delay = 1000  # Default delay in milliseconds

        # Frame for listbox and buttons
        self.frame = tk.Frame(self)
        self.frame.pack(pady=10)

        # Listbox to display selected files
        self.listbox = tk.Listbox(self.frame, width=50, height=15)
        self.listbox.pack(side=tk.LEFT, padx=10)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # Buttons
        self.add_button = tk.Button(self, text="Add PNG Files", command=self.add_files)
        self.add_button.pack(pady=5)

        self.remove_button = tk.Button(self, text="Remove Selected", command=self.remove_selected)
        self.remove_button.pack(pady=5)

        self.move_up_button = tk.Button(self, text="Move Up", command=self.move_up)
        self.move_up_button.pack(pady=5)

        self.move_down_button = tk.Button(self, text="Move Down", command=self.move_down)
        self.move_down_button.pack(pady=5)

        self.set_delay_button = tk.Button(self, text="Set Delay (ms)", command=self.set_delay)
        self.set_delay_button.pack(pady=5)

        self.convert_button = tk.Button(self, text="Convert to GIF", command=self.convert_to_gif)
        self.convert_button.pack(pady=5)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
        for file in files:
            if file not in self.image_list:
                self.image_list.append(file)
                self.listbox.insert(tk.END, os.path.basename(file))

    def remove_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No item selected.")
            return
        index = selected[0]
        self.image_list.pop(index)
        self.listbox.delete(index)

    def move_up(self):
        selected = self.listbox.curselection()
        if not selected or selected[0] == 0:
            return
        index = selected[0]
        self.image_list[index], self.image_list[index - 1] = self.image_list[index - 1], self.image_list[index]
        self.update_listbox()

    def move_down(self):
        selected = self.listbox.curselection()
        if not selected or selected[0] == len(self.image_list) - 1:
            return
        index = selected[0]
        self.image_list[index], self.image_list[index + 1] = self.image_list[index + 1], self.image_list[index]
        self.update_listbox()

    def set_delay(self):
        delay = simpledialog.askinteger("Set Delay", "Enter delay between frames (ms):", minvalue=100, maxvalue=10000)
        if delay:
            self.delay = delay

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for file in self.image_list:
            self.listbox.insert(tk.END, os.path.basename(file))

    def convert_to_gif(self):
        if not self.image_list:
            messagebox.showwarning("Warning", "No images selected.")
            return
        output_file = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
        if not output_file:
            return

        # Load images
        images = []
        for file in self.image_list:
            img = Image.open(file)
            img = img.convert("RGBA")  # Ensure consistent mode
            images.append(img)

        # Save as animated GIF
        images[0].save(
            output_file,
            save_all=True,
            append_images=images[1:],
            duration=self.delay,
            loop=0
        )

        messagebox.showinfo("Success", f"GIF saved as {output_file}")
        self.preview_gif(output_file)

    def preview_gif(self, gif_file):
        preview = tk.Toplevel(self)
        preview.title("GIF Preview")

        img = Image.open(gif_file)
        frames = []

        try:
            while True:
                frames.append(ImageTk.PhotoImage(img.copy()))
                img.seek(len(frames))  # Go to the next frame
        except EOFError:
            pass

        label = tk.Label(preview)
        label.pack()

        def animate(index=0):
            label.config(image=frames[index])
            self.after(self.delay, animate, (index + 1) % len(frames))

        animate()

if __name__ == "__main__":
    app = GifMakerApp()
    app.mainloop()
