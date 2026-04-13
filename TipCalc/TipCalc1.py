"""
Revision: 1.0
Changelog:
- Initial release of the Tip Calculator GUI.
- Implemented real-time calculation using StringVar/IntVar traces.
- Added validation for non-numeric bill inputs.
- Integrated tip selection (10%, 15%, 20%) and diner splitting (1-6).
- Included a dedicated Quit button and standard window closing support.
"""

import tkinter as tk
from tkinter import ttk, messagebox

class TipCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Pythonic Tip Calculator")
        self.root.geometry("350x450")
        self.root.resizable(False, False)

        # -- Reactive Variables --
        self.bill_var = tk.StringVar(value="")
        self.tip_percent_var = tk.IntVar(value=15)
        self.num_diners_var = tk.IntVar(value=1)
        
        # Output Variables
        self.tip_amount_var = tk.StringVar(value="$0.00")
        self.total_bill_var = tk.StringVar(value="$0.00")
        self.per_person_var = tk.StringVar(value="$0.00")

        # Set up Traces for Real-Time Updates
        self.bill_var.trace_add("write", self.calculate)
        self.tip_percent_var.trace_add("write", self.calculate)
        self.num_diners_var.trace_add("write", self.calculate)

        self.setup_ui()

    def setup_ui(self):
        """Builds the GUI layout using ttk widgets for a modern look."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 1. Bill Input
        ttk.Label(main_frame, text="Total Bill ($):", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bill_entry = ttk.Entry(main_frame, textvariable=self.bill_var, width=15)
        self.bill_entry.grid(row=0, column=1, sticky=tk.E, pady=5)
        self.bill_entry.focus()

        # 2. Tip Percentage (Dropdown/OptionMenu)
        ttk.Label(main_frame, text="Tip Percentage:", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        tip_options = [10, 15, 20, 25] # Added 25 as a bonus
        self.tip_menu = ttk.OptionMenu(main_frame, self.tip_percent_var, 15, *tip_options)
        self.tip_menu.grid(row=1, column=1, sticky=tk.E, pady=5)

        # 3. Number of Diners (Spinbox)
        ttk.Label(main_frame, text="Number of Diners:", font=("Helvetica", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.diner_spin = ttk.Spinbox(main_frame, from_=1, to=6, textvariable=self.num_diners_var, width=13)
        self.diner_spin.grid(row=2, column=1, sticky=tk.E, pady=5)

        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky="ew", pady=15)

        # -- Results Section --
        results_font = ("Helvetica", 10)
        
        ttk.Label(main_frame, text="Tip Amount:", font=results_font).grid(row=4, column=0, sticky=tk.W)
        ttk.Label(main_frame, textvariable=self.tip_amount_var, font=results_font).grid(row=4, column=1, sticky=tk.E)

        ttk.Label(main_frame, text="Total Bill (w/ Tip):", font=results_font).grid(row=5, column=0, sticky=tk.W)
        ttk.Label(main_frame, textvariable=self.total_bill_var, font=results_font).grid(row=5, column=1, sticky=tk.E)

        ttk.Label(main_frame, text="Amount Per Person:", font=("Helvetica", 12, "bold"), foreground="#2e7d32").grid(row=6, column=0, sticky=tk.W, pady=10)
        ttk.Label(main_frame, textvariable=self.per_person_var, font=("Helvetica", 12, "bold"), foreground="#2e7d32").grid(row=6, column=1, sticky=tk.E, pady=10)

        # 4. Quit Button
        self.quit_btn = ttk.Button(main_frame, text="Exit Application", command=self.root.destroy)
        self.quit_btn.grid(row=7, column=0, columnspan=2, pady=20)

    def calculate(self, *args):
        """The core calculation logic triggered on variable changes."""
        try:
            # Handle empty string or non-numeric input gracefully
            bill_str = self.bill_var.get().replace("$", "").strip()
            if not bill_str:
                self.reset_results()
                return
            
            bill_float = float(bill_str)
            tip_percent = self.tip_percent_var.get()
            num_diners = self.num_diners_var.get()

            # Ensure diners is at least 1 to avoid DivisionByZero
            if num_diners < 1:
                num_diners = 1

            # Math logic
            tip_total = bill_float * (tip_percent / 100)
            grand_total = bill_float + tip_total
            per_person = grand_total / num_diners

            # Update Labels
            self.tip_amount_var.set(f"${tip_total:,.2f}")
            self.total_bill_var.set(f"${grand_total:,.2f}")
            self.per_person_var.set(f"${per_person:,.2f}")

        except ValueError:
            # If user enters letters/symbols, we simply stop updating or show an error
            self.tip_amount_var.set("Invalid Input")
            self.total_bill_var.set("Invalid Input")
            self.per_person_var.set("---")

    def reset_results(self):
        """Clears results if the bill entry is empty."""
        self.tip_amount_var.set("$0.00")
        self.total_bill_var.set("$0.00")
        self.per_person_var.set("$0.00")

if __name__ == "__main__":
    root = tk.Tk()
    app = TipCalculator(root)
    root.mainloop()