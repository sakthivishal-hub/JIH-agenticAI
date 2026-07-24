from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class HackathonSearchService:

    def search_hackathons(self, query: str | None = None) -> dict[str, Any]:
        """Search for open hackathons using Tavily AI search."""
        if not settings.TAVILY_API_KEY:
            logger.warning("TAVILY_API_KEY not configured for hackathon search")
            return {"results": [], "answer": "", "error": "Tavily API key not configured"}

        default_query = """
        Find hackathons that are currently open for registration in 2025.
        Include: Artificial Intelligence, Machine Learning, Data Science,
        Python, Web Development, Cyber Security, Cloud Computing.
        Return only active hackathons with registration links.
        """
        search_query = query or default_query

        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            response = client.search(
                query=search_query,
                search_depth="advanced",
                max_results=10,
                include_answer=True,
                include_raw_content=False,
            )
            return response
        except Exception as exc:
            logger.error("Hackathon search failed: %s", exc)
            return {"results": [], "answer": "", "error": str(exc)}
