"""Normalization utilities for incoming CreativeBrief payloads."""

from ..schemas.creative import CreativeBrief


def _deduplicate_preserving_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def normalize_brief(brief: CreativeBrief) -> CreativeBrief:
    """Return a clean, normalized copy of a validated CreativeBrief.

    Deduplicates constraints and reference_materials (case-insensitive) while
    preserving order and leaving the input instance unmodified.
    """
    return brief.model_copy(
        update={
            "constraints": _deduplicate_preserving_order(brief.constraints),
            "reference_materials": _deduplicate_preserving_order(brief.reference_materials),
        },
        deep=True,
    )
