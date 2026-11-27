"""Tests for Stage 1 Creative Intelligence prompt templates."""

from app.agents.creative.prompts import build_creative_intelligence_prompt
from app.schemas.creative import CreativeBrief, VideoFormat


def test_build_prompt_includes_optional_fields_and_sections() -> None:
    brief = CreativeBrief(
        project_name="Solar Microgrids",
        video_type=VideoFormat.EXPLAINER,
        idea="Show how solar microgrids keep rural clinics powered.",
        objective="Educate donors",
        target_audience="Healthcare NGOs",
        platform="YouTube",
        desired_duration_seconds=60,
        aspect_ratio="16:9",
        tone_and_style="Hopeful and clear",
        language="en",
        brand_or_product_info="SunGrid",
        constraints=["Avoid technical jargon"],
        reference_materials=["2025 Impact Report"],
    )

    prompt = build_creative_intelligence_prompt(brief)

    assert "Video Type: explainer" in prompt
    assert "Project Name: Solar Microgrids" in prompt
    assert "Constraints (must follow):" in prompt
    assert "- Avoid technical jargon" in prompt
    assert "Reference Materials (context):" in prompt
    assert "- 2025 Impact Report" in prompt


def test_build_prompt_appends_validation_error_on_retry() -> None:
    brief = CreativeBrief(idea="Short social teaser for a new coffee roast.")
    prompt = build_creative_intelligence_prompt(brief, validation_error="Expected 3 concepts")

    assert "failed schema validation" in prompt
    assert "Expected 3 concepts" in prompt
