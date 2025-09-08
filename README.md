# email2md

Convert email files (.eml) into a single chronologically ordered Markdown document. Perfect for creating diaries or journals from email collections.

## What does this tool do?

- Processes multiple .eml files and extracts both text and image content from each email
- Saves images in dated subfolders (e.g. `.images/2025-09-08/filename.jpg`) for easy organization
- Generates a single Markdown file with all emails organized by date, including references to images so they display in the markdown preview
- Combines multiple emails from the same day into one chapter
- Supports both plain text and HTML email content
- Configurable output: you can exclude text or images if desired

## Features

- Processes multiple .eml files into a single Markdown document
- Orders entries chronologically
- Combines multiple emails from the same day
- Handles both plain text and HTML email content
- Supports image attachments
- Configurable output with text and/or images

## Installation

### Regular Installation

```bash
pip install .
```

### Development Setup

First, ensure you have UV installed:
```bash
pip install uv
```

Then install the package with development dependencies:

```bash
uv pip install -e ".[dev]"
```

Now you can run nox commands:

```bash
nox -s tests
```

Or using regular pip:

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Basic usage (outputs normal markdown with text and images)
email2md --all

# Only images (no text)
email2md --no-text

# Only text (no images)
email2md --no-img

# Specify input directory
email2md -i /path/to/emails

# Specify output file
email2md -o output.md

# Enable debug output
email2md -d
```

## Development

This project uses:
- Nox for automation
- Ruff for linting and formatting
- MyPy for type checking
- Pytest for testing

Development commands:
```bash
# Run all checks
nox

# Run specific checks
nox -s lint
nox -s format
nox -s typecheck
nox -s tests
nox -s coverage
```

## Getting Email Files

### From Thunderbird

1. Search the emails in Thunderbird
2. Select the mails you want to convert
3. Right-click and select 'Save As'
4. Move the saved .eml files to your input folder

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
