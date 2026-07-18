"""
Resume analysis router.

Owns the full HTTP lifecycle of POST /api/analyze:
  1. Validate the upload (file type, size, non-empty job description)
  2. Extract + clean the resume's PDF text
  3. Build the Gemini prompt
  4. Stream back NDJSON (newline-delimited JSON) - one complete JSON object
     per line, per analysis field, as soon as Gemini finishes generating it

All actual business logic (PDF parsing, cleaning, prompting, calling
Gemini) lives in services/ - this file only orchestrates those calls and
translates results/errors into the correct HTTP behavior.
"""

import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.config import settings
from app.services.llm_client import LLMClientError, stream_analysis
from app.services.pdf_parser import PDFParsingError, extract_text_from_pdf
from app.services.prompt_templates import build_analysis_prompt
from app.utils.text_cleaning import clean_resume_text

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.get("/ping")
async def ping() -> dict[str, str]:
    """Trivial endpoint to confirm this router is mounted correctly (Step 1)."""
    return {"message": "analyze router is wired up correctly"}


@router.post("")
async def analyze_resume(
    resume: UploadFile = File(..., description="The candidate's resume as a PDF file."),
    job_description: str = Form(..., description="The job description text to match against."),
) -> StreamingResponse:
    """
    Analyze a resume against a job description.

    Streams back NDJSON - each line is one complete JSON object like
    `{"field": "ats_score", "value": 78}`. The frontend (Step 5) reads the
    stream line-by-line and updates the matching UI card as each field
    arrives, rather than waiting for the full analysis to complete.
    """
    # --- Validation happens BEFORE the StreamingResponse begins, so we can
    # still return normal HTTP error codes (400, etc). Once streaming
    # starts, the status code is locked in at 200 and can't be changed -
    # that's why Gemini-side failures are handled differently, below. ---

    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF.")

    file_bytes = await resume.read()

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.",
        )

    if not job_description or not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except PDFParsingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    cleaned_text = clean_resume_text(raw_text)
    prompt = build_analysis_prompt(cleaned_text, job_description)

    def event_generator():
        """
        Generator consumed by StreamingResponse. Runs AFTER the 200 status
        and headers have already been sent to the client, so any failure
        here can't change the HTTP status - instead we emit one final
        {"field": "error", ...} line so the frontend can detect and
        surface the failure mid-stream.
        """
        try:
            for chunk in stream_analysis(prompt):
                yield json.dumps(chunk.model_dump()) + "\n"
        except LLMClientError as exc:
            error_chunk = {"field": "error", "value": str(exc)}
            yield json.dumps(error_chunk) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
