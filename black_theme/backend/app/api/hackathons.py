from fastapi import APIRouter

from app.services.hackathon_search_service import HackathonSearchService

router = APIRouter(prefix="/hackathons", tags=["Hackathons"])


@router.get("/search")
def search_hackathons():
    service = HackathonSearchService()

    return service.search_hackathons()