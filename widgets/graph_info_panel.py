from pathlib import Path
import sqlite3

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.work_service import WorkService


class GraphInfoPanel(QWidget):

    closed = Signal()

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setMinimumWidth(280)
        self.setMaximumWidth(420)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #f7f7f7;
            }
            QLabel {
                color: #222;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            """
        )

        self.node_data = None

        self.build_ui()
        self.set_empty_state()
        self.hide()

    def build_ui(self):

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("Information")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.title_label.setWordWrap(True)
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(28, 28)
        self.close_button.clicked.connect(self.handle_close)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.close_button)

        self.layout.addLayout(header_layout)

        divider = QFrame(self)
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(divider)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 8, 0, 0)
        self.content_layout.setSpacing(6)

        self.content_label = QLabel("Select a node to view its details.")
        self.content_label.setWordWrap(True)
        self.content_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.content_layout.addWidget(self.content_label)

        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

    def set_empty_state(self):

        self.content_label.setText("Select a node to view its details.")
        self.title_label.setText("Information")

    def handle_close(self):

        self.hide()
        self.closed.emit()

    def set_node_data(self, node_data):

        self.node_data = node_data

        if not node_data:
            self.set_empty_state()
            return

        node_type = node_data.get("type", "")
        label = node_data.get("label", "")
        self.title_label.setText(label or "Information")

        if node_type == "work":
            self.render_work_data(node_data)
        elif node_type == "reference":
            self.render_reference_data(node_data)
        elif node_type == "category":
            self.render_category_data(node_data)
        elif node_type == "tag":
            self.render_tag_data(node_data)
        elif node_type == "attachment":
            self.render_attachment_data(node_data)
        else:
            self.set_empty_state()

    def render_work_data(self, node_data):

        work_title = node_data.get("label", "")
        work_service = WorkService()
        work = None

        for candidate in work_service.get_all_works():
            if candidate.title == work_title:
                work = candidate
                break

        if work is None:
            self.content_label.setText("No work details available.")
            return

        summary = self._get_work_summary(work)
        references = self._get_work_references(work.id)
        attachments = self._get_work_attachments(work.id)

        text = []
        text.append("<b>Title</b><br>{}".format(work.title or "-"))
        text.append("<b>Category</b><br>{}".format(work.category or "-"))
        text.append("<b>Tags</b><br>{}".format(
            ", ".join(work.tags) if work.tags else "-"
        ))
        text.append("<b>Summary</b><br>{}".format(summary or "No summary available."))
        text.append("<b>References</b><br>{}".format(
            "<br>".join(references) if references else "-"
        ))
        text.append("<b>Attachments</b><br>{}".format(
            "<br>".join(attachments) if attachments else "-"
        ))

        self.content_label.setText("<br><br>".join(text))

    def render_reference_data(self, node_data):

        reference_title = node_data.get("label", "")
        connection = sqlite3.connect("database/database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT title, authors, year, journal, doi, url, abstract
            FROM reference_library
            WHERE title = ?
            LIMIT 1
            """,
            (reference_title,),
        )
        row = cursor.fetchone()
        connection.close()

        if row is None:
            self.content_label.setText("No reference details available.")
            return

        title, authors, year, journal, doi, url, abstract = row
        works = self._get_references_works(reference_title)

        text = []
        text.append("<b>Title</b><br>{}".format(title or "-"))
        text.append("<b>Authors</b><br>{}".format(authors or "-"))
        text.append("<b>Year</b><br>{}".format(year or "-"))
        text.append("<b>Journal</b><br>{}".format(journal or "-"))
        text.append("<b>DOI</b><br>{}".format(doi or "-"))
        text.append("<b>URL</b><br>{}".format(url or "-"))
        text.append("<b>Abstract</b><br>{}".format(abstract or "No abstract available."))
        text.append("<b>Works using this reference</b><br>{}".format(
            "<br>".join(works) if works else "-"
        ))

        self.content_label.setText("<br><br>".join(text))

    def render_category_data(self, node_data):

        category_name = node_data.get("label", "")
        connection = sqlite3.connect("database/database.db")
        cursor = connection.cursor()
        cursor.execute(
            "SELECT title FROM works WHERE category = ? ORDER BY title",
            (category_name,),
        )
        works = [row[0] for row in cursor.fetchall()]
        connection.close()

        text = []
        text.append("<b>Category name</b><br>{}".format(category_name or "-"))
        text.append("<b>Number of works</b><br>{}".format(len(works)))
        text.append("<b>List of works</b><br>{}".format(
            "<br>".join(works) if works else "-"
        ))
        self.content_label.setText("<br><br>".join(text))

    def render_tag_data(self, node_data):

        tag_name = node_data.get("label", "")
        connection = sqlite3.connect("database/database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT works.title
            FROM works
            JOIN work_tags ON work_tags.work_id = works.id
            JOIN tags ON tags.id = work_tags.tag_id
            WHERE tags.name = ?
            ORDER BY works.title
            """,
            (tag_name,),
        )
        works = [row[0] for row in cursor.fetchall()]
        connection.close()

        text = []
        text.append("<b>Tag name</b><br>{}".format(tag_name or "-"))
        text.append("<b>Number of works</b><br>{}".format(len(works)))
        text.append("<b>List of works</b><br>{}".format(
            "<br>".join(works) if works else "-"
        ))
        self.content_label.setText("<br><br>".join(text))

    def render_attachment_data(self, node_data):

        attachment_name = node_data.get("label", "")
        connection = sqlite3.connect("database/database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT filename, filetype, work_id
            FROM attachments
            WHERE filename = ?
            LIMIT 1
            """,
            (attachment_name,),
        )
        row = cursor.fetchone()
        connection.close()

        if row is None:
            self.content_label.setText("No attachment details available.")
            return

        filename, filetype, work_id = row
        work_title = "-"
        if work_id is not None:
            connection = sqlite3.connect("database/database.db")
            cursor = connection.cursor()
            cursor.execute("SELECT title FROM works WHERE id = ?", (work_id,))
            result = cursor.fetchone()
            connection.close()
            if result:
                work_title = result[0]

        text = []
        text.append("<b>File name</b><br>{}".format(filename or "-"))
        text.append("<b>File type</b><br>{}".format(filetype or "-"))
        text.append("<b>Work it belongs to</b><br>{}".format(work_title))
        self.content_label.setText("<br><br>".join(text))

    def _get_work_summary(self, work):

        note_path = Path(work.folder) / work.markdown_file
        if not note_path.exists():
            return ""

        try:
            text = note_path.read_text(encoding="utf-8")
        except Exception:
            return ""

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            if line.startswith("#"):
                continue
            if line.startswith("##"):
                continue
            return line

        return ""

    def _get_work_references(self, work_id):

        connection = sqlite3.connect("database/database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT reference_library.title
            FROM work_references
            JOIN reference_library ON reference_library.id = work_references.reference_id
            WHERE work_references.work_id = ?
            ORDER BY reference_library.title
            """,
            (work_id,),
        )
        rows = [row[0] for row in cursor.fetchall()]
        connection.close()
        return rows

    def _get_work_attachments(self, work_id):

        connection = sqlite3.connect("database/database.db")
        cursor = connection.cursor()
        cursor.execute(
            "SELECT filename FROM attachments WHERE work_id = ? ORDER BY filename",
            (work_id,),
        )
        rows = [row[0] for row in cursor.fetchall()]
        connection.close()
        return rows

    def _get_references_works(self, reference_title):

        connection = sqlite3.connect("database/database.db")
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT works.title
            FROM work_references
            JOIN works ON works.id = work_references.work_id
            JOIN reference_library ON reference_library.id = work_references.reference_id
            WHERE reference_library.title = ?
            ORDER BY works.title
            """,
            (reference_title,),
        )
        rows = [row[0] for row in cursor.fetchall()]
        connection.close()
        return rows
