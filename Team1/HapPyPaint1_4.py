"""
Revision: 1.4.0
Changelog:
- Added basic pixelated stamps: Circle, Square, Triangle, and Smiley Face.
- Implemented stamp drawing logic with current color.
- Added "Stamps" toolbar section with buttons.
- Added "Stamp Size" and "Stamp Spacing" sliders.
- Added "Pencil" tool to return to normal drawing.
- Updated UI layout for the new stamp controls.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import math

class HappyPaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hap.Py Paint :)")
        self.root.geometry("1100x850") # Added width for stamp controls
        self.root.configure(bg="#C0C0C0")

        # --- Application State ---
        self.pen_color = "black"
        self.pen_width = 3
        self.last_x, self.last_y = None, None
        
        # New Stamp States
        self.current_stamp = None # None is normal pen mode
        self.stamp_size_scale = 1 # Multiplier for pixel stamp size (e.g., 1x, 2x, etc.)
        self.stamp_spacing = 5 # Minimum pixels between stamps while drawing
        self.last_stamped_x, self.last_stamped_y = None, None

        self.canvas_size = 512
        self.image = Image.new("RGB", (self.canvas_size, self.canvas_size), "white")
        self.draw = ImageDraw.Draw(self.image)
        
        self.undo_stack = []
        self.redo_stack = []
        self.save_state()

        # Define 16x16 Pixel Stamp Masks (0=transparent, 1=solid)
        self.stamp_data = self.load_stamp_masks()

        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        """Creates the layout with the new Stamps widget."""
        
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

        # Color Picker Section
        self.color_section = tk.LabelFrame(self.toolbar, text="Color Picker", bg="#C0C0C0")
        self.color_section.pack(side=tk.LEFT, padx=10, pady=5)
        self.wheel_canvas = tk.Canvas(self.color_section, width=80, height=80, bg="#C0C0C0", highlightthickness=0)
        self.wheel_canvas.pack(side=tk.LEFT, padx=5)
        self.draw_color_wheel()
        self.wheel_canvas.bind("<Button-1>", self.handle_wheel_click)
        self.indicator_frame = tk.Frame(self.color_section, bg="#C0C0C0")
        self.indicator_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(self.indicator_frame, text="Active", bg="#C0C0C0", font=("Arial", 7)).pack()
        self.color_indicator = tk.Canvas(self.indicator_frame, width=30, height=30, bg="#C0C0C0", highlightthickness=0)
        self.color_indicator.pack()
        self.update_indicator()

        # Pen Width (Pencil size)
        self.width_frame = tk.LabelFrame(self.toolbar, text="Pen Size", bg="#C0C0C0")
        self.width_frame.pack(side=tk.LEFT, padx=5)
        self.width_slider = tk.Scale(self.width_frame, from_=1, to=20, orient=tk.HORIZONTAL, command=self.set_width)
        self.width_slider.set(self.pen_width)
        self.width_slider.pack(padx=5)

        # --- NEW: Stamps Section ---
        self.stamp_section = tk.LabelFrame(self.toolbar, text="Stamps", bg="#C0C0C0")
        self.stamp_section.pack(side=tk.LEFT, padx=5, pady=5)

        # Basic Stamp tools
        self.stamp_buttons = {}
        stamp_names = ["Pencil", "Smiley", "Circle", "Square", "Triangle"]
        for name in stamp_names:
            btn = tk.Button(self.stamp_section, text=name, command=lambda n=name: self.set_stamp(n))
            btn.pack(side=tk.LEFT, padx=1)
            self.stamp_buttons[name] = btn
        
        # Depress Pencil by default
        self.stamp_buttons["Pencil"].config(relief=tk.SUNKEN)

        # Stamp Controls
        self.stamp_ctrl_frame = tk.Frame(self.stamp_section, bg="#C0C0C0")
        self.stamp_ctrl_frame.pack(side=tk.LEFT, padx=5)
        
        # Stamp Size slider
        self.size_scale = tk.Scale(self.stamp_ctrl_frame, from_=1, to=5, orient=tk.HORIZONTAL, label="Stamp Size", command=self.set_stamp_size)
        self.size_scale.set(self.stamp_size_scale)
        self.size_scale.pack(padx=2)

        # Stamp Spacing slider
        self.spacing_scale = tk.Scale(self.stamp_ctrl_frame, from_=1, to=50, orient=tk.HORIZONTAL, label="Spacing (px)", command=self.set_stamp_spacing)
        self.spacing_scale.set(self.stamp_spacing)
        self.spacing_scale.pack(padx=2)

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

    # --- Stamp Mask Loading (Hardcoded 16x16 pixel data) ---
    def load_stamp_masks(self):
        """Defines binary pixel masks for initial stamps."""
        # Simple pixelated smiley face data, 16x16, inspired by image_1.png
        # We can define others similarly.
        # This is a bit of a data-entry job. For now, I'll provide a 
        # hardcoded 'Smiley' and make generic shapes in `get_pixelated_mask`.

        # Placeholder: I will define basic shapes with pixelated logic in `paint`.
        # This function can be used to load externally defined masks.
        return {}

    # --- Stamp Logic ---
    def set_stamp(self, stamp_name):
        """Sets the current stamp and updates UI button states."""
        # Deselect all stamp buttons
        for name, btn in self.stamp_buttons.items():
            btn.config(relief=tk.RAISED)

        if stamp_name == "Pencil":
            self.current_stamp = None
        else:
            self.current_stamp = stamp_name
            self.stamp_buttons[stamp_name].config(relief=tk.SUNKEN)

    def set_stamp_size(self, val):
        self.stamp_size_scale = int(val)

    def set_stamp_spacing(self, val):
        self.stamp_spacing = int(val)

    def get_pixelated_mask(self, stamp_name):
        """Generates pixelated masks for initial stamps."""
        mask = Image.new('L', (16, 16), 0)
        mdraw = ImageDraw.Draw(mask)
        if stamp_name == "Circle":
            mdraw.ellipse((1, 1, 14, 14), fill=255, outline=255) # Filled disk
        elif stamp_name == "Square":
            mdraw.rectangle((1, 1, 14, 14), fill=255)
        elif stamp_name == "Triangle":
            mdraw.polygon([(1, 14), (8, 1), (14, 14)], fill=255)
        elif stamp_name == "Smiley":
            # Drawing a simple pixelated smiley directly onto the mask
            mdraw.ellipse((1, 1, 14, 14), fill=255) # base
            mdraw.rectangle((4, 4, 6, 6), fill=0) # Left eye
            mdraw.rectangle((9, 4, 11, 6), fill=0) # Right eye
            # Smile shape (pixel perfect)
            for x, y in [(3, 9), (4, 10), (5, 11), (6, 11), (7, 11), (8, 11), (9, 11), (10, 11), (11, 11), (12, 11), (13, 11), (14, 10), (15, 9)]:
                mask.putpixel((x-1, y), 0) # adjust for data grid
            # This logic can be replaced by external binary data load.
        
        # Scale the mask up for visual "pixelated" effect using NEAREST
        scaled_mask = mask.resize((16 * self.stamp_size_scale, 16 * self.stamp_size_scale), resample=Image.NEAREST)
        return scaled_mask

    # --- Drawing Logic with Stamp Integration ---
    def paint(self, event):
        """Handles drawing for both pencil lines and stamps with current color and spacing."""
        if self.current_stamp:
            # Stamp Drawing Logic (Places individual stamps with spacing)
            if self.last_stamped_x and self.last_stamped_y:
                dx = event.x - self.last_stamped_x
                dy = event.y - self.last_stamped_y
                # Only stamp if the mouse has moved further than the spacing from the last stamp
                if math.hypot(dx, dy) < self.stamp_spacing:
                    return # Skip this stamp placement

            self.last_stamped_x, self.last_stamped_y = event.x, event.y

            # 1. Get and prepare the stamp
            mask = self.get_pixelated_mask(self.current_stamp)
            s_width, s_height = mask.size
            
            # 2. Create a solid colored 'ink' image of the correct size
            stamp_ink = Image.new("RGB", (s_width, s_height), self.pen_color)
            
            # 3. Composite onto our PIL image with the mask
            offset_x = event.x - s_width // 2
            offset_y = event.y - s_height // 2
            # `Image.composite` ensures pixelated scaling is preserved.
            # Using simple paste with mask is often faster for this.
            self.image.paste(stamp_ink, (offset_x, offset_y), mask)
            
            # 4. We cannot update only a portion of the canvas efficiently, so refresh
            self.refresh_canvas()

        else:
            # Normal Pencil Logic (Connects points with lines)
            if self.last_x and self.last_y:
                self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                        width=self.pen_width, fill=self.pen_color,
                                        capstyle=tk.ROUND, smooth=tk.TRUE)
                self.draw.line([self.last_x, self.last_y, event.x, event.y],
                               fill=self.pen_color, width=self.pen_width)
            self.last_x, self.last_y = event.x, event.y

    def on_release(self, event):
        """When mouse is released, reset coords, stamp states, and save for Undo."""
        self.last_x, self.last_y = None, None
        self.last_stamped_x, self.last_stamped_y = None, None # Reset stamp history
        self.save_state()
        self.redo_stack.clear()

    # --- Base Logic ---
    def setup_bindings(self):
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def set_color(self, new_color):
        self.pen_color = new_color
        self.update_indicator()

    def update_indicator(self):
        self.color_indicator.delete("all")
        self.color_indicator.create_oval(3, 3, 27, 27, fill=self.pen_color, outline="black", width=2)

    def draw_color_wheel(self):
        self.wheel_colors = ["red", "orange", "yellow", "green", "cyan", "blue", "magenta", "black"]
        angle = 360 / len(self.wheel_colors)
        for i, col in enumerate(self.wheel_colors):
            start = i * angle
            self.wheel_canvas.create_arc(5, 5, 75, 75, start=start, extent=angle, fill=col, outline="white", tags=col)

    def handle_wheel_click(self, event):
        item = self.wheel_canvas.find_closest(event.x, event.y)
        tags = self.wheel_canvas.gettags(item)
        if tags: self.set_color(tags[0])

    def set_width(self, val):
        self.pen_width = int(val)

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