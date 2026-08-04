from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFormLayout,
    QGroupBox
)

from pathlib import Path
import subprocess

from matplotlib.pylab import rint

class ReferenceProperties(QWidget):

    def __init__(self):

        super().__init__()

        self.build_ui()


    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )


        self.title_label = QLabel(
            "Title:"
        )

        self.author_label = QLabel(
            "Authors:"
        )

        self.journal_label = QLabel(
            "Journal:"
        )

        self.year_label = QLabel(
            "Year:"
        )

        self.doi_label = QLabel(
            "DOI:"
        )

        self.url_label = QLabel(
            "URL:"
        )

        # ---------------- Abstract ----------------

        abstract_box = QGroupBox(
            "Abstract"
        )

        abstract_layout = QVBoxLayout()


        self.abstract_text = QTextEdit()

        self.abstract_text.setReadOnly(
            True
        )


        abstract_layout.addWidget(
            self.abstract_text
        )


        abstract_box.setLayout(
            abstract_layout
        )

        
        layout.addWidget(
            abstract_box
        )

        self.pdf_button = QPushButton(
            "Open PDF"
        )

        self.pdf_button.clicked.connect(
            self.open_pdf
        )

        self.delete_button = QPushButton(
            "Delete Reference"
        )

        self.delete_button.clicked.connect(
            self.delete_reference
        )

        layout.addWidget(
            self.title_label
        )

        layout.addWidget(
            self.author_label
        )

        layout.addWidget(
            self.journal_label
        )

        layout.addWidget(
            self.year_label
        )

        layout.addWidget(
            self.doi_label
        )

        layout.addWidget(
            self.url_label
        )

        layout.addWidget(
            self.pdf_button
        )

        layout.addWidget(
            self.delete_button
        )


    # -------------------------------------------------
    # Load Reference
    # -------------------------------------------------

    def load_reference(self, ref):

        self.current_reference = ref


        self.title_label.setText(
            f"Title: {ref.title}"
        )


        self.author_label.setText(
            f"Authors: {ref.authors or ''}"
        )


        self.journal_label.setText(
            f"Journal: {ref.journal or ''}"
        )


        self.year_label.setText(
            f"Year: {ref.year or ''}"
        )


        self.doi_label.setText(
            f"DOI: {ref.doi or ''}"
        )


        self.url_label.setText(
            f"URL: {ref.url or ''}"
        )


        self.abstract_text.setText(
            ref.abstract or "No abstract available"
        )

    def open_pdf(self):

        if not hasattr(self, "current_reference"):

#             print("No reference selected")
            return


        pdf_path = self.current_reference.pdf


#         print("PDF PATH:", pdf_path)


        if not pdf_path:

#             print("No PDF attached to this reference")
            return


        from pathlib import Path
        import webbrowser


        path = Path(pdf_path)


#         print("EXISTS:", path.exists())


        if path.exists():

            webbrowser.open(
                path.resolve().as_uri()
            )

        else:
            # print(
            #     "PDF file not found:",
            #     path
            # )
            pass

    def delete_reference(self):

        if not hasattr(self, "current_reference"):

#             print("No reference selected")
            return


        from PySide6.QtWidgets import QMessageBox
        from services.reference_service import ReferenceService


        reply = QMessageBox.question(
            self,
            "Delete Reference",
            f"Delete '{self.current_reference.title}'?",
            QMessageBox.Yes | QMessageBox.No
        )


        if reply == QMessageBox.Yes:

            service = ReferenceService()

            service.delete_reference(
                self.current_reference.id
            )


            QMessageBox.information(
                self,
                "Deleted",
                "Reference deleted successfully."
            )


            self.current_reference = None

            self.title_label.setText("Title:")
            self.author_label.setText("Authors:")
            self.journal_label.setText("Journal:")
            self.year_label.setText("Year:")
            self.doi_label.setText("DOI:")
            self.url_label.setText("URL:")

            self.abstract_text.clear()