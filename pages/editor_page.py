from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QFileDialog,
    QToolBar,
    QMessageBox,
    QSplitter,
)

import markdown


class MarkdownEditor(QWidget):

    def __init__(self):
        super().__init__()

        self.current_file = None

        self.build_ui()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(self)

        self.toolbar = QToolBar()

        layout.addWidget(self.toolbar)

        self.create_toolbar()

        splitter = QSplitter(Qt.Horizontal)

        self.editor = QTextEdit()
        self.preview = QTextEdit()

        self.preview.setReadOnly(True)

        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)

        splitter.setSizes([700, 700])

        layout.addWidget(splitter)

        self.editor.textChanged.connect(self.update_preview)

    # ---------------------------------------------------------
    # Toolbar
    # ---------------------------------------------------------

    def create_toolbar(self):

        self.toolbar.addAction(QAction("Open", self))
        self.toolbar.actions()[-1].triggered.connect(self.open_markdown)

        self.toolbar.addAction(QAction("Save", self))
        self.toolbar.actions()[-1].triggered.connect(self.save_markdown)

        self.toolbar.addSeparator()

        self.toolbar.addAction(QAction("B", self))
        self.toolbar.actions()[-1].triggered.connect(
            lambda: self.wrap_selection("**", "**")
        )

        self.toolbar.addAction(QAction("I", self))
        self.toolbar.actions()[-1].triggered.connect(
            lambda: self.wrap_selection("*", "*")
        )

        self.toolbar.addAction(QAction("Code", self))
        self.toolbar.actions()[-1].triggered.connect(
            lambda: self.wrap_selection("```python\n", "\n```")
        )

        self.toolbar.addSeparator()

        self.toolbar.addAction(QAction("H1", self))
        self.toolbar.actions()[-1].triggered.connect(
            lambda: self.insert_prefix("# ")
        )

        self.toolbar.addAction(QAction("H2", self))
        self.toolbar.actions()[-1].triggered.connect(
            lambda: self.insert_prefix("## ")
        )

        self.toolbar.addAction(QAction("Bullet", self))
        self.toolbar.actions()[-1].triggered.connect(
            lambda: self.insert_prefix("- ")
        )

        self.toolbar.addSeparator()

        self.toolbar.addAction(QAction("Equation", self))
        self.toolbar.actions()[-1].triggered.connect(
            self.insert_equation
        )

        self.toolbar.addAction(QAction("Image", self))
        self.toolbar.actions()[-1].triggered.connect(
            self.insert_image
        )

        self.toolbar.addAction(QAction("PDF", self))
        self.toolbar.actions()[-1].triggered.connect(
            self.insert_pdf
        )

        self.toolbar.addAction(QAction("Citation", self))
        self.toolbar.actions()[-1].triggered.connect(
            self.insert_citation
        )

    # ---------------------------------------------------------
    # Markdown Preview
    # ---------------------------------------------------------

    def update_preview(self):

        text = self.editor.toPlainText()

        html = markdown.markdown(
            text,
            extensions=[
                "tables",
                "fenced_code"
            ]
        )

        self.preview.setHtml(html)

    # ---------------------------------------------------------
    # Formatting
    # ---------------------------------------------------------

    def wrap_selection(self, before, after):

        cursor = self.editor.textCursor()

        text = cursor.selectedText()

        cursor.insertText(before + text + after)

    def insert_prefix(self, prefix):

        cursor = self.editor.textCursor()

        cursor.movePosition(QTextCursor.StartOfLine)

        cursor.insertText(prefix)

    # ---------------------------------------------------------
    # Equation
    # ---------------------------------------------------------

    def insert_equation(self):

        cursor = self.editor.textCursor()

        cursor.insertText(

"""$$

Your Equation

$$
"""
        )

    # ---------------------------------------------------------
    # Image
    # ---------------------------------------------------------

    def insert_image(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if filename:

            name = Path(filename).name

            cursor = self.editor.textCursor()

            cursor.insertText(
                f"\n![](images/{name})\n"
            )

    # ---------------------------------------------------------
    # PDF
    # ---------------------------------------------------------

    def insert_pdf(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF",
            "",
            "PDF (*.pdf)"
        )

        if filename:

            name = Path(filename).name

            cursor = self.editor.textCursor()

            cursor.insertText(
                f"\n[{name}](pdf/{name})\n"
            )

    # ---------------------------------------------------------
    # Citation
    # ---------------------------------------------------------

    def insert_citation(self):

        cursor = self.editor.textCursor()

        cursor.insertText(
            "[@citation_key]"
        )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    def save_markdown(self):

        if self.current_file is None:

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Markdown",
                "",
                "Markdown (*.md)"
            )

            if not filename:
                return

            self.current_file = filename

        with open(self.current_file, "w", encoding="utf-8") as f:

            f.write(
                self.editor.toPlainText()
            )

        QMessageBox.information(
            self,
            "Saved",
            "Markdown file saved successfully."
        )

    # ---------------------------------------------------------
    # Open
    # ---------------------------------------------------------

    def open_markdown(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown",
            "",
            "Markdown (*.md)"
        )

        if not filename:
            return

        self.current_file = filename

        with open(filename, "r", encoding="utf-8") as f:

            self.editor.setPlainText(
                f.read()
            )