from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.resume import router as resume_router
from app.api.opportunities import router as opportunities_router
from app.api.recommendations import router as recommendations_router
from app.api.hackathons import router as hackathon_router

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