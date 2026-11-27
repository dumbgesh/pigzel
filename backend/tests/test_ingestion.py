"""Tests for CreativeBrief ingestion and normalization."""

from app.ingestion.brief_normalizer import normalize_brief
from app.schemas.creative import CreativeBrief


def test_normalize_brief_deduplicates_constraints_and_references() -> None:
    brief = CreativeBrief(
        idea="Create an explainer about urban composting.",
        constraints=["No jargon", "no jargon", "Keep under 60s"],
        reference_materials=["Brand guide", "brand guide", "Color palette PDF"],
    )

    normalized = normalize_brief(brief)

    assert normalized.constraints == ["No jargon", "Keep under 60s"]
    assert normalized.reference_materials == ["Brand guide", "Color palette PDF"]
    assert normalized is not brief
    assert len(brief.constraints) == 3
