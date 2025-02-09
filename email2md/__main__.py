import argparse
import logging
import sys
from pathlib import Path
from collections import defaultdict

from .config import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_FILE, DATE_KEY_FORMAT
from .email_processor import EmailProcessor
from .markdown_generator import MarkdownGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert .eml files to Markdown.",
        epilog="To save emails from Thunderbird:\n"
        "1. Search the emails in Thunderbird.\n"
        "2. Select the mails, Right-click and select 'Save As'.\n"
        "3. Move the saved .eml files to the specified input folder.",
    )
    parser.add_argument(
        "--no-img", "-ni", action="store_true", help="Exclude attached images from the Markdown."
    )
    parser.add_argument(
        "--no-text", "-nt", action="store_true", help="Exclude message text from the Markdown."
    )
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug output.")
    parser.add_argument(
        "--input-dir",
        "-i",
        type=str,
        default=str(DEFAULT_INPUT_DIR),
        help="Directory containing the .eml files.",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        type=str,
        default=str(DEFAULT_OUTPUT_FILE),
        help="Output Markdown file.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    input_dir = Path(args.input_dir)
    output_file = Path(args.output_file)
    images_dir = output_file.parent / "images"

    if not args.no_img:
        images_dir.mkdir(exist_ok=True)

    # Process emails
    emails_by_date = defaultdict(list)
    no_content_files = []

    for eml_path in input_dir.glob("*.eml"):
        subject, date, body, images = EmailProcessor.process_email(eml_path)

        if not body and not images:
            no_content_files.append(eml_path)
            logging.warning(f"No content found in file: {eml_path}")

        date_key = date.strftime(DATE_KEY_FORMAT)
        emails_by_date[date_key].append((subject, date, body, images))

    # Generate markdown
    markdown_gen = MarkdownGenerator(images_dir)

    for date_key in sorted(emails_by_date.keys()):
        emails = sorted(emails_by_date[date_key], key=lambda x: x[1])
        main_email = max(emails, key=lambda x: len(x[2]))

        markdown_gen.add_chapter(
            subject=main_email[0],
            date=main_email[1],
            body="\n\n".join(email[2] for email in emails if email[2]),
            images=[img for email in emails for img in email[3]],
            no_text=args.no_text,
            no_images=args.no_img,
        )

    # Write output
    with output_file.open("w") as f:
        f.write(markdown_gen.get_content())

    logging.info(f"Markdown file created at: {output_file}")

    if no_content_files:
        logging.error(f"Files with no content: {no_content_files}")
        sys.exit(1)


if __name__ == "__main__":
    main()
