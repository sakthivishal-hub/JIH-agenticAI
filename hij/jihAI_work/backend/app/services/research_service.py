"""
Research Opportunities Service for JihAI Platform.
Uses Tavily to discover research positions, REU programs, and academic fellowships.
"""
from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class ResearchSearchService:

    RESEARCH_QUERIES = {
        "all": "undergraduate research internship positions open apply 2025",
        "ai": "artificial intelligence machine learning research positions undergraduate 2025",
        "biotech": "biotech biology biotechnology research internship positions 2025",
        "climate": "climate science environmental research fellowship internship 2025",
        "cs": "computer science HCI human computer interaction research positions 2025",
        "reu": "NSF REU Research Experience Undergraduates program open application 2025",
    }

    def search_research(self, topic: str = "all", custom_query: str | None = None) -> dict[str, Any]:
        """Search for research opportunities using Tavily."""
        if not settings.TAVILY_API_KEY:
            logger.warning("TAVILY_API_KEY not configured for research search")
            return {"results": [], "answer": "", "error": "Tavily API key not configured"}

        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            query = custom_query or self.RESEARCH_QUERIES.get(topic, self.RESEARCH_QUERIES["all"])

            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=12,
                include_answer=True,
                include_raw_content=False,
            )
            return {
                "results": response.get("results", []),
                "answer": response.get("answer", ""),
                "topic": topic,
            }
        except Exception as exc:
            logger.error("Research search failed: %s", exc)
            return {"results": [], "answer": "", "error": str(exc)}
