from pathlib import Path
import json
import uuid



class GraphService:


    def __init__(self):

        self.graph_file = Path(
            "graph/graph.json"
        )


        self.graph_file.parent.mkdir(
            exist_ok=True
        )


        self.initialize()



    # -------------------------------------------------
    # Initialize Graph
    # -------------------------------------------------

    def initialize(self):

        if not self.graph_file.exists():

            self.graph_file.write_text(

                json.dumps(
                    {
                        "nodes": [],
                        "edges": []
                    },
                    indent=4
                ),

                encoding="utf-8"
            )


        self.load()



    # -------------------------------------------------
    # Load
    # -------------------------------------------------

    def load(self):

        try:

            with open(
                self.graph_file,
                "r",
                encoding="utf-8"
            ) as file:

                self.graph = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            self.graph = {
                "nodes": [],
                "edges": []
            }

            self.save()



    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    def save(self):

        with open(
            self.graph_file,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(

                self.graph,

                file,

                indent=4

            )



    # -------------------------------------------------
    # Create Node
    # -------------------------------------------------

    def create_node(
            self,
            label,
            node_type
    ):


        node_id = (

            node_type

            +

            "_"

            +

            str(uuid.uuid4())[:8]

        )


        node = {

            "id": node_id,

            "label": label,

            "type": node_type

        }


        self.graph["nodes"].append(
            node
        )


        self.save()


        return node_id



    # -------------------------------------------------
    # Add Work
    # -------------------------------------------------

    def add_work(
            self,
            title
    ):


        return self.create_node(

            title,

            "work"

        )



    # -------------------------------------------------
    # Add Reference
    # -------------------------------------------------

    def add_reference(
            self,
            title
    ):


        return self.create_node(

            title,

            "reference"

        )



    # -------------------------------------------------
    # Connect Nodes
    # -------------------------------------------------

    def connect(
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
    # Link Work and Reference
    # -------------------------------------------------

    def cite(
            self,
            work_id,
            reference_id
    ):


        self.connect(

            work_id,

            reference_id,

            "cites"

        )



    # -------------------------------------------------
    # Find Node
    # -------------------------------------------------

    def find_node(
            self,
            label
    ):


        for node in self.graph["nodes"]:

            if node["label"] == label:

                return node


        return None



    # -------------------------------------------------
    # Delete Node
    # -------------------------------------------------

    def delete_node(
            self,
            node_id
    ):


        self.graph["nodes"] = [

            node

            for node in self.graph["nodes"]

            if node["id"] != node_id

        ]



        self.graph["edges"] = [

            edge

            for edge in self.graph["edges"]

            if (

                edge["source"] != node_id

                and

                edge["target"] != node_id

            )

        ]


        self.save()



    # -------------------------------------------------
    # Get Complete Graph
    # -------------------------------------------------

    def get_graph(self):

        return self.graph



    # -------------------------------------------------
    # Get Connections
    # -------------------------------------------------

    def get_connections(
            self,
            node_id
    ):


        result = []


        for edge in self.graph["edges"]:


            if edge["source"] == node_id:

                result.append(edge)


            elif edge["target"] == node_id:

                result.append(edge)


        return result