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
)
from pathlib import Path
from services.markdown_service import MarkdownService
from services.reference_service import ReferenceService
from PySide6.QtWidgets import QSizePolicy
from services.work_service import WorkService


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


        self.tags = QListWidget()

        self.tags.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.tags.customContextMenuRequested.connect(
            self.tag_menu
        )

        self.tags.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.tags.customContextMenuRequested.connect(
            lambda pos: print("RIGHT CLICK EVENT", pos)
        )

#         print("TAG SIGNAL CONNECTED")

        tag_layout.addWidget(
            self.tags
        )


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

#         print("TAG MENU OPENED")

        from PySide6.QtWidgets import QMenu, QInputDialog


        menu = QMenu()


        add_action = menu.addAction(
            "Add Tag"
        )

        remove_action = menu.addAction(
            "Remove Tag"
        )


        action = menu.exec(
            self.tags.mapToGlobal(position)
        )


        if action == add_action:

            self.add_tag()


        elif action == remove_action:

            self.remove_tag()

    def add_tag(self):

        from PySide6.QtWidgets import QInputDialog


        if self.current_work is None:
            return


        tag, ok = QInputDialog.getText(
            self,
            "Add Tag",
            "Tag name:"
        )


        if ok and tag.strip():

            self.work_service.add_tag_to_work(
                self.current_work.id,
                tag.strip()
            )


            # Refresh tags display
            self.current_work.tags = self.work_service.get_work_tags(
                self.current_work.id
            )


            self.tags.clear()


            for t in self.current_work.tags:

                self.tags.addItem(t)

    def remove_tag(self):

        if self.current_work is None:
            return


        item = self.tags.currentItem()


        if item is None:
            return


        tag_name = item.text()


        self.work_service.remove_tag_from_work(
            self.current_work.id,
            tag_name
        )


        # Refresh tags display

        self.current_work.tags = self.work_service.get_work_tags(
            self.current_work.id
        )


        self.tags.clear()


        for t in self.current_work.tags:

            self.tags.addItem(t)