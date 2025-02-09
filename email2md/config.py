from pathlib import Path
import pytz
import os

# Timezone configuration
TIMEZONE = pytz.timezone("Europe/Berlin")

# Default paths - use current working directory
DEFAULT_INPUT_DIR = Path(os.getcwd())
DEFAULT_OUTPUT_FILE = DEFAULT_INPUT_DIR / "Mail-to-Linus.md"
DEFAULT_IMAGES_DIR = DEFAULT_INPUT_DIR / ".images"

# Date formats
DATE_FORMAT_FILENAME = "%Y-%m-%d %H:%M"
DATE_KEY_FORMAT = "%Y-%m-%d"

# Document settings
DOCUMENT_TITLE = "Mails to Linus"
