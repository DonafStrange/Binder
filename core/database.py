import sqlite3
from pathlib import Path


class DatabaseManager:

    def __init__(self, db_path="database/database.db"):

        self.db_path = Path(db_path)

        self.connection = sqlite3.connect(self.db_path)

        self.connection.row_factory = sqlite3.Row

        self.create_tables()

    # -----------------------------------------------------

    def create_tables(self):

        cursor = self.connection.cursor()

        # ---------------- Works ----------------

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS works(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            category TEXT,

            description TEXT,

            folder TEXT,

            markdown_file TEXT,

            created TEXT,

            modified TEXT,

            favorite INTEGER DEFAULT 0,

            archived INTEGER DEFAULT 0

        )

        """)

        # ---------------- References ----------------

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS references_table(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            citation_key TEXT UNIQUE,

            title TEXT,

            authors TEXT,

            journal TEXT,

            year TEXT,

            doi TEXT,

            url TEXT,

            pdf TEXT,

            notes TEXT

        )

        """)

        # ---------------- Tags ----------------

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS tags(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE

        )

        """)

        # ---------------- Work Tags ----------------

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS work_tags(

            work_id INTEGER,

            tag_id INTEGER,

            PRIMARY KEY(work_id,tag_id)

        )

        """)

        # ---------------- Citations ----------------

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS citations(

            work_id INTEGER,

            reference_id INTEGER,

            PRIMARY KEY(work_id,reference_id)

        )

        """)

        # ---------------- Attachments ----------------

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS attachments(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            work_id INTEGER,

            filename TEXT,

            filepath TEXT,

            filetype TEXT

        )

        """)

        self.connection.commit()

    # -----------------------------------------------------

    def execute(self, query, values=()):

        cursor = self.connection.cursor()

        cursor.execute(query, values)

        self.connection.commit()

        return cursor

    # -----------------------------------------------------

    def fetchone(self, query, values=()):

        cursor = self.connection.cursor()

        cursor.execute(query, values)

        return cursor.fetchone()

    # -----------------------------------------------------

    def fetchall(self, query, values=()):

        cursor = self.connection.cursor()

        cursor.execute(query, values)

        return cursor.fetchall()

    # -----------------------------------------------------

    def close(self):

        self.connection.close()