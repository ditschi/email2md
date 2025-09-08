#!/usr/bin/env python3

import sys
import argparse
import logging
from pathlib import Path

from email2md.config import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_FILE, IMAGES_DIR_NAME
from email2md.email_processor import EmailProcessor
from email2md.markdown_generator import MarkdownGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="email2md",
        description="Convert .eml files to a single Markdown document with chapters.",
        epilog="""
Examples:
  email2md                           # Process all .eml files in current directory
  email2md -i /path/to/emails       # Process .eml files from specific directory
  email2md --no-img                 # Exclude images from output
  email2md --no-text               # Only include images in output
  email2md -d                      # Enable debug output
        """,
    )
    parser.add_argument(
        "--no-img", "-ni", action="store_true", help="Exclude attached images from the Markdown"
    )
    parser.add_argument(
        "--no-text", "-nt", action="store_true", help="Exclude message text from the Markdown"
    )
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug output")
    parser.add_argument(
        "--input-dir",
        "-i",
        type=str,
        default=str(DEFAULT_INPUT_DIR),
        help="Directory containing the .eml files",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        type=str,
        default=str(DEFAULT_OUTPUT_FILE),
        help="Output Markdown file",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format="%(levelname)s: %(message)s"
    )

    input_dir = Path(args.input_dir)
    output_file = Path(args.output_file)

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Use IMAGES_DIR_NAME for the images directory
    images_dir = output_file.parent / IMAGES_DIR_NAME

    if not input_dir.exists():
        logging.error(f"Input directory does not exist: '{input_dir}'")
        sys.exit(1)

    # Process all emails
    failed_files = []
    emails = []
    processor = EmailProcessor()

    for eml_path in input_dir.glob("*.eml"):
        try:
            result = processor.process_email(eml_path, images_dir)
            emails.append(result)
        except Exception as e:
            logging.error(f"Failed to process '{eml_path}': {e}")
            failed_files.append(eml_path)

    if not emails:
        logging.error("No email files were successfully processed")
        sys.exit(1)

    # Generate markdown
    try:
        if not args.no_img:
            images_dir.mkdir(exist_ok=True)

        markdown_gen = MarkdownGenerator(images_dir, output_file)
        for email in sorted(emails, key=lambda x: x[1]):
            markdown_gen.add_chapter(*email, no_text=args.no_text, no_images=args.no_img)

        # Write output
        output_file.write_text(markdown_gen.get_content())
        logging.info(f"Successfully created: '{output_file}'")

        # Print processing summary
        processor.print_summary()

        if failed_files:
            logging.error(f"Failed to process {len(failed_files)} files:")
            for f in failed_files:
                logging.error(f"  - '{f}'")

        # Exit with error if there were emails with no content
        if processor.stats.no_content_files:
            sys.exit(1)

    except Exception as e:
        logging.error(f"Failed to generate markdown: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
