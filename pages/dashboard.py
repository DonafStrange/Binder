from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLineEdit,
    QFrame,
)


class InfoCard(QFrame):
    """Simple statistics card."""

    def __init__(self, title, value):
        super().__init__()

        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(90)

        layout = QVBoxLayout(self)

        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
        """)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color:gray;
            font-size:12px;
        """)

        layout.addWidget(value_label)
        layout.addWidget(title_label)


class Dashboard(QWidget):

    def __init__(self):
        super().__init__()

        self.build_ui()

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        title = QLabel("Research Dashboard")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        main_layout.addWidget(title)

        # --------------------------------------------------
        # Search Bar
        # --------------------------------------------------

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Search works, references, tags, equations..."
        )

        main_layout.addWidget(self.search)

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        stats_layout = QGridLayout()

        stats_layout.addWidget(
            InfoCard("Works", 12), 0, 0)

        stats_layout.addWidget(
            InfoCard("References", 185), 0, 1)

        stats_layout.addWidget(
            InfoCard("Attachments", 64), 0, 2)

        stats_layout.addWidget(
            InfoCard("Tags", 41), 0, 3)

        main_layout.addLayout(stats_layout)

        # --------------------------------------------------
        # Middle Layout
        # --------------------------------------------------

        middle_layout = QHBoxLayout()

        # Recent Works

        works_group = QGroupBox("Recent Works")

        works_layout = QVBoxLayout()

        self.work_list = QListWidget()

        self.work_list.addItems([
            "Wilson-Cowan Delay Model",
            "EEG Smartphone Experiment",
            "DWI Preprocessing",
            "Alzheimer Simulation",
            "Computational Psychiatry Notes"
        ])

        works_layout.addWidget(self.work_list)

        works_group.setLayout(works_layout)

        middle_layout.addWidget(works_group)

        # Recent References

        ref_group = QGroupBox("Recent References")

        ref_layout = QVBoxLayout()

        self.ref_list = QListWidget()

        self.ref_list.addItems([
            "Wilson & Cowan (1972)",
            "Breakspear (2017)",
            "MNE Documentation",
            "MRtrix3 Documentation",
            "Friston (2010)"
        ])

        ref_layout.addWidget(self.ref_list)

        ref_group.setLayout(ref_layout)

        middle_layout.addWidget(ref_group)

        main_layout.addLayout(middle_layout)

        # --------------------------------------------------
        # Quick Actions
        # --------------------------------------------------

        action_group = QGroupBox("Quick Actions")

        action_layout = QHBoxLayout()

        self.new_work_btn = QPushButton("New Work")
        self.new_ref_btn = QPushButton("New Reference")
        self.graph_btn = QPushButton("Graph View")
        self.import_btn = QPushButton("Import PDF")
        self.export_btn = QPushButton("Export")

        action_layout.addWidget(self.new_work_btn)
        action_layout.addWidget(self.new_ref_btn)
        action_layout.addWidget(self.graph_btn)
        action_layout.addWidget(self.import_btn)
        action_layout.addWidget(self.export_btn)

        action_group.setLayout(action_layout)

        main_layout.addWidget(action_group)

        # --------------------------------------------------
        # Activity
        # --------------------------------------------------

        activity_group = QGroupBox("Recent Activity")

        activity_layout = QVBoxLayout()

        self.activity = QListWidget()

        self.activity.addItems([
            "Edited Wilson-Cowan Delay Model",
            "Added paper: Breakspear (2017)",
            "Imported DWI.pdf",
            "Created tag #EEG",
            "Attached figure1.png"
        ])

        activity_layout.addWidget(self.activity)

        activity_group.setLayout(activity_layout)

        main_layout.addWidget(activity_group)

        main_layout.addStretch()