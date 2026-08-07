from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QSplitter
)
from PySide6.QtCore import Qt

from widgets.graph_canvas import GraphCanvas
from widgets.graph_info_panel import GraphInfoPanel


class GraphWindow(QWidget):

    def __init__(self):

        super().__init__()

        layout = QHBoxLayout(self)

        self.splitter = QSplitter(Qt.Horizontal)

        self.graph = GraphCanvas()

        self.info = GraphInfoPanel()

        self.splitter.addWidget(self.graph)

        self.splitter.addWidget(self.info)

        layout.addWidget(self.splitter)

        # start with information panel hidden
        self.info.hide()

        # graph takes all width
        self.splitter.setSizes([1, 0])

        self.graph.nodeSelected.connect(self.show_node_info)
        self.info.closed.connect(self.close_node_info)

        self.setLayout(layout)

    def show_node_info(self, node_data):

        self.info.set_node_data(node_data)
        self.info.show()
        self.splitter.setSizes([3, 1])

    def close_node_info(self):

        self.info.hide()
        self.splitter.setSizes([1, 0])