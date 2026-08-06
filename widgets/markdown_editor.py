from widgets.reference_picker import ReferencePicker
from widgets.equation_editor import EquationEditor
from PySide6.QtWidgets import QFileDialog
from services.attachment import AttachmentService
from services.work_service import WorkService
from PySide6.QtWidgets import QMenu
import subprocess
from pathlib import Path
import os
import markdown
from PySide6.QtCore import Qt, Signal, QUrl, Slot, QDir
import re
from services.reference_service import ReferenceService

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QSplitter,
)

from PySide6.QtWebEngineWidgets import QWebEngineView
#from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PySide6.QtGui import QDesktopServices
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter

from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings


class MyWebPage(QWebEnginePage):

    def acceptNavigationRequest(
        self,
        url,
        navigation_type,
        is_main_frame
    ):
#         print("CLICKED:", url.toString())
        link = url.toString()


        # -------------------------------
        # Citation PDF
        # -------------------------------

        if link.startswith("reference-pdf://"):

            key = link.replace(
                "reference-pdf://",
                ""
            )


            service = ReferenceService()

            references = service.get_all_references()


            for ref in references:

                if ref.citation_key.lower() == key.lower():

                    if ref.pdf:

                        pdf = Path(ref.pdf).resolve()

#                         print("Opening PDF:", pdf)

                        if pdf.exists():
                            subprocess.Popen(
                                [
                                    "evince",
                                    str(pdf)
                                ]
                            )

                        else:
                            # print("PDF not found:", pdf)
                            pass

                    break


            return False



        # -------------------------------
        # External URL
        # -------------------------------

        if link.startswith("reference-url://"):

            key = link.replace(
                "reference-url://",
                ""
            )


            service = ReferenceService()

            references = service.get_all_references()


            for ref in references:

                if ref.citation_key.lower() == key.lower():

                    if ref.url:

                        QDesktopServices.openUrl(
                            QUrl(ref.url)
                        )

                    break


            return False



        # Existing PDF handling
        if url.toLocalFile().lower().endswith(".pdf"):

            subprocess.Popen(
                [
                    "evince",
                    url.toLocalFile()
                ]
            )

            return False


        return True

