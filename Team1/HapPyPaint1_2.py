"""
Revision: 1.2.0
Changelog:
- Restored color feedback indicator.
- Implemented Undo and Redo functionality using state stacks.
- Optimized canvas state management for 512x512 consistency.
- Added visual 'pressed' state logic for tool selection.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

class HappyPaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hap.Py Paint :)")
        self.root.geometry("950x800")
        self.root.configure(bg="#C0C0C0")

        # --- Application State ---
        self.pen_color = "black"
        self.pen_width = 3
        self.last_x, self.last_y = None, None
        
        self.canvas_size = 512
        self.image = Image.new("RGB", (self.canvas_size, self.canvas_size), "white")
        self.draw = ImageDraw.Draw(self.image)
        
        # Undo/Redo Stacks (Storing PIL Image copies)
        self.undo_stack = []
        self.redo_stack = []
        # Save initial blank state
        self.save_state()

        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        """Creates the layout with restored indicators and new Undo/Redo buttons."""
        
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
        self.file_frame.pack(side=tk.LEFT, padx=5)
        tk.Button(self.file_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        tk.Button(self.file_frame, text="Load", command=self.load_file).pack(side=tk.LEFT, padx=2)

        # Undo/Redo Operations
        self.history_frame = tk.LabelFrame(self.toolbar, text="History", bg="#C0C0C0")
        self.history_frame.pack(side=tk.LEFT, padx=5)
        tk.Button(self.history_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=2)
        tk.Button(self.history_frame, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=2)

        # Color Selection
        self.color_frame = tk.LabelFrame(self.toolbar, text="Colors", bg="#C0C0C0")
        self.color_frame.pack(side=tk.LEFT, padx=5)
        for col in ["black", "red", "green", "blue"]:
            tk.Button(self.color_frame, bg=col, width=3, command=lambda c=col: self.set_color(c)).pack(side=tk.LEFT, padx=2)

        # Color Feedback Indicator (The Circle)
        self.indicator_frame = tk.Frame(self.toolbar, bg="#C0C0C0")
        self.indicator_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(self.indicator_frame, text="Active:", bg="#C0C0C0", font=("Arial", 8)).pack()
        self.color_indicator = tk.Canvas(self.indicator_frame, width=25, height=25, bg="#C0C0C0", highlightthickness=0)
        self.color_indicator.pack()
        self.update_indicator()

        # Brush Width
        self.width_frame = tk.LabelFrame(self.toolbar, text="Width", bg="#C0C0C0")
        self.width_frame.pack(side=tk.LEFT, padx=5)
        self.width_slider = tk.Scale(self.width_frame, from_=1, to=20, orient=tk.HORIZONTAL, command=self.set_width)
        self.width_slider.set(self.pen_width)
        self.width_slider.pack(padx=5)

        # Utilities
        self.util_frame = tk.LabelFrame(self.toolbar, text="Tools", bg="#C0C0C0")
        self.util_frame.pack(side=tk.LEFT, padx=5)
        tk.Button(self.util_frame, text="Eraser", command=lambda: self.set_color("white")).pack(side=tk.LEFT, padx=2)
        tk.Button(self.util_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=2)

        # 2. Fixed Size Canvas
        self.canvas_container = tk.Frame(self.root, bg="#808080", bd=5, relief=tk.SUNKEN)
        self.canvas_container.pack(expand=True, pady=20)

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
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def set_color(self, new_color):
        self.pen_color = new_color
        self.update_indicator()

    def update_indicator(self):
        self.color_indicator.delete("all")
        # Draw a nice circle to represent the pen
        self.color_indicator.create_oval(2, 2, 23, 23, fill=self.pen_color, outline="black")

    def set_width(self, val):
        self.pen_width = int(val)

    def paint(self, event):
        if self.last_x and self.last_y:
            self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                width=self.pen_width, fill=self.pen_color,
                capstyle=tk.ROUND, smooth=tk.TRUE
            )
            self.draw.line(
                [self.last_x, self.last_y, event.x, event.y],
                fill=self.pen_color, width=self.pen_width
            )
        self.last_x, self.last_y = event.x, event.y

    def on_release(self, event):
        """When mouse is released, reset coords and save the state for Undo."""
        self.last_x, self.last_y = None, None
        self.save_state()
        self.redo_stack.clear() # New drawing branch invalidates redo history

    def save_state(self):
        """Push current image to undo stack."""
        # We store a copy of the image, not a reference
        self.undo_stack.append(self.image.copy())
        # Limit stack size to 20 to save memory
        if len(self.undo_stack) > 21:
            self.undo_stack.pop(0)

    def undo(self):
        if len(self.undo_stack) > 1:
            # Move current state to redo stack
            self.redo_stack.append(self.undo_stack.pop())
            # Get the previous state
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
        """Syncs the Tkinter Canvas with the current PIL image state."""
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
        if file_path:
            self.image.save(file_path)
            messagebox.showinfo("Success", "Saved to " + file_path)

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