from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLabel
)


class WorkReferencePanel(QWidget):

    def __init__(self):

        super().__init__()

        self.current_work = None

        self.build_ui()


    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )


        self.title = QLabel(
            "References"
        )


        layout.addWidget(
            self.title
        )


        self.list = QListWidget()


        layout.addWidget(
            self.list
        )


        self.add_button = QPushButton(
            "Add Reference"
        )


        layout.addWidget(
            self.add_button
        )



    # -------------------------------------------------
    # Load Work
    # -------------------------------------------------

    def set_work(self, work):

        self.current_work = work


        self.title.setText(
            f"References: {work.title}"
        )


        self.load_references()



    # -------------------------------------------------
    # Load References
    # -------------------------------------------------

    def load_references(self):

        self.list.clear()


        if self.current_work is None:

            return


        # temporary
        # database connection will come here later

        self.list.addItem(
            "No references added yet"
        )