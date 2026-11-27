"""Contract tests for Stage 2 Storyboard and ImageProvider schemas."""

import pytest
from pydantic import ValidationError

from app.model_gateway.image.base import ImageGenerationRequest, ImageProvider
from app.schemas.storyboard import Scene, Storyboard, VisualBible


def _make_scene(scene_id: str, order: int, duration: float = 5.0) -> Scene:
    return Scene(
        id=scene_id,
        order=order,
        duration_seconds=duration,
        description="Opening establishing shot of a sunlit workshop.",
        shot_type="wide",
        camera_movement="slow pan",
        lighting="warm morning daylight",
        environment="artisan woodworking studio",
        visual_prompt="Wide shot of a sunlit woodworking workshop, warm natural light.",
        audio_cue="Soft ambient room tone.",
    )


def test_storyboard_calculates_total_duration_and_validates_order() -> None:
    bible = VisualBible(
        style_summary="Warm documentary realism with natural daylight.",
        color_palette=["#D9A066", "#2B2D42"],
    )
    sb = Storyboard(
        id="sb_1",
        visual_bible=bible,
        scenes=[_make_scene("s1", 1, 4.5), _make_scene("s2", 2, 5.5)],
    )
    assert sb.total_estimated_duration_seconds == 10.0


def test_storyboard_rejects_non_sequential_order_and_duplicate_ids() -> None:
    bible = VisualBible(style_summary="Clean minimalist studio aesthetic.")

    with pytest.raises(ValidationError):
        Storyboard(
            id="sb_bad_order",
            visual_bible=bible,
            scenes=[_make_scene("s1", 1), _make_scene("s2", 3)],
        )

    with pytest.raises(ValidationError):
        Storyboard(
            id="sb_dup_id",
            visual_bible=bible,
            scenes=[_make_scene("s1", 1), _make_scene("s1", 2)],
        )


def test_image_generation_request_and_protocol_contract() -> None:
    req = ImageGenerationRequest(prompt="Sunlit ceramic studio with wheel", aspect_ratio="16:9")
    assert req.aspect_ratio == "16:9"
    assert hasattr(ImageProvider, "generate_image")
