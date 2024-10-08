import fitz  # PyMuPDF
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Default settings
settings = {
    "min_font_size": 10,
    "left_margin": 50,
    "right_margin": 500
}

def extract_text_from_pdf(pdf_path, min_font_size, left_margin, right_margin):
    document = fitz.open(pdf_path)  # Open the PDF file
    lines = {}  # Dictionary to store lines of text

    for page_num in range(len(document)):  # Iterate through all pages in the PDF
        print(f"Processing page {page_num + 1}/{len(document)}")  # Debug statement
        page = document.load_page(page_num)  # Load the current page
        blocks = page.get_text("dict")["blocks"]  # Get text blocks from the page

        for block in blocks:  # Iterate through each block of text
            for line in block["lines"]:  # Iterate through each line in the block
                for span in line["spans"]:  # Iterate through each span in the line
                    if span["size"] < min_font_size:  # Ignore small fonts
                        continue
                    bbox = span["bbox"]  # Get the bounding box of the span
                    x0, y0, x1, y1 = bbox  # Unpack the bounding box coordinates
                    if x0 < left_margin or x1 > right_margin:  # Ignore text outside margins
                        continue
                    line_key = (page_num, int(y0))  # Use the page number and vertical position as the line key
                    if line_key not in lines:  # If the line key is not in the dictionary
                        lines[line_key] = []  # Initialize a new list for this line key
                    lines[line_key].append((bbox, span["text"]))  # Append the span text and bbox to the line key
    
    return lines  # Return the dictionary of lines

def format_sections_and_authors(lines):
    formatted_entries = []  # List to store formatted entries
    keywords = ["tle", "chap", "par", "sec"]  # Keywords to look for in the text

    # Sort the lines by page number and then by vertical position
    sorted_line_keys = sorted(lines.keys(), key=lambda k: (k[0], k[1]))

    for line_key in sorted_line_keys:  # Iterate through sorted line keys
        line = lines[line_key]  # Get the line corresponding to the current key
        line.sort(key=lambda x: x[0][0])  # Sort spans by horizontal position
        line_text = ' '.join([word[1] for word in line])  # Join span texts into a single line of text
        
        # Split the line into words
        words = line_text.split()
        filtered_words = []  # List to store filtered words
        
        for word in words:  # Iterate through each word in the line
            if word.isdigit():  # Check if the word is a digit
                # Check if the previous word contains any of the keywords
                if filtered_words and any(kw in filtered_words[-1].lower() for kw in keywords):
                    filtered_words.append(word)  # Append the digit if the previous word contains a keyword
            else:
                filtered_words.append(word)  # Append the word if it is not a digit
        
        # Join the filtered words back into a string
        line_text = ' '.join(filtered_words)
        
        formatted_entries.append(line_text)  # Append the formatted line to the list
    
    return formatted_entries  # Return the list of formatted entries

def clean_output(entries):
    print("Original Entries:", entries)  # Debug statement to print original entries
    
    # Remove leading empty entries
    while entries and entries[0].strip() == '':
        entries.pop(0)
    
    # Remove trailing empty entries
    while entries and entries[-1].strip() == '':
        entries.pop()
    
    cleaned_entries = []
    current_group = []

    for entry in entries:
        if entry.strip() == '':
            if current_group:
                cleaned_entry = ' '.join(current_group)
                cleaned_entries.append(cleaned_entry)
                current_group = []
        else:
            current_group.append(entry.strip())
    
    # Add the last group if it exists
    if current_group:
        cleaned_entry = ' '.join(current_group)
        cleaned_entries.append(cleaned_entry)
    
    print("Cleaned Entries:", cleaned_entries)  # Debug statement to print cleaned entries
    return cleaned_entries

def categorize_entries(entries):
    categorized_entries = []

    for entry in entries:
        if not entry.strip() or len(entry.strip()) < 3:
            continue  # Skip empty entries and entries with less than 3 characters

        doc = nlp(entry)
        if all(ent.label_ == "PERSON" for ent in doc.ents):
            categorized_entries.append(' / ' + entry + ' -- ')
        else:
            categorized_entries.append(entry)

    return categorized_entries

