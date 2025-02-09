from html.parser import HTMLParser


class HTMLStripper(HTMLParser):
    """Strip HTML tags from text while preserving content."""

    def __init__(self):
        super().__init__()
        self.reset()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_text(self) -> str:
        return "".join(self.text_parts)


def strip_html_tags(html: str) -> str:
    """Remove HTML tags from a string while preserving the text content."""
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_text()
