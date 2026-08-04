from pathlib import Path
import sqlite3
from datetime import datetime


from services.graph import GraphService



class WorkService:


    def __init__(self):

        self.db_path = Path(
            "database/database.db"
        )

        self.attachments_folder = Path(
            "attachments"
        )

        self.attachments_folder.mkdir(
            exist_ok=True
        )

        self.graph = GraphService()


        self.create_table()



    # -------------------------------------------------
    # Database Table
    # -------------------------------------------------

    def create_table(self):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()


        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS works
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title TEXT,

                category TEXT,

                folder TEXT,

                markdown_file TEXT,

                created TEXT,

                modified TEXT

            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tags
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT UNIQUE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS work_tags
            (
                work_id INTEGER,

                tag_id INTEGER,

                PRIMARY KEY (work_id, tag_id),

                FOREIGN KEY(work_id) REFERENCES works(id),

                FOREIGN KEY(tag_id) REFERENCES tags(id)
            )
            """
        )

        connection.commit()

        connection.close()



    # -------------------------------------------------
    # Create Work
    # -------------------------------------------------

    def create_work(
            self,
            title,
            category
    ):


        folder_name = (

            title

            .replace(
                " ",
                "_"
            )

        )


        folder = Path(
            "works"
        ) / folder_name



        # create folders

        (folder/"images").mkdir(
            parents=True,
            exist_ok=True
        )


        (folder/"pdf").mkdir(
            exist_ok=True
        )


        (folder/"files").mkdir(
            exist_ok=True
        )

        (folder/"codes").mkdir(
            exist_ok=True
        )



        note_file = folder/"note.md"


        if not note_file.exists():

            note_file.write_text(

                f"# {title}\n\n",

                encoding="utf-8"

            )



        now = datetime.now().isoformat()



        # Database insert

        connection = sqlite3.connect(
            self.db_path
        )


        cursor = connection.cursor()


        cursor.execute(

            """
            INSERT INTO works
            (
            title,
            category,
            folder,
            markdown_file,
            created,
            modified
            )

            VALUES(?,?,?,?,?,?)

            """,

            (

            title,

            category,

            str(folder),

            "note.md",

            now,

            now

            )

        )


        connection.commit()


        work_id = cursor.lastrowid


        connection.close()



        # -----------------------------
        # Graph Update
        # -----------------------------


        graph_id = self.graph.add_work(
            title
        )



        return {

            "database_id": work_id,

            "graph_id": graph_id,

            "title": title,

            "folder": str(folder)

        }

    def get_work_tags(self, work_id):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT tags.name
            FROM tags
            JOIN work_tags
                ON tags.id = work_tags.tag_id
            WHERE work_tags.work_id=?
            ORDER BY tags.name
            """,
            (
                work_id,
            )
        )

        tags = [
            row[0]
            for row in cursor.fetchall()
        ]

        connection.close()

        return tags

    def create_tag(self, name):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO tags(name)
            VALUES(?)
            """,
            (
                name,
            )
        )

        tag_id = cursor.lastrowid

        connection.commit()

        connection.close()

        return tag_id

    def add_tag_to_work(self, work_id, tag_name):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()


        # Create tag if it does not exist
        cursor.execute(
            """
            INSERT OR IGNORE INTO tags(name)
            VALUES(?)
            """,
            (
                tag_name,
            )
        )


        # Get tag id
        cursor.execute(
            """
            SELECT id
            FROM tags
            WHERE name=?
            """,
            (
                tag_name,
            )
        )

        tag_id = cursor.fetchone()[0]


        # Link tag with work
        cursor.execute(
            """
            INSERT OR IGNORE INTO work_tags
            (
                work_id,
                tag_id
            )
            VALUES(?,?)
            """,
            (
                work_id,
                tag_id
            )
        )


        connection.commit()

        connection.close()

    # -------------------------------------------------
    # Get All Works
    # -------------------------------------------------

    def get_all_works(self):


        connection = sqlite3.connect(
            self.db_path
        )


        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT
            id,
            title,
            category,
            folder,
            markdown_file,
            created,
            modified

            FROM works

            """
        )


        rows = cursor.fetchall()


        connection.close()


        works=[]


        for row in rows:

            work = WorkObject(

                id=row[0],

                title=row[1],

                category=row[2],

                folder=row[3],

                markdown_file=row[4],

                created=row[5],

                modified=row[6]

            )


            work.tags = self.get_work_tags(
                row[0]
            )


            works.append(
                work
            )


        return works

    def delete_work(self, work_id):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()


        # Get folder before deleting
        cursor.execute(
            """
            SELECT folder
            FROM works
            WHERE id=?
            """,
            (
                work_id,
            )
        )


        result = cursor.fetchone()


        if result:

            folder = Path(
                result[0]
            )


            if folder.exists():

                import shutil

                shutil.rmtree(
                    folder
                )


        # Delete database entry
        cursor.execute(
            """
            DELETE FROM works
            WHERE id=?
            """,
            (
                work_id,
            )
        )


        connection.commit()

        connection.close()

    def remove_tag_from_work(self, work_id, tag_name):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT id
            FROM tags
            WHERE name=?
            """,
            (
                tag_name,
            )
        )

        result = cursor.fetchone()


        if result:

            tag_id = result[0]


            cursor.execute(
                """
                DELETE FROM work_tags
                WHERE work_id=?
                AND tag_id=?
                """,
                (
                    work_id,
                    tag_id
                )
            )


        connection.commit()

        connection.close()


# -------------------------------------------------
# Work Object
# -------------------------------------------------

class WorkObject:


    def __init__(
            self,
            id,
            title,
            category,
            folder,
            markdown_file,
            created,
            modified,
            tags=None
    ):

        self.id=id

        self.title=title

        self.category=category

        self.folder=folder

        self.markdown_file=markdown_file

        self.created=created

        self.modified=modified

        self.tags = tags or []

        self.references=[]

        self.attachments=[]
