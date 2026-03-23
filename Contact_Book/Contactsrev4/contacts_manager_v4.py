"""
PROJECT: Terminal Contact Manager
REVISION: 4.0
AUTHOR: Senior Python Dev (I told it to act as a senior dev, so it's funny that it credited that as the author.)
DESCRIPTION: A final, fully-commented version of the terminal-based contact 
             management system for educational purposes.
NOTE FROM REAL HUMAN: So, I asked it specifically to update the revision number as we went, 
as well, it also kept a most recent changelog in prior versions. This was very helpful,
luckily, I didn't have too many issues, but if I did, that would have helped me to backtrack.

HUMAN NOTE ON COMMENTING: The AI did a pretty good job with commenting. I'm going to add a "~" to
wherever I fill in for additional comments or context.
"""

import json  # Used to convert Python lists/dicts into a text file (.json)
import os    # Used to check if the file exists on your hard drive
import re    # 'Regular Expressions' - A powerful tool for pattern matching (email/phone)

# Global constant to keep track of our development version
REVISION = "4.0"

class ContactManager:
    """
    This class handles the 'Data Layer.' It doesn't care about the terminal 
    or menus; it only cares about reading and writing to the JSON file.
    """
    def __init__(self, filename='contacts.json'):
        self.filename = filename
        # When the program starts, we immediately try to load existing data
        self.contacts = self.load_data()

    def load_data(self):
        """Checks if the file exists and reads it; otherwise, starts with an empty list."""
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as f:
                # json.load converts the text in the file back into a Python List
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If the file is corrupted or unreadable, we return an empty list to prevent a crash
            return []

    def save_data(self):
        """Writes the current contact list into the JSON file."""
        with open(self.filename, 'w') as f:
            # indent=4 makes the JSON file 'pretty' and readable for humans

            #~ I think it's a little creepy that the AI specified 'readable for humans'
            #~ in the comment above. I didn't say anything for it to make that connection
            json.dump(self.contacts, f, indent=4)

    def add_contact(self, contact):
        """Appends a new dictionary to our list and saves it."""
        self.contacts.append(contact)
        self.save_data()

    def delete_contact(self, index):
        """Removes a contact based on its position (index) in the list."""
        if 0 <= index < len(self.contacts):
            self.contacts.pop(index)
            self.save_data()

    def update_contact(self, index, updated_contact):
        """Replaces an old contact dictionary with a new one at the same position."""
        if 0 <= index < len(self.contacts):
            self.contacts[index] = updated_contact
            self.save_data()

