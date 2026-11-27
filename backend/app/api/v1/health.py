"""Health-check endpoint for API v1."""

from fastapi import APIRouter, Depends

from ...core.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Return service health and active configuration summary."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.env,
        "llm_provider": settings.llm_provider,
    }
