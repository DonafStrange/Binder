import json
from pathlib import Path
from services.reference_service import ReferenceService


from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QLabel,
)



class ReferencePicker(QDialog):

    referenceSelected = Signal(str)


    def __init__(self):

        super().__init__()


        self.setWindowTitle(
            "Insert Citation"
        )


        self.resize(
            500,
            400
        )

        self.service = ReferenceService()

        self.references = []

        self.load_references()

        self.build_ui()



    # -------------------------------------------------
    # Load References
    # -------------------------------------------------

    def load_references(self):

        self.references = self.service.get_all_references()



    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )


        layout.addWidget(
            QLabel(
                "Search Reference"
            )
        )


        self.search = QLineEdit()


        self.search.setPlaceholderText(
            "Author, title, year..."
        )


        layout.addWidget(
            self.search
        )


        self.list = QListWidget()


        layout.addWidget(
            self.list
        )


        self.insert = QPushButton(
            "Insert Citation"
        )


        layout.addWidget(
            self.insert
        )


        self.search.textChanged.connect(
            self.search_reference
        )


        self.list.itemDoubleClicked.connect(
            self.insert_reference
        )


        self.insert.clicked.connect(
            self.insert_reference
        )


        self.populate()



    # -------------------------------------------------
    # Populate
    # -------------------------------------------------

    def populate(self):

        self.list.clear()


        for ref in self.references:


            self.list.addItem(

                f"{ref.citation_key} | {ref.title}"

            )



    # -------------------------------------------------
    # Search
    # -------------------------------------------------

    def search_reference(self, text):

        text = text.lower()

        self.list.clear()


        for ref in self.references:

            data = (
                str(ref.id)
                +
                ref.title
                +
                ref.authors
                +
                ref.year
            ).lower()


            if text in data:

                self.list.addItem(
                    f"{ref.id} | {ref.title}"
                )



    # -------------------------------------------------
    # Insert
    # -------------------------------------------------

    def insert_reference(self):

        item = self.list.currentItem()


        if item is None:

            return


        key = item.text().split("|")[0].strip()

        print("EMITTING REFERENCE KEY:", key)


        self.referenceSelected.emit(
            key
        )


        self.close()