from ui.work import WorkWindow
from dialogs.new_reference_dialog import NewReferenceDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QToolBar,
    QStatusBar,
    QTabWidget,
    QScrollArea
)

from PySide6.QtGui import QAction


from widgets.project_tree import ProjectTree
from widgets.properties_panel import PropertiesPanel
from widgets.markdown_editor import MarkdownEditor
#from widgets.attachment_panel import AttachmentPanel
from widgets.reference_library import ReferenceLibrary
from widgets.reference_properties import ReferenceProperties
from widgets.graph_canvas import GraphCanvas
from widgets.graph_window import GraphWindow
#from widgets.work_reference_panel import WorkReferencePanel

from services.work_service import WorkService
from dialogs.category_manager_dialog import CategoryManagerDialog



class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Research Vault"
        )

        self.resize(
            1600,
            950
        )


        self.work_service = WorkService()

        self.current_work = None


        self.create_editor()

        self.create_left_panel()

        self.create_right_panel()

        self.create_reference_panel()

        self.create_menu()

        self.create_toolbar()

        self.create_statusbar()



    # -------------------------------------------------
    # Editor Area
    # -------------------------------------------------

    def create_editor(self):


        self.editor = MarkdownEditor()


        self.setCentralWidget(
            self.editor
        )



    # -------------------------------------------------
    # Left Project Explorer
    # -------------------------------------------------

    def create_left_panel(self):


        self.project_tree = ProjectTree()


        self.project_tree.workSelected.connect(
            self.open_work
        )
        

        dock = QDockWidget(
            "Projects"
        )


        dock.setWidget(
            self.project_tree
        )


        dock.setAllowedAreas(
            Qt.LeftDockWidgetArea
        )


        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            dock
        )



    # -------------------------------------------------
    # Right Panel
    # -------------------------------------------------

    def create_right_panel(self):


        tabs = QTabWidget()


        self.properties = PropertiesPanel()

        self.properties.workDeleted.connect(
            self.project_tree.refresh
        )

        self.properties.referenceClicked.connect(
            self.open_reference
        )

        #self.attachments = AttachmentPanel()

        #self.references = WorkReferencePanel()

        self.reference_properties = ReferenceProperties()


        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setWidget(
            self.properties
        )

        tabs.addTab(
            scroll,
            "Properties"
        )


        '''tabs.addTab(
            self.attachments,
            "Attachments"
        )
        tabs.addTab(
            self.references,
            "References"
        )

        tabs.addTab(
            self.reference_properties,
            "Reference"
        )'''

        dock = QDockWidget(
            "Information"
        )


        dock.setWidget(
            tabs
        )


        dock.setAllowedAreas(
            Qt.RightDockWidgetArea
        )


        self.addDockWidget(
            Qt.RightDockWidgetArea,
            dock
        )


    # -------------------------------------------------
    # Reference Panel
    # -------------------------------------------------

    def create_reference_panel(self):


        self.reference_library = ReferenceLibrary()
        self.reference_library.referenceSelected.connect(
            self.open_reference
        )

        dock = QDockWidget(
            "All References"
        )


        dock.setWidget(
            self.reference_library
        )


        dock.setAllowedAreas(
            Qt.RightDockWidgetArea
        )


        self.addDockWidget(
            Qt.RightDockWidgetArea,
            dock
        )

    # -------------------------------------------------
    # Open Work
    # -------------------------------------------------

    def open_work(self,title):


        works = self.work_service.get_all_works()


        selected = None


        for work in works:

            if work.title == title:

                selected = work

                break



        if selected is None:

            return



        self.current_work = selected



        # Load markdown

        note_file = (

            selected.folder

            +

            "/"

            +

            selected.markdown_file

        )


        self.editor.set_file(
            note_file
        )



        # Update information

        self.properties.load_work(
            selected
        )


        self.status.showMessage(
            f"Opened {title}"
        )



    # -------------------------------------------------
    # Menu
    # -------------------------------------------------

    def create_menu(self):


        menu = self.menuBar()


        file_menu = menu.addMenu(
            "File"
        )

        edit_menu = menu.addMenu("Edit")
        tools_menu = menu.addMenu("Tools")

        manage_categories_action = QAction("Manage Categories", self)
        manage_categories_action.triggered.connect(self.open_category_manager)
        edit_menu.addAction(manage_categories_action)
        tools_menu.addAction(manage_categories_action)

        exit_action = QAction(
            "Exit",
            self
        )


        exit_action.triggered.connect(
            self.close
        )


        file_menu.addAction(
            exit_action
        )



    # -------------------------------------------------
    # Toolbar
    # -------------------------------------------------

    def create_toolbar(self):


        toolbar = QToolBar(
            "Toolbar"
        )


        toolbar.setMovable(
            False
        )


        self.addToolBar(
            toolbar
        )


        save = QAction(
            "Save",
            self
        )


        save.triggered.connect(
            self.editor.save_file
        )


        toolbar.addAction(
            save
        )


        toolbar.addSeparator()


        new = QAction(
            "New Work",
            self
        )

        new.triggered.connect(
            self.open_new_work
        )

        toolbar.addAction(new)

        toolbar.addSeparator()

        reference = QAction(
            "New Reference",
            self
        )

        reference.triggered.connect(
            self.open_new_reference
        )

        toolbar.addAction(
            reference
        )

        toolbar.addSeparator()

        graph = QAction(
            "Connections",
            self
        )

        graph.triggered.connect(
            self.open_graph
        )

        toolbar.addAction(
            graph
        )

        toolbar.addSeparator()

        categories = QAction(
            "Manage Categories",
            self
        )

        categories.triggered.connect(
            self.open_category_manager
        )

        toolbar.addAction(
            categories
        )
    def open_category_manager(self):
        dialog = CategoryManagerDialog(self)
        dialog.exec()

    # -------------------------------------------------
    # New Work
    # -------------------------------------------------

    def open_new_work(self):

        dialog = WorkWindow()

        dialog.workCreated.connect(
            self.on_work_created
        )

        dialog.exec()

    # -------------------------------------------------
    # New Reference
    # -------------------------------------------------

    def open_new_reference(self):

        dialog = NewReferenceDialog()

        dialog.referenceCreated.connect(
            self.on_reference_created
        )

        dialog.exec()

    # -------------------------------------------------
    # Link Graph
    # -------------------------------------------------

    def open_graph(self):

        self.graph_window = GraphWindow()

        self.graph_window.setWindowTitle(
            "Work Connection Graph"
        )

        self.graph_window.resize(
            1200,
            800
        )

        self.graph_window.show()

    # -------------------------------------------------
    # Refresh Projects
    # -------------------------------------------------

    def refresh_projects(self, work=None):

        self.project_tree.load_projects()

        if work and "title" in work:

            self.project_tree.refresh_and_select(
                work["title"]
            )

        self.status.showMessage(
            "Project list updated."
        )

    # -------------------------------------------------
    # Reference Created
    # -------------------------------------------------

    def on_reference_created(self, reference):

        self.status.showMessage(
            f"Reference '{reference['title']}' created."
        )

    def open_reference(self, reference_id):

        references = self.reference_library.service.get_all_references()


        selected = None


        for ref in references:

            if ref.id == reference_id:

                selected = ref

                break


        if selected is None:

            return


        self.reference_properties.load_reference(
            selected
        )

#         print("LOADED REFERENCE:", selected)

        self.reference_properties.show()

#         print("WINDOW SHOWN")

        self.status.showMessage(
            f"Opened reference: {selected.title}"
        )

    # -------------------------------------------------
    # Status Bar
    # -------------------------------------------------

    def create_statusbar(self):


        self.status = QStatusBar()


        self.status.showMessage(
            "Ready"
        )


        self.setStatusBar(
            self.status
        )

    def on_work_created(self, work):

        self.project_tree.refresh()

        self.project_tree.refresh_and_select(
            work["title"]
        )