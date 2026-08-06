from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
)

from services.work_service import WorkService
from services.category_service import CategoryService
from dialogs.category_dialog import CategoryDialog


class WorkWindow(QDialog):


    workCreated = Signal(dict)



    def __init__(self, work=None):

        super().__init__()


        self.work = work

        self.setWindowTitle(
            "Edit Research Work" if self.work else "Create New Research Work"
        )


        self.resize(
            400,
            300
        )


        self.service = WorkService()
        self.category_service = CategoryService()

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

        if self.work:
            self.title.setText(self.work.title)

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
        self.category.currentIndexChanged.connect(self.on_category_selection_changed)
        self._populate_categories()

        layout.addWidget(
            self.category
        )



        self.create_button = QPushButton(
            "Save Changes" if self.work else "Create Work"
        )


        layout.addWidget(
            self.create_button
        )


        self.create_button.clicked.connect(
            self.create_work
        )



    def _populate_categories(self):
        self.category.blockSignals(True)
        self.category.clear()

        categories = self.category_service.get_all_categories()
        for category in categories:
            self.category.addItem(category["name"])

        self.category.addItem("+ Add New Category...")
        self.category.blockSignals(False)

        if self.work and self.work.category:
            self.category.setCurrentText(self.work.category)
        elif self.category.count() > 0:
            self.category.setCurrentIndex(0)

    def on_category_selection_changed(self, index):
        if self.category.count() == 0:
            return

        if self.category.itemText(index) == "+ Add New Category...":
            previous_index = max(0, self.category.count() - 2)
            self.category.blockSignals(True)
            self.category.setCurrentIndex(previous_index)
            self.category.blockSignals(False)

            dialog = CategoryDialog(self)
            if dialog.exec() == QDialog.Accepted:
                self._populate_categories()
                self._select_created_category(dialog.result_category)

    def _select_created_category(self, selected_name=None):
        categories = self.category_service.get_all_categories()
        if not categories:
            return

        for index in range(self.category.count()):
            text = self.category.itemText(index)
            if selected_name and text == selected_name:
                self.category.setCurrentIndex(index)
                return

            if text in {item["name"] for item in categories}:
                self.category.setCurrentIndex(index)
                return

    # -------------------------------------------------
    # Create
    # -------------------------------------------------

    def create_work(self):


        title = self.title.text().strip()


        category = self.category.currentText()
        if category == "+ Add New Category...":
            category = ""



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