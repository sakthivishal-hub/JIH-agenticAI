import asyncio
import re
from typing import Dict, Any


class ResumeSummarizer:
    """
    Generates a concise summary from parsed resume data.
    This version works without an LLM and can later be
    upgraded to Gemini/Groq/OpenAI.
    """

    def summarize(self, resume_data: Dict[str, Any]) -> str:
        if not resume_data:
            return "No resume information available."

        name = resume_data.get("name", "Candidate")
        experience = resume_data.get("experience", [])
        education = resume_data.get("education", [])
        skills = resume_data.get("skills", [])
        projects = resume_data.get("projects", [])

        summary = []

        summary.append(f"{name} is a candidate with")

        if experience:
            summary.append(
                f"{len(experience)} professional experience(s)"
            )

        if education:
            summary.append(
                f"{len(education)} educational qualification(s)"
            )

        if skills:
            top_skills = ", ".join(skills[:8])
            summary.append(
                f"skills including {top_skills}"
            )

        if projects:
            summary.append(
                f"and {len(projects)} completed project(s)"
            )

        return " ".join(summary) + "."

    @staticmethod
    def summarize_text(text: str, max_sentences: int = 3, max_chars: int = 400) -> Dict[str, Any]:
        """Cheap extractive summary for opportunity descriptions. Kept
        non-LLM on purpose: recommender.py calls this once per candidate
        opportunity in the search pool, and the real AI scoring already
        happens once per item in matcher.py -- doubling that with a
        second Gemini call per item would burn quota for no real gain."""
        if not text or not text.strip():
            return {"summary": ""}

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        summary = " ".join(sentences[:max_sentences]).strip()
        if len(summary) > max_chars:
            summary = summary[:max_chars].rsplit(" ", 1)[0] + "..."
        return {"summary": summary}

    async def asummarize(self, text: str) -> Dict[str, Any]:
        """Async entrypoint expected by ai/recommender.py."""
        return await asyncio.to_thread(self.summarize_text, text)


summarizer = ResumeSummarizer()