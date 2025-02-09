from pathlib import Path
from typing import Tuple, List, Dict, NamedTuple
import email
from email import policy
from email.parser import BytesParser
import logging
from datetime import datetime
from collections import defaultdict

from .config import TIMEZONE, DATE_FORMAT_FILENAME
from .html_utils import strip_html_tags

class EmailStats(NamedTuple):
    """Statistics about processed emails."""
    no_text_files: List[Path]
    no_images_files: List[Path]
    no_content_files: List[Path]

def clean_text(text: str) -> str:
    """Clean up text by removing extra whitespace and empty lines."""
    # Remove whitespace at start/end of lines and collapse multiple empty lines
    lines = [line.strip() for line in text.splitlines()]
    # Remove empty lines at start and end, collapse multiple empty lines to one
    lines = [line for i, line in enumerate(lines)
            if line or (i > 0 and i < len(lines)-1 and (lines[i-1] or lines[i+1]))]
    return "\n".join(lines).strip()

class EmailProcessor:
    """Process email files and extract content."""

    def __init__(self):
        self.stats = EmailStats([], [], [])

    @staticmethod
    def get_text_from_part(part) -> str:
        """Extract text content from an email part."""
        content_type = part.get_content_type()

        if not part.get("Content-Disposition"):
            payload = part.get_payload(decode=True)
            charset = part.get_content_charset()

            if payload and charset:
                text = payload.decode(charset)
                if content_type == "text/plain":
                    return text
                elif content_type == "text/html":
                    return strip_html_tags(text)
        return ""

    @staticmethod
    def extract_content_from_multipart(part) -> str:
        """Extract content from multipart email, preferring plain text over HTML."""
        plain_text = []
        html_text = []

        for subpart in part.iter_parts():
            content_type = subpart.get_content_type()
            if content_type == "text/plain" and not subpart.get('Content-Disposition'):
                text = EmailProcessor.get_text_from_part(subpart)
                if text:
                    plain_text.append(clean_text(text))
            elif content_type == "text/html" and not subpart.get('Content-Disposition'):
                text = EmailProcessor.get_text_from_part(subpart)
                if text:
                    html_text.append(clean_text(text))

        # Prefer plain text over HTML
        if plain_text:
            return "\n\n".join(filter(None, plain_text))
        elif html_text:
            return "\n\n".join(filter(None, html_text))
        return ""

    def process_email(self, email_path: Path) -> Tuple[str, datetime, str, List[Tuple[str, bytes]]]:
        """Process a single email file and extract its content."""
        logging.debug(f"Processing file: '{email_path}'")

        with email_path.open("rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)

        # Extract metadata
        subject = msg["subject"]
        date = email.utils.parsedate_to_datetime(msg["date"]).astimezone(TIMEZONE)

        logging.debug(f"Extracted subject: {subject}")
        logging.debug(f"Extracted date: {date.strftime(DATE_FORMAT_FILENAME)}")

        # Extract content
        body = ""
        images = []

        if msg.is_multipart():
            # Handle text content
            if msg.get_content_type() == "multipart/alternative":
                body = EmailProcessor.extract_content_from_multipart(msg)
            else:
                parts = []
                for part in msg.iter_parts():
                    if part.get_content_type() == "multipart/alternative":
                        text = EmailProcessor.extract_content_from_multipart(part)
                    else:
                        text = EmailProcessor.get_text_from_part(part)
                    if text:
                        parts.append(clean_text(text))
                body = "\n\n".join(parts)

            # Handle images separately
            for part in msg.walk():
                if part.get_content_type().startswith("image/"):
                    if img_data := part.get_payload(decode=True):
                        if img_filename := part.get_filename():
                            images.append((img_filename, img_data))
                            logging.debug(f"Found image: {img_filename}")
        else:
            body = clean_text(EmailProcessor.get_text_from_part(msg))

        # Log a concise summary
        logging.info(f"""Processed '{email_path.name}':
    {date} -- {subject}
     -> {len(images)} images, {len(body)}""")

        # Track statistics
        if not body:
            logging.warning(f"No message text found in file: '{email_path}'")
            self.stats.no_text_files.append(email_path)
        if not images:
            logging.warning(f"No images found in file: '{email_path}'")
            self.stats.no_images_files.append(email_path)
        if not body and not images:
            logging.error(f"No content found in file: '{email_path}'")
            self.stats.no_content_files.append(email_path)

        return subject, date, body, images

    def print_summary(self):
        """Print summary of processed emails."""
        logging.info("Processing Summary:")
        logging.info(f"Number of emails with no message text: {len(self.stats.no_text_files)}")
        logging.info(f"Number of emails with no images: {len(self.stats.no_images_files)}")
        if self.stats.no_content_files:
            logging.error(f"Number of emails with no content: {len(self.stats.no_content_files)}")
            logging.error("Files with no content:")
            for f in self.stats.no_content_files:
                logging.error(f"  - '{f}'")
