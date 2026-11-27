"""API integration tests for health and Stage 1 Creative Intelligence endpoints."""

from fastapi.testclient import TestClient

from app.api.v1.creative import get_creative_agent
from app.agents.creative.agent import CreativeIntelligenceAgent
from app.core.config import Settings
from app.core.exceptions import ProviderTransientError
from app.main import create_app
from app.model_gateway.llm.base import LLMRequest, LLMTextResponse


def _make_test_client() -> TestClient:
    settings = Settings(env="test", llm_provider="mock", log_level="WARNING")
    app = create_app(settings=settings)
    return TestClient(app)


def test_health_endpoint() -> None:
    client = _make_test_client()
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["llm_provider"] == "mock"


def test_generate_concepts_endpoint_with_minimal_brief() -> None:
    client = _make_test_client()
    response = client.post(
        "/api/v1/creative/concepts",
        json={"idea": "Explain how urban vertical farms save water."},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["concepts"]) == 3
    assert body["is_mock"] is True
    assert body["provider_name"] == "mock"
    assert body["recommended_concept_id"] == body["direction"]["selected_concept_id"]


def test_generate_concepts_endpoint_rejects_invalid_brief() -> None:
    client = _make_test_client()
    response = client.post(
        "/api/v1/creative/concepts",
        json={"idea": "  "},
    )
    assert response.status_code == 422


def test_generate_concepts_endpoint_returns_503_on_provider_failure() -> None:
    class _FailingProvider:
        provider_name = "failing"
        is_mock = True

        async def generate(self, request: LLMRequest) -> LLMTextResponse:
            raise ProviderTransientError("Rate limit exceeded")

    settings = Settings(env="test", llm_provider="mock", log_level="WARNING")
    app = create_app(settings=settings)
    app.dependency_overrides[get_creative_agent] = lambda: CreativeIntelligenceAgent(
        llm_provider=_FailingProvider()
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/creative/concepts",
        json={"idea": "A documentary-style look at night-shift bakers."},
    )
    assert response.status_code == 503
    assert "Rate limit exceeded" in response.json()["detail"]


def test_generate_concepts_endpoint_with_full_brief_and_deduplication() -> None:
    client = _make_test_client()
    response = client.post(
        "/api/v1/creative/concepts",
        json={
            "project_name": "Night Bakers",
            "video_type": "short_film",
            "idea": "Follow artisan bakers preparing bread before dawn.",
            "objective": "Showcase craftsmanship",
            "target_audience": "Food enthusiasts",
            "platform": "YouTube",
            "desired_duration_seconds": 90,
            "aspect_ratio": "16:9",
            "tone_and_style": "Warm and intimate",
            "language": "en",
            "constraints": ["No voiceover", "no voiceover"],
            "reference_materials": ["Moodboard v1"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["concepts"]) == 3
    assert "16:9" in body["direction"]["visual_guidelines"]
