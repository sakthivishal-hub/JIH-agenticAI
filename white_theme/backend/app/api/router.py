from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.resume import router as resume_router
from app.api.opportunities import router as opportunities_router
from app.api.recommendations import router as recommendations_router
from app.api.hackathons import router as hackathon_router
from app.api.notifications import router as notifications_router
from app.api.bookmarks import router as bookmarks_router
from app.api.research import router as research_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])

api_router.include_router(auth_router)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    resume_router,
    prefix="/resume",
    tags=["Resume"]
)

api_router.include_router(
    opportunities_router,
    prefix="/opportunities",
    tags=["Opportunities"]
)

api_router.include_router(
    recommendations_router,
    prefix="/recommendations",
    tags=["Recommendations"]
)

api_router.include_router(
    hackathon_router,
    prefix="/hackathons",
    tags=["Hackathons"]
)

api_router.include_router(
    notifications_router,
    prefix="/notifications",
    tags=["Notifications"]
)

api_router.include_router(
    bookmarks_router,
    prefix="/bookmarks",
    tags=["Bookmarks"]
)

api_router.include_router(
    research_router,
    prefix="/research",
    tags=["Research"]
)