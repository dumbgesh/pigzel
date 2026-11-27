"""Pydantic v2 contract schemas for Stage 3 — Video Production & Assembly."""

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class JobCapability(StrEnum):
    """Supported production job capabilities."""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ASSEMBLY = "assembly"


class JobStatus(StrEnum):
    """Lifecycle states for a GenerationJob."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AssetType(StrEnum):
    """Categories of generated media artifacts."""

    REFERENCE_IMAGE = "reference_image"
    VIDEO_CLIP = "video_clip"
    AUDIO_TRACK = "audio_track"
    ASSEMBLED_VIDEO = "assembled_video"


class ProductionConfig(BaseModel):
    """Export and rendering preferences for Stage 3."""

    aspect_ratio: str = Field(default="16:9", min_length=3, max_length=20)
    resolution: str = Field(default="1920x1080", min_length=3, max_length=30)
    fps: int = Field(default=24, gt=0, le=120)
    output_format: str = Field(default="mp4", min_length=2, max_length=10)


class GenerationJob(BaseModel):
    """A single unit of media generation or assembly work."""

    id: str = Field(..., min_length=1, max_length=64)
    project_version_id: str = Field(..., min_length=1, max_length=64)
    scene_id: str | None = Field(default=None, max_length=64)
    capability: JobCapability
    provider: str = Field(..., min_length=1, max_length=100)
    status: JobStatus = JobStatus.PENDING
    attempts: int = Field(default=0, ge=0)
    input_params: dict = Field(default_factory=dict)
    output_asset_id: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("id", "project_version_id", "provider")
    @classmethod
    def validate_non_empty(cls, value: str, info) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"{info.field_name} must not be empty.")
        return cleaned


class GeneratedAsset(BaseModel):
    """Metadata pointing to a stored media artifact produced by a GenerationJob."""

    id: str = Field(..., min_length=1, max_length=64)
    project_version_id: str = Field(..., min_length=1, max_length=64)
    scene_id: str | None = Field(default=None, max_length=64)
    asset_type: AssetType
    uri: str = Field(..., min_length=1, max_length=1000)
    mime_type: str = Field(..., min_length=3, max_length=100)
    duration_seconds: float | None = Field(default=None, gt=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
