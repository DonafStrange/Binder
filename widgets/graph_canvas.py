from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
)

from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
from widgets.graph_node import GraphNode
from services.work_service import WorkService
from services.graph import GraphService

class GraphCanvas(QGraphicsView):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.scene = QGraphicsScene()

        self.setScene(self.scene)

        self.work_service = WorkService()

        self.graph_service = GraphService()

        self.graph_service.sync_works()

        self.load_works()

        self.setRenderHint(
            QPainter.Antialiasing
        )

        self.setDragMode(
            QGraphicsView.ScrollHandDrag
        )

        self.create_zoom_buttons()

        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.AnchorUnderMouse
        )

    def load_works(self):

        import random
        import math

        works = self.work_service.get_all_works()

        placed_positions = []

        MIN_DISTANCE = 140

        AREA = 1200

        for work in works:

            while True:

                x = random.randint(
                    -AREA,
                    AREA
                )

                y = random.randint(
                    -AREA,
                    AREA
                )

                good = True

                for px, py in placed_positions:

                    distance = math.hypot(
                        x - px,
                        y - py
                    )

                    if distance < MIN_DISTANCE:

                        good = False

                        break

                if good:

                    placed_positions.append(
                        (x, y)
                    )

                    break


            node = GraphNode(
                work.title
            )

            node.work = work

            node.setPos(
                x,
                y
            )

            self.scene.addItem(
                node
            )

        self.scene.setSceneRect(
            self.scene.itemsBoundingRect()
        )

        self.fitInView(
            self.scene.sceneRect(),
            Qt.KeepAspectRatio
        )

    def zoom_in(self):

        self.scale(
            1.15,
            1.15
        )

    def zoom_out(self):

        self.scale(
            1 / 1.15,
            1 / 1.15
        )


    def fit_graph(self):

        self.fitInView(
            self.scene.itemsBoundingRect(),
            Qt.KeepAspectRatio
        )


    def wheelEvent(self, event):

        if event.angleDelta().y() > 0:

            self.zoom_in()

        else:

            self.zoom_out()

    def keyPressEvent(self, event):

        if event.modifiers() == Qt.ControlModifier:

            if event.key() == Qt.Key_Plus:

                self.zoom_in()

                return


            if event.key() == Qt.Key_Minus:

                self.zoom_out()

                return


            if event.key() == Qt.Key_0:

                self.fit_graph()

                return


        super().keyPressEvent(event)

    def create_zoom_buttons(self):

        self.zoom_in_button = QPushButton(
            "+"
        )

        self.zoom_out_button = QPushButton(
            "-"
        )

        self.fit_button = QPushButton(
            "⊙"
        )


        for button in [
            self.zoom_in_button,
            self.zoom_out_button,
            self.fit_button
        ]:

            button.setFixedSize(
                35,
                35
            )

            button.setStyleSheet(
                """
                QPushButton
                {
                    background-color: rgba(50,50,50,160);
                    color:white;
                    border-radius:17px;
                    font-size:18px;
                }

                QPushButton:hover
                {
                    background-color: rgba(80,80,80,220);
                }
                """
            )


        self.zoom_in_button.clicked.connect(
            self.zoom_in
        )

        self.zoom_out_button.clicked.connect(
            self.zoom_out
        )

        self.fit_button.clicked.connect(
            self.fit_graph
        )


        self.zoom_buttons = [
            self.zoom_in_button,
            self.zoom_out_button,
            self.fit_button
        ]


        for button in self.zoom_buttons:

            button.setParent(
                self
            )

    def resizeEvent(self, event):

        super().resizeEvent(event)


        x = self.width() - 50

        y = self.height() - 140


        for i, button in enumerate(
            self.zoom_buttons
        ):

            button.move(
                x,
                y + i*40
            )