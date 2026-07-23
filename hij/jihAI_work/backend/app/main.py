from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.api.router import api_router
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
from app.core.middleware import register_middlewares

setup_logging()

app = FastAPI(
   debug=True,
   lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_middlewares(app)
register_exception_handlers(app)

app.include_router(api_router)


class HealthResponse(BaseModel):
    status: str


class RootResponse(BaseModel):
    message: str


@app.get("/", response_model=RootResponse)
async def root():
    return RootResponse(message="Welcome to OpportunityOS 🚀")


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="running")


_static_dir = Path(__file__).parent / "static"
if _static_dir.exists():
    app.mount("/app", StaticFiles(directory=str(_static_dir), html=True), name="frontend")