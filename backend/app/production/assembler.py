"""Deterministic media assembly interface for Stage 3 final video export."""

from typing import Protocol, runtime_checkable

from ..schemas.production import GeneratedAsset, ProductionConfig


@runtime_checkable
class MediaAssembler(Protocol):
    """Contract for assembling scene clips and audio tracks into a final video."""

    async def assemble(
        self,
        *,
        project_version_id: str,
        clips: list[GeneratedAsset],
        audio_tracks: list[GeneratedAsset],
        config: ProductionConfig,
    ) -> GeneratedAsset:
        """Concatenate scene clips and mix audio tracks into an assembled video asset."""
        ...
