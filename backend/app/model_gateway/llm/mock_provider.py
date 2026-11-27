"""Deterministic Mock LLM Provider for local development and testing without API keys."""

import json

from .base import LLMRequest, LLMTextResponse


class MockLLMProvider:
    """Mock LLM provider returning realistic, schema-valid creative concepts.

    Explicitly marks responses with `is_mock=True` so callers and tests never
    mistake mock output for real AI inference.
    """

    provider_name = "mock"
    is_mock = True

    def __init__(self, model_name: str = "mock-creative-v1") -> None:
        self._model_name = model_name

    async def generate(self, request: LLMRequest) -> LLMTextResponse:
        video_type = request.metadata.get("video_type", "custom")
        audience = request.metadata.get("target_audience") or "General digital viewers"
        tone = request.metadata.get("tone_and_style") or "Engaging and clear"
        duration = int(request.metadata.get("desired_duration_seconds") or 45)
        idea_preview = request.metadata.get("idea_preview") or "the user's core concept"

        payload = {
            "concepts": [
                {
                    "id": "concept_1",
                    "title": f"Story-First {video_type.replace('_', ' ').title()}",
                    "core_idea": (
                        f"Ground {idea_preview} in a relatable human moment before revealing "
                        "the central insight."
                    ),
                    "creative_approach": (
                        "Character-led narrative opening with an everyday tension, progressing "
                        "to a clear, emotionally resonant resolution."
                    ),
                    "narrative_summary": (
                        "Opens on a recognizable challenge, introduces the turning point at the "
                        "midpoint, and closes with a memorable takeaway."
                    ),
                    "target_audience": audience,
                    "tone": tone,
                    "visual_direction": (
                        "Warm natural lighting, handheld medium shots, and clean visual pacing "
                        "with minimal on-screen text."
                    ),
                    "key_message": f"Experience how {idea_preview} makes a tangible difference.",
                    "suggested_duration_seconds": duration,
                    "reasoning": (
                        "Narrative framing builds empathy early, making it versatile across "
                        f"{video_type} formats."
                    ),
                },
                {
                    "id": "concept_2",
                    "title": "Visual Metaphor & Kinetic Rhythm",
                    "core_idea": (
                        f"Translate {idea_preview} into a bold visual metaphor driven by "
                        "rhythmic editing and sound design."
                    ),
                    "creative_approach": (
                        "High-contrast graphic compositions and match-cut transitions that "
                        "turn abstract ideas into immediate visual clarity."
                    ),
                    "narrative_summary": (
                        "Establishes a visual motif in the first 5 seconds, escalates through "
                        "3 rhythmic beats, and lands on a crisp closing frame."
                    ),
                    "target_audience": audience,
                    "tone": f"Dynamic, {tone.lower()}",
                    "visual_direction": (
                        "Controlled studio lighting, bold color blocking, kinetic typography, "
                        "and precision match-cuts."
                    ),
                    "key_message": f"See {idea_preview} in a striking, unforgettable way.",
                    "suggested_duration_seconds": max(15, min(duration, 60)),
                    "reasoning": (
                        "Strong visual hooks capture attention rapidly and stand out in "
                        "competitive feeds."
                    ),
                },
                {
                    "id": "concept_3",
                    "title": "Documentary Micro-Breakdown",
                    "core_idea": (
                        f"Present {idea_preview} through an authentic, behind-the-scenes "
                        "explanatory lens."
                    ),
                    "creative_approach": (
                        "Direct, credible voiceover paired with observational B-roll and "
                        "annotated visual callouts."
                    ),
                    "narrative_summary": (
                        "Poses a clear opening question, walks step-by-step through the "
                        "evidence, and concludes with a practical summary."
                    ),
                    "target_audience": audience,
                    "tone": "Authentic, informative, and grounded",
                    "visual_direction": (
                        "Clean observational framing, subtle motion graphics, and balanced "
                        "daylight-inspired color grading."
                    ),
                    "key_message": f"Understand the real-world value behind {idea_preview}.",
                    "suggested_duration_seconds": duration,
                    "reasoning": (
                        "Structured clarity builds trust and works especially well when viewers "
                        "want substance over spectacle."
                    ),
                },
            ],
            "recommended_concept_id": "concept_1",
            "recommendation_explanation": (
                "Concept 1 balances emotional engagement with clarity, making it the strongest "
                f"default fit for the requested {video_type} format and target audience."
            ),
            "direction": {
                "selected_concept_id": "concept_1",
                "narrative_summary": (
                    "Three-act micro-structure: relatable opening hook, focused midpoint turn, "
                    "and concise closing takeaway."
                ),
                "pacing_guidance": (
                    f"Target ~{duration}s total runtime with an immediate hook in the first 3 "
                    "seconds and deliberate breathing room on the key message."
                ),
                "visual_guidelines": (
                    "Maintain consistent warm-natural color grading, medium-to-close framing for "
                    "subject connection, and uncluttered compositions."
                ),
                "audio_guidelines": (
                    "Clear, unhurried voiceover supported by subtle ambient music that swells "
                    "gently at the resolution."
                ),
                "production_instructions": [
                    "Establish the core subject and setting within the opening 3 seconds.",
                    "Keep scene transitions motivated by action or voiceover beats.",
                    "Reserve the final 4 seconds for the closing message and brand/title card.",
                ],
            },
        }

        return LLMTextResponse(
            raw_text=json.dumps(payload),
            provider_name=self.provider_name,
            model_name=request.model or self._model_name,
            is_mock=self.is_mock,
        )
