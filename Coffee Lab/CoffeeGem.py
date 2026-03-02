import time
# Calls in existing vending_machine code
import vending_machine as vm

# Gemini has added comments, I have supplemented where it has not, and context to what Gemini has added

class CoffeeVendingMachine(vm.VendingMachine):
    def __init__(self, item_name, item_price, stock):
        super().__init__(item_name, item_price, stock)
        
        # Requirement 3 (Requirements given to Gemini): Default to lowest parameters
        self.strength = 1 
        self.cream = 0
        self.sugar = 0

    def set_cream(self, count):
        # Requirement 1 & 2: Validate funds and range with error messages
        if self.balance < self.item_price:
            print(f"\n>>> ERROR: Insufficient funds! You need ${self.item_price:.2f} to customize your coffee.")
            return 

        if 0 <= count <= 2:
            self.cream = count
            print(f"Cream level set to {count}.")
        else:
            print(f"\n>>> ERROR: '{count}' is out of range. Please enter a value between 0 and 2.")

    def set_sugar(self, count):
        if self.balance < self.item_price:
            print(f"\n>>> ERROR: Insufficient funds! You need ${self.item_price:.2f} to customize your coffee.")
            return 

        if 0 <= count <= 2:
            self.sugar = count
            print(f"Sugar level set to {count}.")
        else:
            print(f"\n>>> ERROR: '{count}' is out of range. Please enter a value between 0 and 2.")

    def set_strength(self, count):
        if self.balance < self.item_price:
            print(f"\n>>> ERROR: Insufficient funds! You need ${self.item_price:.2f} to customize your coffee.")
            return 

        if 1 <= count <= 3:
            self.strength = count
            print(f"Strength level set to {count}.")
        else:
            print(f"\n>>> ERROR: '{count}' is out of range. Please enter a value between 1 and 3.")

    def purchase(self):
        # The parent class purchase() handles balance and stock deduction
        if super().purchase():
            # Requirement 4: Display values WHILE brewing 
            # ~Gemini put WHILE in all caps, because I kept getting on it for it not showing up,
            # It turned out I just didn't have my terminal window open large enough to see the messages.
            print(f"\nBrewing coffee (Strength: {self.strength}, Cream: {self.cream}, Sugar: {self.sugar})", end="")
            for i in range(6):
                print(".", end='', flush=True)
                time.sleep(0.5)
            
            print(f"\nDispensing complete! Enjoy your coffee.")

            # Requirement 3: Reset to defaults after brewing
            self.strength = 1
            self.cream = 0
            self.sugar = 0
        else:
            print("\n>>> ERROR: Purchase failed. Check your balance or the machine's stock.")

    def menu(self):
        while True:
            print(f"\n--- Balance: ${self.balance:.2f} | Price: ${self.item_price:.2f} ---")
            print(f"Current Order -> Strength: {self.strength}, Cream: {self.cream}, Sugar: {self.sugar}")
            print("\nU-Brewit Coffee Dispenser")
            print("1. Add Funds")
            print("2. Set Strength (1-3)")
            print("3. Set Cream (0-2)")
            print("4. Set Sugar (0-2)")
            print("5. Brew Coffee")
            print("6. Refund")
            print("7. Quit")
            # I believe most of the menu logic is largely the same as it was. 
            # Really, the only thing added is the error handling. 
            try:
                option = int(input("Enter Selection: "))
                if option == 1:
                    money = float(input("Enter money submitted: $"))
                    self.insert_money(money)
                elif option == 2:
                    val = int(input("Enter strength (1-3): "))
                    self.set_strength(val)
                elif option == 3:
                    val = int(input("Enter tsp of cream (0-2): "))
                    self.set_cream(val)
                elif option == 4:
                    val = int(input("Enter tsp of sugar (0-2): "))
                    self.set_sugar(val)
                elif option == 5:
                    self.purchase()
                elif option == 6:
                    self.refund()
                elif option == 7:
                    break
                else:
                    print("\n>>> ERROR: Invalid selection. Please choose 1-7.")
            except ValueError:
                print("\n>>> ERROR: Invalid input. Please enter a number.")