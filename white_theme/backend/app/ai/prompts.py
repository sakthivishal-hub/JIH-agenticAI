"""
Centralized AI prompts for OpportunityOS.
Every AI feature imports prompts from here.
No prompt strings should be hardcoded elsewhere.

Prompts are built via functions, not .format() on raw strings --
the JSON schemas below contain literal braces that would collide
with str.format()'s placeholder syntax.
"""
import json

from app.utils.constants import AI_SCORE

SYSTEM_PROMPT = """You are OpportunityOS AI, an expert AI career advisor.
Always:
- Be accurate.
- Never hallucinate.
- Return valid JSON whenever requested, with no markdown fences or preamble.
- If information is missing, return null or an empty list -- never invent it.
- Never invent experience, education, or skills."""

_JSON_ONLY_INSTRUCTION = (
    "Return ONLY valid JSON matching the schema below. "
    "No preamble, no markdown code fences, no extra text."
)


# ==========================================================
# Resume Parser
# ==========================================================
_RESUME_SCHEMA = {
    "full_name": "", "email": "", "phone": "", "location": "",
    "linkedin": "", "github": "", "portfolio": "", "summary": "",
    "education": [{"degree": "", "institution": "", "year": "", "cgpa": ""}],
    "experience": [{"company": "", "role": "", "duration": "", "description": ""}],
    "projects": [{"title": "", "description": "", "technologies": []}],
    "skills": [], "certifications": [], "languages": [],
}


def resume_parser_prompt(resume_text: str) -> str:
    return (
        f"Extract the resume information below.\n\n{_JSON_ONLY_INSTRUCTION}\n"
        f"Schema:\n{json.dumps(_RESUME_SCHEMA, indent=2)}\n\n"
        f"Resume:\n{resume_text}"
    )


# ==========================================================
# Opportunity Matching
# Field names mirror AI_SCORE keys so matcher.py can consume the
# response directly without a renaming step.
# ==========================================================
_MATCH_SCHEMA = {
    **{k.lower(): 0 for k in AI_SCORE},  # skill_match, location_match, career_growth, roi, ...
    "missing_skills": [],
    "strengths": [],
    "recommendation": "",
}


def match_prompt(resume: str, opportunity: str) -> str:
    return (
        f"You are an AI opportunity-matching engine. Compare the resume "
        f"with the opportunity and score each category 0-100.\n\n"
        f"{_JSON_ONLY_INSTRUCTION}\nSchema:\n{json.dumps(_MATCH_SCHEMA, indent=2)}\n\n"
        f"Resume:\n{resume}\n\nOpportunity:\n{opportunity}"
    )


# ==========================================================
# Opportunity Summarizer
# ==========================================================
_SUMMARY_SCHEMA = {
    "title": "", "summary": "", "eligibility": "", "required_skills": [],
    "deadline": "", "location": "", "salary": "", "apply_link": "", "why_apply": "",
}


def summary_prompt(opportunity: str) -> str:
    return (
        f"Summarize the opportunity below.\n\n{_JSON_ONLY_INSTRUCTION}\n"
        f"Schema:\n{json.dumps(_SUMMARY_SCHEMA, indent=2)}\n\n"
        f"Opportunity:\n{opportunity}"
    )


# ==========================================================
# Cover Letter (prose output, not JSON -- correctly excluded above)
# ==========================================================
def cover_letter_prompt(resume: str, opportunity: str) -> str:
    return (
        f"Generate a professional, concise cover letter tailored to this "
        f"opportunity, based only on what's in the resume -- do not invent "
        f"experience.\n\nResume:\n{resume}\n\nOpportunity:\n{opportunity}"
    )


# ==========================================================
# Career Assistant (system-style prompt for a chat feature)
# ==========================================================
CAREER_ASSISTANT_PROMPT = """You are the OpportunityOS Career Assistant.
Help students with: jobs, internships, research, hackathons, resume
improvement, interview preparation, and career guidance.
Provide concise, practical, actionable advice."""