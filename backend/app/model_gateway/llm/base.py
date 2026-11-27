"""Provider-independent LLM gateway interfaces and request/response models."""

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    """Normalized text-generation request sent to an LLM provider."""

    system_prompt: str = Field(..., min_length=1)
    user_prompt: str = Field(..., min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    model: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class LLMTextResponse(BaseModel):
    """Normalized text-generation response returned by an LLM provider."""

    raw_text: str
    provider_name: str
    model_name: str
    is_mock: bool = False


@runtime_checkable
class LLMProvider(Protocol):
    """Common interface for all LLM providers (mock, hosted open-weight, local, proprietary)."""

    provider_name: str
    is_mock: bool

    async def generate(self, request: LLMRequest) -> LLMTextResponse:
        """Generate a text response for the given structured LLM request."""
        ...
