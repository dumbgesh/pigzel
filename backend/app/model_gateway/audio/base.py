"""Provider-independent audio and speech generation interface for Stage 3."""

from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class AudioGenerationRequest(BaseModel):
    """Normalized request for generating voiceover, SFX, or music."""

    prompt: str = Field(..., min_length=2, max_length=3000)
    audio_kind: Literal["voiceover", "sfx", "music"] = "voiceover"
    language: str = Field(default="en", min_length=2, max_length=20)
    duration_seconds: float | None = Field(default=None, gt=0, le=300)


class AudioGenerationResponse(BaseModel):
    """Normalized response returned by an audio generation provider."""

    asset_uri: str = Field(..., min_length=1)
    mime_type: str = Field(default="audio/wav")
    duration_seconds: float = Field(..., gt=0)
    provider_name: str
    model_name: str
    is_mock: bool = False


@runtime_checkable
class AudioProvider(Protocol):
    """Common interface for audio generation providers (planned for Milestone 4)."""

    provider_name: str
    is_mock: bool

    async def generate_audio(self, request: AudioGenerationRequest) -> AudioGenerationResponse:
        """Generate a voiceover, SFX, or music track."""
        ...
