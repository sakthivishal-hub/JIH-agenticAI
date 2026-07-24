"""
AI Opportunity Matcher.

Pipeline:

Resume JSON
        +
Opportunity
        ↓
Gemini
        ↓
Match Scores
        ↓
Normalized Result
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.ai.llm import llm, LLMError
from app.ai.prompts import match_prompt
from app.core.constants import AI_SCORE

logger = logging.getLogger(__name__)


_REQUIRED_KEYS = {
    *(k.lower() for k in AI_SCORE),
    "missing_skills",
    "strengths",
    "recommendation",
}

_LIST_KEYS = {
    "missing_skills",
    "strengths",
}


class MatcherError(Exception):
    """Raised when AI matching fails."""


class OpportunityMatcher:

    @staticmethod
    def _normalize_score(value: Any) -> int:
        """
        Convert score into an integer between 0 and 100.
        """
        try:
            score = int(float(value))
        except (TypeError, ValueError):
            return 0

        return max(0, min(score, 100))

    @classmethod
    def _normalize_response(cls, data: dict) -> dict:
        """
        Ensure downstream modules always receive
        a complete response.
        """

        normalized = {}

        for key in _REQUIRED_KEYS:

            if key in _LIST_KEYS:
                value = data.get(key)

                if isinstance(value, list):
                    normalized[key] = value
                else:
                    normalized[key] = []

                continue

            if key == "recommendation":
                normalized[key] = str(
                    data.get(key, "")
                )

                continue

            normalized[key] = cls._normalize_score(
                data.get(key)
            )

        return normalized

    @staticmethod
    def _weighted_score(scores: dict) -> int:
        """
        Calculate final weighted score using AI_SCORE.
        """

        total = 0

        for category, weight in AI_SCORE.items():

            total += (
                scores.get(category.lower(), 0)
                * weight
            )

        return round(total / 100)

    @classmethod
    def match(
        cls,
        resume: dict,
        opportunity: dict,
    ) -> dict:
        """
        Match a resume with an opportunity.
        """

        prompt = match_prompt(
            resume=str(resume),
            opportunity=str(opportunity),
        )

        try:
            response = llm.generate_json(prompt)

        except LLMError as exc:
            raise MatcherError(
                f"AI matching failed: {exc}"
            ) from exc

        response = cls._normalize_response(response)

        response["overall_score"] = cls._weighted_score(
            response
        )

        return response

    @classmethod
    async def amatch(
        cls,
        resume: dict,
        opportunity: dict,
    ) -> dict:
        """
        Async wrapper.
        """

        return await asyncio.to_thread(
            cls.match,
            resume,
            opportunity,
        )


matcher = OpportunityMatcher()