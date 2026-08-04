from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton
)

from services.reference_service import ReferenceService


class ReferenceLibrary(QWidget):

    referenceSelected = Signal(int)


    def __init__(self):

        super().__init__()

        self.service = ReferenceService()

        self.build_ui()

        self.load_references()


    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )


        self.tree = QTreeWidget()

        self.tree.setHeaderLabels(
            [
                "Title",
                "Year"
            ]
        )


        self.tree.itemClicked.connect(
            self.select_reference
        )


        layout.addWidget(
            self.tree
        )


        refresh = QPushButton(
            "Refresh"
        )


        refresh.clicked.connect(
            self.load_references
        )


        layout.addWidget(
            refresh
        )


    # -------------------------------------------------
    # Load References
    # -------------------------------------------------

    def load_references(self):

        self.tree.clear()


        references = self.service.get_all_references()


        for ref in references:

            item = QTreeWidgetItem(
                [
                    ref.title,
                    ref.year or ""
                ]
            )


            item.setData(
                0,
                Qt.UserRole,
                ref.id
            )


            self.tree.addTopLevelItem(
                item
            )


    # -------------------------------------------------
    # Selection
    # -------------------------------------------------

    def select_reference(
            self,
            item,
            column
    ):

        ref_id = item.data(
            0,
            Qt.UserRole
        )

        self.referenceSelected.emit(
            ref_id
        )

    # -------------------------------------------------
    # External refresh
    # -------------------------------------------------

    def refresh(self):

        self.load_references()