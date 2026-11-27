"""Contract tests for Stage 3 Production schemas and provider/assembler interfaces."""

import pytest
from pydantic import ValidationError

from app.model_gateway.audio.base import AudioGenerationRequest, AudioProvider
from app.model_gateway.video.base import VideoGenerationRequest, VideoProvider
from app.production.assembler import MediaAssembler
from app.schemas.production import (
    AssetType,
    GeneratedAsset,
    GenerationJob,
    JobCapability,
    JobStatus,
    ProductionConfig,
)


def test_generation_job_and_asset_contracts() -> None:
    job = GenerationJob(
        id="job_1",
        project_version_id="ver_1",
        scene_id="scene_1",
        capability=JobCapability.VIDEO,
        provider="mock-video",
    )
    assert job.status == JobStatus.PENDING
    assert job.attempts == 0

    asset = GeneratedAsset(
        id="asset_1",
        project_version_id="ver_1",
        scene_id="scene_1",
        asset_type=AssetType.VIDEO_CLIP,
        uri="outputs/ver_1/scene_1.mp4",
        mime_type="video/mp4",
        duration_seconds=5.0,
    )
    assert asset.asset_type == AssetType.VIDEO_CLIP


def test_production_config_and_job_validation() -> None:
    cfg = ProductionConfig()
    assert cfg.fps == 24
    assert cfg.output_format == "mp4"

    with pytest.raises(ValidationError):
        GenerationJob(
            id="   ",
            project_version_id="ver_1",
            capability=JobCapability.AUDIO,
            provider="mock-audio",
        )


def test_video_audio_and_assembler_protocols_exist() -> None:
    v_req = VideoGenerationRequest(prompt="Sunlit coffee pour", duration_seconds=4.0)
    a_req = AudioGenerationRequest(prompt="Warm acoustic guitar", audio_kind="music")
    assert v_req.duration_seconds == 4.0
    assert a_req.audio_kind == "music"
    assert hasattr(VideoProvider, "generate_clip")
    assert hasattr(AudioProvider, "generate_audio")
    assert hasattr(MediaAssembler, "assemble")
