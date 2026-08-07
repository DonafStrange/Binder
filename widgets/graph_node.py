from PySide6.QtCore import Qt, Signal, QObject

from PySide6.QtGui import (
    QBrush,
    QColor,
    QPen,
    QFont
)

from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsSimpleTextItem,
    QGraphicsItem,
)


class GraphNodeSignals(QObject):

    clicked = Signal(object)


class GraphNode(QGraphicsEllipseItem):

    def __init__(self, title, radius=40):

        super().__init__(
            -radius,
            -radius,
            radius * 2,
            radius * 2
        )

        self.signals = GraphNodeSignals()
        self.clicked = self.signals.clicked

        self.setBrush(
            QBrush(
                QColor("#4A90E2")
            )
        )

        self.setPen(
            QPen(
                QColor("#1F4E79"),
                2
            )
        )

        self.setFlags(

            QGraphicsEllipseItem.ItemIsMovable
            |
            QGraphicsEllipseItem.ItemIsSelectable

        )

        self.label = QGraphicsSimpleTextItem(
            title,
            self
        )

        self.label.setBrush(
            QBrush(
                QColor("white")
            )
        )

        self.label.setFont(
            QFont(
                "Arial",
                8
            )
        )

        rect = self.label.boundingRect()

        self.label.setPos(
            -rect.width() / 2,
            -rect.height() / 2
        )

        self.edges = []

    def add_edge(self, edge):

        self.edges.append(edge)

    def itemChange(self, change, value):

        if change == QGraphicsItem.ItemPositionChange:

            for edge in self.edges:

                edge.update_position()

        return super().itemChange(
            change,
            value
        )

    def mousePressEvent(self, event):

        self.clicked.emit(self)
        super().mousePressEvent(event)