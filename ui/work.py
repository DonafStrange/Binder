from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox
)


from services.work_service import WorkService



class WorkWindow(QDialog):


    workCreated = Signal(dict)



    def __init__(self):

        super().__init__()


        self.setWindowTitle(
            "Create New Research Work"
        )


        self.resize(
            400,
            300
        )


        self.service = WorkService()


        self.build_ui()



    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )


        layout.addWidget(
            QLabel(
                "Work Title"
            )
        )


        self.title = QLineEdit()


        self.title.setPlaceholderText(
            "Example: Wilson Cowan Model"
        )


        layout.addWidget(
            self.title
        )



        layout.addWidget(
            QLabel(
                "Category"
            )
        )


        self.category = QComboBox()


        self.category.addItems(

            [

            "Computational Neuroscience",

            "EEG Analysis",

            "MRI / Neuroimaging",

            "Machine Learning",

            "Literature Review",

            "Other"

            ]

        )


        layout.addWidget(
            self.category
        )



        self.create_button = QPushButton(
            "Create Work"
        )


        layout.addWidget(
            self.create_button
        )


        self.create_button.clicked.connect(
            self.create_work
        )



    # -------------------------------------------------
    # Create
    # -------------------------------------------------

    def create_work(self):


        title = self.title.text().strip()


        category = self.category.currentText()



        if title == "":

            QMessageBox.warning(

                self,

                "Missing",

                "Enter work title"

            )

            return



        result = self.service.create_work(

            title,

            category

        )


        self.workCreated.emit(
            result
        )


        QMessageBox.information(

            self,

            "Created",

            "Research work created"

        )


        self.close()