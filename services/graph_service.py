import json
from pathlib import Path



class GraphService:


    def __init__(self):

        self.graph_file = Path(
            "graph/graph.json"
        )


        self.graph_file.parent.mkdir(
            exist_ok=True
        )


        self.graph = {

            "nodes": [],

            "edges": []

        }


        self.load()



    # -------------------------------------------------
    # Load Graph
    # -------------------------------------------------

    def load(self):

        if self.graph_file.exists():

            self.graph = json.loads(

                self.graph_file.read_text(
                    encoding="utf-8"
                )

            )



    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    def save(self):

        self.graph_file.write_text(

            json.dumps(

                self.graph,

                indent=4

            ),

            encoding="utf-8"

        )



    # -------------------------------------------------
    # Add Node
    # -------------------------------------------------

    def add_node(
            self,
            node_id,
            label,
            node_type
    ):


        for node in self.graph["nodes"]:

            if node["id"] == node_id:

                return



        self.graph["nodes"].append(

            {

                "id": node_id,

                "label": label,

                "type": node_type

            }

        )


        self.save()



    # -------------------------------------------------
    # Add Connection
    # -------------------------------------------------

    def add_edge(
            self,
            source,
            target,
            relation
    ):


        edge = {

            "source": source,

            "target": target,

            "relation": relation

        }


        if edge not in self.graph["edges"]:

            self.graph["edges"].append(
                edge
            )


        self.save()



    # -------------------------------------------------
    # Remove Node
    # -------------------------------------------------

    def remove_node(
            self,
            node_id
    ):


        self.graph["nodes"] = [

            n for n in self.graph["nodes"]

            if n["id"] != node_id

        ]


        self.graph["edges"] = [

            e for e in self.graph["edges"]

            if (
                e["source"] != node_id

                and

                e["target"] != node_id
            )

        ]


        self.save()



    # -------------------------------------------------
    # Get Graph
    # -------------------------------------------------

    def get_graph(self):

        return self.graph



    # -------------------------------------------------
    # Neighbours
    # -------------------------------------------------

    def neighbours(
            self,
            node_id
    ):


        connected=[]


        for edge in self.graph["edges"]:


            if edge["source"] == node_id:

                connected.append(
                    edge["target"]
                )


            elif edge["target"] == node_id:

                connected.append(
                    edge["source"]
                )


        return connected