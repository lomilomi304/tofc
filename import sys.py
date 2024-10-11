import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QButtonGroup, QRadioButton
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor, QKeySequence, QSyntaxHighlighter
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtWidgets import QShortcut

class SeparatorHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        separator_format = QTextCharFormat()
        separator_format.setBackground(QColor("lightgreen"))
        self.highlighting_rules.append((QRegExp(r' -- '), separator_format))

        author_format = QTextCharFormat()
        author_format.setBackground(QColor("lightblue"))
        self.highlighting_rules.append((QRegExp(r' / '), author_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_mode = "Normal"
        self.undo_stack = []
        self.redo_stack = []

    def initUI(self):
        self.setWindowTitle('Text Editor')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Text area
        self.textEdit = QTextEdit()
        self.textEdit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.textEdit)

        # Initialize syntax highlighter
        self.highlighter = SeparatorHighlighter(self.textEdit.document())

        # Buttons
        button_layout = QHBoxLayout()

        self.selectFileBtn = QPushButton('Select File')
        self.selectFileBtn.clicked.connect(self.select_file)
        button_layout.addWidget(self.selectFileBtn)

        self.processBtn = QPushButton('Process Text')
        self.processBtn.clicked.connect(self.process_text)
        button_layout.addWidget(self.processBtn)

        self.undoBtn = QPushButton('Undo')
        self.undoBtn.clicked.connect(self.undo_action)
        button_layout.addWidget(self.undoBtn)

        self.redoBtn = QPushButton('Redo')
        self.redoBtn.clicked.connect(self.redo_action)
        button_layout.addWidget(self.redoBtn)

        self.copyBtn = QPushButton('Copy to Clipboard')
        self.copyBtn.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copyBtn)

        layout.addLayout(button_layout)

        # Mode selection
        mode_layout = QHBoxLayout()
        self.modeGroup = QButtonGroup()

        self.normalModeBtn = QRadioButton('Normal Edit')
        self.normalModeBtn.setChecked(True)
        self.normalModeBtn.toggled.connect(self.mode_changed)
        self.modeGroup.addButton(self.normalModeBtn)
        mode_layout.addWidget(self.normalModeBtn)

        self.titleModeBtn = QRadioButton('Title Mode')
        self.titleModeBtn.toggled.connect(self.mode_changed)
        self.modeGroup.addButton(self.titleModeBtn)
        mode_layout.addWidget(self.titleModeBtn)

        self.authorModeBtn = QRadioButton('Author Mode')
        self.authorModeBtn.toggled.connect(self.mode_changed)
        self.modeGroup.addButton(self.authorModeBtn)
        mode_layout.addWidget(self.authorModeBtn)

        layout.addLayout(mode_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo_action)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.redo_action)
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.toggle_mode("Title"))
        QShortcut(QKeySequence("Ctrl+R"), self, lambda: self.toggle_mode("Author"))
        QShortcut(QKeySequence("Ctrl+E"), self, lambda: self.toggle_mode("Normal"))

        # Connect mouse release event
        self.textEdit.mouseReleaseEvent = self.handle_click

    def toggle_mode(self, mode):
        if mode == "Normal":
            self.normalModeBtn.setChecked(True)
        elif mode == "Title":
            self.titleModeBtn.setChecked(True)
        elif mode == "Author":
            self.authorModeBtn.setChecked(True)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as file:
                self.textEdit.setText(file.read())

    def process_text(self):
        self.save_for_undo()
        text = self.textEdit.toPlainText()
        lines = text.split('\n')
        processed_lines = []

        for line in lines:
            line = line.strip()
            words = line.split()
            new_words = []
            for i, word in enumerate(words):
                if word.isdigit():
                    if i > 0 and any(s in words[i-1].lower() for s in ['chap', 'par', 'sec']):
                        new_words.append(word)
                else:
                    new_words.append(word)
            
            processed_line = ' '.join(new_words)
            
            if processed_line:
                processed_lines.append(processed_line)

        processed_text = '\n'.join(processed_lines)
        
        if processed_text != text:
            self.textEdit.setText(processed_text)
        else:
            print("No changes were made during processing.")

    def handle_click(self, event):
        if event.button() == Qt.LeftButton and self.current_mode != "Normal":
            cursor = self.textEdit.cursorForPosition(event.pos())
            cursor.select(QTextCursor.LineUnderCursor)
            line_number = cursor.blockNumber()
            
            self.save_for_undo()
            
            if self.current_mode == "Title":
                self.handle_title_mode(line_number)
            elif self.current_mode == "Author":
                self.handle_author_mode(line_number)
        
        QTextEdit.mouseReleaseEvent(self.textEdit, event)

    def handle_title_mode(self, line_number):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_number)

        cursor.select(QTextCursor.LineUnderCursor)
        current_line = cursor.selectedText().strip()

        if line_number > 0:
            cursor.movePosition(QTextCursor.Up)
            cursor.select(QTextCursor.LineUnderCursor)
            prev_line = cursor.selectedText()
            
            if prev_line.endswith(" -- "):
                new_line = current_line + " -- "
                cursor.movePosition(QTextCursor.Down)
                cursor.select(QTextCursor.LineUnderCursor)
                cursor.insertText(new_line)
                cursor.movePosition(QTextCursor.Up)
                cursor.movePosition(QTextCursor.EndOfLine)
                cursor.deleteChar()
            else:
                new_line = " -- " + current_line + " -- "
                cursor.movePosition(QTextCursor.Down)
                cursor.select(QTextCursor.LineUnderCursor)
                cursor.insertText(new_line)
                cursor.movePosition(QTextCursor.Up)
                cursor.movePosition(QTextCursor.EndOfLine)
                cursor.deleteChar()
        else:
            new_line = " -- " + current_line + " -- "
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.insertText(new_line)

    def handle_author_mode(self, line_number):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_number)

        cursor.select(QTextCursor.LineUnderCursor)
        current_line = cursor.selectedText().strip()

        if not current_line.startswith(" / "):
            current_line = " / " + current_line
        if not current_line.endswith(" -- "):
            current_line += " -- "
        
        cursor.insertText(current_line)

        if line_number > 0:
            cursor.movePosition(QTextCursor.Up)
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.deleteChar()

        cursor.movePosition(QTextCursor.EndOfLine)
        self.textEdit.setTextCursor(cursor)

    def mode_changed(self):
        if self.normalModeBtn.isChecked():
            self.current_mode = "Normal"
        elif self.titleModeBtn.isChecked():
            self.current_mode = "Title"
        else:
            self.current_mode = "Author"

    def on_text_changed(self):
        # The highlighter will automatically update when the text changes
        pass

    def save_for_undo(self):
        self.undo_stack.append(self.textEdit.toPlainText())
        self.redo_stack.clear()

    def undo_action(self):
        if self.undo_stack:
            current_state = self.textEdit.toPlainText()
            self.redo_stack.append(current_state)
            self.textEdit.setText(self.undo_stack.pop())

    def redo_action(self):
        if self.redo_stack:
            current_state = self.textEdit.toPlainText()
            self.undo_stack.append(current_state)
            self.textEdit.setText(self.redo_stack.pop())

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.textEdit.toPlainText())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextEditor()
    ex.show()
    sys.exit(app.exec_())