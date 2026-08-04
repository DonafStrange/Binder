from pathlib import Path
import shutil


from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QFileDialog,
    QLabel,
    QMessageBox,
)


class AttachmentPanel(QWidget):

    def __init__(self):

        super().__init__()

        self.current_work = None

        self.build_ui()



    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(self)


        title = QLabel(
            "Attachments"
        )


        layout.addWidget(
            title
        )


        self.file_list = QListWidget()


        layout.addWidget(
            self.file_list
        )


        self.image_button = QPushButton(
            "Add Image"
        )


        self.pdf_button = QPushButton(
            "Add PDF"
        )


        self.file_button = QPushButton(
            "Add File"
        )


        layout.addWidget(
            self.image_button
        )

        layout.addWidget(
            self.pdf_button
        )

        layout.addWidget(
            self.file_button
        )



        self.image_button.clicked.connect(
            self.add_image
        )

        self.pdf_button.clicked.connect(
            self.add_pdf
        )

        self.file_button.clicked.connect(
            self.add_file
        )



    # -------------------------------------------------
    # Set Current Work
    # -------------------------------------------------

    def set_work(self, work):

        self.current_work = work

        self.load_files()



    # -------------------------------------------------
    # Load Existing Files
    # -------------------------------------------------

    def load_files(self):

        self.file_list.clear()


        if self.current_work is None:

            return


        folder = Path(
            self.current_work.folder
        )


        for item in folder.rglob("*"):

            if item.is_file():

                self.file_list.addItem(
                    str(
                        item.relative_to(folder)
                    )
                )



    # -------------------------------------------------
    # Image
    # -------------------------------------------------

    def add_image(self):

        self.add_attachment(
            "images",
            [
                "png",
                "jpg",
                "jpeg",
                "svg"
            ]
        )



    # -------------------------------------------------
    # PDF
    # -------------------------------------------------

    def add_pdf(self):

        self.add_attachment(
            "pdf",
            [
                "pdf"
            ]
        )



    # -------------------------------------------------
    # General Files
    # -------------------------------------------------

    def add_file(self):

        self.add_attachment(
            "files",
            None
        )



    # -------------------------------------------------
    # Copy Attachment
    # -------------------------------------------------

    def add_attachment(
            self,
            folder_name,
            extensions
    ):


        if self.current_work is None:

            QMessageBox.warning(
                self,
                "No Work",
                "Select a research work first."
            )

            return



        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select File"
        )


        if not file:

            return



        source = Path(file)


        if extensions:

            if source.suffix.lower().replace(
                ".",""
            ) not in extensions:

                QMessageBox.warning(
                    self,
                    "Invalid",
                    "File type not allowed."
                )

                return



        destination_folder = (

            Path(self.current_work.folder)

            /

            folder_name

        )


        destination_folder.mkdir(
            exist_ok=True
        )


        destination = (
            destination_folder
            /
            source.name
        )


        shutil.copy(
            source,
            destination
        )


        self.load_files()



        QMessageBox.information(
            self,
            "Added",
            f"Added {source.name}"
        )


    # -------------------------------------------------
    # Markdown Link Generator
    # -------------------------------------------------

    def markdown_link(self, filename):

        path = Path(filename)


        if path.parent.name == "images":

            return (
                f"![{path.name}]"
                f"({filename})"
            )


        else:

            return (
                f"[{path.name}]"
                f"({filename})"
            )