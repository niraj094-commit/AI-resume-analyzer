"""
PDF parsing service.

Single responsibility: take raw PDF bytes (as received from the upload)
and return the plain text content. No FastAPI/HTTP concerns live here —
that separation is what makes this function trivially unit-testable and
reusable if we ever add other entry points (e.g. a CLI or batch job).
"""

from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PDFParsingError(Exception):
    """Raised when a PDF can't be read or contains no extractable text.

    Kept as a distinct exception type (rather than letting pypdf's raw
    errors bubble up) so the router layer can catch ONE known error type
    and turn it into a clean 400 response, regardless of which underlying
    library raised it.
    """


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text content from a PDF's raw bytes.

    Args:
        file_bytes: The raw bytes of an uploaded .pdf file.

    Returns:
        The concatenated text of every page, stripped of leading/trailing
        whitespace.

    Raises:
        PDFParsingError: if the file isn't a valid/readable PDF, is
            password-protected, or contains no extractable text at all
            (e.g. a scanned image with no text layer — OCR is out of scope
            for this project).
    """
    try:
        reader = PdfReader(BytesIO(file_bytes))
    except PdfReadError as exc:
        raise PDFParsingError("The uploaded file is not a valid PDF.") from exc

    if reader.is_encrypted:
        # Some PDFs report is_encrypted=True but still open with an empty
        # password (common for "owner password only" PDFs restricting
        # printing/editing, not viewing). Try that before giving up.
        try:
            reader.decrypt("")
        except Exception as exc:
            raise PDFParsingError(
                "The uploaded PDF is password-protected and can't be read."
            ) from exc

    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)

    full_text = "\n".join(pages_text).strip()

    if not full_text:
        raise PDFParsingError(
            "No text could be extracted from this PDF. It may be a scanned "
            "image without a text layer — please upload a text-based PDF."
        )

    return full_text
