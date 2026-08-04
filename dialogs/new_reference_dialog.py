from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QHBoxLayout
)

from services.reference_service import ReferenceService


class NewReferenceDialog(QDialog):

    referenceCreated = Signal(dict)

    def __init__(self):

        super().__init__()

        self.service = ReferenceService()

        self.pdf_path = ""

        self.setWindowTitle(
            "New Reference"
        )

        self.resize(
            500,
            350
        )

        self.build_ui()

    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(self)

        # ---------------- Title ----------------

        layout.addWidget(
            QLabel("Title *")
        )

        self.title = QLineEdit()

        layout.addWidget(
            self.title
        )

        # ---------------- Authors ----------------

        layout.addWidget(
            QLabel("Authors")
        )

        self.authors = QLineEdit()

        layout.addWidget(
            self.authors
        )

        # ---------------- Journal ----------------

        layout.addWidget(
            QLabel("Journal")
        )

        self.journal = QLineEdit()

        layout.addWidget(
            self.journal
        )

        # ---------------- Year ----------------

        layout.addWidget(
            QLabel("Year")
        )

        self.year = QLineEdit()

        layout.addWidget(
            self.year
        )

        # ---------------- DOI ----------------

        layout.addWidget(
            QLabel("DOI")
        )

        self.doi = QLineEdit()

        layout.addWidget(
            self.doi)


        # ---------------- URL ----------------

        layout.addWidget(
            QLabel("URL")
        )

        self.url = QLineEdit()

        layout.addWidget(
            self.url)


        # ---------------- Volume ----------------

        layout.addWidget(
            QLabel("Volume")
        )

        self.volume = QLineEdit()

        layout.addWidget(
            self.volume)


        # ---------------- Issue ----------------

        layout.addWidget(
            QLabel("Issue")
        )

        self.issue = QLineEdit()

        layout.addWidget(
            self.issue)


        # ---------------- Pages ----------------

        layout.addWidget(
            QLabel("Pages")
        )

        self.pages = QLineEdit()

        layout.addWidget(
            self.pages)


        # ---------------- Keywords ----------------

        layout.addWidget(
            QLabel("Keywords")
        )

        self.keywords = QLineEdit()

        self.keywords.setPlaceholderText(
            "EEG, Alzheimer's, Computational Neuroscience"
        )

        layout.addWidget(
            self.keywords)


        # ---------------- Citation Key ----------------

        layout.addWidget(
            QLabel("Citation Key")
        )

        self.citation_key = QLineEdit()

        self.citation_key.setPlaceholderText(
            "Example: Smith2024"
        )

        layout.addWidget(
            self.citation_key
        )

        # ---------------- Abstract ----------------

        layout.addWidget(
            QLabel("Abstract")
        )

        self.abstract = QTextEdit()

        self.abstract.setMaximumHeight(100)

        layout.addWidget(
            self.abstract)

        # ---------------- PDF ----------------

        layout.addWidget(
            QLabel("PDF (Optional)")
        )

        pdf_layout = QHBoxLayout()

        self.pdf_file = QLineEdit()

        self.pdf_file.setReadOnly(True)

        browse = QPushButton(
            "Browse..."
        )

        browse.clicked.connect(
            self.choose_pdf
        )

        pdf_layout.addWidget(
            self.pdf_file
        )

        pdf_layout.addWidget(
            browse
        )

        layout.addLayout(
            pdf_layout
        )

        # ---------------- Buttons ----------------

        buttons = QHBoxLayout()

        cancel = QPushButton(
            "Cancel"
        )

        create = QPushButton(
            "Create"
        )

        cancel.clicked.connect(
            self.close
        )

        create.clicked.connect(
            self.create_reference
        )

        buttons.addStretch()

        buttons.addWidget(
            cancel
        )

        buttons.addWidget(
            create
        )

        layout.addLayout(
            buttons)

    # -------------------------------------------------
    # Browse PDF
    # -------------------------------------------------

    def choose_pdf(self):

        filename, _ = QFileDialog.getOpenFileName(

            self,

            "Select PDF",

            "",

            "PDF Files (*.pdf)"

        )

        if filename:

            self.pdf_path = filename

            self.pdf_file.setText(
                filename
            )

    # -------------------------------------------------
    # Create Reference
    # -------------------------------------------------

    def create_reference(self):

        title = self.title.text().strip()


        if title == "":

            QMessageBox.warning(

                self,

                "Missing Title",

                "Please enter a title."

            )

            return


        result = self.service.create_reference(

            title=title,

            authors=self.authors.text(),

            journal=self.journal.text(),

            year=self.year.text(),

            volume=self.volume.text(),

            issue=self.issue.text(),

            pages=self.pages.text(),

            doi=self.doi.text(),

            url=self.url.text(),

            abstract=self.abstract.toPlainText(),

            keywords=self.keywords.text(),

            citation_key=self.citation_key.text(),

            bibtex="",

            pdf_path=self.pdf_path

        )


        self.referenceCreated.emit(
            result
        )


        QMessageBox.information(

            self,

            "Created",

            "Reference created successfully."

        )


        self.accept()