"""Tests for CreativeIntelligenceAgent and LLM Model Gateway."""

import json
import pytest

from app.agents.creative.agent import CreativeIntelligenceAgent
from app.core.config import Settings
from app.core.exceptions import (
    AgentOutputValidationError,
    ProviderConfigError,
    ProviderTransientError,
)
from app.model_gateway.llm.base import LLMRequest, LLMTextResponse
from app.model_gateway.llm.factory import get_llm_provider
from app.model_gateway.llm.mock_provider import MockLLMProvider
from app.schemas.creative import CreativeBrief, VideoFormat


class _StubProvider:
    """Configurable stub LLMProvider for testing retries and error handling."""

    provider_name = "stub"
    is_mock = True

    def __init__(self, responses: list[str | Exception]) -> None:
        self._responses = list(responses)
        self.calls: list[LLMRequest] = []

    async def generate(self, request: LLMRequest) -> LLMTextResponse:
        self.calls.append(request)
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return LLMTextResponse(
            raw_text=item,
            provider_name=self.provider_name,
            model_name="stub-v1",
            is_mock=True,
        )


@pytest.mark.parametrize(
    "video_type",
    [
        VideoFormat.AD,
        VideoFormat.EXPLAINER,
        VideoFormat.SOCIAL,
        VideoFormat.PROMO,
        VideoFormat.SHORT_FILM,
        VideoFormat.BRAND_FILM,
        VideoFormat.CUSTOM,
    ],
)
def test_agent_with_mock_provider_supports_all_video_formats(video_type: VideoFormat) -> None:
    import asyncio

    agent = CreativeIntelligenceAgent(llm_provider=MockLLMProvider())
    brief = CreativeBrief(
        video_type=video_type,
        idea="Tell the story of an independent bookstore surviving a digital shift.",
        desired_duration_seconds=60,
    )

    result = asyncio.run(agent.run(brief))

    assert len(result.concepts) == 3
    assert len({c.id for c in result.concepts}) == 3
    assert len({c.title for c in result.concepts}) == 3
    assert result.recommended_concept_id in {c.id for c in result.concepts}
    assert result.direction.selected_concept_id == result.recommended_concept_id
    assert result.provider_name == "mock"
    assert result.is_mock is True


def test_agent_retries_and_recovers_from_invalid_model_response() -> None:
    import asyncio

    mock_valid = asyncio.run(
        MockLLMProvider().generate(
            LLMRequest(
                system_prompt="sys",
                user_prompt="usr",
                metadata={"video_type": "explainer", "idea_preview": "test"},
            )
        )
    ).raw_text

    # First response is invalid JSON, second response is fenced valid JSON
    stub = _StubProvider(["not valid json", f"```json\n{mock_valid}\n```"])
    agent = CreativeIntelligenceAgent(llm_provider=stub, max_retries=2)
    brief = CreativeBrief(idea="Explain quantum computing using everyday analogies.")

    result = asyncio.run(agent.run(brief))

    assert len(result.concepts) == 3
    assert len(stub.calls) == 2
    assert "failed schema validation" in stub.calls[1].user_prompt


def test_agent_raises_validation_error_when_retries_exhausted() -> None:
    import asyncio

    bad_payload = json.dumps({"concepts": [], "recommended_concept_id": "x"})
    stub = _StubProvider(["{broken", bad_payload, "{still broken"])
    agent = CreativeIntelligenceAgent(llm_provider=stub, max_retries=2)
    brief = CreativeBrief(idea="Create a short film about a lighthouse keeper.")

    with pytest.raises(AgentOutputValidationError):
        asyncio.run(agent.run(brief))

    assert len(stub.calls) == 3


def test_agent_propagates_provider_transient_error() -> None:
    import asyncio

    stub = _StubProvider([ProviderTransientError("Upstream timeout")])
    agent = CreativeIntelligenceAgent(llm_provider=stub)
    brief = CreativeBrief(idea="Create a 30-second promo for a community bike workshop.")

    with pytest.raises(ProviderTransientError):
        asyncio.run(agent.run(brief))


def test_factory_rejects_unknown_provider() -> None:
    settings = Settings(llm_provider="unknown_vendor")
    with pytest.raises(ProviderConfigError):
        get_llm_provider(settings)
