# scoring.py
from datetime import datetime, timezone

def calculate_overall_score(scores: dict, schema: dict) -> tuple[int, float]:
    """Calculate weighted overall score from individual scores."""
    skill_weights = {s["name"]: s.get("weight", 1) for s in schema.get("skills", [])}
    soft_weights = {s["name"]: s.get("weight", 1) for s in schema.get("soft_skills", [])}

    total_weight = 0
    weighted_sum = 0

    for skill, value in scores.items():
        weight = skill_weights.get(skill) or soft_weights.get(skill) or 1
        total_weight += weight * 3  # max per skill (0–3)
        weighted_sum += weight * value

    if total_weight == 0:
        return 0, 0.0

    match_percent = weighted_sum / total_weight
    overall_score = int(round(match_percent * 100))
    return overall_score, match_percent


def score_resume(jd_text: str, schema: dict, resume_text: str, llm_client) -> dict:
    """
    Use Groq to score a single resume against the JD schema.
    """
    system_prompt = (
        "You are an expert technical recruiter. "
        "Given a job description, a scoring schema, and a resume, you assign skill scores. "
        "Always respond with a single valid JSON object."
    )

    user_prompt = f"""
You will score this candidate for the given role.

Job Description:
\"\"\"{jd_text}\"\"\"

Scoring schema (JSON):
{schema}

Resume:
\"\"\"{resume_text}\"\"\"

Your tasks:
1) Carefully read the full resume and identify the candidate's formal education.
2) Find the MAIN graduation degree (usually a Bachelor's, or the earliest full-time degree).
3) Extract the INSTITUTION/COLLEGE/UNIVERSITY name and the COMPLETION YEAR (4-digit).
4) If multiple degrees exist, choose the one that looks like the main undergraduate degree.
5) If the year is given as a range like "2010 - 2014", use the END year (e.g. 2014).
6) Only if you truly cannot find a year or institution, then use "" for grad_college and 0 for grad_year.


Return JSON with this exact structure:
{{
"candidate_name": string,        // if unsure, use empty string
"candidate_email": string,       // if unsure, use empty string

"grad_college": string,          // main graduation college/university, "" if you genuinely cannot find it
"grad_year": integer,            // 4-digit completion year of main graduation (e.g. 2012), or 0 if really unknown  
  
  "scores": {{
    "<skill_name>": integer        // for every skill and soft skill in schema, 0-3:
                                   // 0 = not present, 1 = basic, 2 = intermediate, 3 = strong
  }},
  "overall_score": integer,        // you may leave this as 0; it will be recomputed
  "match_percent": float,          // 0.0-1.0; you may leave as 0.0; will be recomputed
  "comments": string               // short summary (2-3 sentences) of the candidate fit
}}

Rules:
- Include a score entry for EVERY skill and soft skill in the schema, even if 0.
- Only score based on information in the resume; do not invent details.
- Education may appear in sections like "Education", "Academic Background", or inside a profile summary. Search the whole resume.
"""

    raw_result = llm_client.chat_json(system_prompt, user_prompt)

    scores = raw_result.get("scores", {})
    overall_score, match_percent = calculate_overall_score(scores, schema)

    result = {
        "candidate_name": raw_result.get("candidate_name", ""),
        "candidate_email": raw_result.get("candidate_email", ""),
        "grad_college": raw_result.get("grad_college", ""),
        "grad_year": raw_result.get("grad_year", 0),
        "scores": scores,
        "overall_score": overall_score,
        "match_percent": match_percent,
        "comments": raw_result.get("comments", ""),
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    return result
