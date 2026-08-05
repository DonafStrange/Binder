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
    # Add Category
    # -------------------------------------------------

    def add_category(
            self,
            name
    ):

        return self.create_node(

            name,

            "category"

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


        # check if connection already exists

        for edge in self.graph["edges"]:


            if (
                edge["source"] == source
                and
                edge["target"] == target
            ) or (
                edge["source"] == target
                and
                edge["target"] == source
            ):


                if "relations" not in edge:

                    # convert old format
                    edge["relations"] = [
                        edge.pop("relation")
                    ]


                if relation not in edge["relations"]:

                    edge["relations"].append(
                        relation
                    )


                self.save()

                return



        # create new connection

        edge = {

            "source": source,

            "target": target,

            "relations": [
                relation
            ]

        }


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

    def sync_works(self):

        from services.work_service import WorkService


        work_service = WorkService()

        works = work_service.get_all_works()

        # titles currently in database
        current_titles = [
            work.title
            for work in works
        ]


        # remove old deleted work nodes
        self.graph["nodes"] = [
            node
            for node in self.graph["nodes"]
            if (
                node["type"] != "work"
                or node["label"] in current_titles
            )
        ]


        # remove edges connected to deleted nodes
        valid_ids = {
            node["id"]
            for node in self.graph["nodes"]
        }


        self.graph["edges"] = [
            edge
            for edge in self.graph["edges"]
            if (
                edge["source"] in valid_ids
                and
                edge["target"] in valid_ids
            )
        ]


        # add missing works
        for work in works:

            if self.find_node(work.title) is None:

                self.add_work(
                    work.title
                )
        self.sync_category_connections()
        self.sync_tag_connections()
        self.sync_reference_connections()
        self.sync_attachment_connections()
        self.save()

    # -------------------------------------------------
    # Sync Tag Connections
    # -------------------------------------------------

    def sync_tag_connections(self):


        from services.work_service import WorkService


        work_service = WorkService()

        works = work_service.get_all_works()


        for i, work1 in enumerate(works):

            for work2 in works[i+1:]:


                common_tags = set(
                    work1.tags
                ).intersection(
                    set(work2.tags)
                )


                if common_tags:


                    node1 = self.find_node(
                        work1.title
                    )

                    node2 = self.find_node(
                        work2.title
                    )


                    if node1 and node2:


                        self.connect(

                            node1["id"],

                            node2["id"],

                            "tag"

                        )

    # -------------------------------------------------
    # Sync Category Connections
    # -------------------------------------------------

    # -------------------------------------------------
    # Sync Reference Connections
    # -------------------------------------------------

    def sync_reference_connections(self):


        import sqlite3


        connection = sqlite3.connect(
            "database/database.db"
        )


        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT
                work_references.work_id,
                work_references.reference_id,

                works.title,

                reference_library.title

            FROM work_references


            JOIN works

            ON works.id =
               work_references.work_id


            JOIN reference_library

            ON reference_library.id =
               work_references.reference_id

            """
        )


        rows = cursor.fetchall()


        connection.close()



        for work_id, reference_id, work_title, ref_title in rows:


            work_node = self.find_node(
                work_title
            )


            if work_node is None:

                continue



            reference_node = self.find_node(
                ref_title
            )


            if reference_node is None:


                reference_graph_id = self.create_node(

                    ref_title,

                    "reference"

                )


                reference_node = {

                    "id": reference_graph_id,

                    "label": ref_title,

                    "type": "reference"

                }



            self.connect(

                work_node["id"],

                reference_node["id"],

                "reference"

            )

    def sync_category_connections(self):


        from services.work_service import WorkService


        work_service = WorkService()

        works = work_service.get_all_works()


        for work in works:


            if not work.category:
                continue


            work_node = self.find_node(
                work.title
            )


            if work_node is None:
                continue


            category_node = self.find_node(
                work.category
            )


            if category_node is None:

                category_id = self.add_category(
                    work.category
                )

                category_node = {
                    "id": category_id,
                    "label": work.category,
                    "type": "category"
                }


            self.connect(

                work_node["id"],

                category_node["id"],

                "category"

            )        

    # -------------------------------------------------
    # Sync Attachment Connections
    # -------------------------------------------------

    def sync_attachment_connections(self):


        import sqlite3


        connection = sqlite3.connect(
            "database/database.db"
        )

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT
                attachments.filename,
                attachments.filepath,
                attachments.work_id
            FROM attachments
            """
        )


        attachments = cursor.fetchall()


        for filename, filepath, work_id in attachments:


            # get work title

            cursor.execute(
                """
                SELECT title
                FROM works
                WHERE id=?
                """,
                (
                    work_id,
                )
            )


            result = cursor.fetchone()


            if not result:
                continue


            work_title = result[0]


            work_node = self.find_node(
                work_title
            )


            if work_node is None:
                continue



            # create attachment node

            attachment_node = None

            for node in self.graph["nodes"]:

                if (
                    node["type"] == "attachment"
                    and node.get("filepath") == filepath
                ):
                    attachment_node = node
                    break

            if attachment_node is None:
                attachment_id = self.create_node(
                    filename,
                    "attachment"
                )

                for node in self.graph["nodes"]:
                    if node["id"] == attachment_id:
                        node["filepath"] = filepath
                        attachment_node = node
                        break
            else:
                attachment_id = attachment_node["id"]

            self.connect(

                work_node["id"],

                attachment_id,

                "attachment"

            )


        connection.close()


        self.save()