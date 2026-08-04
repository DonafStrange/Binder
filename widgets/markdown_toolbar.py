from PySide6.QtCore import Signal
from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction


class MarkdownToolbar(QToolBar):

    boldRequested = Signal()
    italicRequested = Signal()
    heading1Requested = Signal()
    heading2Requested = Signal()
    bulletRequested = Signal()
    equationRequested = Signal()
    imageRequested = Signal()
    pdfRequested = Signal()
    citationRequested = Signal()
    saveRequested = Signal()

    def __init__(self):
        super().__init__("Markdown Toolbar")

        self.setMovable(False)

        self.build_toolbar()

    def build_toolbar(self):

        save = QAction("💾 Save", self)
        save.triggered.connect(self.saveRequested)

        bold = QAction("B", self)
        bold.triggered.connect(self.boldRequested)

        italic = QAction("I", self)
        italic.triggered.connect(self.italicRequested)

        h1 = QAction("H1", self)
        h1.triggered.connect(self.heading1Requested)

        h2 = QAction("H2", self)
        h2.triggered.connect(self.heading2Requested)

        bullet = QAction("•", self)
        bullet.triggered.connect(self.bulletRequested)

        equation = QAction("∑", self)
        equation.triggered.connect(self.equationRequested)

        image = QAction("🖼", self)
        image.triggered.connect(self.imageRequested)

        pdf = QAction("PDF", self)
        pdf.triggered.connect(self.pdfRequested)

        cite = QAction("@", self)
        cite.triggered.connect(self.citationRequested)

        self.addAction(save)
        self.addSeparator()

        self.addAction(bold)
        self.addAction(italic)
        self.addSeparator()

        self.addAction(h1)
        self.addAction(h2)
        self.addAction(bullet)
        self.addSeparator()

        self.addAction(equation)
        self.addAction(image)
        self.addAction(pdf)
        self.addAction(cite)