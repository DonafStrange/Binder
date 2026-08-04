from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Work:

    id: int | None = None

    title: str = ""

    category: str = ""

    description: str = ""

    tags: list[str] = field(default_factory=list)

    references: list[int] = field(default_factory=list)

    folder: str = ""

    markdown_file: str = ""

    created: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    modified: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    favorite: bool = False

    archived: bool = False

    # ------------------------------------

    @property
    def path(self):

        return Path(self.folder)

    @property
    def note_path(self):

        return self.path / self.markdown_file

    # ------------------------------------

    def touch(self):

        self.modified = datetime.now().isoformat(timespec="seconds")

    # ------------------------------------

    def to_dict(self):

        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "tags": self.tags,
            "references": self.references,
            "folder": self.folder,
            "markdown_file": self.markdown_file,
            "created": self.created,
            "modified": self.modified,
            "favorite": self.favorite,
            "archived": self.archived,
        }

    # ------------------------------------

    @classmethod
    def from_dict(cls, data):

        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            category=data.get("category", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            references=data.get("references", []),
            folder=data.get("folder", ""),
            markdown_file=data.get("markdown_file", ""),
            created=data.get("created"),
            modified=data.get("modified"),
            favorite=data.get("favorite", False),
            archived=data.get("archived", False),
        )