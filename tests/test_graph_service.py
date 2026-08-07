import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, "/home/donaf-strange/Desktop/Binder")

from services.graph import GraphService
from widgets.graph_canvas import GraphCanvas


class GraphServiceEdgeTests(unittest.TestCase):

    def test_connect_creates_separate_edges_for_different_relations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GraphService()
            service.graph_file = Path(tmpdir) / "graph.json"
            service.graph = {"nodes": [], "edges": []}
            service.save()

            service.graph["nodes"] = [
                {"id": "node_a", "label": "Node A", "type": "category"},
                {"id": "node_b", "label": "Node B", "type": "work"},
            ]
            service.connect("node_a", "node_b", "category")

            service.graph["nodes"] = [
                {"id": "tag_a", "label": "Tag A", "type": "tag"},
                {"id": "category_a", "label": "Category A", "type": "category"},
            ]
            service.connect("tag_a", "category_a", "tag")

            matching_edges = [
                edge
                for edge in service.graph["edges"]
                if edge["source"] in {"node_a", "tag_a"} and edge["target"] in {"node_b", "category_a"}
            ]

            self.assertEqual(len(matching_edges), 2)
            self.assertEqual(
                {edge.get("relation") for edge in matching_edges},
                {"category", "tag"},
            )

    def test_find_node_by_label_and_type_ignores_whitespace_and_case(self):
        service = GraphService()
        service.graph = {
            "nodes": [
                {"id": "cat_1", "label": "Neuro Imaging", "type": "category"},
                {"id": "work_1", "label": "Alpha", "type": "work"},
            ],
            "edges": [],
        }

        node = service.find_node_by_label_and_type(" neuro imaging ", "category")
        self.assertIsNotNone(node)
        self.assertEqual(node["id"], "cat_1")

    def test_edge_type_uses_endpoint_types_over_conflicting_relation_strings(self):
        service = GraphService()
        service.graph = {
            "nodes": [
                {"id": "tag_1", "label": "Tag Name", "type": "tag"},
                {"id": "work_1", "label": "Work Title", "type": "work"},
            ],
            "edges": [
                {
                    "source": "tag_1",
                    "target": "work_1",
                    "relation": "category",
                    "relations": ["category", "tag"],
                }
            ],
        }

        edge = service.graph["edges"][0]
        self.assertEqual(service.resolve_edge_type(edge), "tag")

        service.normalize_edges()
        self.assertEqual(service.graph["edges"][0]["relation"], "tag")
        self.assertEqual(service.graph["edges"][0]["relations"], ["tag"])

    def test_category_edge_respects_category_endpoint_type(self):
        service = GraphService()
        service.graph = {
            "nodes": [
                {"id": "cat_1", "label": "Category A", "type": "category"},
                {"id": "work_1", "label": "Work Title", "type": "work"},
            ],
            "edges": [
                {
                    "source": "cat_1",
                    "target": "work_1",
                    "relation": "tag",
                    "relations": ["tag", "category"],
                }
            ],
        }

        edge = service.graph["edges"][0]
        self.assertEqual(service.resolve_edge_type(edge), "category")

        service.normalize_edges()
        self.assertEqual(service.graph["edges"][0]["relation"], "category")
        self.assertEqual(service.graph["edges"][0]["relations"], ["category"])

    def test_tag_edges_link_to_categories_instead_of_works(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GraphService()
            service.graph_file = Path(tmpdir) / "graph.json"
            service.graph = {"nodes": [], "edges": []}
            service.save()

            category_id = service.add_category("Category A")
            work_one_id = service.add_work("Work 1")
            work_two_id = service.add_work("Work 2")
            tag_id = service.create_node("Tag X", "tag")

            works = [
                SimpleNamespace(title="Work 1", category="Category A", tags=["Tag X"]),
                SimpleNamespace(title="Work 2", category="Category A", tags=["Tag X"]),
            ]

            service.connect(tag_id, work_one_id, "tag", reason="stale", created_by_function="test")
            service.connect(tag_id, work_two_id, "tag", reason="stale", created_by_function="test")
            service.connect(tag_id, tag_id, "tag", reason="stale", created_by_function="test")
            service.sync_category_connections(works)
            service.sync_tag_connections(works)

            category_edges = [
                edge
                for edge in service.graph["edges"]
                if edge.get("source") == category_id and edge.get("target") in {work_one_id, work_two_id}
            ]
            tag_to_work_edges = [
                edge
                for edge in service.graph["edges"]
                if edge.get("relation") == "tag"
                and edge.get("source") == tag_id
                and edge.get("target") in {work_one_id, work_two_id}
            ]
            tag_to_category_edges = [
                edge
                for edge in service.graph["edges"]
                if edge.get("relation") == "tag"
                and edge.get("source") == tag_id
                and edge.get("target") == category_id
            ]
            tag_to_tag_edges = [
                edge
                for edge in service.graph["edges"]
                if edge.get("relation") == "tag"
                and edge.get("source") == tag_id
                and edge.get("target") == tag_id
            ]

            self.assertEqual(len(category_edges), 2)
            self.assertEqual({edge.get("relation") for edge in category_edges}, {"category"})
            self.assertEqual(tag_to_work_edges, [])
            self.assertEqual(tag_to_tag_edges, [])
            self.assertEqual(len(tag_to_category_edges), 1)

    def test_sync_normalizes_duplicate_category_labels_and_whitespace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GraphService()
            service.graph_file = Path(tmpdir) / "graph.json"
            service.graph = {"nodes": [], "edges": []}
            service.save()

            service.create_node("Physics", "category")
            service.create_node(" physics ", "category")
            service.add_work("Work A")
            service.add_work("Work B")

            works = [
                SimpleNamespace(title="Work A", category="Physics", tags=[]),
                SimpleNamespace(title="Work B", category="physics ", tags=[]),
            ]

            service.sync_category_connections(works)

            category_nodes = [node for node in service.graph["nodes"] if node.get("type") == "category"]
            self.assertEqual(len(category_nodes), 1)
            self.assertEqual(category_nodes[0]["label"], "Physics")
            self.assertEqual(
                [edge for edge in service.graph["edges"] if edge.get("relation") == "category"],
                [
                    {"source": category_nodes[0]["id"], "target": service.find_node_by_label_and_type("Work A", "work")["id"], "relation": "category", "relations": ["category"]},
                    {"source": category_nodes[0]["id"], "target": service.find_node_by_label_and_type("Work B", "work")["id"], "relation": "category", "relations": ["category"]},
                ],
            )


if __name__ == "__main__":
    unittest.main()
