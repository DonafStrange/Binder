from pathlib import Path
import shutil
import sqlite3
from datetime import datetime


class ReferenceService:

    def __init__(self):

        self.db_path = Path(
            "database/database.db"
        )

        self.create_table()

    # -------------------------------------------------
    # Create Table
    # -------------------------------------------------

    def create_table(self):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reference_library
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                citation_key TEXT,

                title TEXT NOT NULL,

                authors TEXT,

                journal TEXT,

                year TEXT,

                volume TEXT,

                issue TEXT,

                pages TEXT,

                doi TEXT,

                url TEXT,

                abstract TEXT,

                keywords TEXT,

                bibtex TEXT,

                pdf TEXT,

                folder TEXT,

                created TEXT,

                modified TEXT,

                favorite INTEGER DEFAULT 0,

                read_status TEXT DEFAULT '',

                rating INTEGER DEFAULT 0
            );

            """
        )    

        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS work_references
            (
                work_id INTEGER,

                reference_id INTEGER,

                PRIMARY KEY(
                    work_id,
                    reference_id
                ),

                FOREIGN KEY(work_id)
                REFERENCES works(id),

                FOREIGN KEY(reference_id)
                REFERENCES reference_library(id)
            );

            """
        )

        connection.commit()

        connection.close()

    # -------------------------------------------------
    # Create Reference
    # -------------------------------------------------

    def create_reference(
            self,
            title,
            authors="",
            journal="",
            year="",
            volume="",
            issue="",
            pages="",
            doi="",
            url="",
            abstract="",
            keywords="",
            citation_key="",
            bibtex="",
            pdf_path=""
    ):

        now = datetime.now().isoformat()

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute(

            """
            INSERT INTO reference_library
            (
                title,
                authors,
                journal,
                year,
                volume,
                issue,
                pages,
                doi,
                url,
                abstract,
                keywords,
                citation_key,
                bibtex,
                pdf,
                created,
                modified,
                favorite,
                read_status,
                rating
            )

            VALUES(
                ?,?,?,?,?,?,
                ?,?,?,?,?,?,
                ?,?,?,?,?,?,?
            )
            """,

            (
                title,
                authors,
                journal,
                year,
                volume,
                issue,
                pages,
                doi,
                url,
                abstract,
                keywords,
                citation_key,
                bibtex,
                pdf_path,
                now,
                now,
                0,
                "",
                0
            )

        )
        connection.commit()

        reference_id = cursor.lastrowid

        connection.close()

        if not citation_key:
            citation_key = f"Ref{reference_id:06d}"

        folder = Path(
            "reference_library"
        ) / f"ref_{reference_id:06d}"

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        (folder / "figures").mkdir(
            exist_ok=True
        )

        (folder / "supplementary").mkdir(
            exist_ok=True
        )

        (folder / "figures" / ".gitkeep").touch(
            exist_ok=True
        )

        (folder / "supplementary" / ".gitkeep").touch(
            exist_ok=True
        )

        notes = folder / "notes.md"

        notes.write_text(

            f"# {title}\n\n",

            encoding="utf-8"

        )

        # Copy PDF if available

        pdf_file = ""

        if pdf_path:

            source = Path(pdf_path)

            if source.exists():

                destination = folder / source.name

                shutil.copy2(
                    source,
                    destination
                )

                pdf_file = str(destination)

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute(

            """
            UPDATE reference_library

            SET

                folder=?,

                citation_key=?,

                pdf=?

            WHERE id=?

            """,

            (
                str(folder),
                citation_key,
                pdf_file,
                reference_id
            )

        )

        connection.commit()

        connection.close()

        return {

            "id": reference_id,

            "citation_key": citation_key,

            "title": title,

            "folder": str(folder),

            "pdf": pdf_file

        }

    # -------------------------------------------------
    # Get All references
    # -------------------------------------------------

    def get_all_references(self):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute(

            """
            SELECT

                id,
                citation_key,
                title,
                authors,
                journal,
                year,
                volume,
                issue,
                pages,
                doi,
                url,
                pdf,
                abstract,
                keywords,
                bibtex,
                folder,
                created,
                modified,
                favorite,
                read_status,
                rating

            FROM reference_library

            ORDER BY title

            """

        )

        rows = cursor.fetchall()

        connection.close()

        reference_library = []

        for row in rows:

            reference_library.append(

                ReferenceObject(

                    id=row[0],

                    citation_key=row[1],

                    title=row[2],

                    authors=row[3],

                    journal=row[4],

                    year=row[5],

                    volume=row[6],

                    issue=row[7],

                    pages=row[8],

                    doi=row[9],

                    url=row[10],

                    pdf=row[11],

                    abstract=row[12],

                    keywords=row[13],

                    bibtex=row[14],

                    folder=row[15],

                    created=row[16],

                    modified=row[17],

                    favorite=row[18],

                    read_status=row[19],

                    rating=row[20]

                )

            )

        return reference_library

    # -------------------------------------------------
    # Get Reference by ID
    # -------------------------------------------------

    def get_reference(
            self,
            reference_id
    ):

        for reference in self.get_all_references():

            if reference.id == reference_id:

                return reference

        return None

    # -------------------------------------------------
    # Delete Reference
    # -------------------------------------------------

    def delete_reference(
            self,
            reference_id
    ):

        reference = self.get_reference(
            reference_id
        )

        if reference is None:

            return


        # Remove reference folder
        folder = Path("reference_library") / f"ref_{reference_id:06d}"


        if folder.exists():

            import shutil

            shutil.rmtree(
                folder
            )


        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()


        cursor.execute(
            """
            DELETE FROM reference_library
            WHERE id=?
            """,
            (
                reference_id,
            )
        )


        connection.commit()

        connection.close()

    # -------------------------------------------------
    # Update Favorite
    # -------------------------------------------------

    def set_favorite(
            self,
            reference_id,
            favorite
    ):

        connection = sqlite3.connect(
            self.db_path
        )

        cursor = connection.cursor()

        cursor.execute(

            """
            UPDATE reference_library

            SET favorite=?

            WHERE id=?

            """,

            (
                favorite,
                reference_id
            )

        )

        connection.commit()

        connection.close()

    # -------------------------------------------------
    # Link Reference to Work
    # -------------------------------------------------

    def add_reference_to_work(
            self,
            work_id,
            reference_id
    ):


        connection = sqlite3.connect(
            self.db_path
        )


        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT OR IGNORE INTO work_references
            (
                work_id,
                reference_id
            )
            VALUES (?, ?)
            """,
            (
                work_id,
                reference_id
            )
        )


        connection.commit()

        connection.close()

    # -------------------------------------------------
    # Get Work References
    # -------------------------------------------------

    def get_work_references(
            self,
            work_id
    ):


        connection = sqlite3.connect(
            self.db_path
        )


        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT reference_library.*
            FROM reference_library

            JOIN work_references

            ON reference_library.id =
               work_references.reference_id

            WHERE work_references.work_id=?

            """,
            (
                work_id,
            )
        )


        rows = cursor.fetchall()


        connection.close()


        return rows


# -------------------------------------------------
# Reference Object
# -------------------------------------------------

class ReferenceObject:

    def __init__(

            self,

            id,

            citation_key,

            title,

            authors,

            journal,

            year,

            volume,

            issue,

            pages,

            doi,

            url,

            pdf,

            abstract,

            keywords,

            bibtex,

            folder,

            created,

            modified,

            favorite,

            read_status,

            rating

    ):

        self.id = id

        self.citation_key = citation_key

        self.title = title

        self.authors = authors

        self.journal = journal

        self.year = year

        self.volume = volume

        self.issue = issue

        self.pages = pages

        self.doi = doi

        self.url = url

        self.pdf = pdf

        self.abstract = abstract

        self.keywords = keywords

        self.bibtex = bibtex

        self.folder = folder

        self.created = created

        self.modified = modified

        self.favorite = favorite

        self.read_status = read_status

        self.rating = rating