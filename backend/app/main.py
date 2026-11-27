"""FastAPI application entry point for Pigzel."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api.v1.router import api_v1_router
from .core.config import Settings, get_settings
from .core.exceptions import (
    AgentOutputValidationError,
    IngestionValidationError,
    ProviderConfigError,
    ProviderResponseError,
    ProviderTransientError,
)
from .core.logging import configure_logging

logger = logging.getLogger(__name__)


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(IngestionValidationError)
    async def handle_ingestion_error(_: Request, exc: IngestionValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(ProviderConfigError)
    async def handle_provider_config(_: Request, exc: ProviderConfigError) -> JSONResponse:
        logger.error("Provider configuration error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    @app.exception_handler(ProviderTransientError)
    async def handle_provider_transient(_: Request, exc: ProviderTransientError) -> JSONResponse:
        logger.warning("Transient provider failure: %s", exc)
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(ProviderResponseError)
    async def handle_provider_response(_: Request, exc: ProviderResponseError) -> JSONResponse:
        logger.error("Provider response error: %s", exc)
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(AgentOutputValidationError)
    async def handle_agent_validation(
        _: Request, exc: AgentOutputValidationError
    ) -> JSONResponse:
        logger.error("Agent output validation failure: %s", exc)
        return JSONResponse(status_code=502, content={"detail": str(exc)})


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the Pigzel FastAPI application."""
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)

    app = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.app_version,
        description="Open-source, modular AI-powered video production platform.",
    )

    if settings is not None:
        app.dependency_overrides[get_settings] = lambda: resolved_settings

    _register_exception_handlers(app)
    app.include_router(api_v1_router)
    return app


app = create_app()