class MarkdownEditor(QWidget):

    saved = Signal(str)


    def __init__(self):

        super().__init__()

        self.current_file = None

        self.attachment_service = AttachmentService()

        self.build_ui()


    def open_pdf(self, path):

        file_path = Path(path)

        if file_path.exists():

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(
                    str(file_path.resolve())
                )
            )

    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(self)


        # ---------------- Toolbar ----------------

        buttons = QHBoxLayout()


        self.equation_button = QPushButton(
            "∑ Equation"
        )

        self.attachment_button = QPushButton(
            "📎 Attach File"
        )

        self.reference_button = QPushButton(
            "Citation"
        )

        self.save_button = QPushButton(
            "Save"
        )


        buttons.addWidget(
            self.equation_button
        )

        buttons.addWidget(
            self.attachment_button
        )

        buttons.addWidget(
            self.reference_button
        )


        buttons.addWidget(
            self.save_button
        )


        buttons.addStretch()


        layout.addLayout(buttons)



        # ---------------- Editor ----------------

        self.editor = QTextEdit()


        self.editor.setPlaceholderText(
            "Write your research notes here...\n\n"
            "Markdown supported\n\n"
            "Example:\n\n"
            "$$ E = mc^2 $$"
        )



        # ---------------- Preview ----------------

        self.preview = QWebEngineView()

        self.preview.setPage(
            MyWebPage(self.preview)
        )

        settings = self.preview.settings()
        settings.setAttribute(
            QWebEngineSettings.LocalContentCanAccessRemoteUrls,
            True
        )
        settings.setAttribute(
            QWebEngineSettings.LocalContentCanAccessFileUrls,
            True
        )

        self.preview.loadFinished.connect(
            self.render_mathjax
        )

        splitter = QSplitter(
            Qt.Horizontal
        )


        splitter.addWidget(
            self.editor
        )


        splitter.addWidget(
            self.preview
        )


        splitter.setSizes(
            [
                700,
                700
            ]
        )


        layout.addWidget(
            splitter
        )


        # ---------------- Signals ----------------


        self.save_button.clicked.connect(
            self.save_file
        )


        self.editor.textChanged.connect(
            self.update_preview
        )


        self.equation_button.clicked.connect(
            self.open_equation_editor
        )

        self.attachment_button.clicked.connect(
            self.show_attachment_menu
        )

        self.reference_button.clicked.connect(
            self.open_reference_picker
        )


    # -------------------------------------------------
    # Equation Dialog
    # -------------------------------------------------

    def open_equation_editor(self):

        dialog = EquationEditor()


        dialog.equationInserted.connect(
            self.insert_text
        )


        dialog.exec()

    # -------------------------------------------------
    # Attach Menu
    # -------------------------------------------------
    def show_attachment_menu(self):

        menu = QMenu(self)

        add_new = menu.addAction(
            "📂 Add New File"
        )

        existing = menu.addAction(
            "📎 Use Existing Attachment"
        )


        action = menu.exec(
            self.attachment_button.mapToGlobal(
                self.attachment_button.rect().bottomLeft()
            )
        )


        if action == add_new:

            self.attach_file()


        elif action == existing:

            self.insert_existing_attachment()

    def insert_existing_attachment(self):

        files = self.get_existing_attachments()


        if not files:

            return


        menu = QMenu(self)


        actions = {}


        for file in files:

            action = menu.addAction(
                file.name
            )

            actions[action] = file



        selected = menu.exec(
            self.attachment_button.mapToGlobal(
                self.attachment_button.rect().bottomLeft()
            )
        )


        if selected in actions:

            file = actions[selected]

            work_service = WorkService()


            work_folder = self.current_file.parent


            work_id = work_service.get_work_by_folder(
                work_folder
            )

            if work_id is not None:
                self.attachment_service.register_attachment(
                    work_id,
                    file
                )

            path = os.path.relpath(
                file,
                work_folder
            ).replace("\\", "/")


            suffix = file.suffix.lower()


            if suffix in [

                ".png",
                ".jpg",
                ".jpeg",
                ".bmp",
                ".gif",
                ".webp"

            ]:

                markdown = (
                    f"\n\n![{file.stem}]"
                    f"({path})\n\n"
                )


            else:

                markdown = (
                    f"\n\n[{file.name}]"
                    f"({path})\n\n"
                )


            self.insert_text(
                markdown
            )


            self.update_preview()

    def get_existing_attachments(self):

        attachments = []

        from pathlib import Path

        attachment_root = Path("attachments")

        folders = [
            "images",
            "pdf",
            "files"
        ]

        for folder in folders:

            path = attachment_root / folder

            if path.exists():

                for file in path.iterdir():

                    if file.is_file():

                        attachments.append(file)

        return attachments

    # -------------------------------------------------
    # Attach File
    # -------------------------------------------------
    def attach_file(self):

        if self.current_file is None:

            return

        filename, _ = QFileDialog.getOpenFileName(

            self,

            "Attach File"

        )

        if not filename:

            return

        work_folder = self.current_file.parent

        destination = self.attachment_service.copy_attachment(

            filename,

            work_folder

        )

        markdown = self.attachment_service.markdown_text(

            destination,
            work_folder

        )

        self.insert_text(

            "\n\n"

            + markdown

            + "\n\n"

        )

        self.update_preview()


    # -------------------------------------------------
    # Reference Dialog
    # -------------------------------------------------

    def open_reference_picker(self):

        dialog = ReferencePicker()


        dialog.referenceSelected.connect(
            self.insert_citation
        )


        dialog.exec()



    # -------------------------------------------------
    # Open Markdown File
    # -------------------------------------------------

    def open_file(self, filepath):

        path = Path(filepath)


        if path.exists():

            text = path.read_text(
                encoding="utf-8"
            )


            self.editor.setPlainText(
                text
            )


            self.current_file = path


            self.update_preview()



    # -------------------------------------------------
    # Set File
    # -------------------------------------------------

    def set_file(self, filepath):

        self.current_file = Path(
            filepath
        )


        self.open_file(
            filepath
        )



    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    def save_file(self):

        if self.current_file is None:

            return


        text = self.editor.toPlainText()

        text = self.replace_citations(text)


        # ------------------------------------
        # Sync attachments with database
        # ------------------------------------


        work_service = WorkService()


        work_id = work_service.get_work_by_folder(
            self.current_file.parent
        )


        if work_id is not None:

            self.attachment_service.sync_work_attachments(
                work_id,
                text
            )


        # ------------------------------------
        # Save markdown file
        # ------------------------------------

        self.current_file.write_text(

            text,

            encoding="utf-8"

        )


        self.saved.emit(
            str(self.current_file)
        )



    def render_mathjax(self, ok: bool = True):

        if not ok:

            return


        self.preview.page().runJavaScript(
            """
            function renderMathJax() {
                if (window.MathJax && window.MathJax.startup && typeof window.MathJax.startup.promise !== 'undefined') {
                    window.MathJax.startup.promise.then(function() {
                        return window.MathJax.typesetPromise();
                    }).catch(function(err) {
                        console.log('MathJax typeset failed:', err);
                    });
                } else {
                    window.setTimeout(renderMathJax, 100);
                }
            }
            renderMathJax();
            """
        )

    def insert_citation(self, key):

        if self.current_file is None:
            return


        reference_service = ReferenceService()
        work_service = WorkService()


        work_folder = self.current_file.parent


        work_id = work_service.get_work_by_folder(
            work_folder
        )


        reference_id = reference_service.get_reference_by_key(
            key
        )

        if (
            work_id is not None
            and reference_id is not None
        ):

            reference_service.add_reference_to_work(
                work_id,
                reference_id
            )


        self.insert_text(
            f"[{key}]"
        )

    def replace_citations(self, text):

        service = ReferenceService()

        references = service.get_all_references()


        ref_map = {}

        for ref in references:

            ref_map[ref.citation_key] = ref


        def replace(match):

            key = match.group(1)


            if key not in ref_map:

                return match.group(0)


            ref = ref_map[key]


            html = (
                f'<a href="reference-pdf://{key}">'
                f'{key}'
                f'</a>'
            )


            if ref.url:

                html += (
                    f' <a href="reference-url://{key}">🔗</a>'
                )


            return html


        return re.sub(
            r'\[([A-Za-z0-9_]+)\]',
            replace,
            text
        )

    def replace_code_files(self, text):

        import re


        def replace(match):

            code_path = match.group(1).strip()

            if not self.current_file:
                return match.group(0)


            file_path = (
                self.current_file.parent
                / code_path
            )


            if not file_path.exists():
                return (
                    f"<b>Missing code file:</b> {code_path}"
                )


            try:

                content = file_path.read_text(
                    encoding="utf-8"
                )

                lexer = get_lexer_for_filename(
                    file_path.name
                )


                formatter = HtmlFormatter(
                    style="monokai"
                )


                highlighted = highlight(
                    content,
                    lexer,
                    formatter
                )


                css = formatter.get_style_defs(
                    ".highlight"
                )

            except Exception as e:

                return (
                    f"<b>Error reading code:</b> {e}"
                )


            return (
                "\n\n"
                f"<style>{css}</style>"
                "<div class=\"code-box\">"
                + highlighted +
                "</div>"
                "\n\n"
            )


        return re.sub(
            r"```code-file\s+(.*?)```",
            replace,
            text,
            flags=re.DOTALL
        )

    # -------------------------------------------------
    # Markdown + LaTeX Preview
    # -------------------------------------------------

    def update_preview(self):

        text = self.editor.toPlainText()

        text = self.replace_citations(text)
        text = self.replace_code_files(text)


        html_body = markdown.markdown(

            text,

            extensions=[
                "fenced_code",
                "tables",
            ]

        )

        # Convert attachment paths to absolute file paths
        if self.current_file:

            work_path = self.current_file.parent.resolve()


            html_body = html_body.replace(
                'src="images/',
                f'src="file://{work_path}/images/'
            )


            html_body = html_body.replace(
                'href="pdf/',
                f'href="file://{work_path}/pdf/'
            )

        mathjax_path = (
            Path(__file__).resolve().parent.parent
            / "mathjax"
            / "es5"
            / "tex-mml-chtml.js"
        )

        mathjax_url = QUrl.fromLocalFile(
            str(mathjax_path)
        ).toString()

        html = f"""

<!DOCTYPE html>

<html>

<head>


<script>

window.MathJax = {{

    tex: {{

        inlineMath: [
            ['$', '$']
        ],

        displayMath: [
            ['$$', '$$']
        ],

        processEscapes: true

    }}

}};

</script>

<script async
src="{mathjax_url}">
</script>




<style>

body {{

font-family: Arial;

font-size: 16px;

line-height: 1.8;

margin: 25px;

}}


p {{

margin-top: 15px;

margin-bottom: 15px;

}}


code {{

background:#eeeeee;

padding:3px;

}}


pre {{

background:#eeeeee;

padding:10px;

}}

.code-box {{
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 12px;
    border-radius: 8px;
    max-height: 7.5em;
    overflow-y: auto;
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 13px;
    line-height: 1.5;
    border: 1px solid #333;
}}


.code-box pre {{
    margin: 0;
    white-space: pre;
    background-color: #1e1e1e;
    color: #d4d4d4;
}}


</style>


</head>


<body>


{html_body}


</body>


</html>

"""


        if self.current_file:

            base_url = QUrl.fromLocalFile(
                str(self.current_file.parent.resolve()) + "/"
            )


            self.preview.setHtml(
                html,
                base_url
            )

        else:

            self.preview.setHtml(
                html
            )

            self.preview.page().runJavaScript(
                """
                document.querySelectorAll('a').forEach(function(link){

                    link.onclick = function(event){

                        if(this.href.endsWith('.pdf')){

                            event.preventDefault();

                            window.location.href =
                            'pdf-open://' + this.href;

                        }

                    };

                });
                """
            )

    def render_mathjax(self, ok):

        if not ok:

            return

        self.preview.page().runJavaScript(
            """
            (function() {
                function render() {
                    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
                        window.MathJax.typesetPromise().catch(function(err) {
                            console.error('MathJax rendering failed:', err);
                        });
                        return true;
                    }
                    return false;
                }

                if (!render()) {
                    window.setTimeout(render, 100);
                }
            })();
            """
        )

    # -------------------------------------------------
    # Open Links
    # -------------------------------------------------

    def open_link(self, url):

        path = url.toLocalFile()

        if path:

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(path)
            )

        else:

            QDesktopServices.openUrl(url)

    # -------------------------------------------------
    # Handle PDF / File Links
    # -------------------------------------------------

    def handle_url_change(self, url):

        if url.toLocalFile():

            QDesktopServices.openUrl(
                url
            )

    # -------------------------------------------------
    # Handle Downloads
    # -------------------------------------------------

    def handle_download(self, download):

        filename = download.downloadFileName()

        download.setDownloadDirectory(
            str(Path.home() / "Downloads")
        )

        download.setDownloadFileName(
            filename
        )

        download.accept()

    # -------------------------------------------------
    # Insert Text
    # -------------------------------------------------

    def insert_text(self, text):

        cursor = self.editor.textCursor()


        cursor.insertText(
            text
        )


        self.editor.setTextCursor(
            cursor
        )



    # -------------------------------------------------
    # Insert Equation
    # -------------------------------------------------

    def insert_equation(self, equation):

        self.insert_text(
            f"${equation}$"
        )

