"""
Revision: 1.2
Changelog:
- Added exhaustive, beginner-friendly comments to explain core Python and Pandas concepts.
- Clarified logic for sorting, editing, and data visualization.
- Simplified variable naming where helpful for clarity.

~ As usual, I will be adding my comments with a '~'
~ This time, I might have been a bit more elaborate when I asked for comments, so
~ It seems like Gemini described and noted way more than normal.
~ I didn't really have much more to say because of this.  
"""

# --- LIBRARIES ---
# Pandas is the 'gold standard' for data manipulation in Python. Think of it as Excel on steroids.
import pandas as pd

# The 'os' module allows us to talk to your computer's operating system (e.g., checking if a file exists).
import os

# Matplotlib is the library we use to generate charts and graphs.
import matplotlib.pyplot as plt

# Datetime helps us grab the exact moment an expense is recorded.
from datetime import datetime

# --- CONFIGURATION ---
# We store the filename in a 'Constant' (all caps). This makes it easy to change the file name later in just one place.
FILE_NAME = "expenses.csv"

def initialize_df():
    """
    This function sets up our 'Database' (the CSV file).
    If the file doesn't exist, it creates a new one with headers.
    """
    # Check if the CSV already exists on your hard drive
    if os.path.exists(FILE_NAME):
        # read_csv converts the file into a 'DataFrame' (a Pandas table)
        return pd.read_csv(FILE_NAME)
    else:
        # If no file, we define the columns manually
        columns = ["Date", "Category", "Description", "Amount"]
        # Create an empty table with those columns
        df = pd.DataFrame(columns=columns)
        # Save it so we have a starting point
        save_and_sort_df(df)
        return df

# ~ This sort function is interesting.
# ~ I had an idea of how I was gonna do it, but wasn't quite sure how.
# ~ I think if I had spent a bit of time on it, I could have figured it out,
# ~ But, this is very concise and simple. 
def save_and_sort_df(df):
    """
    This is a helper function. Instead of writing code to save the file
    multiple times, we centralize it here to ensure the 'Sort' rule is always followed.
    """
    # Sort the table by the 'Amount' column. ascending=True means smallest to largest.
    df = df.sort_values(by="Amount", ascending=True)
    # index=False prevents Pandas from writing a 'row number' column into our CSV.
    df.to_csv(FILE_NAME, index=False)

def add_expense(category, description, amount):
    """
    Takes user input and appends it as a new row in our table.
    """
    df = pd.read_csv(FILE_NAME)

    # We create a 'Dictionary' to represent the new row.
    new_entry = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Formats time as YYYY-MM-DD
        "Category": category,
        "Description": description,
        "Amount": float(amount) # Ensure the amount is a number, not just text
    }

    # pd.concat takes the old table and 'glues' the new row to the bottom.
    # ignore_index=True ensures the row numbers stay sequential (0, 1, 2...).
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Save the updated table (which triggers the sort!)
    save_and_sort_df(df)
    print("\n✅ Expense added successfully!")

def view_summary():
    """
    Prints the table to the console and calculates some quick math.
    """
    df = pd.read_csv(FILE_NAME)

    # Check if the table is empty before doing math
    if df.empty:
        print("\n📭 No expenses recorded yet.")
        return

    print("\n--- Current Expenses (Sorted by Amount) ---")
    print(df)

    # Pandas makes math easy: .sum() adds everything, .mean() finds the average.
    total = df["Amount"].sum()
    avg = df["Amount"].mean()
    
    print(f"\n💰 Total Spent: ${total:.2f}") # .2f rounds to 2 decimal places
    print(f"📊 Average Expense: ${avg:.2f}")

    # groupby('Category') clusters rows together so we can see totals for 'Food' vs 'Rent'
    print("\n--- Spending by Category ---")
    print(df.groupby("Category")["Amount"].sum())

def delete_expense():
    """
    Removes a specific row based on the index (the number on the far left).
    """
    df = pd.read_csv(FILE_NAME)
    if df.empty:
        print("Nothing to delete.")
        return

    print(df)
    try:
        # We wrap this in a 'try' block in case the user types something that isn't a number.
        loc = int(input("\nEnter index to delete: "))
        # .drop() removes the row at that index
        df = df.drop(index=loc)
        save_and_sort_df(df)
        print("✅ Expense deleted.")
    except (ValueError, KeyError):
        # This catches errors like typing 'abc' or an index that doesn't exist.
        print("❌ Invalid index. Please try again.")

def edit_expense():
    """
    Updates an existing entry. If the user leaves an input blank, 
    it keeps the old information.
    """
    df = pd.read_csv(FILE_NAME)
    if df.empty:
        print("No expenses to edit.")
        return

    print(df)
    try:
        loc = int(input("\nEnter index to edit: "))
        if loc not in df.index:
            raise KeyError

        print(f"Editing: {df.loc[loc, 'Description']}")
        
        # Logic: (New Input) OR (Old Value). If input is empty, the 'or' uses the second value.
        new_cat = input(f"New Category [{df.loc[loc, 'Category']}]: ") or df.loc[loc, 'Category']
        new_desc = input(f"New Description [{df.loc[loc, 'Description']}]: ") or df.loc[loc, 'Description']
        new_amt = input(f"New Amount [{df.loc[loc, 'Amount']}]: ") or df.loc[loc, 'Amount']

        # df.at[row, column] targets the exact cell we want to change
        df.at[loc, 'Category'] = new_cat
        df.at[loc, 'Description'] = new_desc
        df.at[loc, 'Amount'] = float(new_amt)
        
        # We update the timestamp to show when the edit occurred
        df.at[loc, 'Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_and_sort_df(df)
        print("✅ Expense updated successfully!")
    except (ValueError, KeyError):
        print("❌ Invalid index or amount. Edit cancelled.")

def plot_expenses():
    """
    Uses Matplotlib to create a visual representation of your spending.
    """
    df = pd.read_csv(FILE_NAME)
    if df.empty:
        print("No data to plot.")
        return

    # Calculate totals for each category for the pie slices
    category_totals = df.groupby('Category')['Amount'].sum()
    
    # Create the chart
    plt.figure(figsize=(8, 8)) # Size in inches
    # autopct='%1.1f%%' automatically calculates and displays the percentage on the slice
    plt.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%', startangle=140)
    plt.title('Total Expenses by Category')
    plt.axis('equal') # Ensures the pie is a circle, not an oval
    
    print("Close the chart window to return to the menu.")
    plt.show() # This opens a separate window with your graph

def main():
    """
    The main control loop. This keeps the program running until the user hits 'Exit'.
    """
    initialize_df()

    while True:
        print("\n--- 📈 Expense Tracker CLI ---")
        print("1. Add Expense")
        print("2. View Summary")
        print("3. Delete Expense")
        print("4. Edit Expense")
        print("5. Plot Chart")
        print("6. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            cat = input("Enter Category (e.g., Food, Rent, Fun): ")
            desc = input("Short Description: ")
            try:
                amt = float(input("Amount: "))
                add_expense(cat, desc, amt)
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")
        elif choice == "2":
            view_summary()
        elif choice == "3":
            delete_expense()
        elif choice == "4":
            edit_expense()
        elif choice == "5":
            plot_expenses()
        elif choice == "6":
            print("Goodbye!")
            break # Breaks the 'While True' loop to end the program
        else:
            print("Invalid choice, try again.")

# This line ensures the program only runs if you execute THIS file specifically.
if __name__ == "__main__":
    main()