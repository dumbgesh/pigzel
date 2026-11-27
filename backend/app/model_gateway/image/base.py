"""Provider-independent image generation interface for Stage 2 visual references."""

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    """Normalized request for generating a visual reference or keyframe image."""

    prompt: str = Field(..., min_length=5, max_length=3000)
    aspect_ratio: str = Field(default="16:9", min_length=3, max_length=20)
    style_notes: str | None = Field(default=None, max_length=1000)
    seed: int | None = None


class ImageGenerationResponse(BaseModel):
    """Normalized response returned by an image generation provider."""

    asset_uri: str = Field(..., min_length=1)
    mime_type: str = Field(default="image/png")
    provider_name: str
    model_name: str
    is_mock: bool = False


@runtime_checkable
class ImageProvider(Protocol):
    """Common interface for image generation providers (planned for Milestone 3)."""

    provider_name: str
    is_mock: bool

    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate a single reference image from a structured request."""
        ...
