"""
Pydantic models that define the shape of data flowing in and out of the API.

These are the "contract" between frontend and backend. Keeping them in one
file makes it easy to see the entire API surface at a glance, and lets
FastAPI auto-generate accurate OpenAPI docs at /docs.
"""

from enum import Enum
from typing import Union

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response for the health-check endpoint."""

    status: str = Field(examples=["ok"])
    app_name: str
    environment: str


# ---------------------------------------------------------------------------
# Analysis contract
#
# This is the schema decided in the architecture step: Gemini streams back
# ONE complete JSON object per line (NDJSON), each representing one field of
# the analysis. The frontend parses each line as it arrives and fills in the
# matching card immediately (ATS Score, Match %, Missing Skills, Suggestions)
# instead of waiting for the entire response to finish.
# ---------------------------------------------------------------------------


class AnalysisField(str, Enum):
    """The set of fields Gemini is allowed to stream back. Used to validate
    each parsed line so a malformed/hallucinated field name is caught
    immediately instead of silently reaching the frontend."""

    ATS_SCORE = "ats_score"
    MATCH_PERCENTAGE = "match_percentage"
    MISSING_SKILLS = "missing_skills"
    SUGGESTIONS = "suggestions"
    # Not produced by the LLM - injected by the backend if the Gemini
    # request fails PARTWAY through streaming (see llm_client.py). Since
    # the HTTP response has already started with a 200 status by that
    # point, the only way to signal failure is a special chunk like this.
    ERROR = "error"


class AnalysisChunk(BaseModel):
    """
    One streamed unit of the analysis response.

    Examples of what gets sent down the wire, one per line:
        {"field": "ats_score", "value": 78}
        {"field": "match_percentage", "value": 64}
        {"field": "missing_skills", "value": ["Docker", "Kubernetes"]}
        {"field": "suggestions", "value": ["Quantify your achievements with metrics", "..."]}
        {"field": "error", "value": "Gemini API request failed: ..."}
    """

    field: AnalysisField
    value: Union[int, float, list[str], str]


class AnalysisResult(BaseModel):
    """
    The fully-aggregated result once all chunks have streamed in.

    Not sent over the wire directly during streaming — this is what the
    frontend hook (useStreamingAnalysis, Step 5) assembles internally by
    merging AnalysisChunks together, and it's also useful server-side for
    testing/logging the complete response in one shape.
    """

    ats_score: int = Field(ge=0, le=100)
    match_percentage: int = Field(ge=0, le=100)
    missing_skills: list[str]
    suggestions: list[str]
