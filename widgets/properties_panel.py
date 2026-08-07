from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QInputDialog,
    QMenu,
)
from pathlib import Path
from services.markdown_service import MarkdownService
from services.reference_service import ReferenceService
from PySide6.QtWidgets import QSizePolicy
from services.work_service import WorkService
import shutil

from PySide6.QtWidgets import QListWidget
from widgets.code_viewer import CodeViewer

class TagListWidget(QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())
            if item is not None:
                self.setCurrentItem(item)
            self.customContextMenuRequested.emit(event.pos())
            event.accept()
            return

        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item is not None:
            self.setCurrentItem(item)
        self.customContextMenuRequested.emit(event.pos())
        event.accept()

class PropertiesPanel(QWidget):

    referenceClicked = Signal(int)
    workDeleted = Signal()
    def __init__(self):

        super().__init__()

        self.markdown_service = MarkdownService()

        self.reference_service = ReferenceService()

        self.work_service = WorkService()

        self.build_ui()


    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(self)


        # ---------------- Metadata ----------------

        metadata_box = QGroupBox(
            "Work Information"
        )


        metadata_layout = QFormLayout()


        self.title = QLabel("None")
        self.title.setWordWrap(True)
        self.title.setMaximumWidth(100)
        self.title.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Preferred
        )

        self.category = QLabel(
            "None"
        )

        self.created = QLabel(
            "-"
        )

        self.modified = QLabel(
            "-"
        )


        metadata_layout.addRow(
            "Title:",
            self.title
        )

        metadata_layout.addRow(
            "Category:",
            self.category
        )


        metadata_layout.addRow(
            "Created:",
            self.created
        )


        metadata_layout.addRow(
            "Modified:",
            self.modified
        )


        metadata_box.setLayout(
            metadata_layout
        )


        layout.addWidget(
            metadata_box
        )



        # ---------------- Tags ----------------


        tag_box = QGroupBox(
            "Tags"
        )


        tag_layout = QVBoxLayout()


        self.tags = TagListWidget(self)

        self.tags.customContextMenuRequested.connect(
            self.tag_menu
        )

        self.tags.itemClicked.connect(
            lambda item: None
        )
        self.tags.itemSelectionChanged.connect(
            self.update_tag_buttons_state
        )
        self.tags.setSelectionMode(QListWidget.SingleSelection)

        tag_layout.addWidget(
            self.tags
        )

        tag_buttons = QHBoxLayout()
        tag_buttons.setContentsMargins(0, 6, 0, 0)
        tag_buttons.setSpacing(6)

        self.add_tag_btn = QPushButton("Add Tag")
        self.add_tag_btn.clicked.connect(self.add_tag)
        tag_buttons.addWidget(self.add_tag_btn)

        self.rename_tag_btn = QPushButton("Rename")
        self.rename_tag_btn.clicked.connect(self.rename_tag)
        self.rename_tag_btn.setEnabled(False)
        tag_buttons.addWidget(self.rename_tag_btn)

        self.delete_tag_btn = QPushButton("Delete")
        self.delete_tag_btn.clicked.connect(self.delete_tag)
        self.delete_tag_btn.setEnabled(False)
        tag_buttons.addWidget(self.delete_tag_btn)

        tag_buttons.addStretch()

        tag_layout.addLayout(tag_buttons)


        tag_box.setLayout(
            tag_layout
        )


        layout.addWidget(
            tag_box
        )



        # ---------------- References ----------------


        ref_box = QGroupBox(
            "References"
        )


        ref_layout = QVBoxLayout()


        self.references = QListWidget()

        self.references.itemDoubleClicked.connect(
            self.open_reference
        )


        ref_layout.addWidget(
            self.references
        )


        ref_box.setLayout(
            ref_layout
        )


        layout.addWidget(
            ref_box
        )

        # ---------------- Codes ----------------

        code_box = QGroupBox(
            "Codes"
        )

        code_layout = QVBoxLayout()

        self.codes = QListWidget()

        self.codes.itemDoubleClicked.connect(
            self.open_code
        )

        code_layout.addWidget(
            self.codes
        )

        self.add_code_btn = QPushButton(
            "Add Code"
        )

        self.add_code_btn.clicked.connect(
            self.add_code
        )

        code_layout.addWidget(
            self.add_code_btn
        )

        self.delete_code_btn = QPushButton(
            "Delete Code"
        )

        self.delete_code_btn.clicked.connect(
            self.delete_code
        )

        code_layout.addWidget(
            self.delete_code_btn
        )

        self.insert_code_md_btn = QPushButton(
            "Insert Code Link"
        )

        self.insert_code_md_btn.clicked.connect(
            self.insert_code_reference
        )

        code_layout.addWidget(
            self.insert_code_md_btn
        )

        code_box.setLayout(
            code_layout
        )

        layout.addWidget(
            code_box
        )

        # ---------------- Attachments ----------------


        attachment_box = QGroupBox(
            "Attachments"
        )


        attachment_layout = QVBoxLayout()


        self.attachments = QListWidget()


        attachment_layout.addWidget(
            self.attachments
        )

        self.delete_attachment_btn = QPushButton(
            "Delete Attachment"
        )

        self.delete_attachment_btn.clicked.connect(
            self.delete_attachment
        )

        attachment_layout.addWidget(
            self.delete_attachment_btn
        )

        attachment_box.setLayout(
            attachment_layout
        )


        layout.addWidget(
            attachment_box
        )



        # ---------------- Buttons ----------------


        self.open_folder = QPushButton(
            "Open Folder"
        )


        self.export_btn = QPushButton(
            "Export Work"
        )


        layout.addWidget(
            self.open_folder
        )


        layout.addWidget(
            self.export_btn
        )

        self.delete_work_btn = QPushButton(
            "Delete Work"
        )

        self.delete_work_btn.clicked.connect(
            self.delete_work
        )

        layout.addWidget(
            self.delete_work_btn
        )


        layout.addStretch()



    # -------------------------------------------------
    # Update Data
    # -------------------------------------------------

    def load_work(self, work):
        """
        Receive a Work object
        and update the panel.
        """

        if work is None:

            return

        self.current_work = work

        self.title.setText(
            work.title
        )


        self.category.setText(
            work.category
        )


        self.created.setText(
            work.created
        )


        self.modified.setText(
            work.modified
        )


        self.tags.clear()

        for tag in work.tags:

            self.tags.addItem(
                tag
            )



        self.references.clear()


        for ref in work.references:

            self.references.addItem(
                str(ref)
            )

        self.codes.clear()

        code_folder = Path(work.folder) / "codes"

        if code_folder.exists():

            for file in sorted(code_folder.iterdir()):

                if file.is_file():

                    self.codes.addItem(
                        file.name
                    )

        # ---------------- Load attachments used in this work ----------------

        self.attachments.clear()

        note_file = Path(work.folder) / work.markdown_file

        if note_file.exists():

            import re

            text = note_file.read_text(encoding="utf-8")

            # Find Markdown links/images:
            # ![...](path) or [...](path)

            matches = re.findall(
                r'\[[^\]]*\]\((.*?)\)|!\[[^\]]*\]\((.*?)\)',
                text
            )

            for normal_link, image_link in matches:

                path = normal_link or image_link

                if path:

                    self.attachments.addItem(
                        Path(path).name
                    )

        # Load cited references

        self.references.clear()

        citation_ids = self.markdown_service.extract_citations(

            str(Path(work.folder) / work.markdown_file)

        )
