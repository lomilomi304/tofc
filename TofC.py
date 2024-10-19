import tkinter as tk
from tkinter import ttk
import re

class TextManipulationGUI:
    def __init__(self, master):
        self.master = master
        master.title("Text Manipulation GUI")
        master.geometry("800x600")

        self.current_stage = 0
        self.stages = [
            self.create_input_stage,
            self.create_separate_stage,
            self.create_output_stage
        ]

        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.stored_text = ""
        self.create_input_stage()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_input_stage(self):
        self.clear_frame()
        self.text_input = tk.Text(self.main_frame, wrap=tk.WORD)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        clean_button = ttk.Button(button_frame, text="Clean Text", command=self.clean_text)
        clean_button.pack(side=tk.LEFT, padx=5)

        next_button = ttk.Button(button_frame, text="Separate Lines", command=self.next_stage)
        next_button.pack(side=tk.RIGHT, padx=5)

    def create_separate_stage(self):
        self.clear_frame()
        self.lines_canvas = tk.Canvas(self.main_frame)
        self.lines_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.lines_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lines_canvas.configure(yscrollcommand=scrollbar.set)
        self.lines_frame = ttk.Frame(self.lines_canvas)
        self.lines_canvas.create_window((0, 0), window=self.lines_frame, anchor="nw")

        lines = self.stored_text.split('\n')
        for i, line in enumerate(lines):
            frame = ttk.Frame(self.lines_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)

            line_text = tk.Text(frame, height=2, wrap=tk.WORD)
            line_text.insert(tk.END, line)
            line_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

            if i < len(lines) - 1:
                separator = ttk.Entry(frame, width=5)
                separator.pack(side=tk.LEFT)

        self.lines_frame.update_idletasks()
        self.lines_canvas.configure(scrollregion=self.lines_canvas.bbox("all"))

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        back_button = ttk.Button(button_frame, text="Back", command=self.previous_stage)
        back_button.pack(side=tk.LEFT, padx=5)

        next_button = ttk.Button(button_frame, text="Join Lines", command=self.next_stage)
        next_button.pack(side=tk.RIGHT, padx=5)

    def create_output_stage(self):
        self.clear_frame()
        self.result_text = tk.Text(self.main_frame, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        joined_text = self.join_lines()
        self.result_text.insert(tk.END, joined_text)

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        back_button = ttk.Button(button_frame, text="Back", command=self.previous_stage)
        back_button.pack(side=tk.LEFT, padx=5)

    def clean_text(self):
        text = self.text_input.get("1.0", tk.END)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            words = line.split()
            cleaned_words = []
            for i, word in enumerate(words):
                if word.isdigit() and i > 0:
                    prev_word = words[i-1].lower()
                    if not any(keyword in prev_word for keyword in ['chap', 'part', 'section', 'unit']):
                        continue
                cleaned_words.append(word)
            cleaned_lines.append(' '.join(cleaned_words))
        cleaned_text = '\n'.join(cleaned_lines)
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, cleaned_text)

    def join_lines(self):
        joined_text = ""
        for frame in self.lines_frame.winfo_children():
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Text):
                    joined_text += widget.get("1.0", tk.END).strip()
                elif isinstance(widget, ttk.Entry):
                    joined_text += widget.get()
            joined_text += " "
        return joined_text.strip()

    def next_stage(self):
        if self.current_stage < len(self.stages) - 1:
            if self.current_stage == 0:
                self.stored_text = self.text_input.get("1.0", tk.END).strip()
            self.current_stage += 1
            self.stages[self.current_stage]()

    def previous_stage(self):
        if self.current_stage > 0:
            self.current_stage -= 1
            self.stages[self.current_stage]()

if __name__ == "__main__":
    root = tk.Tk()
    gui = TextManipulationGUI(root)
    root.mainloop()
