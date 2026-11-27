"""Tests for Stage 1 Pydantic v2 input and output schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.creative import (
    CreativeBrief,
    CreativeConcept,
    CreativeDirection,
    CreativeIntelligencePayload,
    VideoFormat,
)


def _make_concept(concept_id: str, title: str) -> CreativeConcept:
    return CreativeConcept(
        id=concept_id,
        title=title,
        core_idea="A clear, engaging central premise.",
        creative_approach="Visual storytelling with concise narration.",
        narrative_summary="Beginning introduces tension, middle resolves, end inspires.",
        target_audience="Tech-savvy creators",
        tone="Warm and confident",
        visual_direction="Natural daylight with clean medium shots.",
        key_message="Create more with less friction.",
        suggested_duration_seconds=45,
        reasoning="Matches the requested format and audience.",
    )


def _make_direction(selected_id: str = "concept_1") -> CreativeDirection:
    return CreativeDirection(
        selected_concept_id=selected_id,
        narrative_summary="Three-act micro-narrative.",
        pacing_guidance="Hook in 3 seconds, steady middle, crisp outro.",
        visual_guidelines="Warm daylight palette, 16:9 framing.",
        audio_guidelines="Clear voiceover with subtle ambient bed.",
        production_instructions=["Open with a human moment", "End with title card"],
    )


def test_minimal_valid_brief_allows_missing_optional_fields() -> None:
    brief = CreativeBrief(idea="Explain how solar microgrids help rural clinics.")
    assert brief.video_type == VideoFormat.CUSTOM
    assert brief.aspect_ratio == "16:9"
    assert brief.language == "en"
    assert brief.project_name is None
    assert brief.constraints == []
    assert brief.reference_materials == []


def test_full_brief_normalizes_whitespace_and_empty_list_items() -> None:
    brief = CreativeBrief(
        project_name="  Clinic Solar  ",
        video_type=VideoFormat.EXPLAINER,
        idea="  Show how modular solar microgrids keep clinic vaccines cold.  ",
        desired_duration_seconds=60,
        constraints=["  No jargon  ", "   ", ""],
        reference_materials=["  Brand guide v2  ", ""],
    )
    assert brief.project_name == "Clinic Solar"
    assert brief.video_type == VideoFormat.EXPLAINER
    assert brief.constraints == ["No jargon"]
    assert brief.reference_materials == ["Brand guide v2"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"idea": "   "},
        {"idea": "hi"},
        {"idea": "Valid idea for a short film.", "desired_duration_seconds": 0},
        {"idea": "Valid idea for a short film.", "desired_duration_seconds": -10},
        {"idea": "Valid idea for a short film.", "video_type": "invalid_format"},
    ],
)
def test_invalid_brief_raises_validation_error(kwargs: dict) -> None:
    with pytest.raises(ValidationError):
        CreativeBrief(**kwargs)


def test_payload_requires_exactly_three_unique_concepts_and_matching_recommendation() -> None:
    c1 = _make_concept("concept_1", "Angle One")
    c2 = _make_concept("concept_2", "Angle Two")
    c3 = _make_concept("concept_3", "Angle Three")

    valid = CreativeIntelligencePayload(
        concepts=[c1, c2, c3],
        recommended_concept_id="concept_1",
        recommendation_explanation="Strongest fit for the brief.",
        direction=_make_direction("concept_1"),
    )
    assert len(valid.concepts) == 3

    # Only 2 concepts -> invalid
    with pytest.raises(ValidationError):
        CreativeIntelligencePayload(
            concepts=[c1, c2],
            recommended_concept_id="concept_1",
            recommendation_explanation="Strongest fit.",
            direction=_make_direction("concept_1"),
        )

    # Duplicate titles (case-insensitive) -> invalid
    with pytest.raises(ValidationError):
        CreativeIntelligencePayload(
            concepts=[c1, _make_concept("concept_2", "angle one"), c3],
            recommended_concept_id="concept_1",
            recommendation_explanation="Strongest fit.",
            direction=_make_direction("concept_1"),
        )

    # Recommended ID not in concepts -> invalid
    with pytest.raises(ValidationError):
        CreativeIntelligencePayload(
            concepts=[c1, c2, c3],
            recommended_concept_id="concept_99",
            recommendation_explanation="Strongest fit.",
            direction=_make_direction("concept_99"),
        )

    # Direction selected_concept_id mismatch -> invalid
    with pytest.raises(ValidationError):
        CreativeIntelligencePayload(
            concepts=[c1, c2, c3],
            recommended_concept_id="concept_1",
            recommendation_explanation="Strongest fit.",
            direction=_make_direction("concept_2"),
        )
