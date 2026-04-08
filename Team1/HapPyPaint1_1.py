"""
Revision: 1.1.0
Changelog:
- Fixed canvas size to 512x512 for consistency.
- Added Save functionality (exports canvas to PNG).
- Added Load functionality (imports PNG to canvas).
- Integrated PIL (Pillow) for image processing.
- Added scrollbars (optional) or centered framing for the fixed canvas.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

class HappyPaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hap.Py Paint :)")
        self.root.geometry("900x750")
        self.root.configure(bg="#C0C0C0")

        # --- Application State ---
        self.pen_color = "black"
        self.pen_width = 3
        self.last_x, self.last_y = None, None
        
        # Internal PIL image for saving/loading
        self.canvas_size = 512
        self.image = Image.new("RGB", (self.canvas_size, self.canvas_size), "white")
        self.draw = ImageDraw.Draw(self.image)
        
        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        """Creates the layout with fixed canvas and new file operations."""
        
        # 1. Top Control Bar
        self.toolbar = tk.Frame(self.root, bg="#C0C0C0", bd=2, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.title_box = tk.Label(
            self.toolbar, text="Hap.Py Paint :)", 
            fg="yellow", bg="black", font=("Comic Sans MS", 16, "bold"),
            padx=10, pady=5
        )
        self.title_box.pack(side=tk.LEFT, padx=20, pady=10)

        # File Operations
        self.file_frame = tk.LabelFrame(self.toolbar, text="File", bg="#C0C0C0")
        self.file_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Button(self.file_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        tk.Button(self.file_frame, text="Load", command=self.load_file).pack(side=tk.LEFT, padx=2)

        # Color Selection
        self.color_frame = tk.LabelFrame(self.toolbar, text="Colors", bg="#C0C0C0")
        self.color_frame.pack(side=tk.LEFT, padx=10)

        for col in ["black", "red", "green", "blue"]:
            tk.Button(self.color_frame, bg=col, width=3, command=lambda c=col: self.set_color(c)).pack(side=tk.LEFT, padx=2)

        # Brush Width
        self.width_frame = tk.LabelFrame(self.toolbar, text="Width", bg="#C0C0C0")
        self.width_frame.pack(side=tk.LEFT, padx=10)
        self.width_slider = tk.Scale(self.width_frame, from_=1, to=20, orient=tk.HORIZONTAL, command=self.set_width)
        self.width_slider.set(self.pen_width)
        self.width_slider.pack(padx=5)

        # Utilities
        self.util_frame = tk.LabelFrame(self.toolbar, text="Tools", bg="#C0C0C0")
        self.util_frame.pack(side=tk.LEFT, padx=10)
        tk.Button(self.util_frame, text="Eraser", command=lambda: self.set_color("white")).pack(side=tk.LEFT, padx=2)
        tk.Button(self.util_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=2)

        # 2. Fixed Size Canvas
        # Centering the canvas in the window
        self.canvas_container = tk.Frame(self.root, bg="#808080", bd=5, relief=tk.SUNKEN)
        self.canvas_container.pack(expand=True)

        self.canvas = tk.Canvas(
            self.canvas_container, 
            bg="white", 
            width=self.canvas_size, 
            height=self.canvas_size, 
            highlightthickness=0
        )
        self.canvas.pack()

    def setup_bindings(self):
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset_coords)

    def set_color(self, new_color):
        self.pen_color = new_color

    def set_width(self, val):
        self.pen_width = int(val)

    def paint(self, event):
        if self.last_x and self.last_y:
            # Draw on Tkinter UI
            self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                width=self.pen_width, fill=self.pen_color,
                capstyle=tk.ROUND, smooth=tk.TRUE
            )
            # Synchronize with internal PIL image for saving
            self.draw.line(
                [self.last_x, self.last_y, event.x, event.y],
                fill=self.pen_color, width=self.pen_width
            )
        self.last_x, self.last_y = event.x, event.y

    def reset_coords(self, event):
        self.last_x, self.last_y = None, None

    def clear_all(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.canvas_size, self.canvas_size), "white")
        self.draw = ImageDraw.Draw(self.image)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.image.save(file_path)
            messagebox.showinfo("Success", "Image saved successfully!")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            # Open and resize to fit our 512x512 standard
            loaded_img = Image.open(file_path).convert("RGB").resize((self.canvas_size, self.canvas_size))
            self.image = loaded_img
            self.draw = ImageDraw.Draw(self.image)
            
            # Update the UI
            self.tk_image = ImageTk.PhotoImage(loaded_img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = HappyPaintApp(root)
    root.mainloop()