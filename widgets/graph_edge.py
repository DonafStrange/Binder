from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtGui import QPen


class GraphEdge(QGraphicsLineItem):

    def __init__(self, source, target, color, weight=1):

        super().__init__()

        self.source = source
        self.target = target

        self.setPen(
            QPen(
                color,
                1 + weight
            )
        )

        self.update_position()


    def update_position(self):

        self.setLine(
            self.source.pos().x(),
            self.source.pos().y(),
            self.target.pos().x(),
            self.target.pos().y()
        )


    def update(self):

        self.update_position()

        super().update()