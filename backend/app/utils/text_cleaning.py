"""
Text cleaning utilities.

PDF text extraction is notoriously messy — extra whitespace, repeated
blank lines, and non-printable/control characters are common. This module
normalizes that before the text gets sent to the LLM, both to reduce
wasted tokens and to avoid confusing the model with extraction artifacts.
"""

import re
import unicodedata


def clean_resume_text(raw_text: str) -> str:
    """
    Normalize raw extracted PDF text into clean, LLM-ready text.

    Steps:
      1. Normalize unicode (e.g. ligatures like "ﬁ" -> "fi")
      2. Strip non-printable/control characters
      3. Collapse runs of 3+ blank lines down to a single blank line
      4. Collapse repeated horizontal whitespace (multiple spaces/tabs) to one space
      5. Trim leading/trailing whitespace on each line and on the whole text

    Args:
        raw_text: Text as returned by pdf_parser.extract_text_from_pdf.

    Returns:
        Cleaned text, ready to be embedded into an LLM prompt.
    """
    # 1. Unicode normalization (NFKC handles ligatures, weird PDF font quirks)
    text = unicodedata.normalize("NFKC", raw_text)

    # 2. Strip non-printable / control characters (keep newlines and tabs for now,
    # they get normalized in later steps)
    text = "".join(ch for ch in text if ch in "\n\t" or not unicodedata.category(ch).startswith("C"))

    # 3. Collapse 3+ consecutive newlines down to exactly 2 (one blank line)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 4. Collapse repeated horizontal whitespace to a single space
    text = re.sub(r"[ \t]{2,}", " ", text)

    # 5. Trim each line, then trim the whole block
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines).strip()

    return text
