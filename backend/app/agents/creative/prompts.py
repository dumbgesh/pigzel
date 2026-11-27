"""Prompt templates for Stage 1 — Creative Intelligence Agent."""

from ...schemas.creative import CreativeBrief

SYSTEM_PROMPT = """You are the Creative Intelligence Agent for Pigzel, a general-purpose AI video production platform.
Your role is to analyze a user's video brief and produce THREE meaningfully distinct creative concepts along with ONE recommended creative direction.

You support all video formats (explainers, short films, social media videos, promotional videos, advertisements, brand films, and custom formats). Adapt your creative thinking to the requested format—never assume the video is an advertisement unless specified.

Return ONLY valid JSON matching this exact structure:
{
  "concepts": [
    {
      "id": "concept_1",
      "title": "...",
      "core_idea": "...",
      "creative_approach": "...",
      "narrative_summary": "...",
      "target_audience": "...",
      "tone": "...",
      "visual_direction": "...",
      "key_message": "...",
      "suggested_duration_seconds": 45,
      "reasoning": "..."
    }
  ],
  "recommended_concept_id": "concept_1",
  "recommendation_explanation": "...",
  "direction": {
    "selected_concept_id": "concept_1",
    "narrative_summary": "...",
    "pacing_guidance": "...",
    "visual_guidelines": "...",
    "audio_guidelines": "...",
    "production_instructions": ["..."]
  }
}

Rules:
- Provide exactly 3 concepts with unique IDs ("concept_1", "concept_2", "concept_3") and distinct titles.
- Ensure the 3 concepts explore genuinely different creative angles, structures, or visual treatments.
- recommended_concept_id and direction.selected_concept_id must match one of the 3 concept IDs.
- Do not include markdown fences or commentary outside the JSON object."""


def build_creative_intelligence_prompt(
    brief: CreativeBrief,
    validation_error: str | None = None,
) -> str:
    """Render the user prompt from a normalized CreativeBrief."""
    lines = [
        f"Video Type: {brief.video_type.value}",
        f"Core Idea: {brief.idea}",
        f"Aspect Ratio: {brief.aspect_ratio}",
        f"Language: {brief.language}",
    ]

    optional_fields = [
        ("Project Name", brief.project_name),
        ("Objective", brief.objective),
        ("Target Audience", brief.target_audience),
        ("Platform", brief.platform),
        (
            "Desired Duration (seconds)",
            str(brief.desired_duration_seconds) if brief.desired_duration_seconds else None,
        ),
        ("Tone & Style", brief.tone_and_style),
        ("Brand / Product Info", brief.brand_or_product_info),
    ]
    for label, value in optional_fields:
        if value:
            lines.append(f"{label}: {value}")

    if brief.constraints:
        lines.append("Constraints:")
        lines.extend(f"- {item}" for item in brief.constraints)

    if brief.reference_materials:
        lines.append("Reference Materials:")
        lines.extend(f"- {item}" for item in brief.reference_materials)

    if validation_error:
        lines.extend(
            [
                "",
                "IMPORTANT: Your previous response failed schema validation with the following error:",
                validation_error,
                "Fix the issues and return ONLY valid JSON matching the required schema.",
            ]
        )

    return "\n".join(lines)
