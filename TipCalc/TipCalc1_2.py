"""
Revision: 1.2
Changelog:
- Added comprehensive documentation and comments for beginners.
- Enhanced error handling with a global exception catcher and pop-up alerts.
- Refined the "Real-Time" logic to ensure stability across different OS behaviors.
- Added a "Reset" mechanism for invalid numeric entries.
"""

import tkinter as tk
from tkinter import messagebox  # Used for the pop-up error box
import ttkbootstrap as tb       # The modern styling library
from ttkbootstrap.constants import *

# A 'Class' is a blueprint for our application. 
# It keeps all our functions and data organized in one place.
class BeginnerFriendlyTipCalc:
    def __init__(self, root):
        """
        The __init__ method runs automatically when the program starts.
        'root' is the main window of our application.
        """
        self.root = root
        self.root.title("Modern Tip Calculator")
        self.root.geometry("420x620")

        # --- REACTION VARIABLES ---
        # In Tkinter, we use special variables (StringVar, IntVar) so the 
        # GUI can 'watch' them and react immediately when they change.
        
        # bill_var: Stores what the user types in the Bill box as a String (Text)
        self.bill_var = tk.StringVar(value="")
        
        # tip_percent_var: Stores the tip percentage as an Integer (Whole Number)
        self.tip_percent_var = tk.IntVar(value=15)
        
        # num_diners_var: Stores how many people are splitting the bill
        self.num_diners_var = tk.IntVar(value=1)
        
        # Output Variables: These hold the results we show to the user
        self.tip_amount_var = tk.StringVar(value="$0.00")
        self.total_bill_var = tk.StringVar(value="$0.00")
        self.per_person_var = tk.StringVar(value="$0.00")

        # --- TRACING (The 'Real-Time' Magic) ---
        # We tell Python: "Whenever these variables are written to (changed), 
        # run the 'calculate' function automatically."
        self.bill_var.trace_add("write", self.calculate)
        self.tip_percent_var.trace_add("write", self.calculate)
        self.num_diners_var.trace_add("write", self.calculate)

        # Draw the User Interface
        self.setup_ui()

    def setup_ui(self):
        """Creates all the buttons, labels, and text boxes."""
        
        # A Frame is like a 'container' or a 'box' to hold our items
        container = tb.Frame(self.root, padding=30)
        container.pack(fill=BOTH, expand=YES)

        # Header Label
        header = tb.Label(
            container, 
            text="TIP CALCULATOR", 
            font=("Helvetica", 18, "bold"), 
            bootstyle=INFO
        )
        header.pack(pady=(0, 20))

        # 1. TOTAL BILL SECTION
        tb.Label(container, text="Total Bill Amount", font=("Helvetica", 10)).pack(anchor=W)
        self.bill_entry = tb.Entry(
            container, 
            textvariable=self.bill_var, 
            font=("Helvetica", 12),
            bootstyle=PRIMARY
        )
        self.bill_entry.pack(fill=X, pady=(5, 15))
        # This makes the cursor start inside the bill box automatically
        self.bill_entry.focus()

        # 2. TIP PERCENTAGE SECTION
        tb.Label(container, text="Select Tip %", font=("Helvetica", 10)).pack(anchor=W)
        tip_frame = tb.Frame(container)
        tip_frame.pack(fill=X, pady=(5, 15))
        
        # We create 3 buttons (10%, 15%, 20%) using a loop to keep code clean
        for percent in [10, 15, 20]:
            tb.Radiobutton(
                tip_frame, 
                text=f"{percent}%", 
                variable=self.tip_percent_var, 
                value=percent,
                bootstyle="info-toolbutton", # Makes them look like clickable boxes
                padding=10
            ).pack(side=LEFT, expand=YES, padx=2, fill=X)

        # 3. NUMBER OF DINERS SECTION
        tb.Label(container, text="Number of Diners (1-6)", font=("Helvetica", 10)).pack(anchor=W)
        self.diner_spin = tb.Spinbox(
            container, 
            from_=1, 
            to=6, 
            textvariable=self.num_diners_var,
            bootstyle=PRIMARY,
            font=("Helvetica", 12)
        )
        self.diner_spin.pack(fill=X, pady=(5, 20))

        # Horizontal line to separate inputs from results
        tb.Separator(container, bootstyle=SECONDARY).pack(fill=X, pady=10)

        # 4. RESULTS SECTION
        # We use a helper function 'create_row' to save space
        self.create_result_row(container, "Calculated Tip:", self.tip_amount_var)
        self.create_result_row(container, "Total with Tip:", self.total_bill_var)

        # Large display for the most important number
        tb.Label(container, text="EACH PERSON PAYS:", font=("Helvetica", 10, "bold"), bootstyle=SUCCESS).pack(pady=(20, 0))
        tb.Label(container, textvariable=self.per_person_var, font=("Helvetica", 28, "bold"), bootstyle=SUCCESS).pack()

        # 5. QUIT BUTTON
        quit_btn = tb.Button(
            container, 
            text="EXIT PROGRAM", 
            command=self.root.destroy, 
            bootstyle=(DANGER, OUTLINE)
        )
        quit_btn.pack(side=BOTTOM, pady=20)

    def create_result_row(self, parent, label_text, variable):
        """A helper function to create a text label on the left and a value on the right."""
        row = tb.Frame(parent)
        row.pack(fill=X, pady=5)
        tb.Label(row, text=label_text, font=("Helvetica", 10)).pack(side=LEFT)
        tb.Label(row, textvariable=variable, font=("Helvetica", 10, "bold")).pack(side=RIGHT)

    def calculate(self, *args):
        """
        The 'Brain' of the app. 
        The *args part is just a Python requirement for 'trace' functions.
        """
        try:
            # 1. Get the text from the entry box
            # .replace("$", "") removes any dollar signs the user might have typed
            # .strip() removes accidental spaces
            raw_input = self.bill_var.get().replace("$", "").strip()

            # 2. If the box is empty, reset the totals to zero and stop
            if not raw_input:
                self.reset_display()
                return

            # 3. Convert text to a Float (a number with decimals)
            bill_amount = float(raw_input)
            
            # 4. Grab our other values
            tip_pct = self.tip_percent_var.get()
            num_people = self.num_diners_var.get()

            # 5. Calculation Logic
            # Math: Total / 100 * percent
            calculated_tip = bill_amount * (tip_pct / 100)
            total_with_tip = bill_amount + calculated_tip
            
            # Ensure we don't divide by zero if something weird happens with the spinbox
            if num_people < 1: 
                num_people = 1
            
            per_person = total_with_tip / num_people

            # 6. Update the GUI
            # :.2f means 'format as a float with 2 decimal places'
            self.tip_amount_var.set(f"${calculated_tip:,.2f}")
            self.total_bill_var.set(f"${total_with_tip:,.2f}")
            self.per_person_var.set(f"${per_person:,.2f}")

        except ValueError:
            # This happens if the user types letters instead of numbers.
            # We show "Invalid Input" in the labels instead of crashing.
            self.tip_amount_var.set("Invalid Number")
            self.total_bill_var.set("Invalid Number")
            self.per_person_var.set("---")
            
        except Exception as e:
            # This is our 'Catch-All' for any other weird errors.
            # It triggers a pop-up as you requested.
            messagebox.showerror("Unexpected Error", 
                                f"A critical error occurred: {e}\n\nThe application will now close.")
            self.root.destroy()

    def reset_display(self):
        """Clears the numbers when the bill input is empty."""
        self.tip_amount_var.set("$0.00")
        self.total_bill_var.set("$0.00")
        self.per_person_var.set("$0.00")

# --- STARTING THE PROGRAM ---
if __name__ == "__main__":
    # Create the window with the 'superhero' dark theme
    app_window = tb.Window(themename="superhero")
    
    # Hand the window over to our Class
    app = BeginnerFriendlyTipCalc(app_window)
    
    # Keep the window open until the user closes it
    app_window.mainloop()