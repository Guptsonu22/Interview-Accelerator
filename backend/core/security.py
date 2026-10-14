import re
import os
from typing import Tuple
from backend.core.config import settings

# Content length limits
MAX_RAW_TEXT_CHARS = 100_000  # ~20,000 words
MAX_ANSWER_CHARS = 10_000
MIN_ANSWER_CHARS = 2

# Allowed file extensions
ALLOWED_EXTENSIONS = settings.allowed_extensions_set

# Suspicious prompt injection patterns to neutralize/flag
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)system\s+prompt",
    r"(?i)you\s+are\s+now\s+an?\s+unrestricted",
    r"(?i)developer\s+mode",
    r"(?i)reveal\s+(the\s+)?(api\s+key|secret|password)",
    r"(?i)give\s+a\s+score\s+of\s+100",
]


def sanitize_filename(filename: str) -> str:
    """Strip dangerous characters and directory traversal markers."""
    clean = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', clean)
    return clean[:100]


def validate_file_upload(filename: str, file_size_bytes: int) -> Tuple[bool, str]:
    """Validate uploaded document file extension and size."""
    if not filename:
        return False, "Filename cannot be empty."

    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File extension '{ext}' is not supported. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        return False, f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."

    if file_size_bytes == 0:
        return False, "Uploaded file is empty (0 bytes)."

    return True, ""


def sanitize_untrusted_text(text: str, max_chars: int = MAX_RAW_TEXT_CHARS) -> str:
    """
    Sanitize untrusted candidate resume or job description text.
    Ensures input is non-empty, truncates to safe length, and removes control characters.
    """
    if not text:
        return ""

    # Strip null bytes and non-printable control characters except newline and tab
    cleaned = "".join(ch for ch in text if ch in ('\n', '\r', '\t') or (ch.isprintable() and ord(ch) >= 32))
    
    # Enforce safe length limit
    return cleaned[:max_chars].strip()


def check_for_prompt_injection(text: str) -> bool:
    """Check if text contains obvious instruction overrides."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True
    return False
