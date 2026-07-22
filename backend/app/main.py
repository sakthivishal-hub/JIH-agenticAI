from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.router import api_router

app = FastAPI(
   debug=True
   
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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