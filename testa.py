import tkinter as tk
from tkinter import filedialog, messagebox
import re

class TextEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple Text Editor")
        self.master.geometry("600x400")

        self.text_lines = []
        self.line_types = []

        self.create_widgets()

    def create_widgets(self):
        self.text_frame = tk.Frame(self.master)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.text_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(self.text_frame, yscrollcommand=self.scrollbar.set)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.text_widget.yview)

        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(fill=tk.X)

        self.open_button = tk.Button(self.button_frame, text="Open File", command=self.open_file)
        self.open_button.pack(side=tk.LEFT)

        self.author_button = tk.Button(self.button_frame, text="Set as Author", command=lambda: self.set_line_type("author"))
        self.author_button.pack(side=tk.LEFT)

        self.title_button = tk.Button(self.button_frame, text="Set as Title", command=lambda: self.set_line_type("title"))
        self.title_button.pack(side=tk.LEFT)

        self.complete_button = tk.Button(self.button_frame, text="Complete", command=self.complete)
        self.complete_button.pack(side=tk.LEFT)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                self.text_lines = file.read().splitlines()
                self.line_types = ["normal"] * len(self.text_lines)
                self.update_text_widget()

    def update_text_widget(self):
        self.text_widget.delete(1.0, tk.END)
        for i, (line, line_type) in enumerate(zip(self.text_lines, self.line_types)):
            if line_type == "author":
                self.text_widget.insert(tk.END, f" / {line} -- \n")
            elif line_type == "title":
                self.text_widget.insert(tk.END, f" -- {line} -- \n")
            else:
                self.text_widget.insert(tk.END, f"{line}\n")

    def set_line_type(self, line_type):
        try:
            current_line = int(self.text_widget.index(tk.INSERT).split('.')[0]) - 1
            self.line_types[current_line] = line_type
            self.update_text_widget()
        except IndexError:
            messagebox.showerror("Error", "No line selected or file is empty.")

    def complete(self):
        result = []
        for line, line_type in zip(self.text_lines, self.line_types):
            if line_type == "author":
                result.append(f" / {line} -- ")
            elif line_type == "title":
                result.append(f" -- {line} -- ")
            else:
                result.append(line)

        final_text = " ".join(result)
        final_text = re.sub(r'(\s*--\s*)+', ' -- ', final_text)
        final_text = re.sub(r'(\s*/\s*)+', ' / ', final_text)
        final_text = re.sub(r'\s*--\s*/\s*', ' / ', final_text)
        final_text = re.sub(r'\s*/\s*--\s*', ' / ', final_text)

        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, final_text)

if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()