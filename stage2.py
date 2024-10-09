import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import pyperclip
from spellchecker import SpellChecker

def remove_page_numbers(text):
    # Remove standalone digits or digit groups surrounded by spaces
    text = re.sub(r'\s+\d+\s+', ' ', text)
    
    # Remove digits at the end of a line
    text = re.sub(r'\s+\d+$', '', text)
    
    # Preserve numbers after words containing 'chap', 'part', or 'sect'
    words = text.split()
    result = []
    skip_next = False
    for i, word in enumerate(words):
        if skip_next:
            skip_next = False
            continue
        if re.match(r'\d+$', word) and i > 0:
            prev_word = words[i-1].lower()
            if any(indicator in prev_word for indicator in ['chap', 'part', 'sect']):
                result.append(words[i-1])
                result.append(word)
                skip_next = True
            else:
                continue
        else:
            result.append(word)
    
    return ' '.join(result).strip()

def remove_ocr_artifacts(text):
    # Remove single non-letter, non-digit characters
    text = re.sub(r'(?<!\w)[\W_](?!\w)', ' ', text)
    
    # Remove groups of 2-3 non-letter, non-digit characters
    text = re.sub(r'(?<!\w)[\W_]{2,3}(?!\w)', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def process_text(text):
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        line = remove_page_numbers(line)
        line = remove_ocr_artifacts(line)
        if line:
            processed_lines.append(line)
    
    return processed_lines

class TextProcessorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Text Processor")
        self.spell_checker = SpellChecker()

        self.create_widgets()
        self.undo_stack = []

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # File selection and processing frame
        file_frame = ttk.Frame(main_frame, padding="5")
        file_frame.grid(column=0, row=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.select_file_button = ttk.Button(file_frame, text="Select File", command=self.select_file)
        self.select_file_button.grid(column=0, row=0, padx=5)
        
        self.process_button = ttk.Button(file_frame, text="Process Text", command=self.process_file)
        self.process_button.grid(column=1, row=0, padx=5)

        # Text area
        self.text_area = tk.Text(main_frame, wrap=tk.WORD, width=80, height=30)
        self.text_area.grid(column=0, row=1, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.text_area.yview)
        scrollbar.grid(column=3, row=1, sticky=(tk.N, tk.S))
        self.text_area.configure(yscrollcommand=scrollbar.set)

        # Control buttons frame
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.grid(column=0, row=2, columnspan=3, sticky=(tk.W, tk.E))
        
        self.author_button = ttk.Button(control_frame, text="Mark as Author", command=self.toggle_author_mode)
        self.author_button.grid(column=0, row=0, padx=5)
        
        self.title_button = ttk.Button(control_frame, text="Mark as Title", command=self.toggle_title_mode)
        self.title_button.grid(column=1, row=0, padx=5)
        
        self.undo_button = ttk.Button(control_frame, text="Undo", command=self.undo_action)
        self.undo_button.grid(column=2, row=0, padx=5)
        
        self.copy_button = ttk.Button(control_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.grid(column=3, row=0, padx=5)

        self.author_mode = False
        self.title_mode = False

        # Configure tags for highlighting
        self.text_area.tag_configure("misspelled", underline=True, foreground="red")
        self.text_area.tag_configure("author", background="lightgreen")
        self.text_area.tag_configure("title", background="lightblue")

        # Bind events
        self.text_area.bind("<KeyRelease>", self.check_spelling)
        self.text_area.bind("<space>", self.check_spelling)

    def select_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.filename:
            self.select_file_button.config(text=f"Selected: {self.filename.split('/')[-1]}")

    def process_file(self):
        if hasattr(self, 'filename'):
            with open(self.filename, 'r', encoding='utf-8') as file:
                text = file.read()
            processed_lines = process_text(text)
            self.text_area.delete('1.0', tk.END)
            for line in processed_lines:
                self.text_area.insert(tk.END, line + '\n')
            self.check_spelling()
            self.highlight_separators()

    def toggle_author_mode(self):
        self.author_mode = not self.author_mode
        self.title_mode = False
        if self.author_mode:
            self.author_button.config(text="Author Mode: ON")
            self.title_button.config(text="Mark as Title")
            self.text_area.config(cursor="pencil")
            self.text_area.bind('<Button-1>', self.mark_author)
        else:
            self.author_button.config(text="Mark as Author")
            self.text_area.config(cursor="")
            self.text_area.unbind('<Button-1>')

    def toggle_title_mode(self):
        self.title_mode = not self.title_mode
        self.author_mode = False
        if self.title_mode:
            self.title_button.config(text="Title Mode: ON")
            self.author_button.config(text="Mark as Author")
            self.text_area.config(cursor="cross")
            self.text_area.bind('<Button-1>', self.mark_title)
        else:
            self.title_button.config(text="Mark as Title")
            self.text_area.config(cursor="")
            self.text_area.unbind('<Button-1>')

    def mark_author(self, event):
        self.mark_line(event, " / ", " -- ", is_title=False)

    def mark_title(self, event):
        self.mark_line(event, "", " -- ", is_title=True)

    def mark_line(self, event, prefix, suffix, is_title):
        # Store the current state for undo
        current_state = self.text_area.get('1.0', tk.END)
        self.undo_stack.append(current_state)

        index = self.text_area.index(f"@{event.x},{event.y}")
        line_start = self.text_area.index(f"{index} linestart")
        line_end = self.text_area.index(f"{index} lineend")
        line = self.text_area.get(line_start, line_end)

        if is_title:
            # Remove line break from previous line
            prev_line_end = self.text_area.index(f"{line_start}-1c")
            prev_line_start = self.text_area.index(f"{prev_line_end} linestart")
            prev_line = self.text_area.get(prev_line_start, prev_line_end)
            
            self.text_area.delete(prev_line_start, line_end)
            self.text_area.insert(prev_line_start, f"{prev_line.rstrip()} {line.strip()}{suffix}")
        else:
            if not line.startswith(prefix):
                self.text_area.delete(line_start, line_end)
                self.text_area.insert(line_start, f"{prefix}{line.strip()}{suffix}")

            # Remove line break and extra spaces from previous line
            prev_line_end = self.text_area.index(f"{line_start}-1c")
            prev_line_start = self.text_area.index(f"{prev_line_end} linestart")
            prev_line = self.text_area.get(prev_line_start, prev_line_end)
            self.text_area.delete(prev_line_start, line_start)
            self.text_area.insert(prev_line_start, prev_line.rstrip())

        self.check_spelling()
        self.highlight_separators()

    def undo_action(self):
        if self.undo_stack:
            previous_state = self.undo_stack.pop()
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', previous_state)
            self.check_spelling()
            self.highlight_separators()

    def copy_to_clipboard(self):
        text = self.text_area.get('1.0', tk.END)
        pyperclip.copy(text)
        tk.messagebox.showinfo("Copied", "Text has been copied to clipboard!")

    def check_spelling(self, event=None):
        self.text_area.tag_remove("misspelled", "1.0", tk.END)
        content = self.text_area.get("1.0", tk.END)
        words = re.findall(r'\b\w+\b', content)
        misspelled = self.spell_checker.unknown(words)
        for word in misspelled:
            start = "1.0"
            while True:
                start = self.text_area.search(r'\m{}\M'.format(word), start, tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                self.text_area.tag_add("misspelled", start, end)
                start = end

    def highlight_separators(self):
        self.text_area.tag_remove("author", "1.0", tk.END)
        self.text_area.tag_remove("title", "1.0", tk.END)
        content = self.text_area.get("1.0", tk.END)
        author_pattern = r' / '
        title_pattern = r' -- '
        
        start = "1.0"
        while True:
            author_start = self.text_area.search(author_pattern, start, tk.END)
            if not author_start:
                break
            author_end = f"{author_start}+{len(author_pattern)}c"
            self.text_area.tag_add("author", author_start, author_end)
            start = author_end

        start = "1.0"
        while True:
            title_start = self.text_area.search(title_pattern, start, tk.END)
            if not title_start:
                break
            title_end = f"{title_start}+{len(title_pattern)}c"
            self.text_area.tag_add("title", title_start, title_end)
            start = title_end

def main():
    root = tk.Tk()
    app = TextProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()