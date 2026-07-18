"""
Prompt template builder.

Builds the exact instruction sent to Gemini. The prompt's job is to make
the model behave like a deterministic API, not a chatty assistant — it
must emit ONLY newline-delimited JSON objects (NDJSON), one per analysis
field, in a fixed order and fixed shape. This is what allows the backend
to re-chunk the raw stream (Step 4) and the frontend to progressively fill
in UI cards as each field arrives (Step 5).
"""

from app.models.schemas import AnalysisField

# The exact field order the model must stream in. Fixed order matters:
# the frontend can start rendering the ATS Score card the instant the
# first line arrives, without waiting to see which field it turns out to be.
FIELD_ORDER = [
    AnalysisField.ATS_SCORE,
    AnalysisField.MATCH_PERCENTAGE,
    AnalysisField.MISSING_SKILLS,
    AnalysisField.SUGGESTIONS,
]


def build_analysis_prompt(resume_text: str, job_description: str) -> str:
    """
    Build the full prompt sent to Gemini for a single analysis request.

    Args:
        resume_text: Cleaned resume text (see utils.text_cleaning).
        job_description: Raw job description text pasted by the user.

    Returns:
        A single prompt string ready to send as the user message to Gemini.
    """
    return f"""You are an ATS (Applicant Tracking System) resume analysis engine.
You will be given a candidate's RESUME and a JOB DESCRIPTION. Analyze how
well the resume matches the job description.

OUTPUT FORMAT — READ CAREFULLY:
You must output EXACTLY 4 lines, and NOTHING else. No preamble, no
markdown code fences, no explanations before or after. Each line must be
a single, complete, valid JSON object, in this EXACT order:

1. {{"field": "ats_score", "value": <integer 0-100>}}
   - How well-structured and ATS-parseable the resume itself is
     (formatting, section headers, keyword density, length).

2. {{"field": "match_percentage", "value": <integer 0-100>}}
   - How well the resume's content matches THIS SPECIFIC job description
     (skills, experience, keywords overlap).

3. {{"field": "missing_skills", "value": [<string>, <string>, ...]}}
   - A list of important skills/keywords from the job description that
     are missing or weak in the resume. 3-8 items. Empty list if none.

4. {{"field": "suggestions", "value": [<string>, <string>, ...]}}
   - 3-5 concrete, actionable suggestions to improve the resume for this
     specific job. Each suggestion should be a single sentence.

RULES:
- Output must be valid JSON per line — no trailing commas, no comments.
- Do not wrap the output in markdown code fences (no ```).
- Do not add any text before the first line or after the last line.
- Use double quotes for all JSON strings, never single quotes.

--- RESUME START ---
{resume_text}
--- RESUME END ---

--- JOB DESCRIPTION START ---
{job_description}
--- JOB DESCRIPTION END ---
"""
