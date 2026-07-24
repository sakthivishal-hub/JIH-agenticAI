from fastapi import APIRouter, Query

from app.services.hackathon_search_service import HackathonSearchService

router = APIRouter()


@router.get("/search")
def search_hackathons(q: str = Query("AI ML hackathon open registration", description="Search query for hackathons")):
    service = HackathonSearchService()
    return service.search_hackathons(query=q)
