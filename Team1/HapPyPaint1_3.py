"""
Revision: 1.3.0
Changelog:
- Replaced color buttons with a custom 8-segment Color Wheel.
- Implemented RGB (Red, Green, Blue) + CMYK (Cyan, Magenta, Yellow, Black) selection.
- Refined UI layout to keep the Color Wheel and Indicator grouped.
- Maintained Undo/Redo and Save/Load stability.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import math

class HappyPaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hap.Py Paint :)")
        self.root.geometry("1000x850")
        self.root.configure(bg="#C0C0C0")

        # --- Application State ---
        self.pen_color = "black"
        self.pen_width = 3
        self.last_x, self.last_y = None, None
        
        self.canvas_size = 512
        self.image = Image.new("RGB", (self.canvas_size, self.canvas_size), "white")
        self.draw = ImageDraw.Draw(self.image)
        
        self.undo_stack = []
        self.redo_stack = []
        self.save_state()

        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        """Creates the layout with the new Color Wheel widget."""
        
        # 1. Top Control Bar
        self.toolbar = tk.Frame(self.root, bg="#C0C0C0", bd=2, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.title_box = tk.Label(
            self.toolbar, text="Hap.Py Paint :)", 
            fg="yellow", bg="black", font=("Comic Sans MS", 16, "bold"),
            padx=10, pady=5
        )
        self.title_box.pack(side=tk.LEFT, padx=20, pady=10)

        # File & History Frames
        self.create_group(self.toolbar, "File", [("Save", self.save_file), ("Load", self.load_file)])
        self.create_group(self.toolbar, "History", [("Undo", self.undo), ("Redo", self.redo)])

        # --- NEW: Color Wheel Section ---
        self.color_section = tk.LabelFrame(self.toolbar, text="Color Picker", bg="#C0C0C0")
        self.color_section.pack(side=tk.LEFT, padx=10, pady=5)

        # Draw the Wheel
        self.wheel_canvas = tk.Canvas(self.color_section, width=80, height=80, bg="#C0C0C0", highlightthickness=0)
        self.wheel_canvas.pack(side=tk.LEFT, padx=5)
        self.draw_color_wheel()
        self.wheel_canvas.bind("<Button-1>", self.handle_wheel_click)

        # Active Color Feedback
        self.indicator_frame = tk.Frame(self.color_section, bg="#C0C0C0")
        self.indicator_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(self.indicator_frame, text="Active", bg="#C0C0C0", font=("Arial", 7)).pack()
        self.color_indicator = tk.Canvas(self.indicator_frame, width=30, height=30, bg="#C0C0C0", highlightthickness=0)
        self.color_indicator.pack()
        self.update_indicator()

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
        self.canvas_container = tk.Frame(self.root, bg="#808080", bd=5, relief=tk.SUNKEN)
        self.canvas_container.pack(expand=True, pady=20)
        self.canvas = tk.Canvas(self.canvas_container, bg="white", width=self.canvas_size, height=self.canvas_size, highlightthickness=0)
        self.canvas.pack()

    def create_group(self, parent, text, buttons):
        frame = tk.LabelFrame(parent, text=text, bg="#C0C0C0")
        frame.pack(side=tk.LEFT, padx=5)
        for txt, cmd in buttons:
            tk.Button(frame, text=txt, command=cmd).pack(side=tk.LEFT, padx=2)

    # --- Color Wheel Logic ---
    def draw_color_wheel(self):
        """Draws 8 wedges for RGB and CMYK colors."""
        # Colors arranged in a common color-theory order
        self.wheel_colors = [
            "red", "orange", "yellow", "green", 
            "cyan", "blue", "magenta", "black"
        ]
        angle = 360 / len(self.wheel_colors)
        for i, col in enumerate(self.wheel_colors):
            start = i * angle
            # Create an arc for each color
            self.wheel_canvas.create_arc(
                5, 5, 75, 75, start=start, extent=angle, 
                fill=col, outline="white", tags=col
            )

    def handle_wheel_click(self, event):
        """Determines which color was clicked based on canvas tags."""
        item = self.wheel_canvas.find_closest(event.x, event.y)
        tags = self.wheel_canvas.gettags(item)
        if tags:
            self.set_color(tags[0])

    def set_color(self, new_color):
        self.pen_color = new_color
        self.update_indicator()

    def update_indicator(self):
        self.color_indicator.delete("all")
        self.color_indicator.create_oval(3, 3, 27, 27, fill=self.pen_color, outline="black", width=2)

    # --- Drawing Logic ---
    def setup_bindings(self):
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def set_width(self, val):
        self.pen_width = int(val)

    def paint(self, event):
        if self.last_x and self.last_y:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                    width=self.pen_width, fill=self.pen_color,
                                    capstyle=tk.ROUND, smooth=tk.TRUE)
            self.draw.line([self.last_x, self.last_y, event.x, event.y],
                           fill=self.pen_color, width=self.pen_width)
        self.last_x, self.last_y = event.x, event.y

    def on_release(self, event):
        self.last_x, self.last_y = None, None
        self.save_state()
        self.redo_stack.clear()

    def save_state(self):
        self.undo_stack.append(self.image.copy())
        if len(self.undo_stack) > 21: self.undo_stack.pop(0)

    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.image = self.undo_stack[-1].copy()
            self.draw = ImageDraw.Draw(self.image)
            self.refresh_canvas()

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.image = state.copy()
            self.draw = ImageDraw.Draw(self.image)
            self.refresh_canvas()

    def refresh_canvas(self):
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def clear_all(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.canvas_size, self.canvas_size), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.save_state()

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path: self.image.save(file_path)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg")])
        if file_path:
            loaded_img = Image.open(file_path).convert("RGB").resize((self.canvas_size, self.canvas_size))
            self.image = loaded_img
            self.draw = ImageDraw.Draw(self.image)
            self.refresh_canvas()
            self.save_state()

if __name__ == "__main__":
    root = tk.Tk()
    app = HappyPaintApp(root)
    root.mainloop()