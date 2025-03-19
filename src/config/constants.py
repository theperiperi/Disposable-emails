import os

# API Configuration
BASE_URL = "https://api.mail.tm"
MERCURE_URL = "https://mercure.mail.tm/.well-known/mercure"
CONFIG_FILE = os.path.expanduser('~/.ote')

# Regular Expressions
REGEX = {
    'otp': r'(\d{4,8})',
    'url': r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'
}

# Default Values
DEFAULT_PASSWORD = "TempPass123!" 