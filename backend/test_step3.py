from app.services.pdf_parser import extract_text_from_pdf
from app.utils.text_cleaning import clean_resume_text
from app.services.prompt_templates import build_analysis_prompt

with open("Resume1.pdf", "rb") as f:
    raw = extract_text_from_pdf(f.read())

cleaned = clean_resume_text(raw)
print("--- CLEANED RESUME TEXT ---")
print(cleaned)

prompt = build_analysis_prompt(cleaned, "Paste a sample job description here.")
print("\n--- FULL PROMPT ---")
print(prompt)