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


summarizer = ResumeSummarizer()