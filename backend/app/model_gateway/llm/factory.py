"""Factory for resolving the configured LLM provider."""

from ...core.config import Settings
from ...core.exceptions import ProviderConfigError
from .base import LLMProvider
from .mock_provider import MockLLMProvider


def get_llm_provider(settings: Settings) -> LLMProvider:
    """Instantiate the configured LLM provider from application settings."""
    provider = settings.llm_provider.strip().lower()

    if provider == "mock":
        return MockLLMProvider(model_name=settings.llm_model)

    raise ProviderConfigError(
        f"Unsupported or unconfigured LLM provider '{settings.llm_provider}'. "
        "Set PIGZEL_LLM_PROVIDER=mock for local development/testing, or register "
        "a hosted/local provider adapter."
    )
