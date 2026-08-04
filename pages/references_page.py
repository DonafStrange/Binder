from pathlib import Path
import json
import uuid


from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QLabel,
    QFormLayout,
    QGroupBox,
    QFileDialog,
    QMessageBox
)


class ReferencesPage(QWidget):

    def __init__(self):

        super().__init__()

        self.reference_file = Path(
            "references/references.json"
        )

        self.references = []

        self.build_ui()

        self.load_references()



    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        main = QHBoxLayout(self)


        # LEFT LIST

        left = QVBoxLayout()


        self.reference_list = QListWidget()


        self.reference_list.itemClicked.connect(
            self.load_selected
        )


        left.addWidget(
            QLabel("References")
        )


        left.addWidget(
            self.reference_list
        )


        self.add_button = QPushButton(
            "Add Reference"
        )


        left.addWidget(
            self.add_button
        )


        self.add_button.clicked.connect(
            self.new_reference
        )


        main.addLayout(
            left,
            1
        )



        # RIGHT FORM

        form_box = QGroupBox(
            "Reference Information"
        )


        form = QFormLayout()


        self.key = QLineEdit()

        self.title = QLineEdit()

        self.authors = QLineEdit()

        self.year = QLineEdit()

        self.doi = QLineEdit()

        self.notes = QTextEdit()


        form.addRow(
            "Citation Key",
            self.key
        )


        form.addRow(
            "Title",
            self.title
        )


        form.addRow(
            "Authors",
            self.authors
        )


        form.addRow(
            "Year",
            self.year
        )


        form.addRow(
            "DOI",
            self.doi
        )


        form.addRow(
            "Notes",
            self.notes
        )


        form_box.setLayout(
            form
        )


        right = QVBoxLayout()


        right.addWidget(
            form_box
        )


        self.pdf_button = QPushButton(
            "Attach PDF"
        )


        self.save_button = QPushButton(
            "Save Reference"
        )


        right.addWidget(
            self.pdf_button
        )


        right.addWidget(
            self.save_button
        )


        self.pdf_button.clicked.connect(
            self.attach_pdf
        )


        self.save_button.clicked.connect(
            self.save_reference
        )


        main.addLayout(
            right,
            2
        )



    # -------------------------------------------------
    # Load JSON
    # -------------------------------------------------

    def load_references(self):

        if self.reference_file.exists():

            self.references = json.loads(
                self.reference_file.read_text()
            )


        else:

            self.references = []


        self.refresh_list()



    # -------------------------------------------------
    # List Refresh
    # -------------------------------------------------

    def refresh_list(self):

        self.reference_list.clear()


        for ref in self.references:

            self.reference_list.addItem(

                f"{ref['key']} : {ref['title']}"

            )



    # -------------------------------------------------
    # New
    # -------------------------------------------------

    def new_reference(self):

        self.key.clear()

        self.title.clear()

        self.authors.clear()

        self.year.clear()

        self.doi.clear()

        self.notes.clear()



        self.key.setText(

            "REF_" +

            str(uuid.uuid4())[:8]

        )



    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    def save_reference(self):


        reference = {

            "key":
            self.key.text(),


            "title":
            self.title.text(),


            "authors":
            self.authors.text(),


            "year":
            self.year.text(),


            "doi":
            self.doi.text(),


            "notes":
            self.notes.toPlainText(),


            "pdf":
            ""

        }


        found = False


        for i,r in enumerate(self.references):

            if r["key"] == reference["key"]:

                self.references[i] = reference

                found = True


        if not found:

            self.references.append(
                reference
            )


        self.save_json()


        self.refresh_list()



        QMessageBox.information(
            self,
            "Saved",
            "Reference saved"
        )



    # -------------------------------------------------
    # PDF
    # -------------------------------------------------

    def attach_pdf(self):

        file,_ = QFileDialog.getOpenFileName(

            self,

            "Select PDF",

            filter="PDF (*.pdf)"

        )


        if not file:

            return


        folder = Path(
            "references/papers"
        )


        folder.mkdir(
            exist_ok=True
        )


        destination = (

            folder

            /

            Path(file).name

        )


        destination.write_bytes(

            Path(file).read_bytes()

        )


        self.current_pdf = str(
            destination
        )



    # -------------------------------------------------
    # Load Item
    # -------------------------------------------------

    def load_selected(self,item):


        key = item.text().split(":")[0].strip()


        for ref in self.references:

            if ref.citation_key == key:


                self.key.setText(
                    ref.citation_key
                )

                self.title.setText(
                    ref.title
                )

                self.authors.setText(
                    ref.authors
                )

                self.year.setText(
                    ref.year
                )

                self.doi.setText(
                    ref.doi
                )

                self.notes.setText(
                    ref.abstract
                )


    # -------------------------------------------------
    # Save JSON
    # -------------------------------------------------

    def save_json(self):

        self.reference_file.parent.mkdir(
            exist_ok=True
        )


        self.reference_file.write_text(

            json.dumps(

                self.references,

                indent=4

            )

        )