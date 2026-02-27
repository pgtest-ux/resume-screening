# jd_parser.py
from pathlib import Path
from docx import Document  # python-docx


def read_jd_text(jd_path: Path) -> str:
    """Read JD file (.txt or .docx)."""
    if not jd_path.exists():
        raise FileNotFoundError(f"JD file not found: {jd_path}")

    if jd_path.suffix.lower() == ".txt":
        return jd_path.read_text(encoding="utf-8")

    if jd_path.suffix.lower() == ".docx":
        doc = Document(jd_path)
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError(f"Unsupported JD format: {jd_path.suffix}")


def extract_scoring_schema(jd_text: str, llm_client) -> dict:
    """
    Use LLM (Groq) to parse JD and extract a scoring schema.
    """
    system_prompt = (
        "You are an assistant that extracts structured hiring criteria from job descriptions. "
        "Always respond with a single valid JSON object matching the requested schema."
    )

    user_prompt = f"""
Given the following Job Description, extract a scoring schema.

Return JSON with this exact structure:
{{
  "role_title": string,
  "role_level": string,  // e.g. "Junior", "Mid", "Senior", "Lead"
  "skills": [
    {{
      "name": string,              // e.g. "Python"
      "weight": integer,           // importance 1-3 (3 is most important)
      "years_expected": integer,   // typical years of experience expected, or 0 if not specified
      "level_expected": string     // e.g. "Junior", "Mid", "Senior", or "" if not specified
    }}
  ],
  "soft_skills": [
    {{
      "name": string,
      "weight": integer
    }}
  ],
  "education": string,
  "other_criteria": string
}}

Rules:
- Include 5-15 core technical skills that are clearly relevant.
- Use weight 3 for must-have skills, 2 for important, 1 for nice-to-have.
- If years of experience is not explicitly stated, estimate based on role_level.

Job Description:
\"\"\"{jd_text}\"\"\"
"""

    schema = llm_client.chat_json(system_prompt, user_prompt)
    return schema
