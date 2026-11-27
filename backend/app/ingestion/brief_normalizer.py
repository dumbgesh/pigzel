"""Normalization utilities for incoming CreativeBrief payloads."""

from ..schemas.creative import CreativeBrief


def normalize_brief(brief: CreativeBrief) -> CreativeBrief:
    """Return a clean, normalized copy of a validated CreativeBrief.

    Pydantic field validators already strip strings and filter empty list items;
    this function provides an explicit ingestion boundary for future context
    enrichment (e.g., extracting text from uploaded reference files).
    """
    return brief.model_copy(deep=True)
