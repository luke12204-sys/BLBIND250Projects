"""
Revision: 1.3
Changelog:
- Fixed crash when input fields are empty during typing.
- Switched all inputs to StringVar to allow for "empty" states.
- Refined validation: only shows "Invalid" if actual letters/symbols are typed.
- Added logic to treat an empty 'Diners' box as 1 and empty 'Tip' box as 0 
  to prevent calculation errors while the user is editing.

  ~ As usual, I'm using a '~' to specify what I am typing. 
  ~ This one, I actually did have to massage a few mishaps. 
  ~ This revision, where I had it redo things so that the program wouldn't crash,
  ~ as in the changelog, completely changed how all variables are handled. So,
  ~ It's actually somehow 60 lines of code shorter than the previous one, with better results. 

  ~ I also had to do a specific revision for error handling, in my other projects, when it's a 
  ~ more basic mathmatical situation, it will, as a given, put that stuff in. 
  ~ This time, I did a revision where it would add in error handling, and give feedback when something is off.
  ~ Other than that, the basics of the program came out pretty much perfect in the first revision, it just
  ~ needed a bit more fine tuning. 
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class RobustTipCalc:
    def __init__(self, root):
        self.root = root
        self.root.title("Robust Tip Calculator")
        self.root.geometry("420x620")

        # --- REACTION VARIABLES ---
        # We now use StringVar for EVERY input. StringVars are "brave"—they 
        # don't care if the box is empty, unlike IntVars which would crash.
        self.bill_var = tk.StringVar(value="")
        self.tip_percent_var = tk.StringVar(value="15")
        self.num_diners_var = tk.StringVar(value="1")
        
        # Output Variables
        self.tip_amount_var = tk.StringVar(value="$0.00")
        self.total_bill_var = tk.StringVar(value="$0.00")
        self.per_person_var = tk.StringVar(value="$0.00")

        # Watch for changes
        self.bill_var.trace_add("write", self.calculate)
        self.tip_percent_var.trace_add("write", self.calculate)
        self.num_diners_var.trace_add("write", self.calculate)

        self.setup_ui()

    def setup_ui(self):
        container = tb.Frame(self.root, padding=30)
        container.pack(fill=BOTH, expand=YES)

        # Header
        tb.Label(container, text="TIP CALCULATOR", font=("Helvetica", 18, "bold"), bootstyle=INFO).pack(pady=(0, 20))

        # 1. TOTAL BILL
        tb.Label(container, text="Total Bill Amount", font=("Helvetica", 10)).pack(anchor=W)
        self.bill_entry = tb.Entry(container, textvariable=self.bill_var, font=("Helvetica", 12), bootstyle=PRIMARY)
        self.bill_entry.pack(fill=X, pady=(5, 15))
        self.bill_entry.focus()

        # 2. TIP PERCENTAGE
        tb.Label(container, text="Select Tip %", font=("Helvetica", 10)).pack(anchor=W)
        tip_frame = tb.Frame(container)
        tip_frame.pack(fill=X, pady=(5, 15))
        
        for percent in ["10", "15", "20"]:
            tb.Radiobutton(
                tip_frame, text=f"{percent}%", variable=self.tip_percent_var, 
                value=percent, bootstyle="info-toolbutton", padding=10
            ).pack(side=LEFT, expand=YES, padx=2, fill=X)

        # 3. NUMBER OF DINERS
        tb.Label(container, text="Number of Diners (1-6)", font=("Helvetica", 10)).pack(anchor=W)
        self.diner_spin = tb.Spinbox(
            container, from_=1, to=6, textvariable=self.num_diners_var,
            bootstyle=PRIMARY, font=("Helvetica", 12)
        )
        self.diner_spin.pack(fill=X, pady=(5, 20))

        tb.Separator(container, bootstyle=SECONDARY).pack(fill=X, pady=10)

        # 4. RESULTS
        self.create_result_row(container, "Calculated Tip:", self.tip_amount_var)
        self.create_result_row(container, "Total with Tip:", self.total_bill_var)

        tb.Label(container, text="EACH PERSON PAYS:", font=("Helvetica", 10, "bold"), bootstyle=SUCCESS).pack(pady=(20, 0))
        tb.Label(container, textvariable=self.per_person_var, font=("Helvetica", 28, "bold"), bootstyle=SUCCESS).pack()

        # 5. QUIT
        quit_btn = tb.Button(container, text="EXIT PROGRAM", command=self.root.destroy, bootstyle=(DANGER, OUTLINE))
        quit_btn.pack(side=BOTTOM, pady=20)

    def create_result_row(self, parent, label_text, variable):
        row = tb.Frame(parent)
        row.pack(fill=X, pady=5)
        tb.Label(row, text=label_text, font=("Helvetica", 10)).pack(side=LEFT)
        tb.Label(row, textvariable=variable, font=("Helvetica", 10, "bold")).pack(side=RIGHT)

    def calculate(self, *args):
        """The core logic, now hardened against empty fields."""
        try:
            # --- STEP 1: Get raw text ---
            bill_txt = self.bill_var.get().replace("$", "").strip()
            tip_txt = self.tip_percent_var.get().strip()
            diner_txt = self.num_diners_var.get().strip()

            # --- STEP 2: Handle Empty States ---
            # If the bill is empty, we don't show an error, we just reset to $0.00
            if not bill_txt:
                self.reset_display()
                return

            # If tip or diners are empty (while user is typing), 
            # we assume 0% tip and 1 diner so the math doesn't break.
            bill_val = float(bill_txt)
            tip_val = float(tip_txt) if tip_txt else 0.0
            diner_val = int(diner_txt) if diner_txt and int(diner_txt) > 0 else 1

            # --- STEP 3: The Math ---
            tip_total = bill_val * (tip_val / 100)
            grand_total = bill_val + tip_total
            per_person = grand_total / diner_val

            # --- STEP 4: Update UI ---
            self.tip_amount_var.set(f"${tip_total:,.2f}")
            self.total_bill_var.set(f"${grand_total:,.2f}")
            self.per_person_var.set(f"${per_person:,.2f}")

        except ValueError:
            # Only show "Invalid" if there's actually text that isn't a number
            self.tip_amount_var.set("Invalid Input")
            self.total_bill_var.set("Invalid Input")
            self.per_person_var.set("---")
            
        except Exception as e:
            # Serious unexpected errors
            messagebox.showerror("Critical Error", f"Something went wrong: {e}")
            self.root.destroy()

    def reset_display(self):
        self.tip_amount_var.set("$0.00")
        self.total_bill_var.set("$0.00")
        self.per_person_var.set("$0.00")

if __name__ == "__main__":
    app_window = tb.Window(themename="superhero")
    app = RobustTipCalc(app_window)
    app_window.mainloop()