#         print("Citation IDs:", citation_ids)

        all_references = self.reference_service.get_all_references()


        for ref in all_references:
            # print(
            #     "Reference:",
            #     ref.id,
            #     ref.citation_key,
            #     ref.title
            # )

            if ref.citation_key in citation_ids:
                # print("ADDING:", ref.citation_key)

                item = QListWidgetItem(f"{ref.citation_key} | {ref.title}")
                item.setData(Qt.UserRole, ref.id)
                self.references.addItem(item)

    def open_reference(self, item):

        #print("REFERENCE CLICKED")

        reference_id = item.data(Qt.UserRole)

        if reference_id is None:
            text = item.text()
            try:
                reference_id = int(text.split("|")[0].strip())
            except (TypeError, ValueError):
                citation_key = text.split("|")[0].strip()
                for ref in self.reference_service.get_all_references():
                    if ref.citation_key == citation_key:
                        reference_id = ref.id
                        break

        if reference_id is None:
            return

        self.referenceClicked.emit(
            int(reference_id)
        )

    def add_code(self):

        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Code File",
            "",
            (
                "Code Files ("
                "*.py "
                "*.m "
                "*.mlx "
                "*.cpp "
                "*.c "
                "*.h "
                "*.hpp "
                "*.java "
                "*.jl "
                "*.R "
                "*.sh "
                "*.ipynb "
                "*.json "
                "*.yaml "
                "*.yml "
                "*.xml "
                "*.sql"
                ");;All Files (*)"
            )
        )

        if not filename:
            return

        source = Path(filename)

        code_folder = Path(
            self.current_work.folder
        ) / "codes"


        code_folder.mkdir(
            exist_ok=True
        )


        destination = code_folder / source.name


        shutil.copy(
            source,
            destination
        )

        self.update_code_markdown()

        self.load_work(
            self.current_work
        )
    def insert_code_reference(self):

        item = self.codes.currentItem()

        if item is None:
            return


        code_name = item.text()


        note_file = (
            Path(self.current_work.folder)
            / self.current_work.markdown_file
        )


        with open(
            note_file,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                f"\n```code-file\ncodes/{code_name}\n```\n"
            )

    def open_code(self, item):

        code_file = (
            Path(self.current_work.folder)
            / "codes"
            / item.text()
        )

        self.code_window = CodeViewer(
            code_file
        )

        self.code_window.show()

    def delete_code(self):

        item = self.codes.currentItem()

        if item is None:
            return


        code_file = (
            Path(self.current_work.folder)
            / "codes"
            / item.text()
        )


        if code_file.exists():

            code_file.unlink()


        self.codes.takeItem(
            self.codes.row(item)
        )

    def update_code_markdown(self):

        code_folder = (
            Path(self.current_work.folder)
            / "codes"
        )


        code_files = list(
            code_folder.iterdir()
        )


        note_file = (
            Path(self.current_work.folder)
            / self.current_work.markdown_file
        )


        self.markdown_service.update_code_section(
            note_file,
            code_files
        )

    def delete_attachment(self):

        item = self.attachments.currentItem()

        if item is None:
