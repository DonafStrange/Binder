from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)

from services.category_service import CategoryService


class CategoryDialog(QDialog):

    def __init__(self, parent=None, category_id=None, initial_name=""):
        super().__init__(parent)

        self.category_service = CategoryService()
        self.category_id = category_id
        self.result_category = None
        self.setWindowTitle("New Category" if category_id is None else "Rename Category")
        self.resize(320, 140)

        self.build_ui(initial_name)

    def build_ui(self, initial_name):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Category Name"))

        self.name_edit = QLineEdit(initial_name)
        self.name_edit.setPlaceholderText("Enter category name")
        layout.addWidget(self.name_edit)

        buttons = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_button)

        self.create_button = QPushButton("Create" if self.category_id is None else "Rename")
        self.create_button.clicked.connect(self.save)
        buttons.addWidget(self.create_button)

        layout.addLayout(buttons)

    def save(self):
        name = self.name_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "Missing", "Enter a category name")
            return

        if self.category_id is None:
            existing = self.category_service.get_category_by_name(name)
            if existing is not None:
                self.result_category = existing["name"]
                self.accept()
                return

            self.category_service.add_category(name)
            self.result_category = name
        else:
            existing = self.category_service.get_category_by_name(name)
            if existing is not None and existing["id"] != self.category_id:
                QMessageBox.warning(self, "Duplicate", "That category already exists")
                return

            self.category_service.rename_category(self.category_id, name)
            self.result_category = name

        self.accept()