def main(pdf_path):
    # Extract text from the PDF with specified font size and margins
    lines = extract_text_from_pdf(pdf_path, settings["min_font_size"], settings["left_margin"], settings["right_margin"])
    print("Grouped Lines:", lines)  # Debug statement to print grouped lines
    
    # Format the extracted lines into sections and authors
    entries = format_sections_and_authors(lines)
    print("Formatted Entries:", entries)  # Debug statement to print formatted entries
    
    return entries

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        file_label.config(text=file_path)
        scan_button.pack(pady=10)  # Show the scan button when a file is selected

def scan_file():
    file_path = file_label.cget("text")
    if file_path and file_path != "No file selected":
        entries = main(file_path)
        cleaned_entries = clean_output(entries)
        categorized_entries = categorize_entries(cleaned_entries)
        
        output_text.delete(1.0, tk.END)
        for entry in categorized_entries:
            output_text.insert(tk.END, entry + "\n")

def clear_output():
    file_label.config(text="No file selected")
    output_text.delete(1.0, tk.END)
    scan_button.pack_forget()  # Hide the scan button when clearing the output

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    tk.Label(settings_window, text="Minimum Font Size:").grid(row=0, column=0, padx=10, pady=5)
    min_font_size_entry = tk.Entry(settings_window)
    min_font_size_entry.grid(row=0, column=1, padx=10, pady=5)
    min_font_size_entry.insert(0, str(settings["min_font_size"]))

    tk.Label(settings_window, text="Left Margin:").grid(row=1, column=0, padx=10, pady=5)
    left_margin_entry = tk.Entry(settings_window)
    left_margin_entry.grid(row=1, column=1, padx=10, pady=5)
    left_margin_entry.insert(0, str(settings["left_margin"]))

    tk.Label(settings_window, text="Right Margin:").grid(row=2, column=0, padx=10, pady=5)
    right_margin_entry = tk.Entry(settings_window)
    right_margin_entry.grid(row=2, column=1, padx=10, pady=5)
    right_margin_entry.insert(0, str(settings["right_margin"]))

    def save_settings():
        settings["min_font_size"] = int(min_font_size_entry.get())
        settings["left_margin"] = int(left_margin_entry.get())
        settings["right_margin"] = int(right_margin_entry.get())
        settings_window.destroy()

    def reset_to_default():
        min_font_size_entry.delete(0, tk.END)
        min_font_size_entry.insert(0, "10")
        left_margin_entry.delete(0, tk.END)
        left_margin_entry.insert(0, "50")
        right_margin_entry.delete(0, tk.END)
        right_margin_entry.insert(0, "500")

    save_button = tk.Button(settings_window, text="Save", command=save_settings)
    save_button.grid(row=3, column=0, pady=10)

    reset_button = tk.Button(settings_window, text="Reset to Default", command=reset_to_default)
    reset_button.grid(row=3, column=1, pady=10)

# Create the main application window
root = tk.Tk()
root.title("PDF Scanner")

# Create a button to select the PDF file
select_button = tk.Button(root, text="Select PDF File", command=select_file)
select_button.pack(pady=10)

# Create a button to scan the selected PDF file (initially hidden)
scan_button = tk.Button(root, text="Scan", command=scan_file, 
                        bg="blue", fg="white", font=("Helvetica", 12, "bold"), 
                        relief=tk.RAISED, bd=5)

# Create a label to display the selected file path
file_label = tk.Label(root, text="No file selected")
file_label.pack(pady=10)

# Create a frame to hold the clear button and align it to the right
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, pady=10)

# Create a button to clear the output and place it in the frame
clear_button = tk.Button(button_frame, text="Clear", command=clear_output)
clear_button.pack(side=tk.RIGHT, padx=30)

# Create a button to open the settings window and place it in the frame
settings_button = tk.Button(button_frame, text="Settings", command=open_settings)
settings_button.pack(side=tk.RIGHT, padx=30)

# Create a frame to hold the scrolled text widget and horizontal scrollbar
output_frame = tk.Frame(root)
output_frame.pack(pady=10)

# Create a horizontal scrollbar
h_scrollbar = tk.Scrollbar(output_frame, orient=tk.HORIZONTAL)
h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

# Create a scrolled text widget to display the output
output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.NONE, width=80, height=20, xscrollcommand=h_scrollbar.set)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Configure the horizontal scrollbar
h_scrollbar.config(command=output_text.xview)

# Run the application
root.mainloop()