#             print("No attachment selected")
            return


        from PySide6.QtWidgets import QMessageBox
        from pathlib import Path


        filename = item.text()


        reply = QMessageBox.question(
            self,
            "Delete Attachment",
            f"Delete '{filename}'?",
            QMessageBox.Yes | QMessageBox.No
        )


        if reply != QMessageBox.Yes:
            return


        if not hasattr(self, "current_work"):

#             print("No work selected")
            return


        attachment_folder = Path(
            "attachments"
        )

        deleted = False

        for file in attachment_folder.rglob(filename):

            if file.is_file():

                file.unlink()

                # print(
                #     "Deleted:",
                #     file
                # )

                deleted = True

                break


        if deleted:

            self.attachments.takeItem(
                self.attachments.row(item)
            )

        else:

            # print(
            #     "Attachment not found"
            # )
            pass

    # -------------------------------------------------
    # Clear
    # -------------------------------------------------

    def clear(self):

        self.title.setText(
            "None"
        )

        self.category.setText(
            "None"
        )

        self.tags.clear()

        self.references.clear()

        self.attachments.clear()

    def delete_work(self):

        if not hasattr(self, "current_work"):

#             print("No work selected")
            return


        from PySide6.QtWidgets import QMessageBox


        reply = QMessageBox.question(
            self,
            "Delete Work",
            f"Delete '{self.current_work.title}'?",
            QMessageBox.Yes | QMessageBox.No
        )


        if reply == QMessageBox.Yes:

            self.work_service.delete_work(
                self.current_work.id
            )


            QMessageBox.information(
                self,
                "Deleted",
                "Work deleted successfully."
            )

            self.clear()

            self.workDeleted.emit()

    def tag_menu(self, position):

        menu = QMenu()

        add_action = menu.addAction("Add New Tag")
        rename_action = menu.addAction("Rename Tag")
        remove_action = menu.addAction("Delete Tag")

        action = menu.exec(
            self.tags.mapToGlobal(position)
        )

        if action == add_action:
            self.add_tag()
        elif action == rename_action:
            self.rename_tag()
        elif action == remove_action:
            self.delete_tag()

    def update_tag_buttons_state(self):
        has_selection = self.tags.currentItem() is not None
        self.rename_tag_btn.setEnabled(has_selection)
        self.delete_tag_btn.setEnabled(has_selection)

    def refresh_tags(self):

        if not hasattr(self, "current_work") or self.current_work is None:
            return

        self.current_work.tags = self.work_service.get_work_tags(
            self.current_work.id
        )

        self.tags.clear()

        for tag in self.current_work.tags:
            self.tags.addItem(tag)

        self.update_tag_buttons_state()

    def add_tag(self):

        if self.current_work is None:
            return

        tag, ok = QInputDialog.getText(
            self,
            "Add New Tag",
            "Tag name:"
        )

        if ok and tag.strip():
            self.work_service.add_tag_to_work(
                self.current_work.id,
                tag.strip()
            )
            self.refresh_tags()

    def rename_tag(self):

        if self.current_work is None:
            return

        item = self.tags.currentItem()

        if item is None:
            return

        current_name = item.text().strip()
        if not current_name:
            return

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Tag",
            "New tag name:",
            text=current_name
        )

        if not ok:
            return

        new_name = new_name.strip()
        if not new_name:
            return

        if new_name.lower() == current_name.lower():
            return

        tag_id = self.work_service.get_tag_id_by_name(current_name)
        if tag_id is None:
            return

        if self.work_service.get_tag_id_by_name(new_name) is not None and self.work_service.get_tag_id_by_name(new_name) != tag_id:
            reply = QMessageBox.question(
                self,
                "Duplicate Tag",
                f"A tag named '{new_name}' already exists. Merge it into the existing tag?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        self.work_service.rename_tag(tag_id, new_name)
        self.refresh_tags()

    def delete_tag(self):

        if self.current_work is None:
            return

        item = self.tags.currentItem()

        if item is None:
            return

        tag_name = item.text().strip()
        if not tag_name:
            return

        reply = QMessageBox.question(
            self,
            "Delete Tag",
            "Delete this tag from the selected work?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.work_service.remove_tag_from_work(
            self.current_work.id,
            tag_name
        )
        self.refresh_tags()