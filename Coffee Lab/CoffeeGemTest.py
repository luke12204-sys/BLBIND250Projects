from CoffeeGem import CoffeeVendingMachine
# I normally have a standard file, and the after I have given a file to Gemini, I add
# an indicator like adding 'Gem' or something like that to indicate that this is the
# Post-AI version, as well as keeping an original in case I need to re-upload with a different prompt
def main():
    # Constructing the machine: $1.50 per cup, 10 cups in stock
    my_coffee_machine = CoffeeVendingMachine("Premium Coffee", 1.50, 10)
    
    # Launch the menu
    my_coffee_machine.menu()

if __name__ == "__main__":
    main()