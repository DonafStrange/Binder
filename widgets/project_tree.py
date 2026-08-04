from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QMenu,
)

from services.work_service import WorkService


class ProjectTree(QWidget):
    """
    Left panel showing all research works grouped by category.
    """

    workSelected = Signal(str)

    def __init__(self):
        super().__init__()

        self.service = WorkService()

        self.build_ui()
        self.load_projects()

    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Research Works")
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)

        self.tree.itemClicked.connect(self.on_item_clicked)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(
            self.show_context_menu
        )

        layout.addWidget(self.tree)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_projects)

        layout.addWidget(self.refresh_button)

    # -------------------------------------------------
    # Load projects from database
    # -------------------------------------------------

    def load_projects(self):
        self.tree.clear()

        works = self.service.get_all_works()

        categories = {}

        for work in works:

            category = work.category or "Uncategorized"

            if category not in categories:

                category_item = QTreeWidgetItem([category])
                category_item.setFlags(
                    category_item.flags() & ~Qt.ItemIsSelectable
                )

                categories[category] = category_item

                self.tree.addTopLevelItem(category_item)

            work_item = QTreeWidgetItem([work.title])

            work_item.setData(
                0,
                Qt.UserRole,
                work.id
            )

            categories[category].addChild(work_item)

        self.tree.expandAll()

    # -------------------------------------------------
    # Selection
    # -------------------------------------------------

    def on_item_clicked(self, item, column):
        # Ignore category headers
        if item.childCount() > 0:
            return

        self.workSelected.emit(item.text(0))

    # -------------------------------------------------
    # Context Menu
    # -------------------------------------------------

    def show_context_menu(self, position):

        item = self.tree.itemAt(position)

        menu = QMenu(self)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.load_projects)

        menu.addAction(refresh_action)

        if item and item.childCount() == 0:

            open_action = QAction("Open", self)
            open_action.triggered.connect(
                lambda: self.workSelected.emit(item.text(0))
            )

            menu.addAction(open_action)

            # Future actions
            # rename_action = QAction("Rename", self)
            # delete_action = QAction("Delete", self)
            # menu.addAction(rename_action)
            # menu.addAction(delete_action)

        menu.exec(
            self.tree.viewport().mapToGlobal(position)
        )

    # -------------------------------------------------
    # Refresh externally
    # -------------------------------------------------

    def refresh(self):
        """
        Can be called from MainWindow after
        creating or deleting a work.
        """
        self.load_projects()

    # -------------------------------------------------
    # Select work by title
    # -------------------------------------------------

    def select_work(self, title):

        root = self.tree.invisibleRootItem()

        for i in range(root.childCount()):

            category = root.child(i)

            for j in range(category.childCount()):

                item = category.child(j)

                if item.text(0) == title:

                    self.tree.setCurrentItem(item)

                    self.workSelected.emit(title)

                    return


    # -------------------------------------------------
    # Refresh and open a work
    # -------------------------------------------------

    def refresh_and_select(self, title):

        self.load_projects()

        self.select_work(title)