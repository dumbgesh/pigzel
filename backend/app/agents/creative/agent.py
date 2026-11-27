"""Stage 1 — Creative Intelligence Agent implementation."""

import json
import logging
import re

from pydantic import ValidationError

from ...core.exceptions import AgentOutputValidationError
from ...model_gateway.llm.base import LLMProvider, LLMRequest
from ...schemas.creative import (
    CreativeBrief,
    CreativeIntelligencePayload,
    CreativeIntelligenceResult,
)
from .prompts import SYSTEM_PROMPT, build_creative_intelligence_prompt

logger = logging.getLogger(__name__)

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```$", re.DOTALL | re.IGNORECASE)


def _extract_json_text(raw_text: str) -> str:
    """Strip optional markdown code fences around JSON responses."""
    cleaned = raw_text.strip()
    match = _CODE_FENCE_RE.match(cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


class CreativeIntelligenceAgent:
    """Generates three distinct creative concepts and a recommended direction from a brief."""

    def __init__(self, llm_provider: LLMProvider, max_retries: int = 2) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        self._llm = llm_provider
        self._max_retries = max_retries

    async def run(self, brief: CreativeBrief) -> CreativeIntelligenceResult:
        """Execute Stage 1 against the configured LLM provider and validate the output."""
        last_error: str | None = None
        idea_preview = brief.idea[:80].strip()

        metadata = {
            "video_type": brief.video_type.value,
            "aspect_ratio": brief.aspect_ratio,
            "language": brief.language,
            "idea_preview": idea_preview,
        }
        if brief.target_audience:
            metadata["target_audience"] = brief.target_audience
        if brief.tone_and_style:
            metadata["tone_and_style"] = brief.tone_and_style
        if brief.desired_duration_seconds is not None:
            metadata["desired_duration_seconds"] = str(brief.desired_duration_seconds)

        for attempt in range(self._max_retries + 1):
            user_prompt = build_creative_intelligence_prompt(brief, validation_error=last_error)
            request = LLMRequest(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.7,
                metadata=metadata,
            )

            response = await self._llm.generate(request)
            json_text = _extract_json_text(response.raw_text)

            try:
                raw_data = json.loads(json_text)
                payload = CreativeIntelligencePayload.model_validate(raw_data)
                return CreativeIntelligenceResult(
                    **payload.model_dump(),
                    provider_name=response.provider_name,
                    model_name=response.model_name,
                    is_mock=response.is_mock,
                )
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = str(exc)
                logger.warning(
                    "CreativeIntelligenceAgent validation failed (attempt %d/%d): %s",
                    attempt + 1,
                    self._max_retries + 1,
                    last_error,
                )

        raise AgentOutputValidationError(
            f"Creative Intelligence output failed validation after {self._max_retries + 1} "
            f"attempts: {last_error}"
        )
