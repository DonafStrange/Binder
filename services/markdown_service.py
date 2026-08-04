import re
from pathlib import Path


class MarkdownService:


    def extract_citations(self, markdown_file):

        file = Path(markdown_file)

        if not file.exists():
            return []

        text = file.read_text(
            encoding="utf-8"
        )


        citations = []


        # Old style citations:
        # [@15]
        old = re.findall(
            r"\[@(\d+)\]",
            text
        )

        citations.extend(old)


        # New citation links:
        # reference-pdf://Ref000015
        # reference-url://WILSON19721

        new = re.findall(
            r"reference-(?:pdf|url)://([A-Za-z0-9_]+)",
            text
        )

        citations.extend(new)


        return list(set(citations))