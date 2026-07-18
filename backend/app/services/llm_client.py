"""
Gemini LLM client service.

Uses the `google-genai` SDK (the current, actively-maintained unified
Google GenAI SDK). Note: the older `google-generativeai` package is fully
deprecated/archived by Google with no further updates - it does not
recognize newer model name strings, so it is NOT used here.

Responsible for:
  1. Creating a Gemini client with the API key
  2. Sending the analysis prompt with streaming enabled
  3. Re-chunking Gemini's raw token stream into complete, valid JSON objects
     (Gemini streams arbitrary-sized text fragments, NOT clean line-by-line
     output, so a naive split on "\n" would break objects apart mid-parse)
  4. Yielding each complete, schema-validated AnalysisChunk as soon as it's
     fully received - this is what enables the frontend to progressively
     fill in UI cards instead of waiting for the entire response.

This is the most complex module in the backend, intentionally isolated
here so the re-chunking logic (JSONStreamRechunker) can be unit-tested
completely independently of the Gemini SDK and FastAPI routing.
"""

import json
from collections.abc import Generator

from google import genai
from pydantic import ValidationError

from app.config import settings
from app.models.schemas import AnalysisChunk

_client: genai.Client | None = None


class LLMClientError(Exception):
    """Raised for any Gemini API failure: missing/invalid API key, quota
    exceeded, network error, content safety block, or a response that
    doesn't match our expected JSON schema."""


def _get_client() -> genai.Client:
    """Lazily create the Gemini client exactly once per process, so
    importing this module doesn't require GEMINI_API_KEY to be set - only
    actually calling stream_analysis() does."""
    global _client
    if _client is None:
        if not settings.GEMINI_API_KEY:
            raise LLMClientError(
                "GEMINI_API_KEY is not set. Add it to backend/.env before "
                "calling the analyze endpoint."
            )
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


class JSONStreamRechunker:
    """
    Buffers arbitrary text fragments and extracts complete, top-level JSON
    objects as soon as they're fully available - regardless of how the
    underlying stream happened to split its chunks.

    Example of the problem this solves: Gemini might stream text in pieces
    like '{"field": "ats' then '_score", "value": 78}\\n{"fi' then 'eld": ...'.
    A naive `for line in stream: json.loads(line)` approach breaks
    immediately here, because chunk boundaries rarely land on JSON object
    boundaries.

    Instead, this class uses `json.JSONDecoder.raw_decode`, which can parse
    a JSON value starting at the beginning of a string and report exactly
    where it stopped - even if there's leftover text afterward. That lets
    us repeatedly ask "is there a complete object at the front of the
    buffer yet?" as new text arrives, and only consume the buffer once an
    object is fully parsed.
    """

    def __init__(self) -> None:
        self._buffer = ""
        self._decoder = json.JSONDecoder()

    def feed(self, text: str) -> list[dict]:
        """
        Add new text to the internal buffer, and return a list of every
        complete JSON object that can now be extracted (there may be zero,
        one, or several, depending on how much text just arrived).
        """
        self._buffer += text
        results: list[dict] = []

        while True:
            stripped = self._buffer.lstrip()
            if not stripped:
                self._buffer = ""
                break
            try:
                obj, end_index = self._decoder.raw_decode(stripped)
            except json.JSONDecodeError:
                # Buffer doesn't contain a complete object yet - stop and
                # wait for more text on the next feed() call.
                break
            results.append(obj)
            self._buffer = stripped[end_index:]

        return results


def _normalize_model_name(model: str) -> str:
    """
    Ensure the model name is a fully-qualified resource path
    (e.g. "models/gemini-3.5-flash"), which is what Gemini's API actually
    expects internally. Some SDK versions/call paths don't reliably add
    this prefix automatically, which surfaces as a confusing
    "unexpected model name format" 400 error - normalizing it ourselves
    avoids depending on that SDK behavior.
    """
    return model if model.startswith("models/") else f"models/{model}"


def stream_analysis(prompt: str) -> Generator[AnalysisChunk, None, None]:
    """
    Send `prompt` to Gemini with streaming enabled, and yield validated
    AnalysisChunk objects one at a time, as soon as each is fully received.

    Raises:
        LLMClientError: on any Gemini API failure, or if a streamed object
            doesn't match the expected AnalysisChunk schema.
    """
    client = _get_client()
    rechunker = JSONStreamRechunker()

    try:
        response_stream = client.models.generate_content_stream(
            model=_normalize_model_name(settings.GEMINI_MODEL),
            contents=prompt,
        )

        for piece in response_stream:
            text = getattr(piece, "text", "") or ""
            if not text:
                continue

            for obj in rechunker.feed(text):
                try:
                    yield AnalysisChunk.model_validate(obj)
                except ValidationError as exc:
                    raise LLMClientError(
                        f"Gemini returned an object that doesn't match the "
                        f"expected schema: {obj}"
                    ) from exc

    except LLMClientError:
        raise
    except Exception as exc:  # noqa: BLE001 - deliberately broad: any SDK
        # failure (auth, quota, network, safety block) should surface as
        # our own error type, not leak a raw SDK exception to the router.
        raise LLMClientError(f"Gemini API request failed: {exc}") from exc