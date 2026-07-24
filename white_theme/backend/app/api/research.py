"""
Research Opportunities API endpoint.
Searches for research positions, REUs, and academic fellowships via Tavily.
"""
from fastapi import APIRouter, Query

from app.services.research_service import ResearchSearchService

router = APIRouter()


@router.get("/search")
def search_research(
    topic: str = Query("all", description="Research topic: all, ai, biotech, climate, cs, reu"),
    q: str | None = Query(None, max_length=200, description="Custom search query"),
):
    """Search for research opportunities using Tavily AI-powered search."""
    service = ResearchSearchService()
    return service.search_research(topic=topic, custom_query=q)
