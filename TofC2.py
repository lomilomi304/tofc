import tkinter as tk
from tkinter import ttk
import re

class TextManipulationGUI:
    def __init__(self, master):
        self.master = master
        master.title("Text Manipulation GUI")
        master.geometry("1200x600")  # Wider initial window to accommodate split view
        
        # Configure the style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('Header.TFrame', background='#2c3e50')
        self.style.configure('Content.TFrame', background='#ffffff')
        
        # Configure regular button style
        self.style.configure('TButton', 
                           padding=6,
                           font=('Segoe UI', 9))
        
        # Configure action button style (for primary actions)
        self.style.configure('Action.TButton',
                           padding=6,
                           font=('Segoe UI', 9, 'bold'))
        
        # Configure separator button styles with colors
        self.style.configure('Slash.TButton',
                           padding=4,
                           width=3,
                           font=('Segoe UI', 8),
                           background='#e0f0ff')  # Light blue
        
        self.style.configure('Dash.TButton',
                           padding=4,
                           width=3,
                           font=('Segoe UI', 8),
                           background='#e0ffe0')  # Light green
        
        self.style.configure('Clear.TButton',
                           padding=4,
                           width=3,
                           font=('Segoe UI', 8),
                           background='#ffe0e0')  # Light red
        
        # Configure label style
        self.style.configure('TLabel',
                           font=('Segoe UI', 10),
                           background='#f0f0f0',
                           foreground='#2c3e50')
        
        self.current_stage = 0
        self.stages = [
            self.create_input_stage,
            self.create_separate_stage,
            self.create_output_stage
        ]

        # Create main container with padding
        self.main_frame = ttk.Frame(master, style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.stored_text = ""
        self.lines_data = []
        self.removed_lines = []  # Store removed lines for undo functionality
        self.preview_window = None  
        self.create_input_stage()
    def undo_action(self):
        if self.removed_lines:
            last_action = self.removed_lines.pop()
            if last_action["type"] == "remove":
                self.lines_data.insert(last_action["index"], last_action["data"])
            elif last_action["type"] == "separator":
                self.lines_data[last_action["index"]]["separator"] = last_action["data"]
            self.refresh_view()
    def sentence_case(self, text):
        """Convert text to sentence case, including after colons"""
        if not text:
            return text
            
        # Split by colon and process each part
        parts = text.split(':')
        processed_parts = []
        
        for i, part in enumerate(parts):
            if not part.strip():
                processed_parts.append(part)
                continue
                
            # Convert to lowercase first
            part = part.lower()
            
            # Capitalize first letter if it exists
            if len(part) > 0:
                # Find the first letter character
                match = re.search(r'[a-zA-Z]', part)
                if match:
                    idx = match.start()
                    part = part[:idx] + part[idx].upper() + part[idx + 1:]
            
            processed_parts.append(part)
        
        return ':'.join(processed_parts)

    def clear_frame(self):
        self.master.unbind_all("<MouseWheel>")
        
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def configure_text_widget(self, text_widget):
        """Configure common text widget properties"""
        text_widget.configure(
            font=('Segoe UI', 10),
            selectbackground='#3498db',
            selectforeground='white',
            padx=8,
            pady=8,
            background='white',
            foreground='#2c3e50',
            relief=tk.FLAT,
            borderwidth=1
        )

    def remove_chapters(self):
        """Remove lines that contain only the word 'chapter' followed by non-letter characters"""
        text = self.text_input.get("1.0", tk.END).strip()
        lines = text.split('\n')
        filtered_lines = [line for line in lines if not re.match(r'^\s*chapter\s*[^a-zA-Z]*$', line, re.IGNORECASE)]
        filtered_text = '\n'.join(filtered_lines)
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, filtered_text)
            
    def create_preview_window(self):
        """Create a separate window for preview"""
        if self.preview_window is None or not self.preview_window.winfo_exists():
            self.preview_window = tk.Toplevel(self.master)
            self.preview_window.title("Preview")
            self.preview_window.geometry("400x200")
            
            preview_label = ttk.Label(self.preview_window,
                                    text="Preview",
                                    font=('Segoe UI', 11, 'bold'))
            preview_label.pack(padx=10, pady=(10, 5))
            
            self.preview_text = tk.Text(self.preview_window, height=8, wrap=tk.WORD)
            self.configure_text_widget(self.preview_text)
            self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))


    def create_input_stage(self):
        self.clear_frame()
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
        
        # Header
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_label = ttk.Label(header_frame, 
                               text="Input Text",
                               font=('Segoe UI', 12, 'bold'),
                               foreground='white',
                               background='#2c3e50')
        header_label.pack(pady=10)

        # Text input area with border
        input_container = ttk.Frame(self.main_frame, style='Content.TFrame')
        input_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.text_input = tk.Text(input_container, wrap=tk.WORD)
        self.configure_text_widget(self.text_input)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        clean_button = ttk.Button(button_frame, 
                                text="Clean Text",
                                style='TButton',
                                command=self.clean_text)
        clean_button.pack(side=tk.LEFT, padx=5)

        remove_chapters_button = ttk.Button(button_frame,
                                            text="Remove Chapters",
                                            style='TButton',
                                            command=self.remove_chapters)
        remove_chapters_button.pack(side=tk.LEFT, padx=5)

        next_button = ttk.Button(button_frame,
                               text="Separate Lines",
                               style='Action.TButton',
                               command=self.next_stage)
        next_button.pack(side=tk.RIGHT, padx=5)

    def create_separate_stage(self):
        self.clear_frame()
        
        # Create a PanedWindow for split view
        paned_window = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, 
                                    sashwidth=4, sashrelief=tk.RAISED)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left side (main content)
        left_frame = ttk.Frame(paned_window, style='TFrame')
        
        # Header
        header_frame = ttk.Frame(left_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_label = ttk.Label(header_frame,
                            text="Separate Lines",
                            font=('Segoe UI', 12, 'bold'),
                            foreground='white',
                            background='#2c3e50')
        header_label.pack(pady=10)
        
        # Create main container with scrollbar
        container = ttk.Frame(left_frame, style='Content.TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(container, background='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # Create frame for content
        self.lines_frame = ttk.Frame(canvas, style='Content.TFrame')
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas for content
        canvas_window = canvas.create_window((0, 0), window=self.lines_frame, 
                                        anchor="nw", width=canvas.winfo_reqwidth())
        
        # Configure mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Handle canvas resize
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.lines_frame.bind('<Configure>', configure_scroll_region)
        
        def configure_window_size(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', configure_window_size)

        # Initialize or use existing lines_data
        if not self.lines_data:
            lines = self.stored_text.split('\n')
            self.lines_data = [{"text": line.strip(), "separator": ""} for line in lines if line.strip()]

        # Create undo button at the top
        undo_frame = ttk.Frame(self.lines_frame, style='Content.TFrame')
        undo_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def undo_remove():
            if self.removed_lines:
                last_line = self.removed_lines.pop()
                self.lines_data.insert(last_line["index"], last_line["data"])
                self.refresh_view()
        
        undo_btn = ttk.Button(undo_frame, text="Undo Remove",
                            style='TButton', command=undo_remove)
        undo_btn.pack(side=tk.RIGHT, padx=5)

        # Helper function to convert text to title case
        def to_title_case(text):
            exceptions = ["and", "or", "but", "nor", "so", "for", "yet", "a", "an", "the", "in", "on", "at", "to", "by", "with", "of"]
            words = text.split()
            title_cased = [word.capitalize() if word.lower() not in exceptions else word.lower() for word in words]
            return ' '.join(title_cased)

        # Create widgets for each line
        for i, line_data in enumerate(self.lines_data):
            line_frame = ttk.Frame(self.lines_frame, style='Content.TFrame')
            line_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Button frame for separator buttons
            btn_frame = ttk.Frame(line_frame, style='Content.TFrame')
            btn_frame.pack(side=tk.LEFT, padx=(0, 5))
            
            def make_separator_handler(idx, sep, color, title_case=False):
                def handler():
                    self.lines_data[idx]["separator"] = sep
                    self.lines_data[idx]["separator_color"] = color
                    if title_case:
                        self.lines_data[idx]["text"] = to_title_case(self.lines_data[idx]["text"])
                    self.update_preview()
                return handler
            
            def make_remove_handler(idx):
                def handler():
                    removed_line = {"index": idx, "data": self.lines_data[idx]}
                    self.removed_lines.append(removed_line)
                    del self.lines_data[idx]
                    self.refresh_view()
                return handler
            
            # Only show separator buttons for lines after the first one
            if i > 0:
                slash_btn = ttk.Button(btn_frame, text="/",
                                    style='Slash.TButton',
                                    command=make_separator_handler(i, " / ", '#91c3f1', title_case=True))
                slash_btn.pack(side=tk.LEFT, padx=2)
                
                dash_btn = ttk.Button(btn_frame, text="--",
                                    style='Dash.TButton',
                                    command=make_separator_handler(i, " -- ", '#9be89b'))
                dash_btn.pack(side=tk.LEFT, padx=2)
            
            clear_btn = ttk.Button(btn_frame, text="×",
                                style='Clear.TButton',
                                command=make_remove_handler(i))
            clear_btn.pack(side=tk.LEFT, padx=2)

            # Text display
            text_display = tk.Text(line_frame, height=2, wrap=tk.WORD)
            self.configure_text_widget(text_display)
            text_display.insert(tk.END, line_data["text"])
            text_display.configure(state='disabled')
            text_display.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Navigation buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=10)

        back_button = ttk.Button(button_frame,
                            text="Back",
                            style='TButton',
                            command=self.previous_stage)
        back_button.pack(side=tk.LEFT, padx=5)

        next_button = ttk.Button(button_frame,
                            text="Join Lines",
                            style='Action.TButton',
                            command=self.next_stage)
        next_button.pack(side=tk.RIGHT, padx=5)
        
        # Right side (preview)
        right_frame = ttk.Frame(paned_window, style='TFrame')
        
        preview_label = ttk.Label(right_frame,
                                text="Preview",
                                font=('Segoe UI', 11, 'bold'))
        preview_label.pack(padx=10, pady=(10, 5))
        
        self.preview_text = tk.Text(right_frame, wrap=tk.WORD)
        self.configure_text_widget(self.preview_text)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Add both sides to the paned window with specific weights
        paned_window.add(left_frame, width=600)  # Set initial width for left pane
        paned_window.add(right_frame, width=400)  # Set initial width for right pane
        
        # Store the paned window reference
        self.paned_window = paned_window
        
        # Set initial position of the separator
        def set_initial_sash_position(event=None):
            window_width = self.master.winfo_width()
            sash_position = int(window_width * 0.6)  # 60% of window width
            self.paned_window.sash_place(0, sash_position, 0)
            if event:
                self.master.unbind('<Map>')
        
        # Bind to window mapping event
        self.master.bind('<Map>', set_initial_sash_position)
        # Call immediately in case window is already mapped
        self.master.after(10, set_initial_sash_position)
        
        # Update preview initially
        self.update_preview()

    def refresh_view(self):
        """Refresh the separate stage view while maintaining sash position"""
        if hasattr(self, 'paned_window'):
            current_sash_position = self.paned_window.sash_coord(0)[0]
            self.create_separate_stage()
            self.paned_window.after(10, lambda: self.paned_window.sash_place(0, current_sash_position, 0))

    def update_preview(self):
        self.preview_text.configure(state='normal')
        self.preview_text.delete(1.0, tk.END)
        
        for i, line_data in enumerate(self.lines_data):
            if i > 0 and line_data["separator"]:
                # Add separator with background color
                start_index = self.preview_text.index("end-1c")
                self.preview_text.insert(tk.END, line_data["separator"])
                end_index = self.preview_text.index("end-1c")
                if "separator_color" in line_data and line_data["separator_color"]:
                    self.preview_text.tag_add(f"sep_{i}", start_index, end_index)
                    self.preview_text.tag_configure(f"sep_{i}", background=line_data["separator_color"])
            
            self.preview_text.insert(tk.END, line_data["text"])
        
        self.preview_text.configure(state='disabled')
        
    def create_output_stage(self):
        self.clear_frame()
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.destroy()
        
        # Header
        header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_label = ttk.Label(header_frame,
                            text="Final Text",
                            font=('Segoe UI', 12, 'bold'),
                            foreground='white',
                            background='#2c3e50')
        header_label.pack(pady=10)
        
        # Result text area
        result_container = ttk.Frame(self.main_frame, style='Content.TFrame')
        result_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.result_text = tk.Text(result_container, wrap=tk.WORD)
        self.configure_text_widget(self.result_text)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        final_text = ""
        for i, line_data in enumerate(self.lines_data):
            if i > 0 and line_data["separator"]:
                final_text += line_data["separator"]
            final_text += line_data["text"]
        
        # Add period if not already present
        if not final_text.rstrip().endswith('.'):
            final_text += '.'
        
        self.result_text.insert(tk.END, final_text)

        # Navigation buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        back_button = ttk.Button(button_frame,
                            text="Back",
                            style='TButton',
                            command=self.previous_stage)
        back_button.pack(side=tk.LEFT, padx=5)

        new_button = ttk.Button(button_frame,
                            text="New",
                            style='Action.TButton',
                            command=self.reset_app)
        new_button.pack(side=tk.RIGHT, padx=5)

    def reset_app(self):
        # Reset all stored data
        self.stored_text = ""
        self.lines_data = []
        self.removed_lines = []
        self.current_stage = 0
        
        # Return to input stage
        self.create_input_stage()
        
    def is_roman_numeral(self, text):
        """Check if a string is a valid roman numeral"""
        pattern = r'^[MDCLXVI]+$'
        return bool(re.match(pattern, text.upper()))

    def clean_text(self):
        """Clean the input text by removing unwanted characters and lines"""
        text = self.text_input.get("1.0", tk.END).strip()
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            words = line.split()
            cleaned_words = []
            skip_next = False

            for i, word in enumerate(words):
                if skip_next:
                    skip_next = False
                    continue
                # Check for standalone roman numerals
                if self.is_roman_numeral(word):
                    continue

                # Check for numbers after chapter-related words
                if word.isdigit() and i > 0:
                    prev_word = words[i-1].lower()
                    if not any(keyword in prev_word for keyword in ['chap', 'part', 'section', 'unit']):
                        continue

                cleaned_words.append(word)

            # Join words and apply sentence casing
            if cleaned_words:
                cleaned_line = ' '.join(cleaned_words)
                cleaned_line = self.sentence_case(cleaned_line)
                # Check if the cleaned line contains only non-letter characters
                if re.search('[a-zA-Z]', cleaned_line):
                    cleaned_lines.append(cleaned_line)

        cleaned_text = '\n'.join(cleaned_lines)
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, cleaned_text)

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