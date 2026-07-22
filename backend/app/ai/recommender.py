"""
AI Recommendation Engine.
Pipeline:
Resume
    ↓
Resume Parser
    ↓
Summarized Opportunities
    ↓
AI Matcher (concurrent, bounded)
    ↓
Rank Results
    ↓
Top Recommendations
"""
from __future__ import annotations

import asyncio
import logging
from copy import deepcopy
from typing import Any

from app.ai.matcher import matcher
from app.ai.summarizer import summarizer
from app.ai.llm import LLMError
from app.core.constants import AI_SCORE

logger = logging.getLogger(__name__)

# Caps how many opportunities get sent through the LLM matcher at once.
# Tune based on your Gemini rate limit -- too high risks 429s under load.
_MAX_CONCURRENT_MATCHES = 5


class RecommendationError(Exception):
    """Raised when recommendation generation fails entirely (e.g. bad
    resume input). Per-opportunity failures are logged and skipped,
    not raised here -- one bad listing shouldn't kill the whole batch."""


class RecommendationEngine:
    """Ranks opportunities against a resume using the AI matcher."""

    @staticmethod
    def _compute_overall_score(match: dict[str, Any]) -> float:
        """Computes the weighted overall score from AI_SCORE weights,
        rather than trusting the LLM to have included an 'overall_score'
        field itself -- the match_prompt schema doesn't ask for one, so
        we derive it deterministically from the sub-scores it does return."""
        total = 0.0
        for key, weight in AI_SCORE.items():
            sub_score = match.get(key.lower(), 0) or 0
            total += (sub_score / 100) * weight
        return round(total, 2)

    @staticmethod
    async def _prepare_opportunity(opportunity: dict[str, Any]) -> dict[str, Any]:
        """Converts a raw opportunity into summarized format if needed."""
        if "summary" in opportunity and opportunity["summary"]:
            return deepcopy(opportunity)
        text = opportunity.get("description", "")
        try:
            summary = await summarizer.asummarize(text)
        except LLMError as exc:
            logger.warning(
                "Summarization failed for opportunity id=%s, using raw description: %s",
                opportunity.get("id"), exc,
            )
            summary = {"summary": text[:300]}
        merged = deepcopy(opportunity)
        merged.update(summary)
        return merged

    @classmethod
    async def _score_one(
        cls,
        semaphore: asyncio.Semaphore,
        resume: dict[str, Any],
        opportunity: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Scores a single opportunity. Returns None (not raises) on
        failure so one bad item doesn't take down the whole batch."""
        async with semaphore:
            try:
                prepared = await cls._prepare_opportunity(opportunity)
                match = await matcher.amatch(resume, prepared)
            except LLMError as exc:
                logger.warning(
                    "Matching failed for opportunity id=%s, skipping: %s",
                    opportunity.get("id"), exc,
                )
                return None
            except Exception:
                logger.exception(
                    "Unexpected error scoring opportunity id=%s, skipping",
                    opportunity.get("id"),
                )
                return None

            return {
                **prepared,
                "match": match,
                "overall_score": cls._compute_overall_score(match),
            }

    @classmethod
    async def arecommend(
        cls,
        resume: dict[str, Any],
        opportunities: list[dict[str, Any]],
        *,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Scores opportunities concurrently (bounded by a semaphore to
        respect API rate limits), then ranks and returns the top_k."""
        if not resume:
            raise RecommendationError("Cannot generate recommendations without a parsed resume.")
        if not opportunities:
            return []

        semaphore = asyncio.Semaphore(_MAX_CONCURRENT_MATCHES)
        tasks = [cls._score_one(semaphore, resume, opp) for opp in opportunities]
        results = await asyncio.gather(*tasks)

        scored = [r for r in results if r is not None]
        if not scored and opportunities:
            logger.error("All %d opportunities failed to score.", len(opportunities))

        scored.sort(key=lambda item: item["overall_score"], reverse=True)
        return scored[:top_k]

    @classmethod
    def recommend(
        cls,
        resume: dict[str, Any],
        opportunities: list[dict[str, Any]],
        *,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Synchronous entrypoint for non-async call sites (scripts,
        scheduler jobs). FastAPI routes should call arecommend directly."""
        return asyncio.run(cls.arecommend(resume, opportunities, top_k=top_k))


recommender = RecommendationEngine