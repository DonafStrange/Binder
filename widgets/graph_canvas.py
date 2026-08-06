from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
)

from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QBrush,
)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
from widgets.graph_node import GraphNode
from services.work_service import WorkService
from services.graph import GraphService
from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtGui import QPen

class GraphCanvas(QGraphicsView):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.scene = QGraphicsScene()

        self.setScene(self.scene)

        self.filter_widget = QWidget(self)

        self.filter_layout = QVBoxLayout(
            self.filter_widget
        )

        self.filter_widget.setGeometry(
            10,
            10,
            180,
            180
        )

        self.work_service = WorkService()

        self.graph_service = GraphService()

        self.node_items = {}
        self.edge_items = []

        self.edge_filters = {

            "shared_reference": True,

            "reference": True,

            "attachment": True,

            "tag": True,

            "category": True

        }

        self.graph_service.sync_works()

        self.load_works()

        self.load_edges()

        self.setRenderHint(
            QPainter.Antialiasing
        )

        self.setDragMode(
            QGraphicsView.ScrollHandDrag
        )

        self.create_zoom_buttons()

        self.create_edge_filters()

        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.AnchorUnderMouse
        )

    def load_works(self):

        graph_nodes = self.graph_service.graph["nodes"]

        # --------------------------------------------
        # Layer positions
        # --------------------------------------------

        layer_y = {
            "category": -500,
            "tag": -250,
            "work": 0,
            "reference": 250,
            "attachment": 500
        }

        # --------------------------------------------
        # Group nodes by type
        # --------------------------------------------

        layers = {
            "category": [],
            "tag": [],
            "work": [],
            "reference": [],
            "attachment": []
        }

        for graph_node in graph_nodes:

            node_type = graph_node["type"]

            if node_type in layers:

                layers[node_type].append(graph_node)

        SPACING_X = 180

        # --------------------------------------------
        # Draw every layer
        # --------------------------------------------

        for node_type, nodes in layers.items():

            count = len(nodes)

            if count == 0:
                continue

            total_width = (count - 1) * SPACING_X
            start_x = -total_width / 2

            for i, graph_node in enumerate(nodes):

                node = GraphNode(
                    graph_node["label"]
                )

                node.graph_id = graph_node["id"]
                node.graph_type = graph_node["type"]

                # ------------------------------------
                # Node colours
                # ------------------------------------

                if node_type == "reference":

                    node.setBrush(
                        QBrush(QColor("orange"))
                    )

                elif node_type == "attachment":

                    node.setBrush(
                        QBrush(QColor("gold"))
                    )

                elif node_type == "tag":

                    node.setBrush(
                        QBrush(QColor("magenta"))
                    )

                elif node_type == "category":

                    node.setBrush(
                        QBrush(QColor("green"))
                    )

                x = start_x + i * SPACING_X
                offset = 30

                if i % 2 == 0:
                    y = layer_y[node_type] - offset
                else:
                    y = layer_y[node_type] + offset

                node.setPos(
                    x,
                    y
                )

                self.scene.addItem(
                    node
                )

                self.node_items[
                    graph_node["label"]
                ] = node

        self.scene.setSceneRect(
            self.scene.itemsBoundingRect()
        )

        self.fitInView(
            self.scene.sceneRect(),
            Qt.KeepAspectRatio
        )

    def load_edges(self):

        for edge_item in list(self.edge_items):
            self.scene.removeItem(edge_item)

        self.edge_items.clear()

        for edge in self.graph_service.graph["edges"]:

            source = None
            target = None

            for node in self.graph_service.graph["nodes"]:
                if node["id"] == edge["source"]:
                    source = node["label"]
                if node["id"] == edge["target"]:
                    target = node["label"]

            if source is None or target is None:
                continue

            node1 = self.node_items.get(source)
            node2 = self.node_items.get(target)

            if node1 is None:
                print("Missing node:", source)

            if node2 is None:
                print("Missing node:", target)

            if node1 is None or node2 is None:
                continue

            relations = edge.get("relations", [])
            if not relations:
                continue

            visible = False
            for relation in relations:
                if self.edge_filters.get(relation, True):
                    visible = True
                    break

            if not visible:
                continue

            print(
                "Drawing:",
                relation,
                source,
                "->",
                target
            )

            line = QGraphicsLineItem(
                node1.pos().x(),
                node1.pos().y(),
                node2.pos().x(),
                node2.pos().y()
            )

            weight = edge.get("weight", 1)

            relation = relations[0]
            if relation == "shared_reference":
                color = Qt.green
            elif relation == "reference":
                color = Qt.blue
            elif relation == "attachment":
                color = Qt.darkYellow
            elif relation == "tag":
                color = Qt.magenta
            else:
                color = Qt.gray

            pen = QPen(color, 1 + weight)
            line.setPen(pen)

            self.scene.addItem(line)
            self.edge_items.append(line)

        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.scene.update()
        self.viewport().update()

    def create_edge_filters(self):

        for relation in self.edge_filters:

            box = QCheckBox(
                relation,
                self.filter_widget
            )

            box.setChecked(True)

            box.stateChanged.connect(
                lambda state, r=relation:
                    self.toggle_edge_filter(
                        r,
                        state
                    )
            )

            self.filter_layout.addWidget(
                box
            )

    def toggle_edge_filter(self, relation, state):

        checked = bool(state)
        if isinstance(state, Qt.CheckState):
            checked = state == Qt.CheckState.Checked
        elif isinstance(state, int):
            checked = state == Qt.CheckState.Checked.value

        self.edge_filters[relation] = checked

        self.load_edges()

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