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

    def update_code_section(self, markdown_file, code_files):

        markdown_file = Path(
            markdown_file
        )


        if not markdown_file.exists():
            return


        content = markdown_file.read_text(
            encoding="utf-8"
        )


        marker = "## Code Files"


        # Remove old code section
        if marker in content:

            content = content.split(
                marker
            )[0]


        content += "\n\n## Code Files\n\n"


        for code in code_files:

            content += (
                f"- [{code.name}]"
                f"(codes/{code.name})\n"
            )


        markdown_file.write_text(
            content,
            encoding="utf-8"
        )