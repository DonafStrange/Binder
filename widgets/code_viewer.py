from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
)

from pathlib import Path
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter
from PySide6.QtWidgets import QPushButton


class CodeViewer(QWidget):

    def __init__(self, file_path):

        super().__init__()

        self.file_path = Path(file_path)

        self.setWindowTitle(
            self.file_path.name
        )

        self.resize(
            800,
            600
        )

        layout = QVBoxLayout(
            self
        )

        self.editor = QTextEdit()

        self.editor.setReadOnly(
            False
        )

        self.editor.setAcceptRichText(
            True
        )

        layout.addWidget(
            self.editor
        )

        self.save_button = QPushButton(
            "Save"
        )

        self.save_button.clicked.connect(
            self.save_code
        )

        layout.addWidget(
            self.save_button
        )

        self.load_code()


    def load_code(self):

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:

                content = file.read()


            lexer = get_lexer_for_filename(
                self.file_path.name
            )

            formatter = HtmlFormatter(
                style="monokai"
            )


            print(type(lexer))
            print(formatter)


            html = highlight(
                content,
                lexer,
                formatter
            )


            css = formatter.get_style_defs(
                ".highlight"
            )


            final_html = f"""
            <html>
            <head>

            <style>

            {css}

            body {{
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: "Courier New";
                font-size: 12pt;
            }}

            .highlight {{
                background-color: #1e1e1e;
            }}

            pre {{
                background-color: #1e1e1e;
                margin: 0;
                padding: 10px;
            }}

            </style>

            </head>

            <body>

            {html}

            </body>
            </html>
            """


            self.editor.setHtml(
                final_html
            )
        except Exception as e:

            self.editor.setText(
                f"Error loading file:\n{e}"
            )   

    def save_code(self):

        text = self.editor.toPlainText()

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                text
            )