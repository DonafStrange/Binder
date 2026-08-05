from pathlib import Path
from os.path import relpath
import shutil
import sqlite3


class AttachmentService:

    # -------------------------------------------------
    # Copy Attachment
    # -------------------------------------------------

    def copy_attachment(
        self,
        source_file,
        work_folder=None,
        work_id=None
    ):

        source = Path(source_file)

        if not source.exists():

            raise FileNotFoundError(source)


        extension = source.suffix.lower()


        # -----------------------------
        # Global attachment folders
        # -----------------------------

        if extension in [

            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".gif",
            ".svg",
            ".webp"

        ]:

            destination_folder = Path(
                "attachments/images"
            )


        elif extension == ".pdf":

            destination_folder = Path(
                "attachments/pdf"
            )


        else:

            destination_folder = Path(
                "attachments/files"
            )


        destination_folder.mkdir(
            parents=True,
            exist_ok=True
        )


        destination = destination_folder / source.name


        # -----------------------------
        # Avoid duplicate names
        # -----------------------------

        counter = 1

        while destination.exists():

            destination = (
                destination_folder
                /
                f"{source.stem}_{counter}{source.suffix}"
            )

            counter += 1


        shutil.copy2(
            source,
            destination
        )

        if work_id is not None:


            connection = sqlite3.connect(
                "database/database.db"
            )


            cursor = connection.cursor()


            cursor.execute(
                """
                INSERT INTO attachments
                (
                    work_id,
                    filename,
                    filepath,
                    filetype
                )

                VALUES (?, ?, ?, ?)

                """,
                (
                    work_id,
                    destination.name,
                    str(destination),
                    extension
                )
            )


            connection.commit()

            connection.close()

        return destination

    
    # -------------------------------------------------
    # Markdown Path
    # -------------------------------------------------

    def markdown_path(
        self,
        attachment_path,
        work_folder
    ):

        return relpath(
            attachment_path,
            work_folder
        ).replace("\\", "/")


    # -------------------------------------------------
    # Markdown Text
    # -------------------------------------------------

    def markdown_text(
        self,
        attachment_path,
        work_folder
    ):

        relative = self.markdown_path(
            attachment_path,
            work_folder
        )

        extension = Path(relative).suffix.lower()

        if extension in [

            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".svg",
            ".webp"

        ]:

            return f"![{Path(relative).stem}]({relative})"

        elif extension == ".pdf":

            return f"[📄 {Path(relative).name}]({relative})"

        else:

            return f"[📁 {Path(relative).name}]({relative})"

    def register_attachment(
        self,
        work_id,
        filepath
    ):

        connection = sqlite3.connect(
            "database/database.db"
        )

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO attachments
            (
                work_id,
                filename,
                filepath,
                filetype
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                work_id,
                filepath.name,
                str(filepath),
                filepath.suffix.lower()
            )
        )

        connection.commit()

        connection.close()

    def sync_work_attachments(
        self,
        work_id,
        markdown_text
    ):

        import re
        import sqlite3


        # Find all attachment paths in markdown
        paths = re.findall(
            r"\]\((.*?)\)",
            markdown_text
        )


        attachments = []


        for path in paths:

            if "attachments/" in path:

                index = path.find(
                    "attachments/"
                )

                clean = path[index:]

                attachments.append(
                    str(
                        Path(clean)
                    )
                )


        connection = sqlite3.connect(
            "database/database.db"
        )

        cursor = connection.cursor()


        # Existing database attachments
        cursor.execute(
            """
            SELECT id, filepath
            FROM attachments
            WHERE work_id=?
            """,
            (
                work_id,
            )
        )


        existing = cursor.fetchall()



        # Remove unused
        for row in existing:

            attachment_id = row[0]

            filepath = row[1]


            if filepath not in attachments:

                cursor.execute(
                    """
                    DELETE FROM attachments
                    WHERE id=?
                    """,
                    (
                        attachment_id,
                    )
                )


        connection.commit()

        connection.close()