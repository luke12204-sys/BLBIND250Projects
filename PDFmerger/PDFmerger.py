import os
import sys
from PyPDF2 import PdfMerger

# Note: Gemini already added a lot of these comments, which I felt accurately described
# most of what is going on. I asked it to explain as it went, to give me a starting place,
# as well as help me understand.
# I have supplemented with additional comments where missing though.

# Get all files in the current directory
files = os.listdir('.') 
# Filter for PDF files specifically, excluding any existing 'my_files.pdf'
pdf_files = [f for f in files if f.endswith('.pdf') and f != 'my_files.pdf']

def MergeTool():
    """Logic to merge the identified PDF files."""
    # Here at the merge tool, is the only place where, when given to Gemini,
    # I hadn't already given it existing, working logic.
    # I would say, that it probably saved me about 30 additional minutes of trial and error. 
    try:
        merger = PdfMerger()
        
        for f in pdf_files:
            merger.append(f)
            
        merger.write("my_files.pdf")
        merger.close()
        print("\nSuccess: Files successfully combined into 'my_files.pdf'.")
    except Exception as e:
        print(f"\nError: A problem occurred during the merge: {e}")

if __name__ == '__main__':
    # 1. List current PDF files
    print("Files in directory:")
    if not pdf_files:
        print("No PDF files found.")
        sys.exit()
        
    for f in pdf_files:
        print(f"- {f}")

    # 2. Prompt user
    confirm = input("\nWould you like to merge these files? (y/n): ").lower()

    # 3. Process choice
    if confirm == 'y':
        MergeTool()
    elif confirm == 'n':
        print("Merge cancelled by user.")
    else:
        print("Invalid input. Please run the script again and enter 'y' or 'n'.")