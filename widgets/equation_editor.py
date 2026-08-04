from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
)


class EquationEditor(QDialog):

    equationInserted = Signal(str)


    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "LaTeX Equation"
        )

        self.resize(
            600,
            400
        )

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
                "Write LaTeX equation:"
            )
        )


        self.editor = QTextEdit()


        self.editor.setPlaceholderText(

            r"""
Example:

\frac{dx}{dt}=Ax+Bu

or

E=mc^2

"""

        )


        layout.addWidget(
            self.editor
        )


        buttons = QHBoxLayout()


        insert = QPushButton(
            "Insert"
        )


        cancel = QPushButton(
            "Cancel"
        )


        buttons.addWidget(
            insert
        )


        buttons.addWidget(
            cancel
        )


        layout.addLayout(
            buttons
        )


        insert.clicked.connect(
            self.insert_equation
        )


        cancel.clicked.connect(
            self.close
        )



    # -------------------------------------------------
    # Insert
    # -------------------------------------------------

    def insert_equation(self):


        equation = self.editor.toPlainText().strip()


        if equation:


            latex = (

                "\n\n$$\n"

                +

                equation

                +

                "\n$$\n\n"

            )


            self.equationInserted.emit(
                latex
            )


        self.close()