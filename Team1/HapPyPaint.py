"""
Revision: 1.0.0
Changelog:
- Initial release of Hap.Py Paint foundation.
- Added canvas drawing with mouse tracking.
- Implemented Red, Green, Blue, and Black color selection.
- Added pen width slider and 'Clear All' functionality.
- Implemented selected color visual feedback.
- Ensured window and canvas are fully resizable.
"""

import tkinter as tk
from tkinter import colorchooser

class HappyPaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hap.Py Paint :)")
        self.root.geometry("900x600")
        self.root.configure(bg="#C0C0C0") # Classic grey background

        # --- Application State ---
        self.pen_color = "black"
        self.eraser_color = "white"
        self.pen_width = 3
        self.last_x, self.last_y = None, None
        
        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        """Creates the layout hierarchy: Top bar for controls and main canvas."""
        
        # 1. Top Control Bar (Toolbar)
        self.toolbar = tk.Frame(self.root, bg="#C0C0C0", height=100, bd=2, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Title Label (Hap.Py Paint :)
        self.title_box = tk.Label(
            self.toolbar, text="Hap.Py Paint :)", 
            fg="yellow", bg="black", 
            font=("Comic Sans MS", 16, "bold"),
            padx=10, pady=5
        )
        self.title_box.pack(side=tk.LEFT, padx=20, pady=10)

        # Color Selection Frame
        self.color_frame = tk.LabelFrame(self.toolbar, text="Colors", bg="#C0C0C0")
        self.color_frame.pack(side=tk.LEFT, padx=10)

        colors = ["black", "red", "green", "blue"]
        self.color_buttons = {}
        for col in colors:
            btn = tk.Button(
                self.color_frame, bg=col, width=3, height=1,
                command=lambda c=col: self.set_color(c)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.color_buttons[col] = btn

        # Feedback Label (Current Color)
        self.status_label = tk.Label(self.toolbar, text="Selected:", bg="#C0C0C0")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        self.color_indicator = tk.Canvas(self.toolbar, width=20, height=20, highlightthickness=1, highlightbackground="black")
        self.color_indicator.pack(side=tk.LEFT, padx=5)
        self.update_indicator()

        # Brush Width Controls
        self.width_frame = tk.LabelFrame(self.toolbar, text="Pen Width", bg="#C0C0C0")
        self.width_frame.pack(side=tk.LEFT, padx=10)
        
        self.width_slider = tk.Scale(self.width_frame, from_=1, to=20, orient=tk.HORIZONTAL, command=self.set_width)
        self.width_slider.set(self.pen_width)
        self.width_slider.pack(padx=5)

        # Utilities (Eraser / Clear)
        self.util_frame = tk.LabelFrame(self.toolbar, text="Tools", bg="#C0C0C0")
        self.util_frame.pack(side=tk.LEFT, padx=10)

        self.erase_btn = tk.Button(self.util_frame, text="Eraser", command=lambda: self.set_color("white"))
        self.erase_btn.pack(side=tk.LEFT, padx=2)

        self.clear_btn = tk.Button(self.util_frame, text="Clear Canvas", command=self.clear_all, fg="darkred")
        self.clear_btn.pack(side=tk.LEFT, padx=2)

        # 2. The Drawing Canvas
        # We put the canvas in a frame to manage padding and resizing effectively
        self.canvas_container = tk.Frame(self.root, bg="#C0C0C0")
        self.canvas_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas = tk.Canvas(self.canvas_container, bg="white", bd=3, relief=tk.SUNKEN, cursor="pencil")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def setup_bindings(self):
        """Connects mouse events to drawing functions."""
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset_coords)

    def set_color(self, new_color):
        self.pen_color = new_color
        self.update_indicator()

    def set_width(self, val):
        self.pen_width = val

    def update_indicator(self):
        """Visually shows the user which color is active."""
        self.color_indicator.delete("all")
        self.color_indicator.create_rectangle(0, 0, 22, 22, fill=self.pen_color)

    def paint(self, event):
        """Calculates and draws a line from the previous mouse position to the current one."""
        if self.last_x and self.last_y:
            self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                width=self.pen_width, fill=self.pen_color,
                capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36
            )
        self.last_x = event.x
        self.last_y = event.y

    def reset_coords(self, event):
        """Resets coords so drawing doesn't 'jump' when clicking in a new spot."""
        self.last_x, self.last_y = None, None

    def clear_all(self):
        """Wipes the canvas clean."""
        self.canvas.delete("all")

if __name__ == "__main__":
    root = tk.Tk()
    app = HappyPaintApp(root)
    root.mainloop()