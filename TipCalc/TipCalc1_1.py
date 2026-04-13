"""
Revision: 1.1
Changelog:
- Migrated UI from standard ttk to ttkbootstrap for a modern, themed interface.
- Implemented 'superhero' dark theme.
- Replaced standard labels with themed Bootstyle labels.
- Maintained real-time calculation logic via StringVar traces.
- Ensured compliance with all previous functional requirements.
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk

class ModernTipCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Tip Calculator")
        self.root.geometry("400x600")
        
        # -- Reactive Variables --
        self.bill_var = tk.StringVar(value="")
        self.tip_percent_var = tk.IntVar(value=15)
        self.num_diners_var = tk.IntVar(value=1)
        
        # Output Variables
        self.tip_amount_var = tk.StringVar(value="$0.00")
        self.total_bill_var = tk.StringVar(value="$0.00")
        self.per_person_var = tk.StringVar(value="$0.00")

        # Traces for real-time calculation
        self.bill_var.trace_add("write", self.calculate)
        self.tip_percent_var.trace_add("write", self.calculate)
        self.num_diners_var.trace_add("write", self.calculate)

        self.setup_ui()

    def setup_ui(self):
        """Creates the layout using ttkbootstrap widgets."""
        # Main container with padding
        container = tb.Frame(self.root, padding=30)
        container.pack(fill=BOTH, expand=YES)

        # Header
        header = tb.Label(
            container, 
            text="TIP CALCULATOR", 
            font=("Helvetica", 18, "bold"), 
            bootstyle=INFO
        )
        header.pack(pady=(0, 20))

        # 1. Bill Input
        tb.Label(container, text="Total Bill Amount", font=("Helvetica", 10)).pack(anchor=W)
        self.bill_entry = tb.Entry(
            container, 
            textvariable=self.bill_var, 
            font=("Helvetica", 12),
            bootstyle=PRIMARY
        )
        self.bill_entry.pack(fill=X, pady=(5, 15))
        self.bill_entry.focus()

        # 2. Tip Percentage (Radio Buttons for a modern feel)
        tb.Label(container, text="Select Tip %", font=("Helvetica", 10)).pack(anchor=W)
        tip_frame = tb.Frame(container)
        tip_frame.pack(fill=X, pady=(5, 15))
        
        for percent in [10, 15, 20]:
            tb.Radiobutton(
                tip_frame, 
                text=f"{percent}%", 
                variable=self.tip_percent_var, 
                value=percent,
                bootstyle="info-toolbutton",
                padding=10
            ).pack(side=LEFT, expand=YES, padx=2, fill=X)

        # 3. Number of Diners
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

        # -- Separator --
        tb.Separator(container, bootstyle=SECONDARY).pack(fill=X, pady=10)

        # -- Display Results --
        self.create_result_row(container, "Tip Amount:", self.tip_amount_var)
        self.create_result_row(container, "Grand Total:", self.total_bill_var)

        # Emphasis on Per Person Amount
        per_person_label = tb.Label(
            container, 
            text="EACH PERSON PAYS:", 
            font=("Helvetica", 10, "bold"),
            bootstyle=SUCCESS
        )
        per_person_label.pack(pady=(20, 0))
        
        per_person_display = tb.Label(
            container, 
            textvariable=self.per_person_var, 
            font=("Helvetica", 24, "bold"),
            bootstyle=SUCCESS
        )
        per_person_display.pack()

        # 4. Quit Button
        quit_btn = tb.Button(
            container, 
            text="QUIT", 
            command=self.root.destroy, 
            bootstyle=(DANGER, OUTLINE),
            width=15
        )
        quit_btn.pack(side=BOTTOM, pady=20)

    def create_result_row(self, parent, label_text, variable):
        """Helper to create consistent result rows."""
        row = tb.Frame(parent)
        row.pack(fill=X, pady=2)
        tb.Label(row, text=label_text, font=("Helvetica", 10)).pack(side=LEFT)
        tb.Label(row, textvariable=variable, font=("Helvetica", 10, "bold")).pack(side=RIGHT)

    def calculate(self, *args):
        """Core calculation logic with validation."""
        try:
            # Clean and validate input
            raw_bill = self.bill_var.get().replace("$", "").strip()
            if not raw_bill:
                self.clear_results()
                return

            bill_float = float(raw_bill)
            tip_pct = self.tip_percent_var.get()
            diners = self.num_diners_var.get()

            # Prevent division by zero if spinbox is manipulated
            diners = max(1, diners)

            tip_total = bill_float * (tip_pct / 100)
            grand_total = bill_float + tip_total
            split = grand_total / diners

            self.tip_amount_var.set(f"${tip_total:,.2f}")
            self.total_bill_var.set(f"${grand_total:,.2f}")
            self.per_person_var.set(f"${split:,.2f}")

        except ValueError:
            # Graceful failure for non-numeric input
            self.tip_amount_var.set("Error")
            self.total_bill_var.set("Error")
            self.per_person_var.set("N/A")

    def clear_results(self):
        self.tip_amount_var.set("$0.00")
        self.total_bill_var.set("$0.00")
        self.per_person_var.set("$0.00")

if __name__ == "__main__":
    # Initialize with a theme (e.g., 'superhero', 'flatly', 'darkly', 'cosmo')
    app_window = tb.Window(themename="superhero")
    ModernTipCalculator(app_window)
    app_window.mainloop()