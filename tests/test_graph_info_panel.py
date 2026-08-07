import os
import sys
import tempfile
import unittest
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication

sys.path.insert(0, "/home/donaf-strange/Desktop/Binder")

from services.graph import GraphService
from widgets.graph_info_panel import GraphInfoPanel
from widgets.graph_node import GraphNode


class GraphInfoPanelDispatchTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_load_node_dispatches_to_work_renderer(self):
        panel = GraphInfoPanel()
        panel.show_work = lambda node=None: setattr(panel, "last_renderer", "work")
        panel.show_reference = lambda node=None: setattr(panel, "last_renderer", "reference")
        panel.show_attachment = lambda node=None: setattr(panel, "last_renderer", "attachment")
        panel.show_category = lambda node=None: setattr(panel, "last_renderer", "category")
        panel.show_tag = lambda node=None: setattr(panel, "last_renderer", "tag")

        node = GraphNode("Example")
        node.graph_type = "work"
        node.work = SimpleNamespace(
            title="Example",
            category="Research",
            tags=["alpha"],
            created="2024-01-01",
            attachments=[],
            references=[],
            folder="works/example",
            markdown_file="note.md",
        )

        panel.load_node(node)

        self.assertEqual(panel.last_renderer, "work")


if __name__ == "__main__":
    unittest.main()
