"""Provider-independent video generation interface for Stage 3."""

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class VideoGenerationRequest(BaseModel):
    """Normalized request for generating a scene video clip."""

    prompt: str = Field(..., min_length=5, max_length=3000)
    duration_seconds: float = Field(..., gt=0, le=60)
    aspect_ratio: str = Field(default="16:9", min_length=3, max_length=20)
    reference_image_uri: str | None = None
    seed: int | None = None


class VideoGenerationResponse(BaseModel):
    """Normalized response returned by a video generation provider."""

    asset_uri: str = Field(..., min_length=1)
    mime_type: str = Field(default="video/mp4")
    duration_seconds: float = Field(..., gt=0)
    provider_name: str
    model_name: str
    is_mock: bool = False


@runtime_checkable
class VideoProvider(Protocol):
    """Common interface for video generation providers (planned for Milestone 4)."""

    provider_name: str
    is_mock: bool

    async def generate_clip(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """Generate a single scene video clip from a structured request."""
        ...
