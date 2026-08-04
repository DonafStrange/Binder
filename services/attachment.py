from pathlib import Path
from os.path import relpath
import shutil


class AttachmentService:

    # -------------------------------------------------
    # Copy Attachment
    # -------------------------------------------------

    def copy_attachment(
        self,
        source_file,
        work_folder=None
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