class ContactCLI:
    """
    This class handles the 'User Interface' (CLI). It manages the loops, 
    the menus, and ensures the user types in valid information.
    """
    def __init__(self):
        # We 'initialize' the manager inside the CLI so they can communicate
        self.manager = ContactManager()

    # --- VALIDATION TOOLS ---
    # These functions act as gatekeepers to ensure only 'clean' data enters the system.

    def validate_name(self, name):
        if not name.strip():
            return False, "Name cannot be empty."
        # This checks every letter; if any are numbers, it returns an error
        if any(char.isdigit() for char in name):
            return False, "Name cannot contain numbers."
        return True, ""

    def validate_phone(self, phone):
        # This Regex allows digits, spaces, dashes, plus signs, and parentheses
        # {7,20} ensures the number isn't too short or impossibly long

        #~ I first had it check for only numbers. But then I felt like there should be allowance for 
        #~ other symbols that you would have in a phone number. So this should support just the numbers,
        #~ standard American format numbers, and international ones as well. 
        pattern = r'^[\d\s\-\(\)\+]{7,20}$'
        if re.match(pattern, phone):
            return True, ""
        return False, "Invalid format. Please make sure you don't include any invalid characters or symbols."

    def validate_email(self, email):
        # This Regex looks for: [text] + [@] + [text] + [.] + [at least 2 letters]

        #~ I had it add the typical logic to make sure that it's a valid email address. 
        #~ So that no russian hackers could sneak anything crazy into my contacts book. 
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, ""
        return False, "Invalid email. Ensure it includes a suffix like .com or .org."

    def get_input(self, prompt, validation_func):
        """
        A helper loop. It will keep asking the user for input until 
        the validation_func says it's okay (True).
        """
        while True:
            value = input(prompt).strip()
            is_valid, error_msg = validation_func(value)
            if is_valid:
                return value
            print(f"  [!] {error_msg}")

    # --- DISPLAY MODES ---

    def show_all_table(self):
        """Prints a neat table view. Addresses are truncated to keep columns aligned."""
        #~ Initially, the AI kept all of the information shortened, so addresses would be cut off
        #~ when displayed. I actually felt like that was a good feature to keep in the "show all" view,
        #~ so that it would be easy to browse if say, dozens or hundreds of contacts were added. But,
        #~ Even though the information would be easily findable in the JSON file, I did feel like for 
        #~ the assignment, and the user experience, it would be best to have a way to see all of the
        #~ information, within the program. So, when someone uses the search function, it then will display
        #~ the complete information, in a more legible way. 

        contacts = self.manager.contacts
        print(f"\n{'='*100}")
        print(f" ALL CONTACTS | REVISION: {REVISION} ".center(100, "="))
        print(f"{'='*100}")
        
        # Format strings like :<18 mean 'left-align and give this 18 spaces of room'
        header = f"{'ID':<4} {'Name':<18} {'Phone':<16} {'Email':<22} {'Address (Truncated)':<30}"
        print(header)
        print("-" * 100)
        
        for idx, c in enumerate(contacts):
            addr = c.get('Address', 'N/A')
            # If the address is long, we cut it off and add '..' for visual neatness
            display_addr = (addr[:27] + '..') if len(addr) > 27 else addr
            print(f"{idx:<4} {c['Name']:<18} {c['Phone']:<16} {c['Email']:<22} {display_addr:<30}")
        
        if not contacts:
            print("The address book is currently empty.".center(100))
        print("-" * 100)

    def search_detailed(self, query):
        """Displays full contact 'cards'. This allows long addresses to be read fully."""
        print(f"\n{'*'*40}")
        print(f" SEARCH RESULTS FOR: '{query}' ".center(40, "*"))
        print(f"{'*'*40}")
        
        found = False
        for idx, c in enumerate(self.manager.contacts):
            # We use .lower() on both sides to make the search case-insensitive
            if query.lower() in c['Name'].lower():
                print(f"\n[ID: {idx}]")
                print(f"  Name:    {c['Name']}")
                print(f"  Phone:   {c['Phone']}")
                print(f"  Email:   {c['Email']}")
                print(f"  Address: {c['Address']}") # No truncation here!
                print("-" * 40)
                found = True
        
        if not found:
            print(f"\nNo contact found matching '{query}'.")

    # --- MAIN ENGINE ---

    #~ There aren't a tone of comments in this section, but it's all
    #~ pretty understandable by the text that is associated within it. 

    def run(self):
        """The main menu loop that keeps the program running until the user quits."""
        while True:
            print(f"\n[Contact Manager Rev {REVISION}]")
            print("1. Add New Contact")
            print("2. View All (Table View)")
            print("3. Search (Full Detailed View)")
            print("4. Update Contact")
            print("5. Delete Contact")
            print("6. Exit")
            
            choice = input("\nSelection: ")

            if choice == '1':
                # We use our 'get_input' helper to ensure data is clean before adding
                name = self.get_input("Name: ", self.validate_name)
                phone = self.get_input("Phone: ", self.validate_phone)
                email = self.get_input("Email: ", self.validate_email)
                address = input("Address: ").strip()
                
                self.manager.add_contact({
                    "Name": name, "Phone": phone, 
                    "Email": email, "Address": address
                })
                print("✓ Saved successfully.")

            elif choice == '2':
                self.show_all_table()

            elif choice == '3':
                query = input("Enter name to search: ")
                self.search_detailed(query)

            elif choice == '4':
                self.show_all_table()
                try:
                    idx = int(input("Enter ID number to edit: "))
                    if 0 <= idx < len(self.manager.contacts):
                        old = self.manager.contacts[idx]
                        print(f"\nEditing: {old['Name']} (Press Enter to keep the current value)")
                        
                        # The 'or' logic here is a neat trick: 
                        # If input() is empty, it evaluates to False, so it takes the 'old' value instead.
                        name = input(f"New Name [{old['Name']}]: ") or old['Name']
                        phone = input(f"New Phone [{old['Phone']}]: ") or old['Phone']
                        email = input(f"New Email [{old['Email']}]: ") or old['Email']
                        address = input(f"New Address [{old['Address']}]: ") or old['Address']
                        
                        self.manager.update_contact(idx, {
                            "Name": name, "Phone": phone, 
                            "Email": email, "Address": address
                        })
                        print("✓ Contact updated.")
                    else:
                        print("Error: That ID does not exist.")
                except ValueError:
                    print("Error: You must enter a valid number for the ID.")

            elif choice == '5':
                self.show_all_table()
                try:
                    idx = int(input("Enter ID number to delete: "))
                    self.manager.delete_contact(idx)
                    print("✓ Contact removed.")
                except (ValueError, IndexError):
                    print("Error: Could not find that contact ID.")

            elif choice == '6':
                print(f"Shutting down Manager Rev {REVISION}. Have a great day!")
                break
            else:
                print("Invalid selection. Please choose 1-6.")

# This block ensures the code only runs if the script is executed directly
# It won't run if this file is imported into another project as a library.
if __name__ == "__main__":
    app = ContactCLI()
    app.run()