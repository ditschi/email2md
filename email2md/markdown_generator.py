from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import logging
from collections import defaultdict

from .config import DOCUMENT_TITLE, DATE_FORMAT_FILENAME, DATE_KEY_FORMAT


class MarkdownGenerator:
    """Generate Markdown content from processed emails."""

    def __init__(self, images_dir: Path):
        self.images_dir = images_dir
        self.content = [f"# {DOCUMENT_TITLE}\n\n"]
        self.daily_content = defaultdict(list)

    def add_chapter(
        self,
        subject: str,
        date: datetime,
        body: str,
        images: List[Tuple[str, bytes]],
        no_text: bool = False,
        no_images: bool = False,
    ) -> None:
        """Collect content for a chapter, organized by date."""
        date_key = date.strftime(DATE_KEY_FORMAT)
        self.daily_content[date_key].append({
            'subject': subject,
            'date': date,
            'body': body if not no_text else "",
            'images': images if not no_images else []
        })

    def _process_images(self, images: List[Tuple[str, bytes]]) -> List[str]:
        """Process and save images, returning their markdown references."""
        image_refs = []
        for img_filename, img_data in images:
            img_path = self.images_dir / img_filename
            with img_path.open('wb') as img_file:
                img_file.write(img_data)
            image_refs.append(f"![{img_filename}](images/{img_filename})\n\n")
        return image_refs

    def get_content(self) -> str:
        """Generate the complete markdown content."""
        for date_key in sorted(self.daily_content.keys()):
            day_entries = sorted(self.daily_content[date_key], key=lambda x: x['date'])

            if len(day_entries) > 1:
                subjects = [e['subject'] for e in day_entries]
                times = [e['date'].strftime("%H:%M") for e in day_entries]
                logging.info(f"Combining {len(day_entries)} emails from {date_key}:")
                for subj, time in zip(subjects, times):
                    logging.info(f"  - {time}: '{subj}'")

            # Use the subject from the entry with the most text content
            main_entry = max(day_entries, key=lambda x: len(x['body']) if x['body'] else 0)
            date_str = main_entry['date'].strftime(DATE_FORMAT_FILENAME)

            # Only add chapter if there's content to show
            has_content = any(e['body'] for e in day_entries) or any(e['images'] for e in day_entries)
            if not has_content:
                continue

            self.content.append(f"## {main_entry['subject']} -- {date_str}\n\n")

            # Add all text content first, in chronological order
            for entry in day_entries:
                if entry['body']:
                    self.content.append(f"{entry['body']}\n\n")

            # Then add all images, in chronological order
            for entry in day_entries:
                if entry['images']:
                    self.content.extend(self._process_images(entry['images']))

        return ''.join(self.content)
