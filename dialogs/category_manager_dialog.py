from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QComboBox,
)

from services.category_service import CategoryService
from dialogs.category_dialog import CategoryDialog


class CategoryManagerDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Manage Categories")
        self.resize(420, 360)

        self.category_service = CategoryService()
        self.build_ui()
        self.refresh_categories()

    def build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Categories"))

        self.category_list = QListWidget()
        layout.addWidget(self.category_list)

        button_row = QHBoxLayout()

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_category)
        button_row.addWidget(self.add_button)

        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.rename_category)
        button_row.addWidget(self.rename_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_category)
        button_row.addWidget(self.delete_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_row.addWidget(self.close_button)

        layout.addLayout(button_row)

    def refresh_categories(self):
        self.category_list.clear()
        categories = self.category_service.get_all_categories()
        for category in categories:
            self.category_list.addItem(category["name"])

    def add_category(self):
        dialog = CategoryDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.refresh_categories()

    def rename_category(self):
        selected_items = self.category_list.selectedItems()
        if not selected_items:
            return

        selected_name = selected_items[0].text()
        category = self.category_service.get_category_by_name(selected_name)
        if category is None:
            return

        dialog = CategoryDialog(self, category_id=category["id"], initial_name=category["name"])
        if dialog.exec() == QDialog.Accepted:
            self.refresh_categories()

    def delete_category(self):
        selected_items = self.category_list.selectedItems()
        if not selected_items:
            return

        selected_name = selected_items[0].text()
        category = self.category_service.get_category_by_name(selected_name)
        if category is None:
            return

        usage_count = self.category_service.get_category_usage_count(category["name"])
        if usage_count == 0:
            self.category_service.delete_category(category["id"])
            self.refresh_categories()
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Delete Category")
        dialog.resize(420, 220)
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(f'Category "{category["name"]}" is currently used by {usage_count} works.'))
        layout.addWidget(QLabel("Choose what to do."))

        self.move_combo = QComboBox()
        categories = self.category_service.get_all_categories()
        for item in categories:
            if item["id"] != category["id"]:
                self.move_combo.addItem(item["name"])
        layout.addWidget(QLabel("Move all works to another category"))
        layout.addWidget(self.move_combo)

        self.remove_radio = None
        layout.addWidget(QLabel("Or remove category from those works"))

        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        buttons.addWidget(cancel_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self._delete_with_choice(dialog, category["id"], category["name"]))
        buttons.addWidget(delete_button)
        layout.addLayout(buttons)

        dialog.exec()

    def _delete_with_choice(self, dialog, category_id, category_name):
        move_to = self.move_combo.currentText().strip() if self.move_combo.count() else None
        if self.move_combo.count() and move_to:
            self.category_service.delete_category(category_id, move_to=move_to)
        else:
            self.category_service.delete_category(category_id, remove_from_works=True)
        dialog.accept()
        self.refresh_categories()
