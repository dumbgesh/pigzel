"""API v1 router aggregation."""

from fastapi import APIRouter

from .creative import router as creative_router
from .health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(creative_router)
